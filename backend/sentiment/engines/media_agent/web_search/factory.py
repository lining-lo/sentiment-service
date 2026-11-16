from sentiment.engines.media_agent.web_search.base import BaseSearchClient
from sentiment.engines.media_agent.web_search.providers.anspire_client import AnspireSearchClient
from sentiment.engines.media_agent.web_search.search_results import SearchProviderResponse


class WebSearchFactory:
    """基于 Anspire Provider 的 Web 检索统一入口"""

    def __init__(self):
        """实例化当前唯一的 Anspire Provider 客户端"""
        self._client: BaseSearchClient = AnspireSearchClient()

    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行综合检索"""
        return await self._client.comprehensive_search(query)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行溯源检索"""
        return await self._client.source_search(query)

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行实时检索"""
        return await self._client.realtime_search(query)
