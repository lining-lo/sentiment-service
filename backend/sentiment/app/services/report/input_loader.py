import json
from dataclasses import dataclass
from pathlib import Path

from sentiment.engines.common.research_tasks import research_task_manager

from sentiment.engines.common.report import get_report_dir
from sentiment.engines.contract.judgement import SectionJudgement
from sentiment.engines.report_engine.models import ReportInput


@dataclass(slots=True)
class ReportInputStatus:
    """综合报告输入文件的准备状态"""

    task_id: str
    found_files: list[str]
    input_file_paths: dict[str, str]

    @property
    def prepared(self) -> bool:
        """判断综合报告所需输入文件是否齐备"""
        return len(self.input_file_paths) == 3


class ReportInputLoader:
    """检查角色产物是否齐备，并加载双 Agent 报告与 Host 研判"""

    def get_report_input_status(self, task_id: str) -> ReportInputStatus:
        """检查所有必需角色的报告文件是否已就绪。"""
        found_files = []
        input_file_paths = {}
        expected_files = {
            "insight": Path(get_report_dir(task_id, "insight")) / "report.md",
            "media": Path(get_report_dir(task_id, "media")) / "report.md",
            "host": Path(get_report_dir(task_id, "host")) / "judgements.json"
        }
        for role_key, path in expected_files.items():
            if path.exists():
                found_files.append(f"{role_key}: {path.name}")
                input_file_paths[role_key] = str(path)

        return ReportInputStatus(
            task_id=task_id,
            found_files=found_files,
            input_file_paths=input_file_paths
        )

    def load_report_input(
            self,
            generation_id: str,
            task_id: str,
            file_paths: dict[str, str]
    ) -> ReportInput:
        """读取双 Agent 报告与 Host 研判，封装最终报告输入"""
        research_task = research_task_manager.get_research_task(task_id)
        raw_judgements = json.loads(Path(file_paths["host"]).read_text(encoding="utf-8"))
        return ReportInput(
            generation_id=generation_id,
            task_id=task_id,
            query=research_task.query,
            insight_report=Path(file_paths["insight"]).read_text(encoding="utf-8"),
            media_report=Path(file_paths["media"]).read_text(encoding="utf-8"),
            host_judgements=[SectionJudgement.model_validate(item) for item in raw_judgements]
        )
