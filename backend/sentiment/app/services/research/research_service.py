from pathlib import Path

from sentiment.engines.common.research_tasks import research_task_manager

from sentiment.engines.common.report import get_report_dir
from sentiment.engines.contract.agent_role import RESEARCH_ROLE_KEYS
from sentiment.engines.orchestrator.orchestrator import OrchestratorResearchAgent


class ResearchService:
    def __init__(self):
        self.orchestrator = OrchestratorResearchAgent()

    def research(self, query: str) -> str:
        """
        职责：开始进行舆论话题的研究
        :param query:
        :return:
        task_id:研究任务ID
        """
        # 1. 创建研究任务
        research_task = research_task_manager.create_task(query)

        # 2. 利用协调者将研究任务转发走
        self.orchestrator.dispatch_task(research_task.task_id, query)

        # 3. 将研究任务的任务ID返回
        return research_task.task_id

    def get_research_results(self, task_id: str) -> tuple[str, dict[str, str]]:
        """读取指定研究任务的各角色报告内容"""

        # 1. 获取指定的研究任务，校验任务是否存在
        research_task = research_task_manager.get_research_task(task_id)
        if research_task is None:
            raise LookupError(f"研究任务不存在: {task_id}")

        # 2. 遍历各个研究角色，读取已生成的 Markdown 报告文件内容
        research_results: dict[str, str] = {}
        for role in RESEARCH_ROLE_KEYS:
            report_file = Path(get_report_dir(task_id, role)) / "report.md"
            if not report_file.exists():
                continue
            research_results[role] = report_file.read_text(
                encoding="utf-8", errors="ignore"
            )

        # 3. 返回任务 ID 及包含所有已就绪角色报告的字典
        return research_task.task_id, research_results
