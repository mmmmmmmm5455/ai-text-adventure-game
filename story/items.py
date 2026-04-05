"""
物品目录（静态定义），与背包中的 item_id 对应。
"""

from __future__ import annotations

from game.inventory import InventoryItem, ItemCategory


def catalog() -> dict[str, InventoryItem]:
    return {
        "healing_potion": InventoryItem(
            item_id="healing_potion",
            name="治疗药水",
            category=ItemCategory.CONSUMABLE,
            quantity=1,
            description="恢复少量生命值。",
        ),
        "ancient_key": InventoryItem(
            item_id="ancient_key",
            name="古老钥匙",
            category=ItemCategory.QUEST,
            quantity=1,
            description="刻有符文的钥匙，或许能打开遗迹深处的门。",
        ),
        "treasure": InventoryItem(
            item_id="treasure",
            name="沉甸甸的宝藏",
            category=ItemCategory.MISC,
            quantity=1,
            description="金光闪烁的战利品，足以改变人生轨迹。",
        ),
        "rusty_sword": InventoryItem(
            item_id="rusty_sword",
            name="生锈短剑",
            category=ItemCategory.WEAPON,
            quantity=1,
            description="勉强能用的武器。",
        ),
        "leather_armor": InventoryItem(
            item_id="leather_armor",
            name="皮甲",
            category=ItemCategory.ARMOR,
            quantity=1,
            description="基础防护。",
        ),
    }
