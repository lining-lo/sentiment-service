from typing import Any, TypedDict

from sentiment.engines.contract.events import HostDiscussionMessageEvent
from sentiment.engines.contract.judgement import SectionJudgement
from sentiment.engines.host_agent.section_pair_store import SectionPairStore


# total=False：所有字段都是可选的，允许按次调用只传入当前需要的增量状态。
# SectionReadyListener 会为每个 task_id 长期保留
# task_id / section_pair_store / judgements 三项，每次事件再补上 event_payload。
class HostState(TypedDict, total=False):
    """Host LangGraph 的事件输入、章节配对与研判状态"""

    # 任务标识：用于区分不同运行的 Host 状态，也决定报告落盘目录
    task_id: str
    # 当前处理的章节就绪事件载荷：每个章节生成完的数据发送给Host的数据。
    # 每次事件驱动图执行时由 SectionReadyListener 注入
    event_payload: dict[str, Any]
    # 双 Agent 章节输出仓库（可变对象）：按 section_key 累积 insight/media 的正文，
    # 并记录哪些章节已研判；跨多次图调用共享，保证事件逐个到达也能配对
    section_pair_store: SectionPairStore
    # 5个章节的研判结果，最终由 save_judgements 落盘
    judgements: list[SectionJudgement]
    # 讨论事件（供事件流推送给前端），每次调用重新生成
    discussion_events: list[HostDiscussionMessageEvent]
    # 存储单个章节临时结果
    section_judgement: SectionJudgement
