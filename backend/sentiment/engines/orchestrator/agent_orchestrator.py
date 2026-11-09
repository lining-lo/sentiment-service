from typing import Callable, Awaitable
from sentiment.engines.common.llm import LLMClient
from sentiment.engines.common.logs import router_logs_by_role
from sentiment.engines.common.report import get_report_dir
from sentiment.engines.common.research_tasks import research_task_manager
from sentiment.engines.contract.agent_role import RoleKey
from sentiment.engines.insight_agent.agent import invoke_insight_agent
from sentiment.engines.media_agent.agent import invoke_media_agent

AgentHandler = Callable[
    [
        str,
        str,
        RoleKey,
        LLMClient,
        str,
    ],
    Awaitable[None],
]


class ResearchAgentOrchestrator:
    def __init__(self) -> None:
        self._agent_handlers: dict[RoleKey, AgentHandler] = {
            "insight": invoke_insight_agent,
            "media": invoke_media_agent,
        }

    def dispatch_tasks(self, task_id: str, query: str) -> None:
        for agent_role in self._agent_handlers.keys():
            # agent_role 的类型自动就是 RoleKey
            research_task_manager.submit_task(
                self.execute_research_task(task_id, query, agent_role)
            )

    async def execute_research_task(self, task_id: str, query: str, role: RoleKey):
        with router_logs_by_role(role):
            llm_client = LLMClient.from_role(role)
            output_dir = get_report_dir(task_id, role)

            await self._agent_handlers[role](
                task_id,
                query,
                role,
                llm_client,
                output_dir,
            )
