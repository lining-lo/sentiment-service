import asyncio
import uuid
from dataclasses import dataclass
from typing import Coroutine


@dataclass(slots=True)
class ResearchTask:
    """单次研究任务的数据记录。"""
    task_id: str
    query: str


class ResearchTaskManager:
    def __init__(self):
        # 1. 存储研究任务
        self.research_tasks: dict[str, ResearchTask] = {}
        # 2. 存储异步任务
        self.async_tasks: set[asyncio.Task] = set()

    def create_task(self, query: str) -> ResearchTask:
        # 1.创建研究任务
        research_task: ResearchTask = ResearchTask(query=query, task_id=str(uuid.uuid4()))
        # 2. 存储研究任务
        self.research_tasks[research_task.task_id] = research_task
        # 3. 返回研究对象
        return research_task

    def get_research_task(self, task_id: str) -> ResearchTask:
        # 1. 根据task_id 获取研究对象
        return self.research_tasks[task_id]

    def submit_task(self, coro: Coroutine):
        # 1. 创建异步任务
        task = asyncio.create_task(coro)
        # 2. 存储异步任务
        self.async_tasks.add(task)
        # 3. 异步任务执行完成之后，从容器中删除任务
        task.add_done_callback(self.async_tasks.discard)

    async def cancel_tasks(self):
        running_tasks = [task for task in self.async_tasks if not task.done()]

        for running_task in running_tasks:
            running_task.cancel()
        # 第二个参数表示 不会因为有一个任务异常，导致后面任务不执行
        return await asyncio.gather(*running_tasks, return_exceptions=True)

# 创建对象
research_task_manager = ResearchTaskManager()