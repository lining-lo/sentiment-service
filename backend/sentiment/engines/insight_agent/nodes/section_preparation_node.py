from typing import Any, Mapping
from loguru import logger
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.contract.evidence import EvidenceRecord
from sentiment.engines.contract.research_graph_state import SectionState
from sentiment.engines.contract.section_definitions import SECTION_DEFINITIONS
from sentiment.engines.insight_agent.state import InsightState


class SectionPreparationNode(ResearchNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        # 获取当前 Agent 的展示名称，用于日志记录
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始初始化固定章节并为各章节选择、排序和截取证据。")

        # 从全局状态中提取所需的数据源：
        # 1. 证据记录ID到证据对象的映射字典
        records_by_id: dict[str, EvidenceRecord] = state.get("records_by_id")
        # 2. 章节路由节点返回的章节 key 以及对应证据的记录 ID 列表
        section_record_ids: dict[str, list[str]] = state.get("section_record_ids")
        # 3. 重排序节点返回的记录 ID 及对应的相关性分数
        rerank_scores: dict[str, float] = state.get("rerank_scores")

        # 初始化用于存放最终输出的列表
        sections: list[SectionState] = []  # 存放所有章节的基础信息（Key 和 Title）
        section_evidence_records: list[list[EvidenceRecord]] = []  # 存放每个章节最终选定的证据列表

        # 遍历预定义的固定章节配置 (SECTION_DEFINITIONS)
        for section_definition in SECTION_DEFINITIONS.values():
            # 1. 构建当前章节的基础状态信息并加入列表
            sections.append(
                {
                    "section_key": section_definition.key,
                    "title": section_definition.title
                }
            )

            # 2. 为当前章节筛选证据：
            # - 调用 _select_section_records 进行业务逻辑处理（根据路由 ID 匹配、按重排分数降序排序等）
            # - 使用切片 [:20] 限制每个章节最多只保留前 20 条证据，防止上下文过长
            # - 将截取后的证据列表追加到 section_evidence_records 中
            section_evidence_records.append(
                _select_section_records(
                    section_definition.key,
                    records_by_id,
                    section_record_ids,
                    rerank_scores
                )[:20]
            )

        logger.info(f"{agent_name} 初始化固定章节并为各章节选择、排序和截取证据完成")

        # 返回更新后的状态字典，供下游节点（如摘要节点）使用
        return {
            "sections": sections,
            "section_evidence_records": section_evidence_records
        }


def _select_section_records(
        section_key: str,
        records_by_id: Mapping[str, EvidenceRecord],
        section_record_ids: Mapping[str, list[str]],
        rerank_scores: Mapping[str, float],
) -> list[EvidenceRecord]:
    """按章节键筛选证据并按统一重排分降序排列"""
    matched_records = [
        # 根据证据的记录Id 获取到 EvidenceRecord
        records_by_id[record_id]
        # 根据章节key获取证据记录的ID
        for record_id in section_record_ids.get(section_key)
    ]
    return sorted(
        matched_records,
        key=lambda record: rerank_scores.get(record.id),
        reverse=True
    )
