# 自定义世界

1. 在 `story/scenes.py`、`characters.py`、`items.py`、`quests.py`、`endings.py` 中增改数据。  
2. 在 `story/world_config.py` 中调整初始解锁场景与任务注册。  
3. 保持 `item_id` 与引擎内逻辑（如 `healing_potion`、`ancient_key`）一致，或同步修改 `engine/story_engine.py` 中的规则。  

无需修改 `frontend/` 即可替换大部分叙事内容。
