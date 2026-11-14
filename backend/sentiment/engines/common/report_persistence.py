from typing import Any

from loguru import logger

from sentiment.engines.common.report import save_report
from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.contract.research_graph_state import ResearchGraphState


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究运行"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """将研究状态中的独立报告保存到文件"""
        agent_name = display_agent_name(self.context.role)

        final_report = state["final_report"]

        md_path = save_report(
            self.context.output_dir,
            "report.md",
            final_report
        )

        logger.info(f"【{agent_name}】报告落盘完成: {md_path}")
        return {}
