from sentiment.engines.common.llm import LLMClient
from sentiment.engines.common.research_graph_runtime import ResearchRunContext, invoke_research_graph, ProgressCallback
from sentiment.engines.contract.agent_role import RoleKey
from sentiment.engines.media_agent.graph import build_graph


async def media_agent_invoker(role: RoleKey,
                              task_id: str,
                              query: str,
                              llm_client: LLMClient,
                              output_dir: str,
                              progress_callback: ProgressCallback
                              ):
    # 驱动执行media用 Langgraph编排的工作流
    context = ResearchRunContext(
        task_id=task_id,
        query=query,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir,
        progress_callback=progress_callback
    )
    await invoke_research_graph(context, build_graph(context), query=query)
