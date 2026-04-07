"""页面级 UI 片段（由 app 手动加载；目录勿命名为 pages，以免与 Streamlit 多页面冲突）。"""

from frontend.screen.character_creation import render_character_creation_ui
from frontend.screen.player_profile import render_profile_card, render_profile_summary, render_profile_comparison
from frontend.screen.snapshot_preview import (
    render_snapshot_preview,
    render_snapshot_summary,
    render_snapshot_comparison,
    render_snapshot_list
)
from frontend.screen.possession_history import (
    render_possession_history,
    render_possession_summary,
    render_possession_statistics,
    render_possession_timeline,
    render_possession_comparison
)
from frontend.screen.character_preview import (
    render_character_preview_sidebar,
    render_preview_comparison,
    CharacterPreviewState
)

__all__ = [
    "render_character_creation_ui",
    "render_profile_card",
    "render_profile_summary",
    "render_profile_comparison",
    "render_snapshot_preview",
    "render_snapshot_summary",
    "render_snapshot_comparison",
    "render_snapshot_list",
    "render_possession_history",
    "render_possession_summary",
    "render_possession_statistics",
    "render_possession_timeline",
    "render_possession_comparison",
    "render_character_preview_sidebar",
    "render_preview_comparison",
    "CharacterPreviewState",
]
