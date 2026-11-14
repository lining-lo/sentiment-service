"""研究 Agent 图的共享上下文、节点基类与执行辅助"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping
from sentiment.engines.common.llm import LLMClient
from sentiment.engines.contract.agent_role import RoleKey


@dataclass(slots=True)
class ResearchRunContext:
    """单次 Insight/Media 研究运行所需的共享依赖与元数据"""
    task_id: str
    query: str
    role: RoleKey
    llm_client: LLMClient
    output_dir: str


class ResearchNode(ABC):
    """研究 Agent 图节点抽象基类"""

    def __init__(self, context: ResearchRunContext):
        """初始化研究节点的共享运行上下文"""
        self.context = context

    @abstractmethod
    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """节点执行入口"""


async def invoke_research_graph(
        graph: Any,
        query: str
):
    """以统一初始状态执行研究 Agent 的 LangGraph"""
    initial_state = {"query": query}
    await graph.ainvoke(initial_state)


def route_after_section_summary(state: Mapping[str, Any]) -> str:
    """按游标判断继续下一章节摘要或全部完成"""
    cursor = state.get("cursor", 0)
    sections = state.get("sections")
    return "next_section" if cursor < len(sections) else "all_done"


SECTION_SUMMARY_LOOP_MAPPING = {
    "next_section": "summarize_sections",
    "all_done": "generate_agent_report"
}
