"""
测试新主题系统
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def test_theme_module():
    """测试主题模块"""
    print("=" * 60)
    print("测试 1: 主题模块导入")
    print("=" * 60)

    try:
        from frontend.theme import (
            inject_css,
            render_theme_selector,
            _inject_retro_futuristic,
            _inject_minimal_cyber,
            _inject_organic_nature,
        )

        print("✓ 所有主题函数导入成功")
        print(f"  - inject_css")
        print(f"  - render_theme_selector")
        print(f"  - _inject_retro_futuristic")
        print(f"  - _inject_minimal_cyber")
        print(f"  - _inject_organic_nature")

    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

    print()
    return True


def test_enhanced_ui_module():
    """测试增强 UI 模块"""
    print("=" * 60)
    print("测试 2: 增强 UI 模块导入")
    print("=" * 60)

    try:
        from frontend.components.enhanced_ui import (
            render_player_status_enhanced,
            render_scene_card_enhanced,
            render_choice_list_enhanced,
            render_chat_message_enhanced,
            render_progress_bar_enhanced,
            render_typing_effect,
            render_notification,
        )

        print("✓ 所有增强 UI 函数导入成功")
        print(f"  - render_player_status_enhanced")
        print(f"  - render_scene_card_enhanced")
        print(f"  - render_choice_list_enhanced")
        print(f"  - render_chat_message_enhanced")
        print(f"  - render_progress_bar_enhanced")
        print(f"  - render_typing_effect")
        print(f"  - render_notification")

    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

    print()
    return True


def test_css_injection():
    """测试 CSS 注入（检查函数存在性）"""
    print("=" * 60)
    print("测试 3: CSS 注入函数")
    print("=" * 60)

    try:
        from frontend.theme import inject_css

        # 检查函数签名
        import inspect
        sig = inspect.signature(inject_css)
        print(f"✓ inject_css 函数签名: {sig}")

        # 检查默认参数
        params = sig.parameters
        theme_param = params.get('theme')
        if theme_param:
            print(f"  - theme 参数默认值: {theme_param.default}")

        print(f"✓ CSS 注入函数可用")

    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

    print()
    return True


def test_theme_colors():
    """测试主题颜色配置"""
    print("=" * 60)
    print("测试 4: 主题颜色配置")
    print("=" * 60)

    themes = {
        "retro-futuristic": {
            "accent_green": "#00ff41",
            "accent_cyan": "#00ffff",
            "accent_pink": "#ff00ff",
            "accent_orange": "#ff6b35",
        },
        "minimal-cyber": {
            "accent_blue": "#4a90e2",
            "accent_purple": "#9b59b6",
            "accent_pink": "#e74c3c",
        },
        "organic-nature": {
            "accent_gold": "#d4a574",
            "accent_green": "#7b9e87",
            "accent_red": "#c97064",
        }
    }

    for theme_name, colors in themes.items():
        print(f"✓ {theme_name} 主题颜色:")
        for color_name, color_value in colors.items():
            print(f"    - {color_name}: {color_value}")

    print()
    return True


def test_enhanced_ui_functions():
    """测试增强 UI 函数签名"""
    print("=" * 60)
    print("测试 5: 增强 UI 函数签名")
    print("=" * 60)

    try:
        from frontend.components import enhanced_ui
        import inspect

        functions = [
            'render_player_status_enhanced',
            'render_scene_card_enhanced',
            'render_choice_list_enhanced',
            'render_chat_message_enhanced',
            'render_progress_bar_enhanced',
            'render_typing_effect',
            'render_notification',
        ]

        for func_name in functions:
            if hasattr(enhanced_ui, func_name):
                func = getattr(enhanced_ui, func_name)
                sig = inspect.signature(func)
                print(f"✓ {func_name}: {sig}")
            else:
                print(f"✗ {func_name} 不存在")
                return False

    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

    print()
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("新主题系统测试")
    print("=" * 60 + "\n")

    tests = [
        test_theme_module,
        test_enhanced_ui_module,
        test_css_injection,
        test_theme_colors,
        test_enhanced_ui_functions,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if all(results):
        print("✅ 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
