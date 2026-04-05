"""
背包系统：分类、堆叠上限、使用与丢弃。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ItemCategory(str, Enum):
    """物品分类。"""

    WEAPON = "武器"
    ARMOR = "防具"
    CONSUMABLE = "消耗品"
    QUEST = "任务物品"
    MISC = "杂物"


@dataclass
class InventoryItem:
    """背包中的物品实例。"""

    item_id: str
    name: str
    category: ItemCategory
    quantity: int = 1
    description: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category.value,
            "quantity": self.quantity,
            "description": self.description,
            "meta": self.meta,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "InventoryItem":
        return InventoryItem(
            item_id=data["item_id"],
            name=data["name"],
            category=ItemCategory(data["category"]),
            quantity=int(data.get("quantity", 1)),
            description=data.get("description", ""),
            meta=dict(data.get("meta", {})),
        )


class Inventory:
    """背包：最多 MAX_SLOTS 个不同条目（可堆叠）。"""

    def __init__(self, max_slots: int) -> None:
        self.max_slots = max_slots
        self._items: list[InventoryItem] = []

    @property
    def items(self) -> list[InventoryItem]:
        return list(self._items)

    def count_entries(self) -> int:
        return len(self._items)

    def add_item(self, item: InventoryItem) -> bool:
        """添加物品；若已满返回 False。"""
        for existing in self._items:
            if existing.item_id == item.item_id and item.category == ItemCategory.CONSUMABLE:
                existing.quantity += item.quantity
                return True
        if len(self._items) >= self.max_slots:
            return False
        self._items.append(item)
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        for i, existing in enumerate(self._items):
            if existing.item_id == item_id:
                if existing.quantity > quantity:
                    existing.quantity -= quantity
                elif existing.quantity == quantity:
                    self._items.pop(i)
                else:
                    return False
                return True
        return False

    def has_item(self, item_id: str, min_qty: int = 1) -> bool:
        for it in self._items:
            if it.item_id == item_id and it.quantity >= min_qty:
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {"max_slots": self.max_slots, "items": [x.to_dict() for x in self._items]}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Inventory":
        inv = Inventory(int(data.get("max_slots", 20)))
        for row in data.get("items", []):
            inv._items.append(InventoryItem.from_dict(row))
        return inv
