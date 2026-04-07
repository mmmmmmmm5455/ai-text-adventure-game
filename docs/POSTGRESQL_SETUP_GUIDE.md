# 📖 PostgreSQL 数据库配置指南

**项目：** AI 文字冒险游戏  
**用途：** 奪舍系统和存档系统  
**日期：** 2026年4月7日

---

## 📋 概述

本指南帮助你在本地配置 PostgreSQL 数据库，启用游戏的高级功能（奪舍系统、存档管理）。

**数据库需求：**
- 数据库版本：PostgreSQL 11+
- 所需功能：UUID、JSONB、触发器、函数
- 数据库大小：初始 < 10 MB

---

## 🔧 安装 PostgreSQL

### Windows

#### 方法 1：使用 PostgreSQL Installer（推荐）

1. **下载 PostgreSQL Installer**
   - 访问：https://www.postgresql.org/download/windows/
   - 下载最新版本的 PostgreSQL Installer（例如：postgresql-15.x.x-x64.exe）

2. **运行安装程序**
   - 双击安装程序
   - 选择安装路径：`C:\Program Files\PostgreSQL\15\`
   - 设置密码（记住这个密码！）
   - 端口：5432（默认）
   - 点击 "Next" 完成安装

3. **验证安装**
   - 打开命令提示符（CMD 或 PowerShell）
   - 输入：`psql --version`
   - 应该显示版本号，例如：`psql (PostgreSQL) 15.x`

#### 方法 2：使用 Chocolatey（简化安装）

1. **安装 Chocolatey**（如果还没有）
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::InstallPackageByName('chocolatey')
   ```

2. **安装 PostgreSQL**
   ```powershell
   choco install postgresql
   ```

---

### macOS

#### 使用 Homebrew（推荐）

```bash
brew install postgresql
```

#### 使用 PostgreSQL Installer

1. 下载：https://www.postgresql.org/download/macosx/
2. 安装并启动

---

### Linux (Ubuntu/Debian)

```bash
# 更新包列表
sudo apt-get update

# 安装 PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 启动 PostgreSQL 服务
sudo service postgresql start

# 设置 postgres 用户密码
sudo -u postgres psql
\password
# 输入新密码两次
\q
```

---

## 🗄️ 创建数据库和用户

### 连接到 PostgreSQL

**Windows/macOS:**
```bash
psql -U postgres
```

**Linux:**
```bash
sudo -u postgres psql
```

### 执行 SQL 命令

```sql
-- 创建数据库
CREATE DATABASE text_adventure;

-- 创建用户
CREATE USER game_user WITH PASSWORD 'your_secure_password_here';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE text_adventure TO game_user;

-- 退出
\q
```

**⚠️ 重要：**
- 将 `your_secure_password_here` 替换为强密码
- 记住这个密码，稍后需要配置到 .env 文件

---

## 🔧 安装 Python 依赖

### 激活虚拟环境

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 安装依赖

```bash
pip install psycopg2-binary
```

---

## 📝 配置 .env 文件

### 创建或编辑 .env 文件

在项目根目录创建 `.env` 文件：

```env
# Ollama 配置
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_TIMEOUT=15.0
OLLAMA_CONNECT_TIMEOUT=3.0
LLM_CACHE_ENABLED=true

# PostgreSQL 数据库配置
DATABASE_URL=postgresql://game_user:your_secure_password_here@127.0.0.1:5432/text_adventure

# 数据库信息
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=text_adventure
DB_USER=game_user
DB_PASSWORD=your_secure_password_here
```

**⚠️ 重要：**
- 将 `your_secure_password_here` 替换为你设置的数据库密码
- 确保 DATABASE_URL 格式正确
- .env 文件不要提交到 Git（已添加到 .gitignore）

---

## 🧪 验证数据库连接

### 运行数据库初始化脚本

```bash
python tools/init_database.py
```

如果一切正常，你应该看到：
```
🗄️️  初始化数据库...
✅ DATABASE_URL 已配置：postgresql://game_user:***@127.0.0.1:5432/text_adventure
✅ 数据库初始化完成！
```

### 手动测试连接

创建测试脚本 `test_db_connection.py`：

```python
import psycopg2
from core.config import get_settings

def test_db_connection():
    """测试数据库连接"""
    settings = get_settings()
    
    if not settings.database_url:
        print("❌ DATABASE_URL 未配置")
        return False
    
    try:
        # 连接数据库
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 数据库连接成功")
        print(f"   PostgreSQL 版本：{version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
        return False

if __name__ == "__main__":
    test_db_connection()
```

