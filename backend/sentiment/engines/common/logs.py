from contextlib import contextmanager
from pathlib import Path
from loguru import logger

from sentiment.engines.contract.settings import get_settings


# 传递角色
@contextmanager
def router_logs_by_role(role: str):
    """为指定角色临时挂一个独立日志文件,块内打出的日志只写入该角色的文件。

    用法:
        with router_logs_by_role("insight_agent"):
            logger.info(...)  # -> {LOG_DIR}/insight_agent.log
    """
    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)

    # contextualize 在块内给每条日志记录写入 extra["role"],
    # 下面的 filter 正是靠这个字段判断该记录是否属于当前角色。
    # 注意:yield 必须放在 with 内部,否则块内日志不带 role,会被 filter 全部丢弃。
    with logger.contextualize(role=role):
        # add 返回 handler id,退出时用它精确移除本次新增的 sink,
        # 不会误删其他角色或全局默认的 handler。
        handler_id = logger.add(
            str(log_dir / f"{role}.log"),
            # {extra[role]} 取自上面 contextualize 注入的字段
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] {name} - {message}",
            level="INFO",
            encoding="utf-8",
            # 单文件超过 1MB 自动轮转
            rotation="1 MB",
            # 只接收 role 匹配的记录,防止不同角色的日志串写到同一个文件
            filter=lambda record: record["extra"].get("role") == role
        )
        try:
            yield
        finally:
            # 用 finally 保证块内抛异常时也能移除 sink,避免 handler 泄漏、文件句柄不释放
            logger.remove(handler_id)
