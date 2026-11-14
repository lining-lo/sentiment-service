from collections import defaultdict
from functools import lru_cache
from typing import Any

import numpy as np
from loguru import logger
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.contract.evidence import EvidenceRecord
from sentiment.engines.contract.section_definitions import get_insight_routing_rules, SECTION_DEFINITIONS
from sentiment.engines.contract.settings import get_settings
from sentiment.engines.insight_agent.state import InsightState


class SectionEvidenceRoutingNode(ResearchNode):
    """将重排证据按规则或语义相似度路由到固定章节"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """根据配置选择规则或语义方式路由证据"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始为章节选择证据")

        # 根据证据对象列表 list[EvidenceRecord]
        records = list(state.get("records_by_id").values())
        # 判断是否启用语义路由
        if _is_semantic_enabled(records):
            section_record_ids = _route_by_semantics(records)
        else:
            # 关键词路由
            section_record_ids = _route_by_rules(records)

        logger.info(f"{agent_name} 章节候选证据完成")
        return {"section_record_ids": section_record_ids}


def _is_semantic_enabled(records):
    """判断当前证据是否启用语义路由"""
    settings = get_settings()
    return (
            bool(records)
            and settings.INSIGHT_SEMANTIC_ROUTING_ENABLED
            and bool(settings.INSIGHT_SEMANTIC_ROUTING_MODEL)
    )


def _route_by_rules(records: list[EvidenceRecord]) -> dict[str, list[str]]:
    """按关键词规则将证据路由到首个匹配章节"""
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    rules = get_insight_routing_rules()
    for record in records:
        text = (
            f"{' '.join(record.retrieval.matched_queries)} "
            f"{record.document.content}"
        )
        # next函数keyword在text中就不找了，找不到就返回None
        section_key = next(
            (
                section_key
                for section_key, keywords in rules.items()
                if any(keyword in text for keyword in keywords)
            ),
            None
        )
        if section_key is not None:
            section_record_ids[section_key].append(record.id)
    return section_record_ids


def _route_by_semantics(records: list[EvidenceRecord]):
    """逐条计算与固定章节向量的相似度，并路由到最相似章节"""
    # 获取每个记录的问题与内容
    contents = [
        (
            f"{' '.join(record.retrieval.matched_queries)} "
            f"{record.document.content}"
        ).strip()
        for record in records
    ]
    # 获取到模型，进行向量化
    record_vectors = _get_embedding_model().encode(
        contents,
        # 对每个输出的向量做 L2 归一化，让向量的欧几里得范数（长度）变成 1 cosine(a,b)
        # 不归一化时，长文本/高频词的向量模长往往更大，会干扰"语义相似度"的判断。归一化后只比较方向，不考虑长度。
        normalize_embeddings=True
    )
    # 获取5个章节的key与向量
    # section_keys:    章节标识列表，例如 ["章节A", "章节B", ...]
    # section_vectors: 章节向量矩阵，形状为 (章节数, 向量维度)，通常已做 L2 归一化
    section_keys, section_vectors = _get_section_vectors()
    # 计算每条记录向量与每个章节向量的相似度（点积）
    # 因为向量都已归一化，所以点积 == 余弦相似度
    # record_vectors:  (记录数30, 向量维度)
    # section_vectors.T: (向量维度1024, 章节数)
    # similarities:    (记录数, 章节数)，第 i 行第 j 列 = 第 i 条记录与第 j 个章节的相似度
    similarities = np.dot(record_vectors, section_vectors.T)
    # 对每条记录，沿"章节"维度取相似度最大的下标
    # axis=1 表示在每一行（每条记录）内部比较
    # best_indices: (记录数,)，每个元素是相似度最高的章节下标
    best_indices = np.argmax(similarities, axis=1)
    # 用于按章节聚合记录 ID：{章节key: [记录id, ...]}
    # 使用 defaultdict(list) 可以在 key 不存在时自动初始化为空列表
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    # 遍历每条记录及其最匹配的章节下标，把记录 id 归入对应章节
    for record, best_idx in zip(records, best_indices):
        # 取出该记录最匹配的章节 key
        section_key = section_keys[best_idx]
        # 把记录 id 追加到该章节下
        section_record_ids[section_key].append(record.id)
    # 返回：章节 key -> 属于该章节的记录 id 列表
    return section_record_ids


# @lru_cache
# def _get_embedding_model():
#     """惰性加载章节语义路由使用的嵌入模型"""
#     from sentence_transformers import SentenceTransformer
#     return SentenceTransformer(str(get_settings().INSIGHT_SEMANTIC_ROUTING_MODEL))
@lru_cache
def _get_embedding_model():
    """惰性加载章节语义路由使用的嵌入模型"""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(str(get_settings().INSIGHT_SEMANTIC_ROUTING_MODEL),
                               device="cpu"  # 强制使用 CPU，避免 GPU 兼容性问题)
                               )


@lru_cache
def _get_section_vectors():
    """缓存固定章节关键词的归一化向量"""
    # 获取到对应的字典数据
    rules = get_insight_routing_rules()
    # 获取到title与keywords
    section_texts = [
        f"{SECTION_DEFINITIONS[section_key].title}: {' '.join(keywords)}"
        for section_key, keywords in rules.items()
    ]
    # 对title与keywords 进行向量化处理
    section_vectors = _get_embedding_model().encode(
        section_texts,
        normalize_embeddings=True
    )
    section_keys = list(rules.keys())
    # 返回章节的key与章节计算的向量
    # section_keys:    章节标识列表，例如 ["章节A", "章节B", ...]
    # section_vectors: 章节向量矩阵，形状为 (章节数, 向量维度)，通常已做 L2 归一化
    return section_keys, section_vectors
