"""MySQL关键词检索"""
import asyncio
from dataclasses import fields
from datetime import datetime
from typing import Any

from sentiment.engines.contract.evidence import EvidenceDocument, Engagement
from sentiment.engines.insight_agent.tools.db_connection import DataBaseConnectionManager, connection_manager
from sentiment.engines.insight_agent.tools.search_results import SearchResult
from sentiment.engines.insight_agent.tools.sql import db_sql_statement


class DatabaseSearchRepository:

    def __init__(self, con_manager: DataBaseConnectionManager = connection_manager):
        self.con_manager = con_manager

    async def db_call(self, search_term: str, limit=100) -> SearchResult:
        # 1. 获取到SQL语句
        sql_stmt = db_sql_statement()

        # 2. 构建查询参数
        search_params = {
            "search_term": f'%{search_term}%',
            "limit": limit
        }

        # 3. 执行SQL语句查询
        rows: list[dict[str, Any]] = await self._fetch_db_results(sql_stmt, search_params)

        # 4. 返回搜索结果对象
        return SearchResult(retrieval_channel="db_call",
                            retrieval_results=[self._mapping_to_document(row) for row in rows])

    async def _fetch_db_results(self,
                                sql_stmt: Any,
                                search_params: dict[str, Any]) -> list[dict[str, Any]]:
        session_factory = self.con_manager.get_async_session_factory()

        async with session_factory() as session:
            result = await  session.execute(sql_stmt, search_params)
            return [dict(row_mapping) for row_mapping in result.mappings().all()]

    def _mapping_to_document(self, row: dict[str, Any]) -> EvidenceDocument:
        return EvidenceDocument(
            platform=row['platform'],
            source_table=row['source_table'],
            source_id=row['mysql_primary_key'],
            content=row['title_or_content'],
            published_at=datetime.fromtimestamp(row['published_at']),
            engagement={
                field.name: row[f'eng_{field.name}'] for field in fields(Engagement)  # type: ignore
            },
            hotness_score=row['hotness_score']
        )


async def main():
    repo = DatabaseSearchRepository()
    term = "高考"
    limit = 10
    try:
        result: SearchResult = await repo.db_call(search_term=term, limit=limit)

        print(f"检索成功,返回通道: {result.retrieval_channel}")
        records = result.retrieval_results
        print(f"共查到 {len(records)} 条数据")
        for idx, record in enumerate(records, start=1):
            print(f"[{idx}] 平台: {record.platform} | 数据表: {record.source_table} | ID: {record.source_id}")
            print(f"    内容: {record.content[:50]}...")
            print(f"    发布时间: {record.published_at}")
            print(f"    互动数据: {record.engagement}")
            print(f"    热度得分: {record.hotness_score}")
            print("-" * 50)

    finally:
        await connection_manager.dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
