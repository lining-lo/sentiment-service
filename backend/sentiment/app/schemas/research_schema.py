from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """研究任务启动请求体"""

    query: str = Field(..., description="研究主题")

    @field_validator("query")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """校验研究主题非空白"""
        value = value.strip()
        if not value:
            raise ValueError("研究主题不能为空")
        return value


class ResearchResponse(BaseModel):
    """研究任务启动结果响应体"""
    task_id: str


class ResearchResultsResponse(BaseModel):
    """各角色研究结果聚合响应体"""
    task_id: str
    results: dict[str, str] = Field(default_factory=dict)
