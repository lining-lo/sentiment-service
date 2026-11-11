"""Milvus 向量检索仓储：数据插入、混合检索与结果映射"""
from dataclasses import fields
from datetime import datetime
from typing import Any
from loguru import logger

from pymilvus import AnnSearchRequest, MilvusClient, RRFRanker

from sentiment.engines.contract.evidence import Engagement
from sentiment.engines.contract.settings import get_settings
from sentiment.engines.insight_agent.tools.search_results import EvidenceDocument, SearchHit
from sentiment.engines.insight_agent.tools.vector.embedder import VectorEmbedder
from sentiment.engines.insight_agent.tools.vector.builder import (
    CollectionSchemaBuilder,
    MILVUS_OUTPUT_FIELDS
)


class VectorSearchRepository:
    """Milvus 数据仓储：提供写文档、混合检索及封装数据结果"""

    def __init__(self):
        """初始化向量仓储配置、编码器与客户端状态"""
        self._settings = get_settings()
        self.collection_name = self._settings.MILVUS_INSIGHT_COLLECTION
        self._embedder = VectorEmbedder()
        self._milvus_client: MilvusClient | None = None

    @property
    def milvus_client(self) -> MilvusClient:
        """懒加载 Milvus 客户端"""
        if self._milvus_client is None:
            self._milvus_client = MilvusClient(
                uri=self._settings.MILVUS_URI,
                db_name=self._settings.MILVUS_DB_NAME,
            )
        return self._milvus_client

    def close(self):
        """释放资源"""
        if self._milvus_client is not None:
            try:
                self._milvus_client.close()
            finally:
                self._milvus_client = None

    def ensure_collection(self, drop_existing: bool = False):
        """确保 Milvus 集合存在"""
        client = self.milvus_client
        if drop_existing and client.has_collection(self.collection_name):
            client.drop_collection(self.collection_name)
        if client.has_collection(self.collection_name):
            return
        schema_builder = CollectionSchemaBuilder(
            client, self._settings.INSIGHT_DENSE_DIM
        )
        client.create_collection(
            collection_name=self.collection_name,
            schema=schema_builder.build_collection_schema(),
            index_params=schema_builder.build_index_parameters(),
        )
        logger.info(f"创建 Milvus 集合 {self.collection_name}")

    # ==================== 1. 写操作====================

    def upsert_documents(self, documents: list[EvidenceDocument]) -> int:
        """批量向量化并写入 Milvus 集合"""

        self.ensure_collection()
        embeddings = self._embedder.encode(doc.content for doc in documents)

        milvus_entities = [
            self._to_milvus_entity(doc, dense_vector=dense, sparse_vector=sparse)
            for doc, (dense, sparse) in zip(documents, embeddings)
            if dense and sparse
        ]
        if not milvus_entities:
            logger.warning(f"插入 Milvus 集合数据失败: {len(milvus_entities)}")
            return 0

        self.milvus_client.upsert(
            collection_name=self.collection_name, data=milvus_entities
        )
        logger.info(f"成功插入 Milvus 集合数据: {len(milvus_entities)}")
        return len(milvus_entities)

    @staticmethod
    def _to_milvus_entity(
            document: EvidenceDocument,
            dense_vector: list[float],
            sparse_vector: dict[int, float]
    ) -> dict[str, Any]:
        """将统一文档模型转为 Milvus 实体字典"""
        return {
            "platform": document.platform,
            "source_table": document.source_table,
            "doc_id": document.doc_id,
            "mysql_primary_key": document.source_id,
            "content": document.content,
            "published_at": int(document.published_at.timestamp()),
            **{
                metric_field.name: float(
                    document.engagement.get(metric_field.name, 0.0)
                )
                for metric_field in fields(Engagement)
            },
            "hotness_score": document.hotness_score,
            "dense_vector": dense_vector,
            "sparse_vector": sparse_vector
        }

    # ==================== 2. 读操作与检索映射 ====================

    def vector_call(
            self,
            query: str,
            limit: int,
            filter_expression: str | None = None
    ) -> list[SearchHit]:
        """按查询内容进行双通道混合检索"""
        if not self.milvus_client.has_collection(self.collection_name):
            logger.warning(f"Milvus 集合不存在，跳过检索: {self.collection_name}")
            return []
        embeddings = self._embedder.encode([query])
        if not embeddings:
            return []
        return self._hybrid_search(embeddings[0], limit, filter_expression)

    def _hybrid_search(
            self,
            query_embedding: tuple[list[float], dict[int, float]],
            limit: int,
            filter_expression: str | None
    ) -> list[SearchHit]:
        """执行稠密-稀疏双路 AnnSearch 并通过 RRF 融合"""
        dense_vector, sparse_vector = query_embedding
        request_filter: dict[str, Any] = {"expr": filter_expression} if filter_expression else {}

        dense_request = AnnSearchRequest(
            data=[dense_vector],
            anns_field="dense_vector",
            param={"metric_type": "COSINE"},
            limit=limit,
            **request_filter
        )
        sparse_request = AnnSearchRequest(
            data=[sparse_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP"},
            limit=limit,
            **request_filter
        )
        raw_result = self.milvus_client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_request, sparse_request],
            ranker=RRFRanker(),
            limit=limit,
            output_fields=MILVUS_OUTPUT_FIELDS,
            # 默认的 Bounded 一致性要求 QueryNode 追上服务端时间戳，
            # 如果报 "Timestamp lag too large"，将其降为 Eventually(最终一致性)
            consistency_level="Eventually",
        )
        return self._map_hits(raw_result)

    @staticmethod
    def _map_hits(raw_result: Any) -> list[SearchHit]:
        """解析 Milvus 混合检索结果，映射为数据模型SearchHit"""
        if not raw_result:
            return []
        hits: list[SearchHit] = []
        for hit_dict in raw_result[0]:
            entity = hit_dict.get("entity")
            hits.append(
                SearchHit(
                    retrieval_score=float(hit_dict.get("distance")),
                    retrieval_channel="vector_call",
                    retrieval_document=EvidenceDocument(
                        platform=entity["platform"],
                        source_table=entity["source_table"],
                        source_id=entity["mysql_primary_key"],
                        content=entity["content"],
                        published_at=datetime.fromtimestamp(
                            int(entity.get("published_at"))
                        ),
                        engagement={
                            metric_field.name: float(
                                entity.get(metric_field.name)
                            )
                            for metric_field in fields(Engagement)
                        },
                        hotness_score=entity["hotness_score"],
                    )
                )
            )
        return hits




if __name__ == "__main__":
    repo = VectorSearchRepository()
    try:
        test_query = "高考难不难"
        top_k = 6
        hits = repo.vector_call(query=test_query, limit=top_k)
        for idx, hit in enumerate(hits, start=1):
            doc = hit.retrieval_document
            print(f"[{idx}] 得分 (Distance/Score): {hit.retrieval_score:.4f}")
            print(f"    平台: {doc.platform} | 数据库主键: {doc.source_id}")
            print(f"    发布时间: {doc.published_at}")
            print(f"    热度得分: {doc.hotness_score}")
            print(f"    内容摘要: {doc.content[:50]}...")
            print("-" * 50)
    finally:
        repo.close()
        logger.info("已关闭 Milvus 客户端连接")