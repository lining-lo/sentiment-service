from fastapi import APIRouter

from sentiment.app.dependencies import SystemConfigServiceDep
from sentiment.app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest

router = APIRouter(prefix="/api/config", tags=["系统配置信息路由"])


@router.get(path="", response_model=ConfigResponse)
def get_config_endpoint(service: SystemConfigServiceDep):
    config_info = service.read_config_info()
    return ConfigResponse(config=config_info)


@router.post(path="")
def update_config_endpoint(request: ConfigUpdateRequest,
                           service: SystemConfigServiceDep):
    service.update_config_info(request.root)
