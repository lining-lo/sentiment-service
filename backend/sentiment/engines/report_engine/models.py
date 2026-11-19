from dataclasses import dataclass
from enum import Enum

from sentiment.engines.contract.judgement import SectionJudgement


@dataclass(slots=True)
class ReportInput:
    """综合报告生成所需的输入"""

    generation_id: str
    task_id: str
    query: str
    insight_report: str
    media_report: str
    host_judgements: list[SectionJudgement]


@dataclass(slots=True)
class ReportOutput:
    """综合报告生成后的输出"""

    html_content: str
    report_filepath: str
    report_filename: str
    markdown_filepath: str
    markdown_filename: str


class ReportGenerationStatus(str, Enum):
    """综合报告生成状态"""

    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(slots=True)
class ReportGeneration:
    """单次综合报告生成过程"""

    report_input: ReportInput
    report_output: ReportOutput | None = None
    status: ReportGenerationStatus = ReportGenerationStatus.RUNNING
    error_message: str = ""

    @property
    def generation_id(self) -> str:
        """获取本次报告生成标识"""
        return self.report_input.generation_id

    @property
    def task_id(self) -> str:
        """获取关联的研究任务标识"""
        return self.report_input.task_id

    def complete(self, report_output: ReportOutput):
        """记录报告输出并标记生成完成"""
        self.report_output = report_output
        self.status = ReportGenerationStatus.COMPLETED

    def fail(self, message: str):
        """记录错误并标记生成失败"""
        self.error_message = message
        self.status = ReportGenerationStatus.ERROR
