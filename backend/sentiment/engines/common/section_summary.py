"""Insight/Media 共享的章节摘要节点基类"""
import json
from typing import Any
from loguru import logger

from langchain_core.prompts import PromptTemplate

from sentiment.engines.common.research_graph_runtime import ResearchNode
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.contract.evidence import build_evidence_context, EvidenceContext, EvidenceRecord
from sentiment.engines.contract.section_definitions import find_section_definition
from sentiment.engines.prompts.shared import SECTION_SUMMARY_USER_PROMPT


class BaseSectionSummaryNode(ResearchNode):
    """章节摘要节点基类:游标推进、证据组装、LLM 生成摘要与事件发布"""

    system_prompt: str = ""
    user_prompt_template: str = SECTION_SUMMARY_USER_PROMPT
    max_rendered_evidence: int = 10
    fallback_body: str = ""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """按游标取证据包生成章节正文并发布就绪事件"""

        """按游标取证据包生成章节正文并发布就绪事件"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始初始化固定章节并为各章节选择、排序和截取证据。")

        cursor = state.get("cursor", 0)
        sections = list(state.get("sections"))
        if cursor >= len(sections):
            return {"sections": sections}

        section = sections[cursor]

        section_records = self._section_records(state, cursor)
        if not section_records:
            logger.info(f"【章节 {section.get('section_key')} 证据上下文为空,跳过生成。")
            section["body"] = self.fallback_body
        else:
            evidence_context = build_evidence_context(
                retrieval_text=self._retrieval_text(),
                records=section_records,
                max_rendered=self.max_rendered_evidence,
            )
            section["body"] = await self._generate_section_body(
                section,
                evidence_context,
            )

        # TODO 发布章节摘要

        sections[cursor] = section
        return {"sections": sections, "cursor": cursor + 1}

    def _section_records(self, state: dict[str, Any], cursor: int) -> list[EvidenceRecord]:
        """取当前游标章节的证据记录,缺省返回空列表"""
        section_records = state.get("section_evidence_records")
        return section_records[cursor]

    def _retrieval_text(self) -> str:
        """章节证据对应的检索文本，默认取研究主题"""
        return self.context.query

    async def _generate_section_body(
            self,
            section: dict[str, Any],
            evidence_context: EvidenceContext
    ) -> str:
        """调用 LLM 生成章节正文并清洗 Markdown"""
        section_key = section["section_key"]
        section_definition = find_section_definition(section_key)

        section_context = {
            "title": section.get("title"),
            "section_key": section_key,
            "section_guidance": section_definition.section_guidance_for(self.context.role)
        }

        user_prompt = PromptTemplate.from_template(template=self.user_prompt_template).format(
            retrieval_text=evidence_context.retrieval_text,
            section_context=json.dumps(section_context, ensure_ascii=False, indent=2),
            evidence_text=evidence_context.evidence_text,
        )

        body = await self.context.llm_client.generate_text(self.system_prompt, user_prompt)

        return body
