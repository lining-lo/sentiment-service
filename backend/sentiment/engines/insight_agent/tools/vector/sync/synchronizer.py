"""Milvus 知识库同步器：从 MySQL 全量拉取并写入 Milvus 集合。"""

import asyncio

from loguru import logger

from sentiment.engines.insight_agent.tools.vector.repository import VectorSearchRepository
from sentiment.engines.insight_agent.tools.vector.sync.reader import DocumentRecordReader
from sentiment.engines.insight_agent.tools.db_connection import connection_manager


class DocumentRecordSynchronizer:
    """的知识库同步器"""

    def __init__(self) -> None:
        """初始化向量仓储与源文档读取器"""
        self._vector_repository = VectorSearchRepository()
        self._source_reader = DocumentRecordReader()

    async def full_sync(self, drop_existing: bool = False) -> int:
        """全量同步 MySQL 文档到 Milvus，返回入库文档数。"""
        all_documents = await self._source_reader.read_all_documents()

        self._vector_repository.ensure_collection(drop_existing=drop_existing)

        count = await asyncio.to_thread(
            self._vector_repository.upsert_documents, all_documents,
        )
        return count


async def main():
    """执行 Milvus 知识库全量同步测试"""
    logger.info("开始启动 Milvus 知识库全量同步测试...")
    synchronizer = DocumentRecordSynchronizer()
    try:
        count = await synchronizer.full_sync(drop_existing=True)
        logger.success(f"知识库全量同步测试完成，共插入 {count} 条记录。")
    finally:
        await connection_manager.dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
