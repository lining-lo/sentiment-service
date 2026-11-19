import os
from typing import Any

from dotenv import set_key

from sentiment.engines.contract.settings import get_settings, reload_setting, ENV_FILE

# 定义一个变量来存储所有返回页面需要的变量列表;
# 允许的配置键
ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_AGENT_API_KEY", "INSIGHT_AGENT_BASE_URL", "INSIGHT_AGENT_MODEL_NAME", "INSIGHT_AGENT_MODEL_PROVIDER",
    "MEDIA_AGENT_API_KEY", "MEDIA_AGENT_BASE_URL", "MEDIA_AGENT_MODEL_NAME", "MEDIA_AGENT_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_AGENT_API_KEY", "HOST_AGENT_BASE_URL", "HOST_AGENT_MODEL_NAME", "HOST_AGENT_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


#  只保留后四位数据
def _mask_secret(text: str):
    if text is None:
        return ""
    # 返回脱敏数据
    return f"****{text[-4:]}"


class SystemService:

    # 定义一个函数
    def read_config_info(self) -> dict[str, Any]:
        # 1. 获取Settings 配置信息
        current_config = get_settings()
        # 声明一个变量：
        result: dict[str, Any] = {}
        # current_config.DB_NAME 能够读取到数据的名称;
        # 2. 循环遍历 ALLOWED_CONFIG_KEYS
        for key in ALLOWED_CONFIG_KEYS:
            # 2.1 读取配置文件中的数据 DB_HOST = current_config.DB_NAME
            text = getattr(current_config, key, None)
            # 2.2 要对数据进行脱敏处理
            if key.endswith("_API_KEY"):
                # 2.2.1 数据脱敏：****最后四位字符
                text = _mask_secret(text)
            result[key] = text
        # 返回数据
        return result

    # 定义一个函数用于修改配置文件信息：config_info: DB_NAME: "media_crawler12"
    def update_config_info(self, config_info: dict[str, Any]):
        # 本质就是修改对应.env配置文件中的属性; 还需要重新加载属性
        # 1. 先做一个防御性检查：
        unknowns_keys = [key for key in config_info.keys() if key not in ALLOWED_CONFIG_KEYS]
        # 2. 判断 unknowns_keys 列表！
        if unknowns_keys:
            raise ValueError(f"Unknown keys: {unknowns_keys}")
        # 3. 修改: 需要使用一个set_key()函数
        for key, value in config_info.items():
            # quote_mode="never" 表示修改成功之后，修的值不会带有引号 DB_DIALECT='mysql'
            set_key(ENV_FILE, key, value, quote_mode="never")
            os.environ[key] = value
        # 4. 重新加载：
        reload_setting()


# import os
# from typing import Any
#
# from sentiment.engines.contract.settings import get_settings, ENV_FILE, reload_setting
# from dotenv import set_key
#
# ALLOWED_CONFIG_KEYS = [
#     "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
#     "INSIGHT_AGENT_API_KEY", "INSIGHT_AGENT_BASE_URL", "INSIGHT_AGENT_MODEL_NAME", "INSIGHT_AGENT_MODEL_PROVIDER",
#     "MEDIA_AGENT_API_KEY", "MEDIA_AGENT_BASE_URL", "MEDIA_AGENT_MODEL_NAME", "MEDIA_AGENT_MODEL_PROVIDER",
#     "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
#     "HOST_AGENT_API_KEY", "HOST_AGENT_BASE_URL", "HOST_AGENT_MODEL_NAME", "HOST_AGENT_MODEL_PROVIDER",
#     "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
# ]
#
#
# def mark_secret(value: str) -> str:
#     """
#     职责:API_KEY值得处理
#     :param value:
#     :return:
#     """
#     if not value:
#         return ""
#
#     return f"****{value[-4:]}"
#
#
# class SystemService:
#
#     def get_config(self) -> dict[str, Any]:
#         """
#         读取配置信息
#         :return:
#         """
#         settings = get_settings()
#
#         config_dict: dict[str, Any] = {}
#
#         for key in ALLOWED_CONFIG_KEYS:
#             value = getattr(settings, key, None)
#
#             text = "" if value is None else value
#
#             if key.endswith("_API_KEY"):
#                 text = mark_secret(value)
#
#             config_dict[key] = text
#
#         return config_dict
#
#     def update_config(self, config_info: dict[str, Any]):
#         """
#         更新配置信息
#         :param config_info:
#         :return:
#         """
#         # 1. 防御性校验
#         unknown_keys = [key for key in config_info.keys() if key not in ALLOWED_CONFIG_KEYS]
#
#         if unknown_keys:
#             raise ValueError(f"位置的配置属性{'、'.join(unknown_keys)}")
#
#         # 2. 更新配置信息
#         for key, value in config_info.items():
#             set_key(ENV_FILE, key, value,quote_mode="never")  # env文件
#             os.environ[key] = value  # 环境变量
#
#         # 3. 重新更新配置类
#         reload_setting()
#
