import os
from typing import Any

from dotenv import set_key

from sentiment.engines.contract.settings import get_settings, ENV_FILE, reload_setting

# 声明一个列表，来储存前端页面需要的key.
ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_AGENT_API_KEY", "INSIGHT_AGENT_BASE_URL", "INSIGHT_AGENT_MODEL_NAME", "INSIGHT_AGENT_MODEL_PROVIDER",
    "MEDIA_AGENT_API_KEY", "MEDIA_AGENT_BASE_URL", "MEDIA_AGENT_MODEL_NAME", "MEDIA_AGENT_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_AGENT_API_KEY", "HOST_AGENT_BASE_URL", "HOST_AGENT_MODEL_NAME", "HOST_AGENT_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


class SystemService:
    def get_config(self):
        # 1. 获取到 .env 配置信息数据.
        current_config = get_settings()
        # 2. 定义一个变量接收数据的返回值.
        result: dict[str, Any] = {}
        # 3. 循环遍历给key进行赋值.
        for key in ALLOWED_CONFIG_KEYS:
            # 给key进行赋值操作. current_config 这个对象中的属性是有数据. 获取对应key的取值. 利用getattr
            # 如果没有同样的key，则赋值None
            text = getattr(current_config, key, None)
            # text 可能有None的情况.
            value = "" if text is None else text
            # 赋值: 注意数据脱敏，保证数据安全.
            if key.endswith("_API_KEY"):
                # 使用****与value后四位进行拼接. 数据脱敏.
                value = f"****{value[-4:]}"
            result[key] = value
        # 4. 返回数据
        return result

    # 定义一个修改的函数
    def update_config(self, config_info: dict[str, Any]):
        # 1. 校验key是否存在；MEDIA_AGENT_MODEL_NAME:"qwen-plus1"
        unknow_keys = [key for key in config_info.keys() if key not in ALLOWED_CONFIG_KEYS]
        # 2. 判断 unknow_keys
        if unknow_keys:
            raise ValueError(f"Unknown keys: {unknow_keys}")
        # 3. 如果有值，则需要修改 .env 配置文件中的数据． set_key(ENV_FILE) os 包下的函数．
        for key, value in config_info.items():
            # quote_mode="never": 这个属性能够将修改的值变为真实数据 data ，并不会对数据添加双引号"data"
            set_key(ENV_FILE, key, value)
            os.environ[key] = value
        # 4. 重新加载
        reload_setting()
