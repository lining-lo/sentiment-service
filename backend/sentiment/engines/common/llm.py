from sentiment.engines.contract.agent_role import RoleKey, ROLE_INFOS
from sentiment.engines.contract.settings import get_settings


class LLMClient:
    """LLM 客户端封装：统一调用与重试。"""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str,
        model_provider: str
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.model_provider = model_provider

    @classmethod
    def from_role(cls, role: RoleKey) -> "LLMClient":
        # 1. 获取配置信息：
        settings = get_settings()
        # 2. 获取到Agent 配置信息前缀
        config_prefix = ROLE_INFOS[role].config_prefix
        # 3. 创建实例对象并返回
        return cls(
            api_key=getattr(settings, f"{config_prefix}_API_KEY"),
            model_name=getattr(settings, f"{config_prefix}_MODEL_NAME"),
            base_url=getattr(settings, f"{config_prefix}_BASE_URL"),
            model_provider=getattr(settings, f"{config_prefix}_MODEL_PROVIDER"),
        )