import asyncio
from dataclasses import dataclass
from functools import wraps
from loguru import logger


@dataclass(slots=True)
class RetryConfig:
    """重试配置"""
    max_retry: int = 3
    init_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0

    def _compute_retry_delay(self, attempt: int) -> float:
        """计算延迟时间，指数退避"""
        return min(self.init_delay * (self.backoff_factor ** attempt), self.max_delay)

    def _no_retryable(self, exc: Exception) -> bool:
        """
        返回 True：不需要重试
        返回 False：需要重试
        4xx并且不是429 → 不重试
        """
        status_code = getattr(exc, "status_code", None)
        if status_code is None:
            resp = getattr(exc, "response", None)
            status_code = getattr(resp, "status_code", None)
        return isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429

    def get_retry_delay(self, exc: Exception, attempt: int, func_name: str) -> float | None:
        # 不需要重试，或者已经用尽次数
        if self._no_retryable(exc) or attempt >= self.max_retry - 1:
            return None
        delay = self._compute_retry_delay(attempt)
        current_try = attempt + 1
        next_try = current_try + 1
        logger.warning(f"函数 {func_name} 第 {current_try} 次尝试失败：{exc}")
        logger.warning(f"将在 {delay:.1f} 秒后进行第 {next_try} 次尝试....")
        return delay

    # 把with_retry写成实例方法，方便 @retry_config.with_retry
    def with_retry(self, func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("装饰器只能修饰async函数.")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(self.max_retry):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    delay = self.get_retry_delay(e, attempt, func.__name__)
                    if delay is None:
                        # 终止重试，抛出原始异常，不要包新的ValueError（更推荐）
                        raise ValueError(f"{func.__name__} 不再重试，异常：{str(e)}") from e
                    await asyncio.sleep(delay)
            # 理论上走不到这里，兜底
            raise RuntimeError(f"{func.__name__} 达到最大重试次数 {self.max_retry}")
        return wrapper


# 全局单例配置
with_retry = RetryConfig().with_retry
