"""
并行请求处理器
支持异步 LLM 调用和批量并行处理
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar, Awaitable
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from loguru import logger


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class AsyncTask:
    """异步任务"""
    id: str
    func: Callable[..., T] | Callable[..., Awaitable[T]]
    args: tuple
    kwargs: dict
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: T | None = None
    error: Exception | None = None
    status: str = "pending"  # pending, running, completed, failed


class ParallelExecutor:
    """并行执行器"""

    def __init__(
        self,
        max_workers: int = 4,
        timeout: float | None = None,
        name: str = "parallel_executor"
    ):
        self._max_workers = max_workers
        self._timeout = timeout
        self._name = name
        self._tasks: list[AsyncTask] = []

    def submit(
        self,
        task_id: str,
        func: Callable[..., T] | Callable[..., Awaitable[T]],
        *args,
        **kwargs
    ) -> None:
        """提交任务

        Args:
            task_id: 任务 ID
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        task = AsyncTask(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            created_at=datetime.now()
        )
        self._tasks.append(task)
        logger.debug(f"提交任务: {task_id}")

    def execute_sync(self) -> dict[str, Any]:
        """同步执行所有任务

        Returns:
            任务结果字典 {task_id: result}
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for task in self._tasks:
                task.status = "pending"
                future = executor.submit(self._run_task, task)
                future_to_task[future] = task

            # 等待所有任务完成
            for future in as_completed(future_to_task, timeout=self._timeout):
                task = future_to_task[future]
                try:
                    task.result = future.result()
                    task.completed_at = datetime.now()
                    task.status = "completed"
                    results[task.id] = task.result
                except Exception as e:
                    task.error = e
                    task.completed_at = datetime.now()
                    task.status = "failed"
                    results[task.id] = None
                    logger.error(f"任务 {task.id} 失败: {e}")

        return results

    async def execute_async(self) -> dict[str, Any]:
        """异步执行所有任务

        Returns:
            任务结果字典 {task_id: result}
        """
        results = {}

        # 创建任务协程
        async def run_task_async(task: AsyncTask):
            try:
                task.status = "running"
                task.started_at = datetime.now()

                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    # 同步函数在事件循环中运行
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)

                task.result = result
                task.completed_at = datetime.now()
                task.status = "completed"
                return task.id, result
            except Exception as e:
                task.error = e
                task.completed_at = datetime.now()
                task.status = "failed"
                logger.error(f"任务 {task.id} 失败: {e}")
                return task.id, None

        # 并行执行所有任务
        tasks = [run_task_async(task) for task in self._tasks]
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # 收集结果
        for task_result in completed_tasks:
            if isinstance(task_result, Exception):
                logger.error(f"任务异常: {task_result}")
            else:
                task_id, result = task_result
                results[task_id] = result

        return results

    def _run_task(self, task: AsyncTask) -> Any:
        """运行单个任务（内部方法）"""
        try:
            task.status = "running"
            task.started_at = datetime.now()
            result = task.func(*task.args, **task.kwargs)
            return result
        except Exception as e:
            raise

    def get_stats(self) -> dict[str, Any]:
        """获取执行统计

        Returns:
            统计信息字典
        """
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.status == "completed")
        failed = sum(1 for t in self._tasks if t.status == "failed")
        pending = sum(1 for t in self._tasks if t.status == "pending")

        # 计算总耗时
        if completed > 0:
            total_time = max(
                (t.completed_at - t.created_at).total_seconds()
                for t in self._tasks
                if t.completed_at is not None
            )
        else:
            total_time = 0.0

        return {
            "name": self._name,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "total_time_seconds": total_time,
            "success_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%",
        }

    def clear(self) -> None:
        """清空任务列表"""
        self._tasks.clear()


class ParallelLLMClient:
    """并行 LLM 客户端"""

    def __init__(
        self,
        llm_client,
        max_concurrent: int = 3,
        timeout: float = 30.0
    ):
        self._llm_client = llm_client
        self._max_concurrent = max_concurrent
        self._timeout = timeout
        self._executor = ParallelExecutor(
            max_workers=max_concurrent,
            timeout=timeout,
            name="parallel_llm"
        )

    def generate_batch(
        self,
        prompts: list[tuple[str, str]],
        async_mode: bool = False
    ) -> dict[str, str]:
        """批量生成文本

        Args:
            prompts: (task_id, prompt) 元组列表
            async_mode: 是否使用异步模式

        Returns:
            生成结果字典 {task_id: result}
        """
        # 提交所有任务
        for task_id, prompt in prompts:
            self._executor.submit(
                task_id,
                self._llm_client.generate_text,
                prompt
            )

        # 执行任务
        if async_mode:
            # 异步执行
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(self._executor.execute_async())
        else:
            # 同步执行
            results = self._executor.execute_sync()

        return results

    def embed_batch(
        self,
        texts: list[tuple[str, str]],
        async_mode: bool = False
    ) -> dict[str, list[float] | None]:
        """批量生成嵌入

        Args:
            texts: (task_id, text) 元组列表
            async_mode: 是否使用异步模式

        Returns:
            嵌入结果字典 {task_id: embedding}
        """
        from engine.llm_client import ollama_embed_text

        # 提交所有任务
        for task_id, text in texts:
            self._executor.submit(
                task_id,
                ollama_embed_text,
                text
            )

        # 执行任务
        if async_mode:
            # 异步执行
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(self._executor.execute_async())
        else:
            # 同步执行
            results = self._executor.execute_sync()

        return results

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典
        """
        return self._executor.get_stats()


def parallel_execute(
    funcs: list[tuple[str, Callable, tuple, dict]],
    max_workers: int = 4,
    async_mode: bool = False
) -> dict[str, Any]:
    """并行执行多个函数

    Args:
        funcs: (task_id, func, args, kwargs) 元组列表
        max_workers: 最大工作线程数
        async_mode: 是否使用异步模式

    Returns:
        执行结果字典 {task_id: result}
    """
    executor = ParallelExecutor(
        max_workers=max_workers,
        name="parallel_execute"
    )

    # 提交所有任务
    for task_id, func, args, kwargs in funcs:
        executor.submit(task_id, func, *args, **kwargs)

    # 执行任务
    if async_mode:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(executor.execute_async())
    else:
        results = executor.execute_sync()

    return results


async def parallel_execute_async(
    funcs: list[tuple[str, Callable, tuple, dict]],
    max_workers: int = 4
) -> dict[str, Any]:
    """并行执行多个函数（异步版本）

    Args:
        funcs: (task_id, func, args, kwargs) 元组列表
        max_workers: 最大工作线程数

    Returns:
        执行结果字典 {task_id: result}
    """
    executor = ParallelExecutor(
        max_workers=max_workers,
        name="parallel_execute_async"
    )

    # 提交所有任务
    for task_id, func, args, kwargs in funcs:
        executor.submit(task_id, func, *args, **kwargs)

    # 异步执行
    results = await executor.execute_async()
    return results
