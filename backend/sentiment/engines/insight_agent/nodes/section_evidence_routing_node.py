from typing import Any

from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.insight_agent.state import InsightState


class SectionEvidenceRoutingNode(ResearchNode):
    """将重排证据按规则或语义相似度路由到固定章节"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """根据配置选择规则或语义方式路由证据"""
        pass
