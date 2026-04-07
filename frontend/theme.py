"""
AI 文字冒险游戏 - Retro-Futuristic 主题
复古未来主义 UI 设计风格
"""

from __future__ import annotations

import streamlit as st


def inject_css(theme: str = "retro-futuristic") -> None:
    """注入自定义 CSS 主题

    Args:
        theme: 主题名称 (retro-futuristic, minimal-cyber, organic-nature)
    """
    if theme == "retro-futuristic":
        _inject_retro_futuristic()
    elif theme == "minimal-cyber":
        _inject_minimal_cyber()
    elif theme == "organic-nature":
        _inject_organic_nature()
    else:
        _inject_retro_futuristic()


def _inject_retro_futuristic() -> None:
    """复古未来主义主题（80年代赛博朋克风格）"""
    st.markdown(
        """
<style>
  /* ====== Retro-Futuristic Theme ====== */

  /* 全局字体 */
  @import url('https://fonts.googleapis.com/css2?family=VT323&family=Orbitron:wght@400;700&display=swap');

  :root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a24;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent-green: #00ff41;
    --accent-orange: #ff6b35;
    --accent-pink: #ff00ff;
    --accent-cyan: #00ffff;
    --border-color: #2a2a35;
  }

  /* 主容器 */
  .stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    font-family: 'VT323', monospace;
  }

  /* 侧边栏 */
  div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    border-right: 2px solid var(--border-color);
  }

  /* 标题字体 */
  h1, h2, h3 {
    font-family: 'Orbitron', sans-serif;
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  /* 卡片样式 */
  .stCard {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    margin: 1rem 0;
  }

  /* 场景卡片 */
  .scene-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  }

  .scene-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    animation: scan-line 3s linear infinite;
  }

  @keyframes scan-line {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  .scene-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--accent-cyan);
    text-shadow: 0 0 10px var(--accent-cyan);
    animation: glow 2s ease-in-out infinite alternate;
  }

  @keyframes glow {
    from { text-shadow: 0 0 5px var(--accent-cyan), 0 0 10px var(--accent-cyan); }
    to { text-shadow: 0 0 10px var(--accent-cyan), 0 0 20px var(--accent-cyan), 0 0 30px var(--accent-cyan); }
  }

  .scene-body {
    line-height: 1.8;
    font-size: 1.1rem;
    color: var(--text-primary);
    white-space: pre-wrap;
  }

  /* 进度条 */
  .stProgress {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    overflow: hidden;
  }

  .stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  /* 按钮 */
  .stButton > button {
    background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-cyan) 100%);
    color: var(--bg-primary);
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 255, 65, 0.3);
  }

  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 255, 65, 0.5);
  }

  .stButton > button:active {
    transform: translateY(0);
  }

  /* 输入框 */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-family: 'VT323', monospace;
  }

  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 10px var(--accent-cyan);
  }

  /* 消息气泡 */
  .chat-message {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    position: relative;
    overflow: hidden;
  }

  .chat-message.user {
    border-left: 3px solid var(--accent-green);
  }

  .chat-message.assistant {
    border-left: 3px solid var(--accent-pink);
  }

  /* 选择列表 */
  .choice-list {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
  }

  .choice-item {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .choice-item:hover {
    border-color: var(--accent-green);
    transform: translateX(10px);
    box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
  }

  .choice-item::before {
    content: '>';
    position: absolute;
    left: 0.5rem;
    color: var(--accent-green);
    font-weight: 700;
    animation: blink 1s infinite;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  /* 任务列表 */
  .quest-item {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-left: 3px solid var(--accent-orange);
  }

  .quest-item.completed {
    border-left-color: var(--accent-green);
    opacity: 0.6;
  }

  /* 属性显示 */
  .stat-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    border-bottom: 1px solid var(--border-color);
  }

  .stat-name {
    color: var(--accent-cyan);
    font-weight: 700;
  }

  .stat-value {
    color: var(--accent-green);
    font-weight: 700;
  }

  /* 扫描线效果 */
  .scanline-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.1) 0px,
      rgba(0, 0, 0, 0.1) 1px,
      transparent 1px,
      transparent 2px
    );
    z-index: 9999;
  }

  /* 闪烁光标 */
  .cursor-blink {
    display: inline-block;
    width: 10px;
    height: 20px;
    background: var(--accent-green);
    animation: cursor-blink 1s infinite;
    margin-left: 2px;
  }

  @keyframes cursor-blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  /* 噪点效果 */
  .noise-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
    z-index: 9998;
  }
</style>

<div class="scanline-overlay"></div>
<div class="noise-overlay"></div>
        """,
        unsafe_allow_html=True,
    )


def _inject_minimal_cyber() -> None:
    """极简赛博风格（现代科技感）"""
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;700&display=swap');

  :root {
    --bg-primary: #0d0d14;
    --bg-secondary: #14141e;
    --bg-card: #1a1a2e;
    --text-primary: #f0f0f0;
    --text-secondary: #888899;
    --accent-blue: #4a90e2;
    --accent-purple: #9b59b6;
    --accent-pink: #e74c3c;
    --border-color: #2a2a3e;
  }

  .stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    font-family: 'Rajdhani', sans-serif;
  }

  div[data-testid="stSidebar"] {
    background: var(--bg-secondary);
    border-right: 2px solid var(--border-color);
  }

  .scene-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  }

  .scene-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: var(--accent-blue);
    text-transform: uppercase;
    letter-spacing: 3px;
  }

  .scene-body {
    line-height: 1.9;
    font-size: 1.15rem;
    color: var(--text-primary);
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def _inject_organic_nature() -> None:
    """有机自然风格（温暖柔和）"""
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

  :root {
    --bg-primary: #1a1814;
    --bg-secondary: #242018;
    --bg-card: #2d2820;
    --text-primary: #e8e0d8;
    --text-secondary: #a89888;
    --accent-gold: #d4a574;
    --accent-green: #7b9e87;
    --accent-red: #c97064;
    --border-color: #3d3628;
  }

  .stApp {
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    color: var(--text-primary);
    font-family: 'Lora', serif;
  }

  div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    border-right: 2px solid var(--border-color);
  }

  .scene-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .scene-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: var(--accent-gold);
    font-family: 'Cormorant Garamond', serif;
  }

  .scene-body {
    line-height: 1.9;
    font-size: 1.15rem;
    color: var(--text-primary);
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_selector() -> str:
    """渲染主题选择器

    Returns:
        选中的主题名称
    """
    st.sidebar.markdown("### 🎨 主题风格")
    theme = st.sidebar.selectbox(
        "选择主题",
        ["retro-futuristic", "minimal-cyber", "organic-nature"],
        format_func=lambda x: {
            "retro-futuristic": "🕹️ 复古未来主义",
            "minimal-cyber": "⚡ 极简赛博",
            "organic-nature": "🌿 有机自然"
        }.get(x, x)
    )
    return theme
