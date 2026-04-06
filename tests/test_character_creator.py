"""角色創建系統測試"""

from __future__ import annotations

import pytest

from game.character_creator import (
    Background,
    CharacterCreator,
    CharacterCreatorConfig,
    CharacterProfile,
    Trait,
)
from game.player import Profession


@pytest.fixture
def config() -> CharacterCreatorConfig:
    CharacterCreatorConfig._reset_instance_for_tests()
    return CharacterCreatorConfig.get_instance()


@pytest.fixture
def creator(config: CharacterCreatorConfig) -> CharacterCreator:
    return CharacterCreator(config)


class TestConfigLoading:
    def test_loads_backgrounds(self, config: CharacterCreatorConfig) -> None:
        assert len(config.backgrounds) > 0
        bg = config.get_background("wasteland_doctor")
        assert bg is not None
        assert bg.name == "廢土醫生"

    def test_loads_traits(self, config: CharacterCreatorConfig) -> None:
        assert len(config.positive_traits) > 0
        assert len(config.negative_traits) > 0
        tr = config.get_trait("iron_stomach")
        assert tr is not None
        assert tr.is_positive is True

    def test_random_background(self, config: CharacterCreatorConfig) -> None:
        bg = config.get_random_background()
        assert isinstance(bg, Background)

    def test_random_traits(self, config: CharacterCreatorConfig) -> None:
        pos, neg = config.get_random_traits()
        assert len(pos) == 2
        assert len(neg) == 2

    def test_config_reload(self, config: CharacterCreatorConfig) -> None:
        same = CharacterCreatorConfig.reload()
        assert same.get_background("wasteland_doctor") is not None


