from typing import Any

from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.insight_agent.state import InsightState


class SectionPreparationNode(ResearchNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        pass
