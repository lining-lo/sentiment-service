from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Engagement:
    """互动指标数据模型"""
    likes: float
    comments: float
    shares: float
    collects: float
    replies: float


@dataclass(slots=True)
class EvidenceDocument:
    """跨 MySQL 与 Milvus 的归一化的文档记录"""

    platform: str
    source_table: str
    source_id: str
    content: str
    published_at: datetime | str
    engagement: dict[str, float] = field(default_factory=dict)
    hotness_score: float = 0.0

    url: str = ""
    title: str = ""
    source_name: str = ""

    @property
    def doc_id(self) -> str:
        """根据来源字段生成稳定文档标识"""
        return f"{self.platform}:{self.source_table}:{self.source_id}"


@dataclass(slots=True)
class RetrievalMeta:
    """召回过程元数据(查询词/通道/分数)"""

    matched_queries: list[str] = field(default_factory=list)
    channel_scores: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceRecord:
    """一次检索中命中的舆情证据及其召回元数据"""

    document: EvidenceDocument
    retrieval: RetrievalMeta = field(default_factory=RetrievalMeta)

    @property
    def id(self) -> str:
        """快捷获取对应证据文档的唯一标识"""
        return self.document.doc_id


@dataclass(slots=True)
class EvidenceContext:
    """供 LLM 提示词使用的已渲染证据上下文"""

    retrieval_text: str = ""
    evidence_text: str = ""


def build_evidence_context(
        retrieval_text: str,
        records: list[EvidenceRecord],
        max_rendered: int
) -> EvidenceContext:
    """统计命中数并渲染有限证据，构建 LLM 提示词上下文"""
    return EvidenceContext(
        retrieval_text=retrieval_text,
        evidence_text="\n\n".join(
            _render_evidence_records(records[:max_rendered])
        ),
    )


def _render_evidence_records(records: list[EvidenceRecord]) -> list[str]:
    """将证据记录渲染为带稳定编号的 LLM 文本块"""
    return [
        _render_evidence_record(record, evidence_number)
        for evidence_number, record in enumerate(records, start=1)
    ]


def _render_evidence_record(record: EvidenceRecord, evidence_number: int) -> str:
    """将单条证据记录格式化渲染为带序号的文本块"""
    document = record.document
    fields = (
        ("平台/站点", document.platform),
        ("来源表/网页数据", document.source_table),
        ("命中查询", " / ".join(record.retrieval.matched_queries)),
        ("内容", _truncate_content(document.content)),
        ("发布时间/抓取时间", document.published_at),
        ("热度分", document.hotness_score),
        ("互动数据", _render_engagement(document.engagement))
    )
    lines = [f"[证据 {evidence_number}]"]
    lines.extend(f"{label}: {value}" for label, value in fields if value)
    return "\n".join(lines)


def _truncate_content(content: str, max_length: int = 3000) -> str:
    """截断超出指定最大长度限制的文本内容"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def _render_engagement(engagement: dict[str, Any]) -> str:
    """将互动数据字典拼接格式化"""
    values = (
        ("点赞", engagement.get('likes')),
        ("评论", engagement.get('comments')),
        ("转发", engagement.get('shares')),
        ("收藏", engagement.get('collects')),
        ("回复", engagement.get('replies')),
    )
    return " / ".join(f"{label} {value}" for label, value in values)
