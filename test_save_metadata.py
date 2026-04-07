"""
测试存档元数据功能（标签和描述）
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import tempfile
import shutil

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from game.save_metadata import (
    SaveMetadata,
    load_metadata,
    save_metadata,
    get_metadata_path,
    PREDEFINED_TAGS,
    get_suggested_tags,
)


def test_save_metadata():
    """测试存档元数据"""
    print("=" * 60)
    print("测试 1: 存档元数据基本功能")
    print("=" * 60)

    metadata = SaveMetadata(
        tags=["主线任务", "低等级"],
        description="这是一个测试存档",
        created_at="2026-04-07T00:00:00",
        updated_at="2026-04-07T00:00:00",
    )

    print(f"✓ 创建元数据对象")
    print(f"  标签: {metadata.tags}")
    print(f"  描述: {metadata.description}")
    print(f"  创建时间: {metadata.created_at}")
    print(f"  更新时间: {metadata.updated_at}")

    # 测试 to_dict
    data = metadata.to_dict()
    print(f"✓ 转换为字典")
    print(f"  字典键: {list(data.keys())}")

    # 测试 from_dict
    metadata2 = SaveMetadata.from_dict(data)
    assert metadata2.tags == metadata.tags
    assert metadata2.description == metadata.description
    print(f"✓ 从字典创建")
    print(f"  恢复成功")

    print()


def test_tag_operations():
    """测试标签操作"""
    print("=" * 60)
    print("测试 2: 标签操作")
    print("=" * 60)

    metadata = SaveMetadata()

    # 添加标签
    metadata.add_tag("主线任务")
    metadata.add_tag("低等级")
    metadata.add_tag("主线任务")  # 重复添加

    print(f"✓ 添加标签")
    print(f"  标签列表: {metadata.tags}")
    assert len(metadata.tags) == 2, f"应该有 2 个标签，实际有 {len(metadata.tags)} 个"

    # 移除标签
    metadata.remove_tag("主线任务")
    print(f"✓ 移除标签")
    print(f"  移除后的标签: {metadata.tags}")
    assert len(metadata.tags) == 1, f"应该有 1 个标签，实际有 {len(metadata.tags)} 个"

    # 检查时间更新
    assert metadata.updated_at != metadata.created_at or metadata.updated_at != ""
    print(f"✓ 时间更新")
    print(f"  更新时间: {metadata.updated_at}")

    print()


def test_description_operations():
    """测试描述操作"""
    print("=" * 60)
    print("测试 3: 描述操作")
    print("=" * 60)

    metadata = SaveMetadata()

    # 设置描述
    metadata.set_description("这是一个新的描述")
    print(f"✓ 设置描述")
    print(f"  描述: {metadata.description}")
    assert metadata.description == "这是一个新的描述"

    # 更新描述
    metadata.set_description("这是更新后的描述")
    print(f"✓ 更新描述")
    print(f"  新描述: {metadata.description}")

    print()


def test_metadata_file_operations():
    """测试元数据文件操作"""
    print("=" * 60)
    print("测试 4: 元数据文件操作")
    print("=" * 60)

    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # 创建存档路径
        save_path = temp_dir / "test_save.json"

        # 创建测试元数据
        metadata = SaveMetadata(
            tags=["主线任务", "低等级"],
            description="测试存档",
        )

        # 保存元数据
        save_metadata(save_path, metadata)
        print(f"✓ 保存元数据")
        print(f"  保存路径: {get_metadata_path(save_path)}")

        # 验证文件存在
        meta_path = get_metadata_path(save_path)
        assert meta_path.exists(), f"元数据文件不存在: {meta_path}"
        print(f"✓ 验证文件存在")

        # 加载元数据
        loaded_metadata = load_metadata(save_path)
        print(f"✓ 加载元数据")
        print(f"  加载的标签: {loaded_metadata.tags}")
        print(f"  加载的描述: {loaded_metadata.description}")

        # 验证数据
        assert loaded_metadata.tags == metadata.tags
        assert loaded_metadata.description == metadata.description
        print(f"✓ 验证数据一致性")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"✓ 清理临时文件")

    print()


def test_get_suggested_tags():
    """测试标签推荐"""
    print("=" * 60)
    print("测试 5: 标签推荐")
    print("=" * 60)

    # 测试 1: 主线任务 + 低等级
    save_data1 = {
        "active_quest_ids": ["main_forest"],
        "completed_quest_ids": [],
        "player": {
            "level": 3,
            "gold": 50,
            "equipped_weapon_id": None,
            "equipped_armor_id": None,
        },
    }

    suggested1 = get_suggested_tags(save_data1)
    print(f"✓ 测试 1: 主线任务 + 低等级")
    print(f"  推荐标签: {suggested1}")
    assert "主线任务" in suggested1
    assert "低等级" in suggested1

    # 测试 2: 高等级 + 资金充足 + 装备齐全
    save_data2 = {
        "active_quest_ids": [],
        "completed_quest_ids": ["side_elder_cat", "side_merchant"],
        "player": {
            "level": 12,
            "gold": 150,
            "equipped_weapon_id": "sword_01",
            "equipped_armor_id": "armor_01",
        },
    }

    suggested2 = get_suggested_tags(save_data2)
    print(f"✓ 测试 2: 高等级 + 资金充足 + 装备齐全")
    print(f"  推荐标签: {suggested2}")
    assert "支线任务" in suggested2
    assert "高等级" in suggested2
    assert "资金充足" in suggested2
    assert "装备齐全" in suggested2

    # 测试 3: 中等级
    save_data3 = {
        "active_quest_ids": [],
        "completed_quest_ids": [],
        "player": {
            "level": 7,
            "gold": 80,
            "equipped_weapon_id": None,
            "equipped_armor_id": None,
        },
    }

    suggested3 = get_suggested_tags(save_data3)
    print(f"✓ 测试 3: 中等级")
    print(f"  推荐标签: {suggested3}")
    assert "中等级" in suggested3

    print()


def test_predefined_tags():
    """测试预定义标签"""
    print("=" * 60)
    print("测试 6: 预定义标签")
    print("=" * 60)

    print(f"✓ 预定义标签数量: {len(PREDEFINED_TAGS)}")
    print(f"  标签列表:")
    for i, tag in enumerate(PREDEFINED_TAGS, 1):
        print(f"    {i}. {tag}")

    # 验证一些关键标签存在
    assert "主线任务" in PREDEFINED_TAGS
    assert "支线任务" in PREDEFINED_TAGS
    assert "低等级" in PREDEFINED_TAGS
    assert "中等级" in PREDEFINED_TAGS
    assert "高等级" in PREDEFINED_TAGS

    print(f"✓ 关键标签验证通过")

    print()


def test_load_missing_metadata():
    """测试加载不存在的元数据"""
    print("=" * 60)
    print("测试 7: 加载不存在的元数据")
    print("=" * 60)

    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # 创建不存在的存档路径
        save_path = temp_dir / "nonexistent_save.json"

        # 加载不存在的元数据
        metadata = load_metadata(save_path)
        print(f"✓ 加载不存在的元数据")
        print(f"  返回空元数据")
        assert metadata.tags == []
        assert metadata.description == ""

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"✓ 清理临时文件")

    print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("存档元数据功能测试")
    print("=" * 60 + "\n")

    try:
        test_save_metadata()
        test_tag_operations()
        test_description_operations()
        test_metadata_file_operations()
        test_get_suggested_tags()
        test_predefined_tags()
        test_load_missing_metadata()

        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True

    except AssertionError as e:
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ 测试出错: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
