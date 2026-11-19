"""研究进度 SSE 事件流"""

import asyncio
import json

from loguru import logger

from sentiment.engines.contract.events import EventType, subscribe, unsubscribe


class ResearchProgressStream:
    """订阅角色进度、结果和错误事件，并推送给在线 SSE 客户端"""

    FORWARDED_EVENT_TYPES = (
        EventType.ROLE_PROGRESS,
        EventType.ROLE_RESULT,
        EventType.ROLE_ERROR
    )

    def __init__(self):
        """初始化 SSE 客户端订阅队列池"""

        # 1. 按研究任务存储活跃客户端的异步事件队列
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    def register_progress_update(self):
        """向全局事件总线注册研究进度事件监听"""

        # 1. 遍历关注的事件类型，将转发方法绑定到事件中心
        for event_type in self.FORWARDED_EVENT_TYPES:
            subscribe(event_type, self._broadcast_progress_update)

    def stop_progress_update(self):
        """注销事件监听并清空 SSE 客户端订阅队列"""

        # 1. 从事件中心注销当前转发函数
        unsubscribe(self._broadcast_progress_update)
        # 2. 清空所有客户端队列以释放连接
        self._subscribers.clear()

    def _broadcast_progress_update(
            self,
            event_type: EventType,
            data: dict
    ):
        """将事件总线中的研究进度事件转发给当前在线客户端。"""

        # 1. 将原生事件字典序列化为 JSON 字符串
        payload = json.dumps({"event": event_type, "data": data}, ensure_ascii=False)

        # 3. 仅将事件推送给订阅当前研究任务的客户端
        #    该任务可能还没有客户端连接，get 缺省值避免对 None 做迭代
        for queue in list(self._subscribers.get(data['task_id'], ())):
            queue.put_nowait(payload)

    async def stream_research_progress(self, request, task_id: str):
        """管理 SSE 客户端连接并持续推送研究进度事件"""

        # 1. 为当前连接创建专属异步队列
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(task_id, set()).add(queue)
        logger.debug(f"SSE 客户端连接: task_id={task_id}")

        try:
            # 2. 首先向客户端推送连接成功消息
            yield {"event": "connected", "data": json.dumps({"status": "connected"})}

            # 3. 等待并消费当前连接队列中的实时事件
            while True:
                if await request.is_disconnected():
                    break
                payload = await queue.get()
                yield {"data": payload}
        finally:
            # 4. 客户端断开时移除对应队列
            #    stop_progress_update 可能已清空池，缺省值避免 None.discard
            self._subscribers.get(task_id, set()).discard(queue)
        logger.debug(f"SSE 客户端关闭: task_id={task_id}")
