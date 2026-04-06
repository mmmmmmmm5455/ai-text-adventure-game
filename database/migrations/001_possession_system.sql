-- 夺舍系统数据库 Schema
-- 版本: 1.0.0
-- PostgreSQL 11+（触发器使用 EXECUTE PROCEDURE；14+ 亦可写成 EXECUTE FUNCTION）
--
-- 依赖: gen_random_uuid() 需 pgcrypto
--   CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 用户表扩展
ALTER TABLE players ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT TRUE;
ALTER TABLE players ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE;

-- 夺舍快照表 (Possession Snapshots)
CREATE TABLE IF NOT EXISTS possession_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,

    character_json JSONB NOT NULL,
    character_name VARCHAR(255) NOT NULL,
    character_level INTEGER NOT NULL DEFAULT 1,
    character_bg_name VARCHAR(255),
    character_hp INTEGER NOT NULL DEFAULT 100,
    character_max_hp INTEGER NOT NULL DEFAULT 100,

    snapshot_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    recent_events JSONB DEFAULT '[]'::jsonb,
    last_words TEXT,
    snapshot_label VARCHAR(255),
    playtime_minutes INTEGER DEFAULT 0,

    game_chapter INTEGER DEFAULT 1,
    current_scene_id VARCHAR(255),

    is_claimed BOOLEAN DEFAULT FALSE,
    claimed_by UUID DEFAULT NULL REFERENCES players(player_id),
    claimed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshots_player_id ON possession_snapshots(player_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_unclaimed ON possession_snapshots(is_claimed) WHERE is_claimed = FALSE;
CREATE INDEX IF NOT EXISTS idx_snapshots_claimed_by ON possession_snapshots(claimed_by) WHERE claimed_by IS NOT NULL;

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_snapshots_updated ON possession_snapshots;
CREATE TRIGGER trigger_snapshots_updated
    BEFORE UPDATE ON possession_snapshots
    FOR EACH ROW
    EXECUTE PROCEDURE update_modified_column();

-- 夺舍历史记录表
CREATE TABLE IF NOT EXISTS possession_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_snapshot_id UUID NOT NULL REFERENCES possession_snapshots(snapshot_id) ON DELETE CASCADE,
    claimant_id UUID NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    inheritance_items JSONB DEFAULT '[]'::jsonb,
    new_player_name VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_possession_history_host ON possession_history(host_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_possession_history_claimant ON possession_history(claimant_id);

-- 存储过程: 创建快照
CREATE OR REPLACE FUNCTION create_possession_snapshot(
    p_player_id UUID,
    p_character_json JSONB,
    p_character_name VARCHAR,
    p_character_level INTEGER,
    p_character_bg_name VARCHAR,
    p_character_hp INTEGER,
    p_character_max_hp INTEGER,
    p_recent_events JSONB DEFAULT '[]'::jsonb,
    p_last_words TEXT DEFAULT NULL,
    p_playtime_minutes INTEGER DEFAULT 0,
    p_game_chapter INTEGER DEFAULT 1,
    p_current_scene_id VARCHAR DEFAULT NULL,
    p_snapshot_label VARCHAR DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_snapshot_id UUID;
BEGIN
    INSERT INTO possession_snapshots (
        player_id, character_json, character_name, character_level,
        character_bg_name, character_hp, character_max_hp,
        recent_events, last_words, playtime_minutes,
        game_chapter, current_scene_id, snapshot_label
    ) VALUES (
        p_player_id, p_character_json, p_character_name, p_character_level,
        p_character_bg_name, p_character_hp, p_character_max_hp,
        p_recent_events, p_last_words, p_playtime_minutes,
        p_game_chapter, p_current_scene_id, p_snapshot_label
    ) RETURNING snapshot_id INTO v_snapshot_id;

    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;

-- 存储过程: 执行夺舍
CREATE OR REPLACE FUNCTION claim_possession(
    p_snapshot_id UUID,
    p_claimant_id UUID,
    p_new_name VARCHAR
) RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    inherited_items JSONB
) AS $$
DECLARE
    v_is_claimed BOOLEAN;
    v_player_id UUID;
    v_inherited_items JSONB;
    v_items JSONB;
BEGIN
    SELECT ps.is_claimed, ps.player_id
    INTO v_is_claimed, v_player_id
    FROM possession_snapshots ps
    WHERE ps.snapshot_id = p_snapshot_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, '快照不存在'::TEXT, '[]'::JSONB;
        RETURN;
    END IF;

    IF v_is_claimed THEN
        RETURN QUERY SELECT FALSE, '该角色已被夺舍'::TEXT, '[]'::JSONB;
        RETURN;
    END IF;

    IF v_player_id = p_claimant_id THEN
        RETURN QUERY SELECT FALSE, '不能夺舍自己的角色'::TEXT, '[]'::JSONB;
        RETURN;
    END IF;

    SELECT COALESCE(ps.character_json->'inventory'->'items', '[]'::jsonb)
    INTO v_items
    FROM possession_snapshots ps
    WHERE ps.snapshot_id = p_snapshot_id;

    SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb)
    INTO v_inherited_items
    FROM jsonb_array_elements(COALESCE(v_items, '[]'::jsonb)) AS elem
    WHERE COALESCE(elem->>'category', '') NOT IN ('QUEST', '任务物品', 'CONSUMABLE', '消耗品');

    IF v_inherited_items IS NULL THEN
        v_inherited_items := '[]'::jsonb;
    END IF;

    UPDATE possession_snapshots
    SET is_claimed = TRUE,
        claimed_by = p_claimant_id,
        claimed_at = NOW()
    WHERE snapshot_id = p_snapshot_id;

    INSERT INTO possession_history (
        host_snapshot_id, claimant_id, inheritance_items, new_player_name
    ) VALUES (
        p_snapshot_id, p_claimant_id, v_inherited_items, p_new_name
    );

    RETURN QUERY SELECT TRUE, '夺舍成功'::TEXT, v_inherited_items;
END;
$$ LANGUAGE plpgsql;
