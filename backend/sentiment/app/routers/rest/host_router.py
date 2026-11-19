from fastapi import APIRouter

from sentiment.app.dependencies import HostServiceDep
from sentiment.app.schemas.host_schema import HostDiscussionRecordsResponse

router = APIRouter(prefix="/api/host", tags=["主持人 Agent"])


@router.get("/discussion", response_model=HostDiscussionRecordsResponse, description=" 获取讨论区里收集到的发言记录")
def get_host_discussion_records_endpoint(
        service: HostServiceDep,
        task_id: str
):
    """返回讨论区发言记录"""
    discussion_records = service.get_discussion_records(task_id)
    return HostDiscussionRecordsResponse(**discussion_records)
