#!/usr/bin/env python
"""
数据库初始化脚本
一键初始化 PostgreSQL 数据库，创建表、索引、触发器和存储过程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.config import get_settings


def init_database():
    """初始化数据库"""
    print("🗄️️  初始化数据库...")
    print("=" * 50)

    # 1. 检查环境变量
    settings = get_settings()

    if not settings.database_url:
        print("❌ DATABASE_URL 未配置")
        print("")
        print("请在 .env 文件中设置 DATABASE_URL")
        print("")
        print("示例：")
        print("DATABASE_URL=postgresql://game_user:password@127.0.1:5432/text_adventure")
        print("")
        print("配置步骤：")
        print("1. 安装 PostgreSQL")
        print("2. 创建数据库和用户")
        print("3. 配置 .env 文件（见 docs/POSTGRESQL_SETUP_GUIDE.md）")
        print("")
        print("详细说明：docs/POSTGRESQL_SETUP_GUIDE.md")
        return False

    print(f"✅ DATABASE_URL 已配置：{settings.database_url}")

    # 2. 连接数据库
    try:
        import psycopg2
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        print("")
        print("请检查：")
        print("1. PostgreSQL 是否正在运行")
        print("2. DATABASE_URL 是否正确")
        print("3. 用户名和密码是否正确")
        return False

    # 3. 读取迁移脚本
    migrations_dir = Path(__file__).parent / "database" / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("⚠️  未找到迁移脚本，跳过")
    else:
        print(f"📜 找到 {len(migration_files)} 个迁移脚本：")
        for sql_file in migration_files:
            print(f"  - {sql_file.name}")

    # 4. 执行迁移脚本
    for sql_file in migration_files:
        print(f"\n📜 执行迁移脚本：{sql_file.name}")

        try:
            # 读取 SQL 文件
            sql_content = sql_file.read_text(encoding="utf-8")

            # 分割 SQL 语句
            sql_statements = []
            current_statement = []
            for line in sql_content.split('\n'):
                line = line.strip()

                # 跳过注释
                if line.startswith('--'):
                    continue

                # 分离语句
                if line.endswith(';'):
                    current_statement.append(line)
                    if current_statement:
                        sql_statements.append(' '.join(current_statement))
                        current_statement = []
                else:
                    if current_statement or line:
                        current_statement.append(line)

            # 执行 SQL 语句
            for sql in sql_statements:
                sql = sql.strip()
                if sql:
                    cursor.execute(sql)
                    conn.commit()

            print(f"  ✅ {sql_file.name} 执行成功")

        except Exception as e:
            print(f"  ❌ {sql_file.name} 执行失败：{e}")
            conn.rollback()
            return False

    # 5. 验证表创建
    print("\n📊 验证表创建...")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()

    print(f"  已创建 {len(tables)} 个表：")
    for table in tables:
        table_name = table[0]
        print(f"    ✅ {table_name}")

    # 6. 测试奪舍系统
    print("\n🎭 测试奪舍系统...")
    try:
        from game.possession_db import PossessionDB

        db = PossessionDB()
        print("  ✅ PossessionDB 初始化成功")

        # 测试列出可奪舍的快照
        snapshots = db.list_claimable_snapshots()
        print(f"  ✅ 可奪舍的快照数量：{len(snapshots)}")

    except Exception as e:
        print(f"  ⚠️ 奪舍系统测试失败（可能预期）：{e}")
        print("  这是正常的，因为数据库中还没有数据")

    # 7. 完成
    cursor.close()
    conn.close()

    print("\n✅ 数据库初始化完成！")
    print("")
    print("下一步：")
    print("  1. 测试游戏：python -m streamlit run frontend/app.py")
    print("  2. 测试奪舍：python tools/possession_cli.py list")
    print("  3. 查看文档：docs/POSTGRESQL_SETUP_GUIDE.md")

    return True


def main():
    """主函数"""
    import sys

    try:
        success = init_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
