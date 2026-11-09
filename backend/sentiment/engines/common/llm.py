import asyncio
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

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


    # 文本渲染函数
    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str) -> str:
        """流式生成纯文本,逐块收集后拼成一个字符串返回。"""
        # 1. 先构建消息内容:system 设定角色/规则,user 放具体问题
        message_context = self.build_message_context(system_prompt, user_prompt)
        # 2. 定义模型
        chat_model = self.init_chat_object_model()
        # 用列表收集再 join,避免在循环里反复做字符串拼接
        final_chunks = []
        # 3. 生成文本:astream 逐 token 返回,content 可能为空(如思考过程/结束块),需要跳过
        try:
            async for chunk in chat_model.astream(message_context):
                if text := chunk.content:
                    final_chunks.append(text)
        except Exception as exec:
            raise ValueError(f"{self.model_name}调用失败，异常信息：{str(exec)}")
        # 返回数据.
        return "".join(final_chunks)


    # 构建消息对象列表
    def build_message_context(self, system_prompt: str, user_prompt: str) -> list[BaseMessage]:
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]


    # 初始化大模型
    def init_chat_object_model(self, is_structed: bool = False) -> BaseChatModel:
        # 1. 获取到模型名称
        model_name = self.model_name.lower()
        kwargs: dict[str, Any] = {}
        # 2. 如果是结构化对象，要关闭kimi的思考模式。
        if is_structed and (model_name in "kimi" or "moonshot" in model_name):
            kwargs['extra_body'] = {
                "thinking": {
                    "type": "disabled"
                }
            }
        return init_chat_model(
            api_key=self.api_key,
            model=self.model_name,
            base_url=self.base_url,
            model_provider=self.model_provider,
            **kwargs,
        )

if __name__ == '__main__':
    async def test():
        llm = LLMClient.from_role(role="media") # "insight", "media", "host", "report"
        result = await llm.generate_text(system_prompt="你是一个法律专家,能够回答一切法律知识",
                                         user_prompt="发生肇事逃逸应该如何判决?")
        print(result)

    asyncio.run(test())