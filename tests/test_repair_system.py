"""修理系統單元測試"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from game.inventory import Inventory, InventoryItem, ItemCategory
from game.player import Profession
from game.repair_system import (
    ConditionNotMet,
    InsufficientGold,
    InsufficientMaterials,
    ItemNotBroken,
    ItemNotRepairable,
    RepairConfig,
    RepairContext,
    RepairError,
    RepairMethod,
    RepairOutcome,
    RepairReceipt,
    RepairResult,
    RepairSystem,
    attempt_equipped_repair,
    can_npc_repair_here,
    ensure_durability,
    get_equipped_item,
    load_repair_config,
)
from story.world_config import new_game_state


# ---------------------------------------------------------------------------
# 測試數據準備
# ---------------------------------------------------------------------------


def make_inventory(with_materials: bool = False, with_enchanted_dust: bool = False) -> Inventory:
    inv = Inventory(max_slots=20)
    inv.add_item(
        InventoryItem(
            item_id="rusty_sword",
            name="生鏽的鐵劍",
            category=ItemCategory.WEAPON,
            quantity=1,
            current_durability=10,
            max_durability=50,
            dimensional_origin="normal",
        )
    )
    inv.add_item(
        InventoryItem(
            item_id="leather_armor",
            name="皮甲",
            category=ItemCategory.ARMOR,
            quantity=1,
            current_durability=60,
            max_durability=80,
            dimensional_origin="normal",
        )
    )
    inv.add_item(
        InventoryItem(
            item_id="healing_potion",
            name="治療藥水",
            category=ItemCategory.CONSUMABLE,
            quantity=3,
        )
    )
    if with_materials:
        inv.add_item(
            InventoryItem(
                item_id="metal_scraps",
                name="金屬碎片",
                category=ItemCategory.MISC,
                quantity=5,
            )
        )
        inv.add_item(
            InventoryItem(
                item_id="leather_pieces",
                name="皮革碎片",
                category=ItemCategory.MISC,
                quantity=3,
            )
        )
    if with_enchanted_dust:
        inv.add_item(
            InventoryItem(
                item_id="enchanted_dust",
                name="附魔粉",
                category=ItemCategory.MISC,
                quantity=2,
            )
        )
    return inv


def make_player(
    is_mancelled: bool = False,
    hp: int = 80,
    gold: int = 200,
    intelligence: int = 10,
    traits=None,
    dimensional_rift_charges: int = 2,
    profession: str = "WARRIOR",
    dimensional_fragments: int = 1,
) -> dict:
    return {
        "name": "阿克",
        "level": 5,
        "hp": hp,
        "max_hp": 100,
        "gold": gold,
        "intelligence": intelligence,
        "traits": traits or [],
        "is_mancelled": is_mancelled,
        "dimensional_rift_charges": dimensional_rift_charges,
        "profession": profession,
        "dimensional_fragments": dimensional_fragments,
    }


def make_rs(with_materials: bool = False, with_enchanted_dust: bool = False):
    inv = make_inventory(with_materials=with_materials, with_enchanted_dust=with_enchanted_dust)
    player = make_player()
    return RepairSystem(player, inv), player, inv


# ---------------------------------------------------------------------------
# InventoryItem 耐久度方法測試
# ---------------------------------------------------------------------------


class TestInventoryItemDurability:
    def test_is_durable(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=30,
            max_durability=50,
        )
        assert item.is_durable is True

    def test_is_not_durable_consumable(self) -> None:
        item = InventoryItem(item_id="potion", name="藥水", category=ItemCategory.CONSUMABLE)
        assert item.is_durable is False

    def test_is_broken_when_zero(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=0,
            max_durability=50,
        )
        assert item.is_broken is True

    def test_durability_ratio(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=25,
            max_durability=50,
        )
        assert item.durability_ratio == 0.5

    def test_damage_decrements(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=10,
            max_durability=50,
        )
        broke = item.damage(3)
        assert item.current_durability == 7
        assert broke is False

    def test_damage_to_zero_triggers_broken(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=2,
            max_durability=50,
        )
        broke = item.damage(3)
        assert item.current_durability == 0
        assert broke is True
        assert item.is_broken is True

    def test_repair_restores_durability(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=10,
            max_durability=50,
        )
        actual = item.repair(20)
        assert actual == 20
        assert item.current_durability == 30

    def test_repair_cannot_exceed_max(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=45,
            max_durability=50,
        )
        actual = item.repair(20)
        assert actual == 5
        assert item.current_durability == 50

    def test_repair_nondurable_returns_zero(self) -> None:
        item = InventoryItem(
            item_id="potion",
            name="藥水",
            category=ItemCategory.CONSUMABLE,
        )
        actual = item.repair(10)
        assert actual == 0

    def test_durability_status_labels(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=10,
            max_durability=50,
        )
        assert "嚴重損壞" in item.durability_status()
        item.current_durability = 0
        assert "已損壞" in item.durability_status()
        item.current_durability = 50
        assert "完好" in item.durability_status()

    def test_to_dict_includes_durability(self) -> None:
        item = InventoryItem(
            item_id="sword",
            name="劍",
            category=ItemCategory.WEAPON,
            current_durability=30,
            max_durability=50,
            dimensional_origin="dimensional",
        )
        d = item.to_dict()
        assert d["current_durability"] == 30
        assert d["max_durability"] == 50
        assert d["dimensional_origin"] == "dimensional"

    def test_from_dict_restores_durability(self) -> None:
        d = {
            "item_id": "sword",
            "name": "劍",
            "category": "武器",
            "quantity": 1,
            "current_durability": 30,
            "max_durability": 50,
            "dimensional_origin": "mold",
        }
        item = InventoryItem.from_dict(d)
        assert item.current_durability == 30
        assert item.max_durability == 50
        assert item.dimensional_origin == "mold"


# ---------------------------------------------------------------------------
# RepairConfig 測試
# ---------------------------------------------------------------------------


class TestRepairConfig:
    def test_loads_success(self) -> None:
        cfg = RepairConfig.get_instance()
        assert cfg.repair_formula["base_success_rate"] == 0.6
        assert cfg.repair_randomness["durability_restored_max"] == 40
        assert cfg.special_repairs["mold_repair"]["hp_cost"] == 10

    def test_get_item_category_repairable(self) -> None:
        cfg = RepairConfig.get_instance()
        assert cfg.get_item_category_config("WEAPON")["repairable"] is True
        assert cfg.get_item_category_config("CONSUMABLE")["repairable"] is False


# ---------------------------------------------------------------------------
# RepairSystem.attempt_repair 測試
# ---------------------------------------------------------------------------


class TestRepairSelf:
    def test_self_repair_success_with_materials(self) -> None:
        rs, player, inv = make_rs(with_materials=True)
        with patch("game.repair_system.random.random", return_value=0.1):
            with patch("game.repair_system.random.randint", return_value=20):
                result = rs.attempt_repair("rusty_sword", RepairMethod.SELF)
        assert result.success is True
        assert result.method == RepairMethod.SELF
        assert result.durability_restored > 0
        assert "成功" in result.message

    def test_self_repair_fail_without_materials(self) -> None:
        rs, player, inv = make_rs(with_materials=False)
        with pytest.raises(InsufficientMaterials):
            rs.attempt_repair("rusty_sword", RepairMethod.SELF)

    def test_self_repair_fail_roll(self) -> None:
        rs, player, inv = make_rs(with_materials=True)
        with patch("game.repair_system.random.random", return_value=0.99):
            result = rs.attempt_repair("rusty_sword", RepairMethod.SELF)
        assert result.result == RepairResult.FAIL
        assert result.durability_restored == 0

    def test_self_repair_consumes_materials(self) -> None:
        rs, player, inv = make_rs(with_materials=True)
        before = next(i.quantity for i in inv.items if i.item_id == "metal_scraps")
        with patch("game.repair_system.random.random", return_value=0.1):
            with patch("game.repair_system.random.randint", return_value=20):
                rs.attempt_repair("rusty_sword", RepairMethod.SELF)
        after = next(i.quantity for i in inv.items if i.item_id == "metal_scraps")
        assert after < before


# ---------------------------------------------------------------------------
# RepairSystem NPC 修理
# ---------------------------------------------------------------------------


class TestRepairNPC:
    def test_npc_repair_always_succeeds(self) -> None:
        rs, player, inv = make_rs(with_materials=False)
        gold_before = player["gold"]
        result = rs.attempt_repair("rusty_sword", RepairMethod.NPC)
        assert result.success is True
        assert result.result == RepairResult.SUCCESS
        assert player["gold"] < gold_before

    def test_npc_repair_insufficient_gold(self) -> None:
        rs, player, inv = make_rs(with_materials=False)
        player["gold"] = 0
        with pytest.raises(InsufficientGold):
            rs.attempt_repair("rusty_sword", RepairMethod.NPC)

    def test_npc_repair_full_restore(self) -> None:
        rs, player, inv = make_rs(with_materials=False)
        result = rs.attempt_repair("rusty_sword", RepairMethod.NPC)
        sword = rs._find_item("rusty_sword")
        assert sword is not None
        assert sword.current_durability == sword.max_durability


# ---------------------------------------------------------------------------
# RepairSystem 霉菌修理
# ---------------------------------------------------------------------------


class TestRepairMold:
    def test_mold_repair_requires_mancelled(self) -> None:
        rs, player, inv = make_rs()
        player["is_mancelled"] = False
        with pytest.raises(ConditionNotMet):
            rs.attempt_repair("rusty_sword", RepairMethod.MOLD)

    def test_mold_repair_success(self) -> None:
        rs, player, inv = make_rs()
        player["is_mancelled"] = True
        player["hp"] = 50
        result = rs.attempt_repair("rusty_sword", RepairMethod.MOLD)
        assert result.success is True
        assert result.result == RepairResult.SUCCESS
        assert result.hp_cost == 10
        assert player["hp"] == 40

    def test_mold_repair_insufficient_hp(self) -> None:
        rs, player, inv = make_rs()
        player["is_mancelled"] = True
        player["hp"] = 5
        with pytest.raises(ConditionNotMet):
            rs.attempt_repair("rusty_sword", RepairMethod.MOLD)


# ---------------------------------------------------------------------------
# RepairSystem 附魔修理
# ---------------------------------------------------------------------------


class TestRepairEnchanted:
    def test_enchanted_requires_dust(self) -> None:
        rs, player, inv = make_rs(with_materials=True, with_enchanted_dust=False)
        with pytest.raises(InsufficientMaterials):
            rs.attempt_repair("rusty_sword", RepairMethod.ENCHANTED)

    def test_enchanted_success(self) -> None:
        rs, player, inv = make_rs(with_materials=True, with_enchanted_dust=True)
        assert inv.has_item("enchanted_dust", 1) is True
        with patch("game.repair_system.random.random", return_value=0.1):
            with patch("game.repair_system.random.randint", return_value=15):
                result = rs.attempt_repair("rusty_sword", RepairMethod.ENCHANTED)
        assert result.success is True
        assert result.method == RepairMethod.ENCHANTED
        assert "enchanted_dust" in result.materials_used


# ---------------------------------------------------------------------------
# RepairSystem 次元修理
# ---------------------------------------------------------------------------


class TestRepairDimensional:
    def test_dimensional_repair_full_restore(self) -> None:
        rs, player, inv = make_rs()
        assert player["dimensional_fragments"] >= 1
        result = rs.attempt_repair("rusty_sword", RepairMethod.DIMENSIONAL)
        assert result.success is True
        assert result.method == RepairMethod.DIMENSIONAL
        sword = rs._find_item("rusty_sword")
        assert sword is not None
        assert sword.current_durability == sword.max_durability


# ---------------------------------------------------------------------------
# RepairSystem 緊急修理
# ---------------------------------------------------------------------------


class TestRepairEmergency:
    def test_emergency_always_succeeds(self) -> None:
        rs, player, inv = make_rs(with_materials=True)
        result = rs.attempt_repair("rusty_sword", RepairMethod.EMERGENCY)
        assert result.success is True
        assert result.method == RepairMethod.EMERGENCY


# ---------------------------------------------------------------------------
# RepairSystem 校驗
# ---------------------------------------------------------------------------


class TestRepairValidation:
    def test_nonexistent_item_raises(self) -> None:
        rs, player, inv = make_rs()
        with pytest.raises(ItemNotRepairable):
            rs.attempt_repair("nonexistent_item", RepairMethod.SELF)

    def test_non_repairable_item_raises(self) -> None:
        rs, player, inv = make_rs()
        with pytest.raises(ItemNotRepairable):
            rs.attempt_repair("healing_potion", RepairMethod.SELF)

    def test_item_not_broken_raises(self) -> None:
        rs, player, inv = make_rs()
        sword = rs._find_item("rusty_sword")
        assert sword is not None
        sword.current_durability = sword.max_durability
        with pytest.raises(ItemNotBroken):
            rs.attempt_repair("rusty_sword", RepairMethod.SELF)

    def test_get_available_methods(self) -> None:
        rs, player, inv = make_rs()
        methods = rs.get_available_methods("rusty_sword")
        assert RepairMethod.SELF in methods
        assert RepairMethod.NPC in methods
        assert RepairMethod.MOLD not in methods

    def test_get_available_methods_mold_for_mancelled(self) -> None:
        rs, player, inv = make_rs()
        player["is_mancelled"] = True
        methods = rs.get_available_methods("rusty_sword")
        assert RepairMethod.MOLD in methods

    def test_get_repair_cost_estimate(self) -> None:
        rs, player, inv = make_rs()
        costs = rs.get_repair_cost_estimate("rusty_sword", RepairMethod.NPC)
        assert RepairMethod.NPC in costs
        assert costs[RepairMethod.NPC]["success_rate"] == "100%"


# ---------------------------------------------------------------------------
# RepairOutcome（資料類）測試
# ---------------------------------------------------------------------------


class TestRepairOutcomeDataclass:
    def test_success_property(self) -> None:
        outcome = RepairOutcome(
            result=RepairResult.SUCCESS,
            item_id="sword",
            method=RepairMethod.SELF,
            durability_restored=20,
        )
        assert outcome.success is True

    def test_fail_not_success(self) -> None:
        outcome = RepairOutcome(
            result=RepairResult.FAIL,
            item_id="sword",
            method=RepairMethod.SELF,
            durability_restored=0,
        )
        assert outcome.success is False

    def test_critical_is_success(self) -> None:
        outcome = RepairOutcome(
            result=RepairResult.CRITICAL_SUCCESS,
            item_id="sword",
            method=RepairMethod.ENCHANTED,
            durability_restored=50,
        )
        assert outcome.success is True
        assert outcome.was_critical is True


# ---------------------------------------------------------------------------
# 與 GameState / ensure_durability 整合
# ---------------------------------------------------------------------------


def _seed_weapon(gs) -> None:
    assert gs.player is not None
    gs.player.inventory.add_item(
        InventoryItem(
            item_id="rusty_sword",
            name="生锈短剑",
            category=ItemCategory.WEAPON,
            quantity=1,
            description="测试武器",
            meta={"durability": 20, "max_durability": 50, "base_value": 100},
        )
    )
    gs.player.equipped_weapon_id = "rusty_sword"
    gs.player.inventory.add_item(
        InventoryItem(
            item_id="metal_scraps",
            name="金属碎片",
            category=ItemCategory.MISC,
            quantity=3,
            description="测试材料",
        )
    )


def test_load_cfg_and_ensure_durability() -> None:
    cfg = load_repair_config()
    it = InventoryItem(item_id="x", name="x", category=ItemCategory.WEAPON, quantity=1)
    cur, max_d = ensure_durability(it, cfg)
    assert max_d == 50
    assert cur == 50


def test_self_repair_success(monkeypatch) -> None:
    gs = new_game_state("修理匠", Profession.WARRIOR.value)
    _seed_weapon(gs)
    vals = iter([0.99, 0.0, 0.99])
    monkeypatch.setattr("game.repair_system.random.random", lambda: next(vals))
    monkeypatch.setattr("game.repair_system.random.randint", lambda a, b: 12)
    msg = attempt_equipped_repair(gs, "weapon", via_npc=False)
    it = get_equipped_item(gs, "weapon")
    assert it is not None
    assert "修理成功" in msg or "Repair succeeded" in msg
    assert int(it.meta.get("durability", 0)) > 20


def test_untrained_self_repair_blocked() -> None:
    gs = new_game_state("法师", Profession.MAGE.value)
    _seed_weapon(gs)
    msg = attempt_equipped_repair(gs, "weapon", via_npc=False)
    assert "无法" in msg or "cannot" in msg.lower()


def test_npc_repair_restores_full() -> None:
    gs = new_game_state("村民", Profession.MAGE.value)
    _seed_weapon(gs)
    assert can_npc_repair_here(gs.current_scene_id)
    assert gs.player is not None
    gs.player.gold = 999
    msg = attempt_equipped_repair(gs, "weapon", via_npc=True)
    it = get_equipped_item(gs, "weapon")
    assert it is not None
    assert int(it.meta.get("durability", 0)) == int(it.meta.get("max_durability", 0))
    assert "修好" in msg or "repaired" in msg.lower()


def test_repair_system_returns_receipt(monkeypatch) -> None:
    gs = new_game_state("修理匠", Profession.WARRIOR.value)
    _seed_weapon(gs)
    vals = iter([0.99, 0.0, 0.99])
    monkeypatch.setattr("game.repair_system.random.random", lambda: next(vals))
    monkeypatch.setattr("game.repair_system.random.randint", lambda a, b: 12)
    res = RepairSystem().attempt_equipped(RepairContext(state=gs, slot="weapon", via_npc=False))
    assert isinstance(res, RepairReceipt)
    assert res.success is True
    assert res.durability_restored == 12
    assert "修理成功" in res.message or "Repair succeeded" in res.message


def test_repair_error_importable() -> None:
    assert issubclass(RepairError, Exception)
