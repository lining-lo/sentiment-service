from typing import Any
from loguru import logger
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.evidence import EvidenceRecord, RetrievalMeta
from sentiment.engines.insight_agent.state import InsightState
from sentiment.engines.contract.agent_role import display_agent_name


class EvidenceRerankingNode(ResearchNode):
    """合并重复召回证据并计算统一重排分"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """合并重复召回结果、计算排名分数并构建证据索引"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始进行去重、重排序")

        merged_records = _dedupe_and_merge(state.get('retrieved_records'))
        #  key=document.id: value=证据的得分
        rerank_scores: dict[str, float] = _calculate_rerank_scores(merged_records)

        # 按重排序分数（rerank_scores）对合并后的记录进行降序排序
        # - merged_records: 待排序的记录列表
        # - rerank_scores: 字典，键为 record.id，值为该记录的重排序得分
        # - key 使用 lambda 取出每条记录对应的分数作为排序依据
        # - reverse=True 表示降序，即分数高的排在前面
        ordered_records = sorted(
            merged_records,
            key=lambda record: rerank_scores.get(record.id),
            reverse=True,
        )
        logger.info(f"{agent_name} 去重、重排序完成")
        return {
            "records_by_id": {record.id: record for record in ordered_records},
            "rerank_scores": rerank_scores
        }


def _dedupe_and_merge(retrieved_records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    """按证据标识去重并合并召回元数据"""
    # 定义一个字典 key是document.doc_id, value=EvidenceRecord
    records_by_id: dict[str, EvidenceRecord] = {}
    # 从数据状态节点中循环遍历获取到证据对象
    for record in retrieved_records:
        # 根据文档Id 获取到 EvidenceRecord 对象
        existing_record = records_by_id.get(record.id)
        # 如何对象是空，则说明字典中没有这个数据，就把这个证据添加到这个字典中.
        if existing_record is None:
            records_by_id[record.id] = record
            continue
        # 如果对象不是空,说明存在相同的证据对象，并对其进行合并
        records_by_id[record.id] = EvidenceRecord(
            document=existing_record.document,
            retrieval=RetrievalMeta(
                # 将两条记录的匹配查询列表合并后去重（set 去重，再转回 list）
                matched_queries=
                list(set(existing_record.retrieval.matched_queries + record.retrieval.matched_queries)),
                # 将两条记录的渠道分数字典合并（后者覆盖前者的同名 key）
                channel_scores={
                    **existing_record.retrieval.channel_scores,
                    **record.retrieval.channel_scores,
                }
            )
        )
    # 返回最终数据
    return list(records_by_id.values())


def _calculate_rerank_scores(merged_records: list[EvidenceRecord]) -> dict[str, float]:
    """结合召回得分与热度计算统一重排分"""
    max_hot_score = max(record.document.hotness_score for record in merged_records)
    # key=document.id: value=证据的得分
    return {
        record.id: _retrieval_score(record) * 0.6
                   + (record.document.hotness_score / max_hot_score) * 0.4
        for record in merged_records
    }


def _retrieval_score(record: EvidenceRecord) -> float:
    """按渠道权重加权召回得分"""
    channel_scores = record.retrieval.channel_scores
    score = (
            channel_scores.get("vector_call", 0.0) * 0.5
            + channel_scores.get("db_call", 0.0) * 0.5
    )
    return score
