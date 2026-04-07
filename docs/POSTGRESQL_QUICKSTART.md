# 🗄️️ PostgreSQL 数据库配置 - 快速开始

**项目：** AI 文字冒险游戏  
**文档类型：** 快速开始指南  
**状态：** ✅ 完成

---

## 🚀 5 分钟快速配置

### 第 1 步：安装 PostgreSQL（2-5 分钟）

**Windows：**
1. 下载 PostgreSQL Installer：https://www.postgresql.org/download/windows/
2. 双击安装，设置密码
3. 完成安装

**macOS：**
```bash
brew install postgresql
```

**Linux (Ubuntu)：**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

---

### 第 2 步：创建数据库（1 分钟）

连接到 PostgreSQL：
```bash
psql -U postgres
```

执行 SQL：
```sql
CREATE DATABASE text_adventure;
CREATE USER game_user WITH PASSWORD '你的密码';
GRANT ALL PRIVILEGES ON DATABASE text_adventure TO game_user;
\q
```

---

### 第 3 步：配置 .env 文件（1 分钟）

复制配置模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
DATABASE_URL=postgresql://game_user:你的密码@127.0.0.1:5432/text_adventure
```

**⚠️ 重要：**
- 将 `你的密码` 替换为你在第 2 步设置的密码
- 不要在配置中使用空密码或简单密码

---

### 第 4 步：安装 Python 依赖（30 秒）

```bash
pip install psycopg2-binary
```

---

### 第 5 步：初始化数据库（10 秒）

```bash
python tools/init_database.py
```

预期输出：
```
🗄️️  初始化数据库...
✅ DATABASE_URL 已配置：postgresql://game_user:***@127.0.0.1:5432/text_adventur
✅ 数据库连接成功
📜 找到 2 个迁移脚本：
  - 001_possession_system.sql
  - 002_possession_pool.sql
  ✅ 001_possession_system.sql 执行成功
  ✅ 002_possession_pool.sql 执行成功
📊 验证表创建...
  已创建 2 个表：
    ✅ possession_snapshots
    ✅ possession_history
🎭 测试奪舍系统...
  ✅ PossessionDB 初始化成功
  ✅ 可奪舍的快照数量：0
✅ 数据库初始化完成！
```

---

## ✅ 验证配置

运行检查脚本：
```bash
python tools/check_config.py
```

预期输出：
```
🔍 配置检查
==================================================
📄 检查 .env 文件...
✅ .env 文件存在：.../.env
🗄️️ 检查 DATABASE_URL...
✅ DATABASE_URL 已配置
   连接字符串：postgresql://game_user@***@127.0.0.1:5432/text_adventur
📦 检查依赖...
✅ psycopg2-binary 已安装
✅ game.possession_db 模块可用
🔗 检查数据库连接...
✅ 数据库连接成功
   PostgreSQL 版本：15.x
📋 配置检查完成

💡 如果所有检查都通过，运行以下命令初始化数据库：
   python tools/init_database.py

📚 详细说明：docs/POSTGRESQL_SETUP_GUIDE.md
```

---

## 🎯 测试奪舍系统

### 查看可奪舍的快照：

```bash
python tools/possession_cli.py list
```

### 查看奪舍历史：

```bash
python tools/possession_cli.py my <player_id>
```

### 奪舍一个快照：

```bash
python tools/possession_cli.py claim <snapshot_id> --name "你的名字" --gender "性别"
```

---

## 📚 更多文档

- **详细配置指南：** `docs/POSTGRESQL_SETUP_GUIDE.md`
- **奪舍系统设计：** `docs/possession/GAME_DESIGN_DOCUMENT.md`
- **TODO 列表：** `TODO.md`
- **README：** `README.md`

---

## 💡 常见问题

### Q1：如何跳过数据库配置？

**A:** 游戏支持离线降级模式（Ollama 不可用时使用），但奪舍系统需要数据库才能使用。

### Q2：可以不用 PostgreSQL 吗？

**A:** 可以使用 SQLite 替代，但需要修改代码。当前版本只支持 PostgreSQL。

### Q3：如何备份数据？

**A:**
```bash
pg_dump -U game_user text_adventure > backup.sql
```

### Q4：忘记密码了怎么办？

**A:** 重置密码：
```bash
psql -U postgres
ALTER USER game_user WITH PASSWORD '新密码';
```

---

## 🎉 完成！

现在你的游戏已经配置好了 PostgreSQL 数据库！🎉

**下一步：**
1. 启动游戏：`python -m streamlit run frontend/app.py`
2. 测试奪舍功能
3. 享受完整游戏体验！

---

**配置时间：** 约 5-10 分钟  
**难度：** 简单  
**支持平台：** Windows、macOS、Linux

**开始配置吧！** 🚀
