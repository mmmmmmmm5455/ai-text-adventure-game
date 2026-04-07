#!/usr/bin/env python
"""
配置检查脚本
快速检查 PostgreSQL 配置状态
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import get_settings


def check_config():
    """检查配置状态"""
    print("🔍 配置检查")
    print("=" * 50)

    # 1. 检查 .env 文件
    print("\n📄 检查 .env 文件...")
    env_file = Path(__file__).parent / ".env"

    if env_file.exists():
        print(f"✅ .env 文件存在：{env_file}")
    else:
        print("❌ .env 文件不存在")
        print("   请复制 .env.example 为 .env 并配置")
        return False

    # 2. 检查 DATABASE_URL
    print("\n🗄️️ 检查 DATABASE_URL...")
    settings = get_settings()

    if settings.database_url:
        print(f"✅ DATABASE_URL 已配置")
        # 隐藏密码
        url_parts = settings.database_url.split('@')
        if len(url_parts) == 2:
            user_part = url_parts[0]
            host_part = url_parts[1].split('/')[0]
            masked_url = f"{user_part}@***@{host_part}"
            print(f"   连接字符串：{masked_url}")
    else:
        print("❌ DATABASE_URL 未配置")
        print("   请在 .env 文件中添加：")
        print("   DATABASE_URL=postgresql://game_user:password@127.0.0.1:5432/text_adventure")

    # 3. 检查依赖
    print("\n📦 检查依赖...")
    try:
        import psycopg2
        print("✅ psycopg2-binary 已安装")
    except ImportError:
        print("❌ psycopg2-binary 未安装")
        print("   运行：pip install psycopg2-binary")

    try:
        from game.possession_db import PossessionDB
        print("✅ game.possession_db 模块可用")
    except ImportError as e:
        print(f"❌ game.possession_db 模块不可用：{e}")

    # 4. 检查数据库连接
    print("\n🔗 检查数据库连接...")
    if not settings.database_url:
        print("⏭️  跳过（DATABASE_URL 未配置）")
    else:
        try:
            import psycopg2
            conn = psycopg2.connect(settings.database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"✅ 数据库连接成功")
            print(f"   PostgreSQL 版本：{version[0]}")
        except Exception as e:
            print(f"❌ 数据库连接失败：{e}")
            print("   请检查：")
            print("   1. PostgreSQL 是否运行")
            print("   2. .env 配置是否正确")

    # 5. 总结
    print("\n" + "=" * 50)
    print("📋 配置检查完成")
    print("")
    print("💡 如果所有检查都通过，运行以下命令初始化数据库：")
    print("   python tools/init_database.py")
    print("")
    print("📚 详细说明：docs/POSTGRESQL_SETUP_GUIDE.md")

    return True


def main():
    """主函数"""
    import sys

    try:
        success = check_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__name__":
    main()
