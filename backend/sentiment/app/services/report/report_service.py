from pathlib import Path
from typing import Any
from uuid import uuid4

from sentiment.engines.common.research_tasks import research_task_manager
from loguru import logger

from sentiment.app.services.report.input_loader import ReportInputLoader, ReportInputStatus
from sentiment.engines.report_engine.engine import ReportEngine
from sentiment.engines.report_engine.models import (
    ReportGeneration,
    ReportGenerationStatus,
    ReportOutput
)


class ReportService:
    """综合报告服务：协调输入加载、任务状态跟踪与报告引擎生成报告"""

    def __init__(self):
        """初始化最终综合报告服务以及组件"""
        self._report_generations: dict[str, ReportGeneration] = {}
        self._input_loader = ReportInputLoader()
        self._report_engine = ReportEngine()

    def get_report_status(self, task_id: str) -> ReportInputStatus:
        """获取最终报告输入文件的准备状态"""
        return self._input_loader.get_report_input_status(task_id)

    def request_report_generation(self, task_id: str) -> ReportGeneration:
        """创建并异步启动报告生成过程"""

        # 1. 获取报告状态
        input_status = self._input_loader.get_report_input_status(task_id)
        if not input_status.prepared:
            raise RuntimeError("报告输入尚未就绪")
        generation = self._prepare_report_generation(
            task_id,
            input_status.input_file_paths
        )

        # 2. 丢到后台事件循环中异步执行生成逻辑(纳入统一任务登记)
        research_task_manager.submit_task(self._run_report_generation(generation))

        # 3. 立即返回生成记录供前端轮询
        return generation

    def get_download_file(self, generation_id: str, file_type: str) -> dict[str, Any]:
        """获取已生成报告文件的下载路径、文件名和媒体类型"""

        # 1. 获取已完成的报告输出
        report_output = self.get_completed_report_output(generation_id)

        # 2. 根据文件类型匹配对应的路径和媒体类型
        if file_type == "html":
            file_path = report_output.report_filepath
            file_name = report_output.report_filename
            media_type = "text/html"
        elif file_type == "md":
            file_path = report_output.markdown_filepath
            file_name = report_output.markdown_filename
            media_type = "text/markdown"
        else:
            raise ValueError("不支持的报告文件类型")

        # 3. 确认落盘文件仍然存在
        if not file_path or not Path(file_path).exists():
            raise LookupError("报告文件不存在或已被清理")

        # 4. 返回文件下载所需的元数据
        return {"file_path": file_path, "file_name": file_name, "media_type": media_type}

    def get_completed_report_output(self, generation_id: str) -> ReportOutput:
        """获取已完成报告生成过程的输出"""
        generation = self._report_generations.get(generation_id)
        if generation is None:
            raise LookupError("报告生成记录不存在")
        if generation.status == ReportGenerationStatus.ERROR:
            raise RuntimeError(f"报告生成失败: {generation.error_message}")
        if generation.status != ReportGenerationStatus.COMPLETED:
            raise RuntimeError("报告尚未完成")
        return generation.report_output

    def _prepare_report_generation(
            self,
            task_id: str,
            input_file_paths: dict[str, str]
    ) -> ReportGeneration:
        """创建报告生成记录，并阻止同一研究任务重复生成"""

        # 1. 检查是否存在正在运行的生成任务，防止重复提交
        if any(
                generation.task_id == task_id
                and generation.status == ReportGenerationStatus.RUNNING
                for generation in self._report_generations.values()
        ):
            raise RuntimeError("当前研究任务已有报告正在生成")

        # 2. 生成唯一的记录 ID 并加载报告输入数据
        generation_id = f"generation_{uuid4().hex}"
        report_input = self._input_loader.load_report_input(
            generation_id=generation_id,
            task_id=task_id,
            file_paths=input_file_paths
        )

        # 3. 创建报告生成记录并存入_report_generations容器
        generation = ReportGeneration(report_input=report_input)
        # 存储到字典的目的是为了后续下载时，根据generation_id获取到报告数据
        self._report_generations[generation.generation_id] = generation

        # 4. 返回创建好的生成记录实例
        return generation

    async def _run_report_generation(self, generation: ReportGeneration):
        """在后台异步执行报告生成的完整工作流"""
        try:
            # 1. 调用综合报告引擎生成最终报告
            report_output = await self._report_engine.generate_report(
                generation.report_input
            )
            # 2. 将生成结果绑定到本次报告生成过程并标记完成
            generation.complete(report_output)

        except Exception as e:
            # 3. 记录日志并更新任务状态为失败
            logger.exception(f"报告生成失败: {str(e)}")
            generation.fail(str(e))
