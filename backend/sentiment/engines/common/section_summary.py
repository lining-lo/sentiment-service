"""Insight/Media 共享的章节摘要节点基类"""
from typing import Any
from sentiment.engines.common.research_graph_runtime import ResearchNode


class BaseSectionSummaryNode(ResearchNode):
    """章节摘要节点基类:游标推进、证据组装、LLM 生成摘要与事件发布"""

    system_prompt: str = ""
    user_prompt_template: str
    max_rendered_evidence: int = 10
    fallback_body: str = ""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """按游标取证据包生成章节正文并发布就绪事件"""
