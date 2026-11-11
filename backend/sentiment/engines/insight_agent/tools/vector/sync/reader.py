"""从 MySQL 读取文档供向量同步。"""
from dataclasses import fields
from datetime import datetime
from typing import Any, Mapping

from sentiment.engines.contract.evidence import Engagement
from sentiment.engines.insight_agent.tools.db_connection import (
    DataBaseConnectionManager,
    connection_manager,
)
from sentiment.engines.insight_agent.tools.search_results import EvidenceDocument
from sentiment.engines.insight_agent.tools.sql import vector_sql_statement


class DocumentRecordReader:
    def __init__(
            self,
            connection_manager: DataBaseConnectionManager = connection_manager,
    ):
        """初始化文档读取器及其数据库连接管理器"""
        self._connection_manager = connection_manager

    async def read_all_documents(self) -> list[EvidenceDocument]:
        """读取并映射全部可用数据库文档"""
        async with self._connection_manager.get_async_engine().connect() as connection:
            result = await connection.execute(vector_sql_statement())
            rows = result.mappings().all()
        return [document for row in rows if (document := self._map_row_to_document(row))]

    @staticmethod
    def _map_row_to_document(row: Mapping[str, Any]) -> EvidenceDocument | None:
        """将数据库行映射为有效的证据文档"""
        content = row.get("content")
        published_at = datetime.fromtimestamp(int(row.get("published_at")))
        if not content.strip():
            return None
        return EvidenceDocument(
            platform=row["platform"],
            source_table=row["source_table"],
            source_id=row["mysql_primary_key"],
            content=content,
            published_at=published_at,
            engagement={
                field.name: float(
                    row.get(f"eng_{field.name}")
                )
                for field in fields(Engagement)
            },
            hotness_score=row["hotness_score"],
        )
