from dataclasses import dataclass

from typing import Literal
# 定义好角色的键 Literal限定这变量只能是其中之一
RoleKey = Literal["insight", "media", "host", "report"]

# 定义角色信息类
# 自动生成 __slots__ 的数据类，让对象更省内存、访问略快，代价是不能动态加属性、不能再用 __dict__。
@dataclass(slots=True)
class RoleInfo:
    """
    角色信息
    """
    display_name: str  # 显示名称
    config_prefix: str  # 配置前缀

# 定义角色信息
ROLE_INFOS: dict[RoleKey, RoleInfo] = {
    "insight": RoleInfo(display_name="私域检索智能体专家", config_prefix="INSIGHT_AGENT"),
    "media": RoleInfo(display_name="公域检索智能体专家", config_prefix="MEDIA_AGENT"),
    "host": RoleInfo(display_name="研判智能体专家", config_prefix="HOST_AGENT"),
    "report": RoleInfo(display_name="报告引擎智能体专家", config_prefix="REPORT_ENGINE"),
}