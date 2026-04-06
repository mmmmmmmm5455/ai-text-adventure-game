# 中文教程：如何打开 / 运行游戏

本游戏是 **Streamlit 网页应用**。启动后，用浏览器打开即可游玩，无需单独安装「游戏客户端」。

---

## 你需要什么

- **Python 3.9+**（已安装并加入 PATH，或使用虚拟环境 `.venv`）
- 已安装依赖：`pip install -r requirements.txt`
- （可选）**Ollama**：用于更好的 AI 场景与对话；不装也能玩，会使用离线降级文案

---

## 方法一：命令行启动（推荐）

在**项目根目录**（包含 `frontend` 文件夹的那一层）打开 PowerShell 或 CMD：

### Windows PowerShell

```powershell
cd "D:\你的路径\ai_text_advanture_game"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
python -m streamlit run frontend/app.py
```

若未使用虚拟环境，把第三行改成全局 Python，或确保 `python` 指向正确环境。

### 成功后的样子

终端里会出现类似：

```text
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

### 打开游戏

在浏览器地址栏输入：

**[http://localhost:8501](http://localhost:8501)**

按回车即可。同一台电脑用手机/平板访问同一局域网时，也可用终端里显示的 **Network URL**（若 Streamlit 打印了）。

---

## 方法二：双击 `start.bat`（Windows）

1. 在资源管理器中进入项目根目录  
2. 双击 **`start.bat`**  

脚本会设置 `PYTHONPATH`、`PYTHONIOENCODING`，并执行 `python -m streamlit run frontend\app.py`。

然后在浏览器打开：**http://localhost:8501**

---

## 方法三：Docker

在项目根目录执行：

```bash
docker compose up --build
```

构建完成后，浏览器打开：**http://localhost:8501**

**说明：** Ollama 默认假设在**宿主机**运行；`docker-compose.yml` 里已配置 `OLLAMA_BASE_URL` 指向 `host.docker.internal`（Docker Desktop 下 Windows/Mac 常用）。若容器内仍是离线文案，请检查宿主 Ollama 是否已启动、模型是否已拉取，详见 `docs/ARCHITECTURE_POLICY.md`。

---

## 停止游戏

- 在运行 Streamlit 的终端里按 **`Ctrl + C`**  
- Docker 方式：在终端按 **`Ctrl + C`** 或执行 `docker compose down`

---

## 常见问题

### 1. 浏览器打不开 / 连接被拒绝

- 确认终端里 Streamlit **没有报错退出**  
- 确认地址是 **http://localhost:8501**（注意 `http`，不是 `https`）  
- 若 8501 被占用，可在启动命令后加参数：  
  `python -m streamlit run frontend/app.py --server.port 8502`  
  然后访问 **http://localhost:8502**

### 2. 提示找不到模块 / 无法导入 `game`

- 必须在**项目根目录**运行，且设置 **`PYTHONPATH`** 为项目根（方法一、方法二已处理）  
- 推荐始终使用：`python -m streamlit run frontend/app.py`，不要只 `streamlit run` 且工作目录错误

### 3. 界面里全是「离线」占位文字

- 未安装或未启动 **Ollama**，或模型未下载：在项目目录外执行 `ollama pull llama3`、`ollama pull nomic-embed-text`  
- 安装并启动 Ollama 后，回到游戏点「刷新场景描写」再试

### 3b. 终端里 `UnicodeEncodeError` / `cp950`（Windows）

- 已在 `frontend/app.py` 与测试里尽量把 stdout 设为 UTF-8；若仍报错，请像上面那样设置 **`PYTHONIOENCODING=utf-8`**，或使用 **`start.bat`**。  
- **连接超时**：可在 `.env` 里调整 `OLLAMA_CONNECT_TIMEOUT`（秒），连接失败时更快走降级，不必长时间卡住。

### 4. 第一次进入要填 Email

- Streamlit 有时会提示 Email，**直接按回车跳过**即可

---

## 游戏内怎么开始

1. 浏览器打开 **http://localhost:8501**  
2. 左侧或中间按提示 **创建角色**（名字、职业、性别）  
3. 点 **开始冒险**  
4. 在 **探索** 里移动、与 NPC 交谈、使用广场/旅店等功能  

存档与数据默认在项目下的 **`data`** 目录（见 `README.md` 与存档说明）。

---

## 与测试命令的区别

- **打开游戏**：`python -m streamlit run frontend/app.py`（并设置 `PYTHONPATH`）→ 用浏览器玩  
- **跑自动化测试**：`python -m pytest tests -q` → 不打开浏览器，只验证代码  

两者不要混淆。
