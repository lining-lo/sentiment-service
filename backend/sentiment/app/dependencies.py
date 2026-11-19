from typing import Annotated
from fastapi import Depends

from sentiment.app.services.host.host_service import HostService
from sentiment.app.services.lifecycle.lifecycle_service import AppLifecycleManager
from sentiment.app.services.report.report_service import ReportService
from sentiment.app.services.research.research_service import ResearchService
from sentiment.app.services.sse.research_progress_stream import ResearchProgressStream
from sentiment.app.services.system.system_service import SystemService

_research_service = ResearchService()


def get_research_service() -> ResearchService:
    """提供全局研究工作流服务单例"""
    return _research_service


_report_service = ReportService()


def get_report_service() -> ReportService:
    """提供全局报告生成服务单例"""
    return _report_service


_host_service = HostService()


def get_host_service() -> HostService:
    """提供全局主持人研判服务单例"""
    return _host_service


_config_service = SystemService()


def get_config_service():
    """提供全局系统配置服务单例"""
    return _config_service


_research_progress_stream = ResearchProgressStream()


def get_research_progress_stream() -> ResearchProgressStream:
    """提供全局研究进度 SSE 事件流单例"""
    return _research_progress_stream


_lifecycle_manager = AppLifecycleManager(_host_service, _research_progress_stream)


def get_lifecycle_manager() -> AppLifecycleManager:
    """提供全局生命周期管理器单例"""
    return _lifecycle_manager


ResearchServiceDep = Annotated[ResearchService, Depends(get_research_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
HostServiceDep = Annotated[HostService, Depends(get_host_service)]
SystemConfigServiceDep = Annotated[SystemService, Depends(get_config_service)]
