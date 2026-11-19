from fastapi import APIRouter

from sentiment.app.dependencies import ResearchServiceDep
from sentiment.app.schemas.research_schema import (
    ResearchRequest,
    ResearchResponse,
    ResearchResultsResponse
)

router = APIRouter(prefix="/api/research", tags=["研究路由"])


@router.post("", response_model=ResearchResponse, description="开始研究接口")
async def start_research_endpoint(payload: ResearchRequest, service: ResearchServiceDep):
    """POST /api/research 启动研究工作流"""
    return ResearchResponse(task_id=service.research(payload.query))


@router.get("/results", response_model=ResearchResultsResponse, description="获取研究结果接口")
def get_research_result_endpoint(
        service: ResearchServiceDep,
        task_id: str
):
    """获取指定研究任务的各角色结果"""
    resolved_task_id, research_results = service.get_research_results(task_id)
    return ResearchResultsResponse(task_id=resolved_task_id, results=research_results)
