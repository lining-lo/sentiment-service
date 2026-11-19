from enum import Enum
from typing import Any, Callable, Literal, Mapping

from loguru import logger
from pydantic import BaseModel

from sentiment.engines.contract.agent_role import display_agent_name, RoleInfo, RoleKey


class EventType(str, Enum):
    """研究流程中可发布的事件类型"""

    SECTION_READY = "section_ready"
    HOST_DISCUSSION_MESSAGE = "host_discussion_message"
    ROLE_PROGRESS = "role_progress"
    ROLE_ERROR = "role_error"
    ROLE_RESULT = "role_result"


class RoleProgressEvent(BaseModel):
    task_id: str
    role: str
    status: str
    message: str
    progress_pct: int = 0


class RoleResultEvent(BaseModel):
    task_id: str
    role: str


class RoleErrorEvent(BaseModel):
    task_id: str
    role: str
    error: str


class SectionReadyEvent(BaseModel):
    task_id: str
    source: str
    section_key: str
    body: str


class HostDiscussionMessageEvent(BaseModel):
    task_id: str
    source: Literal["insight", "media", "host"]
    content: str
    section_key: str


EventCallback = Callable[[EventType, dict[str, Any]], None]
_subscribers: dict[EventType, set[EventCallback]] = {}


def subscribe(event_type: EventType, callback: EventCallback):
    """为指定事件类型注册订阅回调"""
    _subscribers.setdefault(event_type, set()).add(callback)


def publish(event_type: EventType, data: dict[str, Any]):
    """向指定事件类型的所有订阅者发布数据"""
    # 该事件类型可能还没有订阅者，缺省值避免 list(None) 抛 TypeError
    for callback in list(_subscribers.get(event_type, ())):
        try:
            callback(event_type, data)
        except Exception as exc:
            logger.error(f"事件订阅者执行失败：{exc}")


def unsubscribe(callback: EventCallback):
    """从所有事件类型中移除指定订阅回调"""
    for subscribers in _subscribers.values():
        subscribers.discard(callback)


def publish_role_progress(event: RoleProgressEvent):
    """发布角色研究进度事件"""
    publish(EventType.ROLE_PROGRESS, event.model_dump())


def publish_role_result(event: RoleResultEvent):
    """发布角色研究结果事件"""
    publish(EventType.ROLE_RESULT, event.model_dump())


def publish_role_error(event: RoleErrorEvent):
    """发布角色研究错误事件"""
    publish(EventType.ROLE_ERROR, event.model_dump())


def publish_section_ready(
        section: Mapping[str, Any],
        role: RoleKey,
        task_id: str
):
    """从研究 Agent 图状态构造并发布章节就绪事件"""
    agent_name = display_agent_name(role)
    event = SectionReadyEvent(
        task_id=task_id,
        source=role,
        section_key=section["section_key"],
        body=section.get("body")
    )
    publish(EventType.SECTION_READY, event.model_dump())
    logger.info(f"【{agent_name}】 发布 [章节{event.section_key}] 事件,内容={event.body[:20]}...")


def publish_host_discussion_message(event: HostDiscussionMessageEvent):
    """发布主持人讨论消息事件"""
    publish(EventType.HOST_DISCUSSION_MESSAGE, event.model_dump())
