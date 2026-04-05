"""玩家与背包测试。"""

from __future__ import annotations

from game.inventory import InventoryItem, ItemCategory
from game.player import Player, Profession, item_healing_potion


def test_level_up() -> None:
    p = Player.create("勇者", Profession.WARRIOR)
    msgs = p.gain_xp(500)
    assert p.level >= 2
    assert isinstance(msgs, list)


def test_visible_equipment_line() -> None:
    p = Player.create("测试", Profession.WARRIOR)
    p.equipped_weapon_id = "rusty_sword"
    text = p.visible_equipment_for_npc()
    assert "生锈" in text or "武器" in text


def test_player_gender_roundtrip_dict() -> None:
    p = Player.create("a", Profession.BARD, gender="非二元")
    d = p.to_dict()
    p2 = Player.from_dict(d)
    assert p2.gender == "非二元"


def test_old_save_defaults_gender() -> None:
    p = Player.create("a", Profession.WARRIOR)
    d = p.to_dict()
    del d["gender"]
    p2 = Player.from_dict(d)
    assert p2.gender == "未指定"


def test_inventory_and_potion() -> None:
    p = Player.create("盗贼", Profession.ROGUE)
    p.inventory.add_item(item_healing_potion())
    p.take_damage(50)
    hp_after_damage = p.hp
    err = p.use_consumable("healing_potion")
    assert err is None
    assert p.hp > hp_after_damage
