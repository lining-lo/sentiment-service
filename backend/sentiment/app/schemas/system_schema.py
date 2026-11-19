from typing import Any

from pydantic import RootModel, BaseModel, Field, field_validator


class ConfigUpdateRequest(RootModel[dict[str, Any]]):
    """
    配置请求数据模型
    """

    @field_validator("root")
    @classmethod
    def not_empty(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("请求体不能为空")
        return value


class ConfigResponse(BaseModel):
    """
    配置响应数据模型
    """
    config: dict[str, Any] = Field(default_factory=dict)
