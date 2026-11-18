from enum import Enum
from typing import Any, Callable, Literal, Mapping

from loguru import logger
from pydantic import BaseModel

from sentiment.engines.contract.agent_role import display_agent_name


class EventType(str, Enum):
    """研究流程中可发布的事件类型"""

    # 研究 Agent（insight/media）完成一个章节时发布，由 Host 监听并触发研判
    SECTION_READY = "section_ready"
    # Host 讨论区消息（Agent 章节输出、主持人裁决等）发布给前端/事件流
    HOST_DISCUSSION_MESSAGE = "host_discussion_message"


class SectionReadyEvent(BaseModel):
    """章节就绪事件：表示某个 Agent 已产出一个章节的正文"""

    # 所属任务，Host 用它区分并累积不同运行的状态
    task_id: str
    # 产出方角色，对应 RoleKey，值为 "insight" 或 "media"
    source: str
    # 章节标识，与 SECTION_DEFINITIONS 的 key 对应
    section_key: str
    # 该章节正文（Markdown）
    body: str


class HostDiscussionMessageEvent(BaseModel):
    """Host 讨论消息事件：统一承载各角色在讨论区展示的内容"""

    task_id: str
    # 消息来源：两个研究 Agent 或主持人本身
    source: Literal["insight", "media", "host"]
    # 展示内容（章节正文摘要或主持人裁决 Markdown）
    content: str
    # 关联章节，便于前端按章节聚合讨论
    section_key: str


# 订阅回调约定：参数为 (事件类型, 事件载荷 dict)，必须是同步、非阻塞的
EventCallback = Callable[[EventType, dict[str, Any]], None]

# 进程内事件注册表：事件类型 -> 回调集合（set 天然去重，但无顺序保证）
_subscribers: dict[EventType, set[EventCallback]] = {}


def subscribe(event_type: EventType, callback: EventCallback):
    """为指定事件类型注册订阅回调"""
    # setdefault 保证首次订阅时初始化该事件类型的回调集合
    _subscribers.setdefault(event_type, set()).add(callback)


def publish(event_type: EventType, data: dict[str, Any]):
    """向指定事件类型的所有订阅者发布数据"""
    # 拷贝成 list 再遍历：允许回调在执行过程中取消订阅而不影响本次分发
    for callback in list(_subscribers.get(event_type)):
        try:
            callback(event_type, data)
        except Exception as exc:
            # 单个订阅者异常只记录日志，不中断其他订阅者
            logger.error(f"事件订阅者执行失败：{exc}")


def unsubscribe(callback: EventCallback):
    """从所有事件类型中移除指定订阅回调"""
    # 只按回调本身注销，因此会清理它在所有事件类型下的注册
    for subscribers in _subscribers.values():
        subscribers.discard(callback)


def publish_section_ready(
        state: Mapping[str, Any],
        section: Mapping[str, Any]
):
    """从研究 Agent 图状态构造并发布章节就绪事件"""
    # 从图状态中取角色与任务信息；角色同时作为事件来源标识
    role = state["role"]
    agent_name = display_agent_name(role)
    event = SectionReadyEvent(
        task_id=state["task_id"],
        source=role,
        section_key=section["section_key"],
        body=section.get("body")
    )
    # 序列化为普通 dict 后广播，避免订阅者直接依赖 Pydantic 模型
    publish(EventType.SECTION_READY, event.model_dump())
    logger.info(f"【{agent_name}】 发布 [章节{event.section_key}] 事件,内容={event.body[:20]}...")


def publish_host_discussion_message(event: HostDiscussionMessageEvent):
    """发布主持人讨论消息事件"""
    # 统一走 publish 分发，订阅方负责推送到 WebSocket/SSE 等通道
    publish(EventType.HOST_DISCUSSION_MESSAGE, event.model_dump())
