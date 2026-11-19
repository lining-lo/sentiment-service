"""SSE 实时事件流路由"""

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from sentiment.app.dependencies import get_research_progress_stream

router = APIRouter(tags=["SSE实时事件流路由"])


@router.get("/api/events/stream")
async def stream_research_progress(request: Request, task_id: str):
    """推送研究进度 SSE 事件流"""

    # EventSourceResponse 把一个持续产生事件的生成器转换为浏览器能够接收的SSE长连接。
    return EventSourceResponse(
        get_research_progress_stream().stream_research_progress(request, task_id)
    )
