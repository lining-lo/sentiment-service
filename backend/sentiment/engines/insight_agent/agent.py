from sentiment.engines.common.llm import LLMClient
from sentiment.engines.contract.agent_role import RoleKey


async def invoke_insight_agent(
        run_id: str,
        query: str,
        role: RoleKey,
        llm_client: LLMClient,
        output_dir: str,
):
    pass
