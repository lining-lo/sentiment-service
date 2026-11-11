"""数据库与向量检索共享的结果模型"""
from dataclasses import dataclass, field
from sentiment.engines.contract.evidence import  EvidenceDocument


@dataclass(slots=True)
class SearchResult:
    """MySQL召回结果集合"""

    retrieval_channel: str
    retrieval_results: list[EvidenceDocument] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    """Milvus包含检索元数据的单条向量命中结果"""

    retrieval_score: float
    retrieval_channel: str
    retrieval_document: EvidenceDocument
