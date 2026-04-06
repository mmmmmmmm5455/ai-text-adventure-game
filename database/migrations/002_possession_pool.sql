-- 奪舍 / 快照池 Schema（與 database/possession_db.py 對齊）
-- PostgreSQL 14+（觸發器使用 EXECUTE FUNCTION）。新裝環境請用本檔。
-- 注意：migrations/001_possession_system.sql 為舊版（possession_snapshots 表名），
--       請勿與本檔在同一資料庫重複套用，除非先做資料遷移。

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE TABLE IF NOT EXISTS players (
    player_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username        VARCHAR(64)  NOT NULL UNIQUE,
    display_name    VARCHAR(64)  NOT NULL,
    password_hash   VARCHAR(256) NOT NULL,
    email           VARCHAR(256),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    is_banned       BOOLEAN      NOT NULL DEFAULT FALSE,
    is_public       BOOLEAN      NOT NULL DEFAULT TRUE,
    privacy_opt_out BOOLEAN      NOT NULL DEFAULT FALSE,
    is_deleted      BOOLEAN      NOT NULL DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_players_username ON players USING btree (username);
CREATE INDEX IF NOT EXISTS idx_players_public  ON players USING btree (is_public) WHERE is_public = TRUE;

CREATE TABLE IF NOT EXISTS player_snapshots (
    snapshot_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id            UUID        NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    snapshot_label       VARCHAR(128),
    snapshot_time        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    character_json       JSONB       NOT NULL,
    character_name       VARCHAR(64) NOT NULL,
    character_level      SMALLINT    NOT NULL DEFAULT 1,
    character_bg_name    VARCHAR(64),
    character_hp         SMALLINT,
    character_max_hp     SMALLINT,
    recent_events        JSONB       NOT NULL DEFAULT '[]',
    last_words           TEXT,
    game_chapter         SMALLINT    DEFAULT 1,
    playtime_minutes     INTEGER     DEFAULT 0,
    is_claimed           BOOLEAN     NOT NULL DEFAULT FALSE,
    claimed_by_player_id UUID        REFERENCES players(player_id),
    claimed_at           TIMESTAMPTZ,
    is_deleted           BOOLEAN     NOT NULL DEFAULT FALSE,
    deleted_at           TIMESTAMPTZ,
    tags                 TEXT[]      DEFAULT '{}',
    CONSTRAINT no_self_claim CHECK (
        player_id IS DISTINCT FROM claimed_by_player_id OR claimed_by_player_id IS NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_snapshots_player ON player_snapshots USING btree (player_id) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_snapshots_public ON player_snapshots USING btree (is_claimed, snapshot_time DESC)
    WHERE is_deleted = FALSE AND is_claimed = FALSE;
CREATE INDEX IF NOT EXISTS idx_snapshots_claimed_by ON player_snapshots USING btree (claimed_by_player_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_name_trgm ON player_snapshots USING gin (character_name gin_trgm_ops) WHERE is_deleted = FALSE;

CREATE TABLE IF NOT EXISTS snapshot_events (
    event_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_id   UUID        NOT NULL REFERENCES player_snapshots(snapshot_id) ON DELETE CASCADE,
    event_index   SMALLINT    NOT NULL,
    event_type    VARCHAR(64)  NOT NULL,
    event_summary TEXT         NOT NULL,
    scene_id      VARCHAR(128),
    round_count   INTEGER,
    metadata      JSONB       NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_snapshot ON snapshot_events USING btree (snapshot_id, event_index);
CREATE INDEX IF NOT EXISTS idx_events_type ON snapshot_events USING btree (event_type);

CREATE TABLE IF NOT EXISTS possession_records (
    record_id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    host_snapshot_id    UUID        REFERENCES player_snapshots(snapshot_id) ON DELETE SET NULL,
    host_player_id      UUID        REFERENCES players(player_id),
    possessor_player_id UUID        NOT NULL REFERENCES players(player_id),
    possessor_new_character_id UUID,
    possessed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    continuation_count  SMALLINT    NOT NULL DEFAULT 0,
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_possessions_possessor ON possession_records USING btree (possessor_player_id);
CREATE INDEX IF NOT EXISTS idx_possessions_host ON possession_records USING btree (host_player_id);

CREATE TABLE IF NOT EXISTS snapshot_schedule_log (
    log_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id    UUID        NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    executed_at  TIMESTAMPTZ,
    status       VARCHAR(32)  NOT NULL DEFAULT 'pending',
    snapshot_id  UUID        REFERENCES player_snapshots(snapshot_id),
    error_msg    TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schedule_log_player ON snapshot_schedule_log USING btree (player_id, scheduled_at DESC);

CREATE OR REPLACE FUNCTION update_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE players SET last_active_at = NOW() WHERE player_id = NEW.player_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_last_active ON player_snapshots;
CREATE TRIGGER trg_update_last_active
AFTER INSERT OR UPDATE ON player_snapshots
FOR EACH ROW EXECUTE PROCEDURE update_last_active();

CREATE OR REPLACE VIEW view_claimable_snapshots AS
SELECT
    s.snapshot_id,
    s.character_name,
    s.character_level,
    s.character_bg_name,
    s.character_hp,
    s.character_max_hp,
    s.snapshot_time,
    s.last_words,
    s.recent_events,
    s.game_chapter,
    s.playtime_minutes,
    p.display_name AS host_display_name,
    p.username AS host_username,
    s.snapshot_label
FROM player_snapshots s
JOIN players p ON p.player_id = s.player_id
WHERE s.is_deleted = FALSE
  AND s.is_claimed = FALSE
  AND p.is_public = TRUE
  AND p.is_banned = FALSE
  AND p.privacy_opt_out = FALSE
  AND p.is_deleted = FALSE
ORDER BY s.snapshot_time DESC;
