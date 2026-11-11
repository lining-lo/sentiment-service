from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Engagement:
    """互动指标数据模型"""
    # 点赞数 接收不同平台的点赞数
    likes: float
    # 评论数 接收不同平台的评论数
    comments: float
    # 分享数 接收不同平台的分享数
    shares: float
    # 收藏数 接收不同平台的收藏数
    collects: float
    # 回复数 接收不同平台的回复数
    replies: float


@dataclass(slots=True)
class EvidenceDocument:
    """跨 MySQL 与 Milvus 的归一化的文档记录"""
    # 平台
    platform: str
    # 表来源与哪个平台哪张表
    source_table: str
    # 来源Id 就是数据库表Id
    source_id: str
    # 来源内容，既有内容也有评论的内容
    content: str
    # 记录发布时间 create_time
    published_at: datetime | str
    # 互动链：点赞数，评论数，收藏数，分享数
    engagement: dict[str, float] = field(default_factory=dict)
    # 热度值：根据互动链的指标计算这个值
    hotness_score: float = 0.0

    # 文档的 URL
    url: str = ""
    # 文档的标题
    title: str = ""
    # 文档的来源名称
    source_name: str = ""

    @property
    def doc_id(self) -> str:
        """根据来源字段生成稳定文档标识"""
        return f"{self.platform}:{self.source_table}:{self.source_id}"


@dataclass(slots=True)
class RetrievalMeta:
    """召回过程元数据(查询词/通道/分数)"""
    # 匹配查询词列表 高考难不难（高考，难不难）
    matched_queries: list[str] = field(default_factory=list)
    # 检索通道得分
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