class TestManualCreation:
    def test_set_name_and_gender(self, creator: CharacterCreator) -> None:
        creator.set_name("測試冒險者").set_gender("男")
        assert creator.profile.name == "測試冒險者"
        assert creator.profile.gender == "男"

    def test_choose_valid_background(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        bg_id = config.list_background_ids()[0]
        creator.choose_background(bg_id)
        assert creator.profile.background is not None

    def test_choose_invalid_background_raises(self, creator: CharacterCreator) -> None:
        with pytest.raises(ValueError, match="無效的背景ID"):
            creator.choose_background("nonexistent_bg")

    def test_add_positive_trait(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.add_trait("iron_stomach")
        assert len(creator.profile.positive_traits) == 1
        assert creator.profile.positive_traits[0].name == "鐵胃"

    def test_add_negative_trait(self, creator: CharacterCreator) -> None:
        creator.add_trait("bad_sense_of_direction", positive=False)
        assert len(creator.profile.negative_traits) == 1

    def test_trait_limit(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.add_trait("iron_stomach")
        creator.add_trait("social_butterfly")
        with pytest.raises(ValueError, match="正面特質已達上限"):
            creator.add_trait("first_aid_master")

    def test_duplicate_trait_raises(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.add_trait("iron_stomach")
        with pytest.raises(ValueError, match="特質已存在"):
            creator.add_trait("iron_stomach")

    def test_distribute_stats_valid(self, creator: CharacterCreator) -> None:
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        assert creator.profile.stats == {"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2}

    def test_distribute_stats_out_of_range_raises(self, creator: CharacterCreator) -> None:
        with pytest.raises(ValueError, match="必須在 1~10 之間"):
            creator.distribute_stats({"str": 11, "per": 5, "end": 5, "cha": 5, "int": 5, "agl": 5})

    def test_distribute_stats_wrong_sum_raises(self, creator: CharacterCreator) -> None:
        with pytest.raises(ValueError, match="屬性總和"):
            creator.distribute_stats({"str": 5, "per": 5, "end": 5, "cha": 5, "int": 5, "agl": 5})

    def test_auto_distribute_random(self, creator: CharacterCreator) -> None:
        creator.auto_distribute_random()
        assert sum(creator.profile.stats.values()) == 20
        assert all(1 <= v <= 8 for v in creator.profile.stats.values())

    def test_validate_missing_name(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("x")
        creator.choose_background(config.list_background_ids()[0])
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        creator.profile.name = ""
        errors = creator.validate()
        assert any("姓名" in e for e in errors)

    def test_validate_missing_background(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("test")
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        errors = creator.validate()
        assert any("背景" in e for e in errors)

    def test_validate_stats_wrong_total(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("test")
        creator.choose_background(config.list_background_ids()[0])
        creator.profile.stats = {"str": 5, "per": 5, "end": 5, "cha": 5, "int": 5, "agl": 5}
        errors = creator.validate()
        assert any("屬性總和" in e for e in errors)

    def test_validate_complete(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("冒險者").set_gender("自訂")
        creator.choose_background(config.list_background_ids()[0])
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        assert creator.validate() == []

    def test_build_success(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("阿克").set_gender("男")
        creator.choose_background("wasteland_doctor")
        creator.add_trait("iron_stomach")
        creator.add_trait("bad_sense_of_direction", positive=False)
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        player = creator.build()
        assert player.name == "阿克"
        assert player.gender == "男"
        assert player.profession == Profession.WARRIOR
        assert player.traits == ["iron_stomach", "bad_sense_of_direction"]
        assert player.background_id == "wasteland_doctor"
        assert player.background_name == "廢土醫生"
        assert player.max_hp == 120
        assert player.max_mp == 30

    def test_build_respects_profession(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        creator.set_name("法師").set_gender("女")
        creator.choose_background(config.list_background_ids()[0])
        creator.distribute_stats({"str": 3, "per": 5, "end": 3, "cha": 3, "int": 4, "agl": 2})
        player = creator.build(profession=Profession.MAGE)
        assert player.profession == Profession.MAGE
        assert player.max_hp == 70
        assert player.max_mp == 80

    def test_add_recommended_traits(self, creator: CharacterCreator, config: CharacterCreatorConfig) -> None:
        bg = config.get_background("wasteland_doctor")
        assert bg is not None
        creator.add_recommended_traits(bg)
        assert len(creator.profile.positive_traits) == 2
        trait_names = [t.name for t in creator.profile.positive_traits]
        assert "急救精通" in trait_names
        assert "冷靜" in trait_names


class TestLLMBasedCreation:
    def test_accept_llm_result(self, creator: CharacterCreator) -> None:
        llm_result = {
            "background_id": "test_bg",
            "name": "測試背景",
            "description": "這是一個測試背景。",
            "recommended_traits": [],
            "stat_bonus": {"str": 1, "int": 1},
            "starting_gold_bonus": 50,
            "starting_items": [],
        }
        creator.accept_llm_result(llm_result)
        assert creator.profile.background is not None
        assert sum(creator.profile.stats.values()) == 20
        creator.set_name("測試員")
        player = creator.build()
        assert player.strength == creator.profile.stats["str"] + 1
        assert player.intelligence == creator.profile.stats["int"] + 1
        assert player.gold == 20 + 50

    def test_starting_items_from_background(self, creator: CharacterCreator) -> None:
        llm_result = {
            "background_id": "loot_bg",
            "name": "補給背景",
            "description": "",
            "recommended_traits": [],
            "stat_bonus": {},
            "starting_gold_bonus": 0,
            "starting_items": ["healing_potion"],
        }
        creator.accept_llm_result(llm_result)
        creator.set_name("拾荒者")
        player = creator.build()
        assert player.inventory.has_item("healing_potion", 1)

    def test_quick_random_without_llm(self, config: CharacterCreatorConfig) -> None:
        CharacterCreatorConfig._reset_instance_for_tests()
        player = CharacterCreator.quick_random(llm_client=None, config=config)
        assert player.name != ""


class TestCharacterProfile:
    def test_get_effect_finds_key(self) -> None:
        profile = CharacterProfile()
        t = Trait("test", "測試", "desc", {"healing_bonus": 0.3}, True)
        profile.positive_traits.append(t)
        assert profile.get_effect("healing_bonus") == 0.3
        assert profile.get_effect("nonexistent", default=99) == 99

    def test_summary_format(self) -> None:
        profile = CharacterProfile()
        profile.name = "測試"
        profile.gender = "男"
        bg = Background(
            id="test",
            name="測試背景",
            description="這是測試。",
            recommended_traits=[],
            stat_bonus={},
            starting_gold_bonus=0,
            starting_items=[],
        )
        profile.background = bg
        summary = profile.summary()
        assert "測試" in summary
        assert "力量" in summary
        assert "敏捷" in summary
