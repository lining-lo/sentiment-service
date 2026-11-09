from typing import Annotated
from fastapi import Depends
from sentiment.app.services.system_service import SystemService

# 定义一个变量：
_system_service = SystemService()


# 定义一个函数, 返回SystemService对象
def get_system_service():
    return _system_service


# 声明一个对象，依赖注入; 第一个参数表示属于什么数据类型，第二个参数注入的依赖对象.
# FastAPI 官网有案例...
SystemServiceDep = Annotated[SystemService, Depends(get_system_service)]
