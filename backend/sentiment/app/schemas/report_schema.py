from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    """报告生成请求体"""

    task_id: str = Field(..., min_length=1, description="关联的研究任务 ID")


class ReportStatusResponse(BaseModel):
    """报告生成状态响应体"""

    task_id: str
    prepared: bool = False
    found_files: list[str] = Field(default_factory=list)


class GenerateReportResponse(BaseModel):
    """报告生成过程创建响应体"""

    generation_id: str
    task_id: str
