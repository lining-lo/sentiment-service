from loguru import logger
from typing import Any

from sentiment.engines.contract.events import EventType, subscribe, unsubscribe
from sentiment.engines.host_agent.section_ready_listener import SectionReadyListener
from sentiment.app.services.host.discuss_buffer import DiscussionBuffer


class HostService:

    def __init__(self):
        """初始化研判监听器与讨论缓冲区"""
        self._listener = SectionReadyListener()
        self.discussion_buffer = DiscussionBuffer()

    def register_discussion_buffer(self):
        """注册主持人讨论消息监听"""
        subscribe(EventType.HOST_DISCUSSION_MESSAGE, self._on_discussion_message)

    def stop_discussion_buffer(self):
        """注销主持人讨论消息监听"""
        unsubscribe(self._on_discussion_message)

    def _on_discussion_message(self, _event_type: EventType, data: dict[str, Any]):
        """将主持人讨论消息写入缓冲区"""
        self.discussion_buffer.append_message(data)

    def get_discussion_records(self, task_id: str) -> dict[str, Any]:
        """获取指定任务的主持人讨论记录"""
        return self.discussion_buffer.read_messages(task_id)

    def register_host_listener(self):
        """注册并启动 Host 研判监听器"""
        self._listener.start()
        logger.info("HostService: 研判引擎启动成功")

    def stop_host_listener(self):
        """停止 Host 研判监听器"""
        self._listener.stop()
        logger.info("HostService: 研判引擎已停止")
