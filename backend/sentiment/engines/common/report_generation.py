from typing import Any
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.research_graph_state import ResearchGraphState


class ReportGenerationNode(ResearchNode):
    """将 Agent 的章节正文整合为独立研究报告"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """调用整合研究状态中的章节并生成独立报告"""
