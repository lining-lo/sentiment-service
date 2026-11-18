import asyncio
from typing import Any

from loguru import logger

from sentiment.engines.common.research_tasks import research_task_manager
from sentiment.engines.contract.events import (
    EventType,
    publish_host_discussion_message,
    subscribe,
    unsubscribe
)
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.host_agent.graph import build_graph
from sentiment.engines.host_agent.section_judge import HostSectionJudge
from sentiment.engines.host_agent.section_pair_store import SectionPairStore
from sentiment.engines.host_agent.state import HostState


class SectionReadyListener:
    """串行消费章节就绪事件并驱动 Host LangGraph"""

    def __init__(self):
        """初始化 Host 图及任务状态存储"""
        # 每个监听器持有一张 Host 图（内部复用同一个研判器实例）
        self._graph = build_graph(HostSectionJudge())
        # 跨事件保留的按任务状态：task_id -> {task_id, section_pair_store, judgements}
        # 事件是逐个到达的，必须靠这里累积，配对/去重才能跨多次图调用生效
        self._host_states: dict[str, HostState] = {}
        # 在 start() 中创建；这里只声明类型
        self._event_queue: asyncio.Queue[dict[str, Any]]

    def start(self):
        """订阅章节就绪事件并启动消费任务"""
        # 队列必须在事件循环内创建，且先于订阅，避免回调入队时还没有队列
        self._event_queue = asyncio.Queue()
        # 注册同步回调：publish 时只是入队，真正的研判在后台协程里做
        subscribe(EventType.SECTION_READY, self._enqueue_event)
        # 交给任务管理器托管后台协程，监听器本身不阻塞调用方
        research_task_manager.submit_task(self._process_events())
        logger.info("SectionReadyListener: 已启动 Host 章节研判")

    def stop(self):
        """取消事件订阅并释放运行状态"""
        # 先注销回调，防止停止后仍有事件入队
        unsubscribe(self._enqueue_event)
        # 清空累积状态；后台消费协程由任务管理器负责取消
        self._host_states.clear()
        logger.info("SectionReadyListener: 已停止")

    def _enqueue_event(
            self,
            _event_type: EventType,
            event_payload: dict[str, Any]
    ):
        """将章节就绪事件加入串行消费队列"""
        # 回调运行在发布方（可能是其他协程）的上下文中：
        # 只做非阻塞入队，避免在这里直接跑 LLM 研判
        self._event_queue.put_nowait(event_payload)

    async def _process_events(self):
        """持续消费章节就绪事件并发布 Host 讨论事件"""

        # 单消费者循环：事件严格串行处理，保证同一 task 的配对状态不会被并发改写
        while True:

            # =========================================

            # 阻塞等待下一条章节就绪事件（队列为空时让出事件循环）
            event_payload = await self._event_queue.get()

            # =======================================
            task_id = event_payload["task_id"]
            # 取该任务的长期状态；首次收到该任务事件时初始化
            host_state = self._host_states.get(task_id)
            if host_state is None:
                host_state = {
                    "task_id": task_id,
                    # 配对仓库必须跨事件复用（可变对象），否则双 Agent 输出永远配不齐
                    "section_pair_store": SectionPairStore(),
                    "judgements": []
                }
            # 每次调用在图状态中额外注入本次事件载荷
            # discussion_events 不在此处传入，由本轮节点重新生成
            invocation_state: HostState = {
                **host_state,
                "event_payload": event_payload
            }
            # 执行一次 Host 图：收集输出 -> 若配对齐全则研判 -> 落盘
            updated_state: HostState = await self._graph.ainvoke(invocation_state)
            discussion_events = updated_state["discussion_events"]
            # 只回写需要长期保留的三项状态；
            # event_payload / section_judgement / discussion_events 属于单次调用
            self._host_states[task_id] = {
                "task_id": task_id,
                "section_pair_store": updated_state["section_pair_store"],
                "judgements": updated_state["judgements"]
            }

            # ==================
            # 把本轮产生的讨论事件（Agent 输出 + 可能的 Host 裁决）广播出去
            for discussion_event in discussion_events:
                logger.info(
                    f"【{display_agent_name('host')}】发送讨论事件 "
                    f"来源={display_agent_name(discussion_event.source)} "
                    f"章节={discussion_event.section_key} "
                    f"内容={discussion_event.content[:20]}..."
                )
                publish_host_discussion_message(discussion_event)
