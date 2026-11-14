from typing import Any

from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.insight_agent.state import InsightState


class EvidenceRerankingNode(ResearchNode):
    """合并重复召回证据并计算统一重排分"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """合并重复召回结果、计算排名分数并构建证据索引"""
        pass
