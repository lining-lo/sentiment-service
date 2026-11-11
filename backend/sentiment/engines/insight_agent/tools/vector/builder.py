"""Milvus 集合 schema 与索引参数的构建器"""
from dataclasses import fields
from typing import Any

from pymilvus import DataType

from sentiment.engines.contract.evidence import Engagement

MILVUS_OUTPUT_FIELDS: list[str] = [
    "doc_id",
    "platform",
    "source_table",
    "mysql_primary_key",
    "content",
    "published_at",
    *(metric_field.name for metric_field in fields(Engagement)),
    "hotness_score"
]

class CollectionSchemaBuilder:
    """构建 Milvus 集合的 schema 与索引参数"""

    def __init__(self, milvus_client: Any, dense_vector_dimension: int) -> None:
        """保存 Milvus 客户端与稠密向量维度"""
        self._milvus_client = milvus_client
        self._dense_vector_dimension = dense_vector_dimension

    def build_collection_schema(self) -> Any:
        """定义 Milvus 集合字段与混合向量列结构"""
        collection_schema = self._milvus_client.create_schema(
            auto_id=False, enable_dynamic_field=False,
        )
        collection_schema.add_field("doc_id", DataType.VARCHAR, is_primary=True, max_length=256)
        collection_schema.add_field("platform", DataType.VARCHAR, max_length=32)
        collection_schema.add_field("source_table", DataType.VARCHAR, max_length=64)
        collection_schema.add_field("mysql_primary_key", DataType.INT64)
        collection_schema.add_field("content", DataType.VARCHAR, max_length=65535)
        collection_schema.add_field("published_at", DataType.INT64)
        for metric_field in fields(Engagement):
            collection_schema.add_field(metric_field.name, DataType.FLOAT)
        collection_schema.add_field("hotness_score", DataType.FLOAT)
        collection_schema.add_field(
            "dense_vector",
            DataType.FLOAT_VECTOR,
            dim=self._dense_vector_dimension,
        )
        collection_schema.add_field("sparse_vector", DataType.SPARSE_FLOAT_VECTOR)
        return collection_schema

    def build_index_parameters(self) -> Any:
        """配置稠密/稀疏向量列的索引类型与度量"""
        index_parameters = self._milvus_client.prepare_index_params()
        index_parameters.add_index(
            field_name="dense_vector",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )
        index_parameters.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="IP",
        )
        return index_parameters
