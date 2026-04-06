"""
背包系统：分类、堆叠上限、使用与丢弃。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_LOW_DURABILITY_WARNING = 0.3


class ItemCategory(str, Enum):
    """物品分类。"""

    WEAPON = "武器"
    ARMOR = "防具"
    CONSUMABLE = "消耗品"
    QUEST = "任务物品"
    MISC = "杂物"


@dataclass(init=False)
class InventoryItem:
    """背包中的物品实例。"""

    item_id: str
    name: str
    category: ItemCategory
    quantity: int = 1
    description: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        item_id: str,
        name: str,
        category: ItemCategory,
        quantity: int = 1,
        description: str = "",
        meta: dict[str, Any] | None = None,
        *,
        current_durability: int | None = None,
        max_durability: int | None = None,
        dimensional_origin: str | None = None,
    ) -> None:
        self.item_id = item_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.description = description
        self.meta = dict(meta or {})
        if current_durability is not None:
            self.meta.setdefault("durability", current_durability)
        if max_durability is not None:
            self.meta.setdefault("max_durability", max_durability)
        if dimensional_origin is not None:
            self.meta.setdefault("dimensional_origin", dimensional_origin)

    @property
    def is_durable(self) -> bool:
        md = self.meta.get("max_durability")
        if md is None:
            return False
        return int(md) > 0

    @property
    def is_broken(self) -> bool:
        if not self.is_durable:
            return False
        cur = self.meta.get("durability")
        if cur is None:
            return False
        return int(cur) <= 0

    @property
    def durability_ratio(self) -> float:
        if not self.is_durable:
            return 1.0
        cur = int(self.meta.get("durability", 0))
        mx = int(self.meta.get("max_durability", 1))
        if mx <= 0:
            return 1.0
        return cur / mx

    @property
    def current_durability(self) -> int | None:
        if not self.is_durable:
            return None
        return int(self.meta.get("durability", 0))

    @current_durability.setter
    def current_durability(self, value: int | None) -> None:
        if value is None:
            self.meta.pop("durability", None)
        else:
            self.meta["durability"] = int(value)

    @property
    def max_durability(self) -> int | None:
        if not self.is_durable:
            return None
        return int(self.meta.get("max_durability", 0))

    @max_durability.setter
    def max_durability(self, value: int | None) -> None:
        if value is None:
            self.meta.pop("max_durability", None)
        else:
            self.meta["max_durability"] = int(value)

    @property
    def dimensional_origin(self) -> str:
        return str(self.meta.get("dimensional_origin", "normal"))

    @dimensional_origin.setter
    def dimensional_origin(self, value: str) -> None:
        self.meta["dimensional_origin"] = value

    def damage(self, amount: int) -> bool:
        """扣除耐久；若本擊後耐久歸零則回傳 True。"""
        if amount < 0 or not self.is_durable:
            return False
        cur = int(self.meta.get("durability", 0))
        new_cur = max(0, cur - amount)
        self.meta["durability"] = new_cur
        return new_cur == 0

    def repair(self, amount: int) -> int:
        """恢復耐久（不超過上限）；不可修裝備回傳 0。"""
        if amount < 0:
            return 0
        if not self.is_durable:
            return 0
        mx = int(self.meta.get("max_durability", 0))
        cur = int(self.meta.get("durability", mx))
        new_cur = min(mx, cur + amount)
        gained = new_cur - cur
        self.meta["durability"] = new_cur
        return gained

    def durability_status(self) -> str:
        """粗分耐久狀態（與 repair_system.json 低耐久閾值對齊）。"""
        if not self.is_durable:
            return ""
        if self.is_broken:
            return "已損壞"
        r = self.durability_ratio
        if r >= 1.0 - 1e-9:
            return "完好"
        if r < _LOW_DURABILITY_WARNING:
            return "嚴重損壞"
        return "輕微磨損"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category.value,
            "quantity": self.quantity,
            "description": self.description,
            "meta": dict(self.meta),
        }
        if self.is_durable:
            d["current_durability"] = int(self.meta.get("durability", 0))
            d["max_durability"] = int(self.meta.get("max_durability", 0))
            d["dimensional_origin"] = str(self.meta.get("dimensional_origin", "normal"))
        return d

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "InventoryItem":
        meta = dict(data.get("meta", {}))
        if "current_durability" in data:
            meta.setdefault("durability", int(data["current_durability"]))
        if "max_durability" in data:
            meta.setdefault("max_durability", int(data["max_durability"]))
        if "dimensional_origin" in data:
            meta.setdefault("dimensional_origin", str(data["dimensional_origin"]))
        return InventoryItem(
            item_id=data["item_id"],
            name=data["name"],
            category=ItemCategory(data["category"]),
            quantity=int(data.get("quantity", 1)),
            description=data.get("description", ""),
            meta=meta,
        )


class Inventory:
    """背包：最多 MAX_SLOTS 个不同条目（可堆叠）。"""

    def __init__(self, max_slots: int) -> None:
        self.max_slots = max_slots
        self._items: list[InventoryItem] = []

    @property
    def items(self) -> list[InventoryItem]:
        return list(self._items)

    def find_item(self, item_id: str) -> InventoryItem | None:
        for it in self._items:
            if it.item_id == item_id:
                return it
        return None

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
