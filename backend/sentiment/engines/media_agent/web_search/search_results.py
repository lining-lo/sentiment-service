from dataclasses import dataclass, field
from typing import Literal

SearchTool = Literal["comprehensive_search", "source_search", "realtime_search"]

SEARCH_TOOL_DESCRIPTIONS: dict[SearchTool, str] = {
    "comprehensive_search": (
        "不限近期和站点范围的综合检索，适合比较不同媒体与信源的叙事差异，"
        "并分析社会背景、争议成因和潜在影响；"
        "优先用于“平台与群体差异”和“深层原因与影响”章节；"
        "需要多来源报道或媒体叙事时，也可用于其余章节。"
    ),
    "source_search": (
        "限定政府和中央媒体站点的溯源检索，适合核验事件经过、公开通报、"
        "官方回应和权威报道；不保证结果均为事件当事方的一手材料；"
        "优先用于“事件背景与概览”章节；需要政策背景、治理回应或正式结论时，"
        "也可用于“深层原因与影响”章节。"
    ),
    "realtime_search": (
        "限定近一周微博、知乎和今日头条内容的时效性检索，"
        "适合追踪热度变化、传播节点、公域可见观点和争议表达；"
        "优先用于“舆情热度与传播”和“公众情感与观点”章节；"
        "需要近期进展时，也可用于“事件背景与概览”章节。"
    ),
}


@dataclass(frozen=True, slots=True)
class WebpageResult:
    """单条网页检索结果的领域模型"""

    title: str
    url: str
    content: str
    date: str
    score: float


@dataclass(frozen=True, slots=True)
class SearchProviderResponse:
    """Provider 检索结果的统一响应模型"""
    query: str
    webpages: list[WebpageResult] = field(default_factory=list)
