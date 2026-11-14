import asyncio

from sentiment.engines.common.llm import LLMClient
from sentiment.engines.common.research_graph_runtime import ResearchRunContext, invoke_research_graph
from sentiment.engines.contract.agent_role import RoleKey
from sentiment.engines.contract.settings import get_settings
from sentiment.engines.insight_agent.graph import build_insight_graph


async def invoke_insight_agent(
        run_id: str,
        query: str,
        role: RoleKey,
        llm_client: LLMClient,
        output_dir: str
):
    """
    insightAgent 入口
    """
    context = ResearchRunContext(
        task_id=run_id,
        query=query,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir
    )

    await  invoke_research_graph(build_insight_graph(context), query)


async def main_test():
    await invoke_insight_agent(
        run_id="1234_test",
        query="高考",
        role="insight",
        llm_client=LLMClient.from_role("insight"),
        output_dir=get_settings().RUNTIME_DIR
    )


if __name__ == '__main__':
    asyncio.run(main_test())
