from typing import Any
from pydantic import Field, BaseModel


# 封装读取的数据结果
class ConfigResponse(BaseModel):
    # 需要给这个类配置一个config 属性;
    config: dict[str, Any] = Field(default_factory=dict)
