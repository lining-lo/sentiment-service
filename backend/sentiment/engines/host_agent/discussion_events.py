from sentiment.engines.contract.events import HostDiscussionMessageEvent
from sentiment.engines.contract.judgement import SectionJudgement
from sentiment.engines.host_agent.models import AgentSectionOutput


def build_agent_discussion_event(
        task_id: str,
        output: AgentSectionOutput
) -> HostDiscussionMessageEvent:
    """构造 Insight 或 Media 的章节讨论事件"""
    return HostDiscussionMessageEvent(
        task_id=task_id,
        source=output.source,  # type: ignore
        content=output.body[:2000],
        section_key=output.section_key,
    )


def build_judgement_discussion_event(
        task_id: str,
        judgement: SectionJudgement
) -> HostDiscussionMessageEvent:
    """构造 Host 单章节研判讨论事件"""
    return HostDiscussionMessageEvent(
        task_id=task_id,
        source="host",
        content=judgement.content,
        section_key=judgement.section_key
    )
