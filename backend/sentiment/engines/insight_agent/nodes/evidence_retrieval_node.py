from typing import Any
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.insight_agent.state import InsightState


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """执行私域召回并返回尚未合并的原始命中记录"""
        pass
