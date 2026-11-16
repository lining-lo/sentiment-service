import json
from typing import Any
from loguru import logger
from langchain_core.prompts import PromptTemplate

from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.contract.section_definitions import (
    SECTION_DEFINITIONS,
    get_section_definitions_for_role
)
from sentiment.engines.media_agent.search_plan import MediaSearchPlanOutput
from sentiment.engines.media_agent.state import MediaSectionState, MediaState
from sentiment.engines.media_agent.web_search.search_results import SEARCH_TOOL_DESCRIPTIONS
from sentiment.engines.prompts.media import (
    MEDIA_SEARCH_PLAN_SYSTEM_PROMPT,
    MEDIA_SEARCH_PLAN_USER_PROMPT
)


class SearchPlanningNode(ResearchNode):
    """为固定 Media 章节生成搜索工具与关键词"""

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """调用 LLM 生成搜索策略，并与固定章节定义合并为运行状态"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"【{agent_name}】开始执行公域信息搜索")
        planned = await self._generate_search_plan(self.context.query)

        sections: list[MediaSectionState] = [
            MediaSectionState(
                section_key=section_definition.key,
                title=section_definition.title,
                search_tool=planed_section.search_tool,
                search_keywords=[keyword.strip() for keyword in planed_section.search_keywords]
            )
            for section_definition, planed_section in zip(
                SECTION_DEFINITIONS.values(),
                planned.sections
            )
        ]

        logger.info(f"【{agent_name}】执行公域信息搜索完成")
        return {"sections": sections}

    async def _generate_search_plan(
            self,
            research_topic: str
    ) -> MediaSearchPlanOutput:
        """组装搜索规划提示词并调用 LLM 返回结构化计划"""

        search_tools = [
            {"name": tool, "description": description}
            for tool, description in SEARCH_TOOL_DESCRIPTIONS.items()
        ]

        prompt = PromptTemplate.from_template(MEDIA_SEARCH_PLAN_USER_PROMPT).format(
            research_topic=research_topic,
            section_contexts=json.dumps(
                get_section_definitions_for_role("media"),
                ensure_ascii=False,
                indent=2,
            ),
            search_tools=json.dumps(
                search_tools,
                ensure_ascii=False,
                indent=2,
            )
        )

        return await self.context.llm_client.generate_object(
            MEDIA_SEARCH_PLAN_SYSTEM_PROMPT,
            prompt,
            MediaSearchPlanOutput
        )
