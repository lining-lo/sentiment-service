import asyncio
import jieba.analyse
from datetime import datetime, timedelta

from sentiment.engines.contract.evidence import EvidenceRecord, EvidenceDocument, RetrievalMeta
from sentiment.engines.insight_agent.tools.db.repository import DatabaseSearchRepository
from sentiment.engines.insight_agent.tools.search_results import SearchHit, SearchResult
from sentiment.engines.insight_agent.tools.vector.repository import VectorSearchRepository
from sentiment.engines.contract.settings import get_settings


class RetrivalService:

    def __init__(self):
        self.db_repository = DatabaseSearchRepository()
        self.vector_repository = VectorSearchRepository() if get_settings().INSIGHT_VECTOR_ENABLED else None

    async def retrival_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责：查询两个通道结果都完成，返回两个通道结果
        :param query:
        :return:
        """
        # 从db_call 与 vector_call 两个通道查询结果
        db_evidence, vector_evidence = await  asyncio.gather(
            self._retrival_db_evidence(query), self._retrival_vector_evidence(query)
        )

        return [*db_evidence, *vector_evidence]

    async def _retrival_vector_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责： 从向量数据库中查询检索到的结果
        记录来源milvus，记录的得分milvus计算的0-1
        :param query:
        :return:
        """

        # 1. 判断是否启用了向量检索
        if self.vector_repository is None:
            return []

        # 2. (开启新线程)检索
        search_hits: list[SearchHit] = await asyncio.to_thread(self.vector_repository.vector_call, query, 50,
                                                               build_filter_expr())

        # 3. 结果处理
        return [
            map_document_to_evidence(
                document=hit.retrieval_document,
                matched_queries=query,
                retrival_channel=hit.retrieval_channel,
                retrival_score=hit.retrieval_score
            )
            for hit in search_hits
        ]

    async def _retrival_db_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责：从MySQL数据库中查询检索到的结果
        只要记录来源于db通道，记录的得分固定是1.0（0.5）
        :param query:
        :return:
        """

        # 1. 对查询问题分词
        terms = extract_terms(query)

        # 2. 分别用分词后的词进行模糊查询
        results: list[SearchResult] = await asyncio.gather(
            *(self.db_repository.db_call(term, limit=20) for term in terms)
        )

        # 3. 结果处理
        return [
            map_document_to_evidence(
                document=document,
                matched_queries=term,
                retrival_channel=search_result.retrieval_channel,
                retrival_score=0.05
            )
            for term, search_result in zip(terms, results)
            for document in search_result.retrieval_results
        ]


def extract_terms(query: str) -> list[str]:
    """
    高考难不难----->jieba分词器
    1. 简单
    2. 指定分词的数量
    3. 去掉无用的词性：的、了、啊
    分词的数量：需要根据压测给到（2--6-8-->10）
    :param query:
    :return:
    """
    final_terms = [query]
    for term in jieba.analyse.extract_tags(query, 3):
        # 分词之后的长度在[2,4]才需要并且分词之后的数据与元数据不等
        if 2 <= len(term) <= 4 and term not in final_terms:
            final_terms.append(term)

    return final_terms


# 表示只召回最近 INSIGHT_VECTOR_FILTER_DAYS 天内的数据
def build_filter_expr() -> str:
    # 从全局设置中获取筛选天数（INSIGHT_VECTOR_FILTER_DAYS）
    days = get_settings().INSIGHT_VECTOR_FILTER_DAYS

    # 计算起始时间戳：当前时间减去 days 天，并转换为整数时间戳
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())

    # 返回过滤表达式：published_at 大于等于起始时间 published_at>=1760955907
    return f"published_at>={start_time}"


def map_document_to_evidence(document: EvidenceDocument,
                             matched_queries: str,
                             retrival_channel: str,
                             retrival_score: float
                             ) -> EvidenceRecord:
    return EvidenceRecord(
        document=document,
        retrieval=RetrievalMeta(
            matched_queries=[matched_queries],
            channel_scores={
                retrival_channel: retrival_score
            }
        )
    )


async def main_test():
    retrival_service = RetrivalService()

    results = await  retrival_service.retrival_evidence(query="高考难不难")

    print(len(results))


if __name__ == '__main__':
    asyncio.run(main_test())
