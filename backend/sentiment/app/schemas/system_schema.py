from typing import Any
from pydantic import Field, BaseModel, field_validator, RootModel


# 封装读取的数据结果
class ConfigResponse(BaseModel):
    # 需要给这个类配置一个config 属性;
    config: dict[str, Any] = Field(default_factory=dict)

class ConfigUpdateRequest(RootModel[dict[str, Any]]):
    """
    配置更新请求数据模型
    root: 接收前端修改字典的key
    """
    @field_validator("root")
    @classmethod
    def not_empty(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("请求体不能为空")
        return value
