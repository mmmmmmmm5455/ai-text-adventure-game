"""自定义异常类型。"""


class GameEngineError(Exception):
    """引擎层通用错误。"""


class LLMUnavailableError(GameEngineError):
    """本地 LLM 不可用或调用失败。"""


class SaveLoadError(GameEngineError):
    """存档读写失败。"""