运行测试：
```bash
python test_db_connection.py
```

预期输出：
```
✅ 数据库连接成功
   PostgreSQL 版本：15.x
```

---

## 🚀 常见问题排查

### 问题 1：连接被拒绝

**错误信息：**
```
connection refused
```

**解决方案：**
1. 检查 PostgreSQL 服务是否运行
   - Windows：在服务管理器中查看 postgresql-x64-15 服务
   - macOS：`brew services list | grep postgres`
   - Linux：`sudo service postgresql status`

2. 检查端口是否正确
   - 默认端口：5432
   - Windows：检查防火墙设置
   - macOS/Linux：检查 `sudo ufw allow 5432/tcp`

3. 检查用户名和密码是否正确
   - 用户名：game_user
   - 密码：你设置的密码

---

### 问题 2：找不到数据库

**错误信息：**
```
database "text_adventure" does not exist
```

**解决方案：**
1. 连接到 PostgreSQL
```bash
psql -U postgres
```

2. 查看数据库列表
```sql
\l
```

3. 如果不存在，创建数据库
```sql
CREATE DATABASE text_adventure;
```

4. 授予权限
```sql
GRANT ALL PRIVILEGES ON DATABASE text_adventure TO game_user;
```

---

### 问题 3：认证失败

**错误信息：**
```
password authentication failed
```

**解决方案：**
1. 确认密码正确
2. 重置密码
```bash
psql -U postgres
ALTER USER game_user WITH PASSWORD 'new_password';
```

3. 更新 .env 文件中的密码
```env
DATABASE_URL=postgresql://game_user:new_password@127.0.0.1:5432/text_adventure
```

---

## 📊 数据库架构说明

### 主要表

#### possession_snapshots
存储角色奪舍快照

#### possession_history
存储奪舍历史记录

### 初始化脚本

初始化脚本会自动：
1. 创建所有必需的表
2. 创建索引
3. 创建触发器
4. 创建函数
5. 创建存储过程

运行：
```bash
python tools/init_database.py
```

---

## 🔐 安全建议

### 密码管理

1. **使用强密码**
   - 至少 12 个字符
   - 包含大小写字母、数字、特殊字符
   - 避免使用常见密码

2. **不要提交密码到 Git**
   - .env 文件已添加到 .gitignore
   - 不要包含密码在代码中
   - 使用环境变量

3. **定期更换密码**
   - 每 3-6 个月更换一次
   - 使用密码管理器

---

## 📝 环境变量

### 必需环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|---------|
| DATABASE_URL | 数据库连接字符串 | `postgresql://user:password@host:port/database` |
| DB_HOST | 数据库主机 | `127.0.0.1` |
| DB_PORT | 数据库端口 | `5432` |
| DB_NAME | 数据库名称 | `text_adventure` |
| DB_USER | 数据库用户名 | `game_user` |
| DB_PASSWORD | 数据库密码 | `your_secure_password_here` |

### 可选环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|---------|
| DB_POOL_SIZE | 连接池大小 | 5 |
| DB_MAX_OVERFLOW | 连接池最大溢出 | 10 |
| DB_POOL_TIMEOUT | 连接池超时（秒） | 30 |

---

## 🎯 下一步

### 运行初始化脚本

```bash
cd ai_text_advanture_game
python tools/init_database.py
```

### 测试奪舍系统

```python
from game.possession_db import PossessionDB

db = PossessionDB()
snapshots = db.list_claimable_snapshots()
print(f"可奪舍的快照数量：{len(snapshots)}")
```

---

## 📚 相关文档

- **数据库架构：** `database/migrations/001_possession_system.sql`
- **奪舍系统设计：** `docs/possession/GAME_DESIGN_DOCUMENT.md`
- **TODO 列表：** `TODO.md`

---

## ✅ 配置检查清单

在完成配置前，请确认：

- [ ] PostgreSQL 已安装并运行
- [ ] 数据库 `text_adventure` 已创建
- [ ] 用户 `game_user` 已创建并授权
- [ ] `.env` 文件已配置 DATABASE_URL
- [ ] `psycopg2-binary` 已安装
- [ ] 运行 `python tools/init_database.py` 成功
- [ ] 运行 `python test_db_connection.py` 测试连接

---

**配置完成后，你的游戏就可以使用奪舍系统和高级存档功能了！** 🎉

---

**配置支持：** 如有问题，请查看 `docs/possession/GAME_DESIGN_DOCUMENT.md` 或 `docs/possession/README.md`  
**创建日期：** 2026年4月7日  
**文档版本：** 1.0
