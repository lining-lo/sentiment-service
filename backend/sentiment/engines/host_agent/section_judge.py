import json

from langchain_core.prompts import PromptTemplate

from sentiment.engines.common.llm import LLMClient
from sentiment.engines.contract.judgement import SectionJudgement
from sentiment.engines.host_agent.models import AgentSectionPair
from sentiment.engines.prompts.host import (
    HOST_SECTION_JUDGE_SYSTEM_PROMPT,
    HOST_SECTION_JUDGE_USER_PROMPT
)


class HostSectionJudge:
    """调用 Host LLM 对 Insight 与 Media 的同章节输出进行研判"""

    # 类属性：在模块导入时按 "host" 角色读取配置并创建客户端，
    # 所有实例共享同一个客户端（初始化有读取 .env 的副作用）
    llm_client: LLMClient = LLMClient.from_role("host")

    async def judge_section(
            self,
            section_pair: AgentSectionPair
    ) -> SectionJudgement:
        """生成单章节结构化研判"""

        # 1. 把双 Agent 的章节正文组装成一段 JSON 证据文本
        judgement_evidence = self._build_judgement_context(section_pair)

        # 2. 填充用户提示词模板（模板中只有 judgement_evidence 一个变量）
        prompt = PromptTemplate.from_template(HOST_SECTION_JUDGE_USER_PROMPT).format(
            judgement_evidence=judgement_evidence
        )

        # 3. 结构化输出：由 json_schema 约束模型必须返回 SectionJudgement 的字段
        judgement = await self.llm_client.generate_object(
            HOST_SECTION_JUDGE_SYSTEM_PROMPT,
            prompt,
            SectionJudgement,
        )
        # 4. 用配对信息强制回填 section_key，避免模型漏填或填错章节标识；
        #    model_copy 不做重新校验，其余字段沿用模型返回值
        return judgement.model_copy(update={"section_key": section_pair.section_key})

    def _build_judgement_context(
            self,
            section_pair: AgentSectionPair,
    ) -> str:
        """组装当前双 Agent 的同章节输出"""
        # 章节元信息用于让模型知道当前在研判哪一章
        # 两份正文各截断到 3000 字符，控制提示词长度、避免超出模型上下文
        judgement_context = {
            "section": {
                "key": section_pair.section_key,
                "title": section_pair.title,
            },
            "insight": {"body": section_pair.insight.body[:3000]},
            "media": {"body": section_pair.media.body[:3000]},
        }
        # ensure_ascii=False 保留中文原文，避免出现 \uXXXX 转义
        return json.dumps(judgement_context, ensure_ascii=False)
