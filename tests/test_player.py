"""玩家与背包测试。"""

from __future__ import annotations

from game.inventory import InventoryItem, ItemCategory
from game.player import Player, Profession, item_healing_potion


def test_level_up() -> None:
    p = Player.create("勇者", Profession.WARRIOR)
    msgs = p.gain_xp(500)
    assert p.level >= 2
    assert isinstance(msgs, list)


def test_inventory_and_potion() -> None:
    p = Player.create("盗贼", Profession.ROGUE)
    p.inventory.add_item(item_healing_potion())
    p.take_damage(50)
    hp_after_damage = p.hp
    err = p.use_consumable("healing_potion")
    assert err is None
    assert p.hp > hp_after_damage
