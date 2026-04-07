"""
特质效果系统
计算和应用角色特质的效果
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraitEffect:
    """特质效果计算器"""

    # 正面特质效果
    consumable_bonus: float = 0.0  # 消耗品效果加成
    poison_resistance: float = 0.0  # 毒素抗性
    food_efficiency: float = 0.0  # 食物效率
    charisma_bonus: int = 0  # 魅力加成
    npc_affinity_bonus: float = 0.0  # NPC 好感度加成
    negotiation_bonus: float = 0.0  # 交涉加成
    trade_discount: float = 0.0  # 交易折扣
    healing_bonus: float = 0.0  # 治疗加成
    first_aid_success_bonus: float = 0.0  # 急救成功率加成
    auto_heal_chance: float = 0.0  # 自动治疗概率
    critical_heal_chance: float = 0.0  # 暴击治疗概率
    mental_resistance: float = 0.0  # 精神抗性
    fear_resistance: float = 0.0  # 恐惧抗性
    attribute_stability: bool = False  # 属性稳定
    combat_focus_bonus: float = 0.0  # 战斗专注加成
    perception_bonus: int = 0  # 感知加成
    hidden_item_chance_bonus: float = 0.0  # 隐藏物品概率加成
    exploration_success_bonus: float = 0.0  # 探索成功率加成
    trap_detection_bonus: float = 0.0  # 陷阱检测加成

    # 负面特质效果
    lost_chance_bonus: float = 0.0  # 迷路概率加成
    movement_time_penalty: float = 0.0  # 移动时间惩罚
    navigation_failure_chance: float = 0.0  # 导航失败概率
    perception_penalty: int = 0  # 感知惩罚
    night_perception_penalty: int = 0  # 夜间感知惩罚
    night_exploration_penalty: float = 0.0  # 夜间探索惩罚
    night_combat_penalty: float = 0.0  # 夜间战斗惩罚
    darkness_vulnerability: bool = False  # 黑暗脆弱性
    agility_penalty: int = 0  # 敏捷惩罚
    item_use_failure_chance: float = 0.0  # 物品使用失败概率
    stealth_failure_chance: float = 0.0  # 潜行失败概率
    dodge_penalty: float = 0.0  # 闪避惩罚

    def apply_consumable_effect(self, base_value: float) -> float:
        """应用消耗品效果加成"""
        return base_value * (1.0 + self.consumable_bonus + self.food_efficiency)

    def apply_healing_effect(self, base_value: float) -> float:
        """应用治疗效果加成"""
        heal = base_value * (1.0 + self.healing_bonus)

        # 暴击治疗
        if self.critical_heal_chance > 0 and random_check(self.critical_heal_chance):
            heal *= 1.5  # 1.5 倍暴击治疗

        return heal

    def apply_perception_modifier(self, base_value: int, is_night: bool = False) -> int:
        """应用感知修正"""
        modifier = base_value

        # 基础加成
        modifier += self.perception_bonus

        # 负面惩罚
        modifier += self.perception_penalty

        # 夜间惩罚
        if is_night and self.night_perception_penalty != 0:
            modifier += self.night_perception_penalty

        return max(1, modifier)  # 最小值为 1

    def apply_exploration_bonus(self, base_chance: float, is_night: bool = False) -> float:
        """应用探索成功概率加成"""
        bonus = base_chance

        # 基础加成
        bonus += self.exploration_success_bonus

        # 夜间惩罚
        if is_night and self.night_exploration_penalty != 0:
            bonus += self.night_exploration_penalty

        # 路痴惩罚
        bonus -= self.lost_chance_bonus

        return max(0.0, min(1.0, bonus))  # 限制在 0-1 之间

    def apply_charisma_modifier(self, base_value: int) -> int:
        """应用魅力修正"""
        return base_value + self.charisma_bonus

    def apply_agility_modifier(self, base_value: int) -> int:
        """应用敏捷修正"""
        modified = base_value + (-self.agility_penalty if self.agility_penalty < 0 else 0)
        return max(1, modified)

    def apply_combat_modifier(self, base_value: float, is_night: bool = False) -> float:
        """应用战斗修正"""
        modifier = base_value

        # 战斗专注加成
        modifier += self.combat_focus_bonus

        # 夜间战斗惩罚
        if is_night and self.night_combat_penalty != 0:
            modifier += self.night_combat_penalty

        # 闪避惩罚
        modifier -= self.dodge_penalty

        return modifier

    def apply_negotiation_bonus(self, base_chance: float) -> float:
        """应用交涉加成"""
        return min(1.0, base_chance + self.negotiation_bonus)

    def apply_trade_discount(self, base_price: float) -> float:
        """应用交易折扣"""
        return base_price * (1.0 - self.trade_discount)

    def calculate_item_use_success(self, base_success: float = 1.0) -> bool:
        """计算物品使用成功率"""
        modified = base_success - self.item_use_failure_chance
        return random_check(modified)

    def calculate_trail_detection(self, base_chance: float) -> float:
        """计算陷阱检测概率"""
        return min(1.0, base_chance + self.trap_detection_bonus + self.perception_bonus * 0.05)

    def get_effective_stats(self, base_stats: dict[str, int]) -> dict[str, int]:
        """获取有效属性（考虑特质效果）"""
        effective = base_stats.copy()

        # 魅力
        if self.charisma_bonus != 0:
            effective["charisma"] += self.charisma_bonus

        # 感知
        if self.perception_bonus != 0:
            effective["perception"] += self.perception_bonus
        if self.perception_penalty != 0:
            effective["perception"] += self.perception_penalty

        # 敏捷
        if self.agility_penalty != 0:
            effective["agility"] += self.agility_penalty

        # 确保所有属性最小值为 1
        for key in effective:
            effective[key] = max(1, effective[key])

        return effective

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            # 正面特质效果
            "consumable_bonus": self.consumable_bonus,
            "poison_resistance": self.poison_resistance,
            "food_efficiency": self.food_efficiency,
            "charisma_bonus": self.charisma_bonus,
            "npc_affinity_bonus": self.npc_affinity_bonus,
            "negotiation_bonus": self.negotiation_bonus,
            "trade_discount": self.trade_discount,
            "healing_bonus": self.healing_bonus,
            "first_aid_success_bonus": self.first_aid_success_bonus,
            "auto_heal_chance": self.auto_heal_chance,
            "critical_heal_chance": self.critical_heal_chance,
            "mental_resistance": self.mental_resistance,
            "fear_resistance": self.fear_resistance,
            "attribute_stability": self.attribute_stability,
            "combat_focus_bonus": self.combat_focus_bonus,
            "perception_bonus": self.perception_bonus,
            "hidden_item_chance_bonus": self.hidden_item_chance_bonus,
            "exploration_success_bonus": self.exploration_success_bonus,
            "trap_detection_bonus": self.trap_detection_bonus,

            # 负面特质效果
            "lost_chance_bonus": self.lost_chance_bonus,
            "movement_time_penalty": self.movement_time_penalty,
            "navigation_failure_chance": self.navigation_failure_chance,
            "perception_penalty": self.perception_penalty,
            "night_perception_penalty": self.night_perception_penalty,
            "night_exploration_penalty": self.night_exploration_penalty,
            "night_combat_penalty": self.night_combat_penalty,
            "darkness_vulnerability": self.darkness_vulnerability,
            "agility_penalty": self.agility_penalty,
            "item_use_failure_chance": self.item_use_failure_chance,
            "stealth_failure_chance": self.stealth_failure_chance,
            "dodge_penalty": self.dodge_penalty,
        }

    @classmethod
    def from_traits(cls, trait_effects: list[dict[str, Any]]) -> "TraitEffect":
        """从特质效果列表创建 TraitEffect 对象"""
        effect = cls()

        for trait_effect_dict in trait_effects:
            for key, value in trait_effect_dict.items():
                if hasattr(effect, key):
                    setattr(effect, key, getattr(effect, key) + value)

        return effect


def random_check(chance: float) -> bool:
    """随机检查（用于概率计算）"""
    import random
    return random.random() < chance


def create_trait_effect(player: "Player") -> TraitEffect:
    """为玩家创建特质效果对象"""
    from game.character_creator import CharacterCreatorConfig

    # 获取特质配置
    config = CharacterCreatorConfig.get_instance()

    # 收集所有特质效果
    trait_effects_list = []

    for trait_id in player.traits:
        trait = config.get_trait(trait_id)
        if trait and trait.effects:
            trait_effects_list.append(trait.effects)

    # 创建特质效果对象
    return TraitEffect.from_traits(trait_effects_list)


def calculate_trait_summary(trait_ids: list[str]) -> dict[str, Any]:
    """计算特质效果摘要"""
    from game.character_creator import CharacterCreatorConfig

    config = CharacterCreatorConfig.get_instance()

    effect = TraitEffect()

    for trait_id in trait_ids:
        trait = config.get_trait(trait_id)
        if trait and trait.effects:
            for key, value in trait.effects.items():
                if hasattr(effect, key):
                    current_value = getattr(effect, key)
                    if isinstance(current_value, bool):
                        setattr(effect, key, current_value or bool(value))
                    elif isinstance(current_value, (int, float)):
                        setattr(effect, key, current_value + value)

    return effect.to_dict()
