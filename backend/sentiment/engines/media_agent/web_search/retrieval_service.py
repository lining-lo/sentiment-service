"""Media Web 检索编排与证据标准化"""

import hashlib
from urllib.parse import urlparse

from sentiment.engines.contract.evidence import EvidenceDocument, EvidenceRecord, RetrievalMeta
from sentiment.engines.media_agent.web_search.factory import WebSearchFactory
from sentiment.engines.media_agent.web_search.search_results import (
    SearchProviderResponse,
    SearchTool
)


class MediaRetrievalService:
    """执行单次 Web 检索并将 Provider 结果归一化为证据"""

    def __init__(self):
        """初始化 Web 搜索客户端"""
        self._web_search_factory = WebSearchFactory()

    async def retrieve_evidence(
            self,
            tool_name: SearchTool,
            query: str
    ) -> list[EvidenceRecord]:
        """按工具执行 Web 检索并返回标准化证据"""
        response = await self._search_webpage(tool_name, query)
        return _map_to_evidence_records(response)

    async def _search_webpage(
            self,
            tool_name: SearchTool,
            query: str
    ) -> SearchProviderResponse:
        """按工具类型分派综合、溯源或实时检索"""
        match tool_name:
            case "source_search":
                return await self._web_search_factory.source_search(query)
            case "realtime_search":
                return await self._web_search_factory.realtime_search(query)
            case _:
                return await self._web_search_factory.comprehensive_search(query)


def _map_to_evidence_records(
        response: SearchProviderResponse
) -> list[EvidenceRecord]:
    """将网页结果映射为带稳定哈希 ID 的证据记录"""
    records: list[EvidenceRecord] = []
    for page in response.webpages:
        source_name = _extract_source_name(page.url)
        content = page.content
        url = page.url
        records.append(
            EvidenceRecord(
                document=EvidenceDocument(
                    platform=source_name,
                    source_table="webpage",
                    source_id=_generate_content_hash_id(content),
                    content=content,
                    published_at=page.date,
                    url=url,
                    title=page.title,
                    source_name=source_name
                ),
                retrieval=RetrievalMeta(
                    matched_queries=[response.query],
                    channel_scores={"web_call": page.score}
                )
            )
        )
    return records


def _extract_source_name(url: str) -> str:
    """从网页 URL 提取标准化来源域名"""
    hostname = urlparse(url).hostname.lower()
    return hostname.removeprefix("www.")


def _generate_content_hash_id(content: str) -> str:
    """对标准化内容生成证据标识，内容为空时回退 URL"""
    normalized_content = " ".join(content.split())
    raw_key = normalized_content.strip()
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()  # type: ignore


import asyncio

from sentiment.engines.media_agent.web_search.search_results import SearchTool


async def main() -> None:
    service = MediaRetrievalService()

    query = "高考难不难"
    tools: list[SearchTool] = ["comprehensive_search", "source_search", "realtime_search"]

    for tool in tools:
        print(f"测试工具: {tool} \n")
        records = await service.retrieve_evidence(tool_name=tool, query=query)

        print(f"共获取 {len(records)} 条证据：\n")
        for i, rec in enumerate(records, start=1):
            doc = rec.document
            score = rec.retrieval.channel_scores.get("web_call")

            print(f"[{i}] 站点: {doc.platform}")
            print(f"    来源: {doc.source_name}")
            print(f"    记录唯一ID: {doc.source_id}")
            print(f"    标题: {doc.title}")
            print(f"    url: {doc.url}")
            print(f"    时间: {doc.published_at}")
            print(f"    得分: {score}")
            print(f"    摘要: {doc.content}...\n")


if __name__ == "__main__":
    asyncio.run(main())
