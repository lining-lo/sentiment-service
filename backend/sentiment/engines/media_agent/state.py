from sentiment.engines.contract.evidence import EvidenceRecord
from sentiment.engines.contract.research_graph_state import ResearchGraphState, SectionState
from sentiment.engines.media_agent.web_search.search_results import SearchTool


class MediaSectionState(SectionState):
    """带公域搜索策略的研究章节状态"""

    search_tool: SearchTool
    search_keywords: list[str]


class MediaState(ResearchGraphState[MediaSectionState], total=False):  # type: ignore
    """媒体智能体 LangGraph 全局状态定义"""

    section_evidence_records: list[list[EvidenceRecord]]
    section_queries: list[str]
