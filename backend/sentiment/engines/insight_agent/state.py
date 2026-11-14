from sentiment.engines.contract.evidence import EvidenceRecord
from sentiment.engines.contract.research_graph_state import ResearchGraphState, SectionState


# total: 在实例化的时候，并不会要求将类中的属性都赋值
class InsightState(ResearchGraphState[SectionState], total=False):  # type: ignore
    """全局状态：证据处理结果、章节列表与游标"""
    retrieved_records: list[EvidenceRecord]  # 检索节点返回的数据，接收检索到的证据记录。
    rerank_scores: dict[str, float]  # 重排序节点返回的记录以及记录的分数。
    section_record_ids: dict[str, list[str]]  # 章节路由节点返回的章节 key 以及对应证据的证据记录ID
    records_by_id: dict[str, EvidenceRecord]  # 证据记录ID和证据对象
    section_evidence_records: list[list[EvidenceRecord]]  # 五个章节的证据记录
