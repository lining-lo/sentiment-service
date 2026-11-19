from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

from sentiment.app.dependencies import ReportServiceDep
from sentiment.app.schemas.report_schema import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportStatusResponse
)

router = APIRouter(prefix="/api/report", tags=["报告路由"])


# 查询报告状态
@router.get("/status", response_model=ReportStatusResponse, description="获取报告状态")
def get_report_status_endpoint(
        service: ReportServiceDep,
        task_id: str
):
    """查询报告生成状态"""
    input_status = service.get_report_status(task_id)
    return ReportStatusResponse(
        task_id=input_status.task_id,
        prepared=input_status.prepared,
        found_files=input_status.found_files
    )


# 生成报告接口
@router.post("/generate", response_model=GenerateReportResponse, description="开始生成报告")
async def generate_report_endpoint(payload: GenerateReportRequest, service: ReportServiceDep):
    """异步触发生成报告任务"""
    generation = service.request_report_generation(payload.task_id)
    return GenerateReportResponse(
        generation_id=generation.generation_id,
        task_id=generation.task_id
    )


# 获取已完成报告的HTML文件
@router.get("/result/{generation_id}", description="获取报告生成结果")
def get_generate_result_endpoint(generation_id: str, service: ReportServiceDep):
    """获取已完成报告 HTML"""
    report_output = service.get_completed_report_output(generation_id)
    # 直接返回内存中的 HTML 字符串，用于报告预览
    return Response(content=report_output.html_content, media_type="text/html")


# 下载Html 或Md文件
@router.get("/download/{generation_id}/{file_type}", description="下载HTML/MD格式报告")
def download_report_endpoint(
        generation_id: str,
        file_type: str,
        service: ReportServiceDep
):
    """下载 HTML 或 MD 报告文件"""
    file_info = service.get_download_file(generation_id, file_type)
    # 读取磁盘文件并设置附件响应头，用于文件下载
    return FileResponse(
        file_info["file_path"],
        media_type=file_info["media_type"],
        filename=file_info["file_name"]
    )
