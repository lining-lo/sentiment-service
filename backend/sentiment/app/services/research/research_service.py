from sentiment.engines.common.research_tasks import research_task_manager
from sentiment.engines.orchestrator.agent_orchestrator import ResearchAgentOrchestrator


class ResearchService:
    """研究任务服务:创建研究运行、启动后台研究并读取各角色产物。"""
    def __init__(self) -> None:
        self._orchestrator = ResearchAgentOrchestrator()

    # 定义研究函数
    def research(self, query: str) -> str:
        # 调用manager中的函数创建研究任务
        research_task = research_task_manager.create_task(query)
        # 利用协调者分发任务
        self._orchestrator.dispatch_tasks(
            research_task.task_id,
            query
        )
        # 返回task_id
        return research_task.task_id