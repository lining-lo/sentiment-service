from sentiment.app.dependencies import SystemServiceDep
from sentiment.app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest
from fastapi import APIRouter

router = APIRouter(prefix="/api/config", tags=["系统配置"])


# 读取系统配置信息 返回值类型：ConfigResponse
# 将这个类 SystemServiceDep 放入依赖声明.
# 用户发起请求--FastAPI--Service
@router.get(path="", response_model=ConfigResponse)
def get_config(service: SystemServiceDep):
    # 1. 读取数据
    config = service.get_config()
    # 2. 返回数据
    return ConfigResponse(config=config)


@router.post(path="")
def update_config(request: ConfigUpdateRequest, service: SystemServiceDep):
    service.update_config(request.root)
