from sentiment.engines.common.research_tasks import research_task_manager

from sentiment.app.services.host.host_service import HostService
from sentiment.app.services.sse.research_progress_stream import ResearchProgressStream


class AppLifecycleManager:
    """应用生命周期管理器:统一启动与关闭后台服务组件及引擎共享资源"""

    def __init__(self,
                 host_service: HostService,
                 research_progress_stream: ResearchProgressStream):
        """初始化生命周期管理器并注入依赖组件"""
        self.host_service = host_service
        self.research_progress_stream = research_progress_stream

    def register(self):
        """统一注册并启动所有关联的后台服务组件"""

        # 1. 启动前端实时广播服务
        self.research_progress_stream.register_progress_update()
        # 2. 启动研判讨论缓冲服务
        self.host_service.register_discussion_buffer()
        # 3. 启动 Host 章节研判监听器
        self.host_service.register_host_listener()

    async def shutdown(self):
        """统一注销并停止所有关联的后台服务组件,释放持有的资源"""

        # 1. 停止广播服务，断开事件订阅
        self.research_progress_stream.stop_progress_update()
        # 2. 停止讨论缓冲服务，释放监听
        self.host_service.stop_discussion_buffer()
        # 3. 停止 Host 章节监听 worker
        self.host_service.stop_host_listener()
        # 4. 取消仍在执行的研究/报告后台任务
        await research_task_manager.cancel_tasks()
