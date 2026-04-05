"""背包与任务测试。"""

from __future__ import annotations

from game.inventory import Inventory, InventoryItem, ItemCategory
from game.quest_system import Quest, QuestBook, QuestKind


def test_inventory_cap() -> None:
    inv = Inventory(2)
    a = InventoryItem("a", "A", ItemCategory.MISC, 1)
    b = InventoryItem("b", "B", ItemCategory.MISC, 1)
    c = InventoryItem("c", "C", ItemCategory.MISC, 1)
    assert inv.add_item(a)
    assert inv.add_item(b)
    assert not inv.add_item(c)


def test_quest_book_register() -> None:
    book = QuestBook()
    q = Quest(
        quest_id="t1",
        name="测试",
        description="d",
        objectives=["一步"],
        kind=QuestKind.SIDE,
    )
    book.register(q)
    assert book.get("t1") is not None
