"""
场景定义：场景 ID、名称、描述模板、可前往的出口。
"""

from __future__ import annotations

from dataclasses import dataclass

from core.narrative_language import get_narrative_language


@dataclass(frozen=True)
class Scene:
    scene_id: str
    name: str
    description: str
    exits: tuple[str, ...]


SCENES: dict[str, Scene] = {
    "village_square": Scene(
        scene_id="village_square",
        name="村庄广场",
        description="石板铺就的小广场，中央有一口老井，村民三三两两低声交谈。",
        exits=("misty_forest", "mountain_foot", "tavern"),
    ),
    "misty_forest": Scene(
        scene_id="misty_forest",
        name="迷雾森林",
        description="雾气在树梢间流动，远处传来不自然的嗡鸣，仿佛森林本身在呼吸。",
        exits=("village_square", "ancient_mountains", "mysterious_cave"),
    ),
    "ancient_mountains": Scene(
        scene_id="ancient_mountains",
        name="古老山脉",
        description="陡峭的山路与风化岩壁，矿工的营地散落其间，风中带着金属与尘土的气息。",
        exits=("misty_forest", "underground_ruins"),
    ),
    "mountain_foot": Scene(
        scene_id="mountain_foot",
        name="山脚地带",
        description="通往山脉与村庄之间的缓坡，商队的车辙印深深碾过泥土。",
        exits=("village_square", "ancient_mountains"),
    ),
    "tavern": Scene(
        scene_id="tavern",
        name="山脚旅店",
        description="温暖的炉火与麦酒香气，旅人在这里交换传闻与路线。",
        exits=("village_square", "misty_forest"),
    ),
    "mysterious_cave": Scene(
        scene_id="mysterious_cave",
        name="神秘洞穴",
        description="洞口刻着模糊的符文，阴冷气息涌出，似乎与森林异象相连。",
        exits=("misty_forest", "underground_ruins"),
    ),
    "underground_ruins": Scene(
        scene_id="underground_ruins",
        name="地下遗迹",
        description="坍塌的走廊与古老机关，深处或许藏着封印与真相。",
        exits=("ancient_mountains", "mysterious_cave"),
    ),
}


def get_scene(scene_id: str) -> Scene | None:
    return SCENES.get(scene_id)


_SCENE_NAME_EN: dict[str, str] = {
    "village_square": "Village Square",
    "misty_forest": "Misty Forest",
    "ancient_mountains": "Ancient Mountains",
    "mountain_foot": "Mountain Foot",
    "tavern": "Foothill Tavern",
    "mysterious_cave": "Mysterious Cave",
    "underground_ruins": "Underground Ruins",
}

_SCENE_DESC_EN: dict[str, str] = {
    "village_square": "A stone square with an old well at its center; villagers speak in low voices.",
    "misty_forest": "Mist drifts between treetops and an unnatural hum pulses in the distance.",
    "ancient_mountains": "Steep paths and weathered cliffs; miners' camps dot the windy heights.",
    "mountain_foot": "A gentle slope between village and mountains, marked by caravan wheel tracks.",
    "tavern": "Warm firelight and ale scent; travelers trade rumors and routes here.",
    "mysterious_cave": "Blurred runes mark the entrance, and a cold breath spills from within.",
    "underground_ruins": "Collapsed corridors and old mechanisms hide seals and truth in the depths.",
}


def scene_name(scene_id: str) -> str:
    s = get_scene(scene_id)
    if not s:
        return "Unknown place" if get_narrative_language() == "en" else "未知之地"
    if get_narrative_language() == "en":
        return _SCENE_NAME_EN.get(scene_id, s.name)
    return s.name


def scene_description(scene_id: str) -> str:
    s = get_scene(scene_id)
    if not s:
        return ""
    if get_narrative_language() == "en":
        return _SCENE_DESC_EN.get(scene_id, s.description)
    return s.description
