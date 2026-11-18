import json
from typing import Any

from loguru import logger

from sentiment.engines.common.report import get_report_dir, save_report
from sentiment.engines.contract.agent_role import display_agent_name
from sentiment.engines.host_agent.discussion_events import (
    build_agent_discussion_event,
    build_judgement_discussion_event
)
from sentiment.engines.host_agent.models import AgentSectionOutput
from sentiment.engines.host_agent.section_judge import HostSectionJudge
from sentiment.engines.host_agent.state import HostState


class HostNodes:
    """Host LangGraph 的章节收集、研判、记录与持久化节点"""

    def __init__(self, section_judge: HostSectionJudge):
        """初始化 Host 节点并保存章节研判器"""
        # 研判器封装 LLM 调用，节点本身只负责状态流转
        self._section_judge = section_judge

    async def collect_agent_output(self, state: HostState) -> dict[str, Any]:
        """保存当前 Agent 章节输出并生成对应讨论事件"""
        # 1. 把事件载荷解析成统一的章节输出对象
        #    payload 形如 {"source": "insight"|"media", "section_key": ..., "body": ...}
        agent_output: AgentSectionOutput = AgentSectionOutput.from_section_ready_event(
            state["event_payload"]
        )
        # 2. 存入共享的章节配对仓库（按 section_key + source 累积）
        #    当同一章节的 insight 与 media 都到齐后，该章节才可被研判
        state["section_pair_store"].store_output(agent_output)
        # 3. 为本次输出生成一条讨论事件，供前端/事件流展示
        discussion_events = [
            build_agent_discussion_event(state["task_id"], agent_output)
        ]
        # 返回增量状态：仓库是同一对象引用，事件列表为本轮新增
        return {
            "section_pair_store": state["section_pair_store"],
            "discussion_events": discussion_events
        }

    async def generate_section_judgement(
            self,
            state: HostState
    ) -> dict[str, Any]:
        """调用 Host LLM 为当前已齐备章节生成结构化研判"""
        # 按固定章节顺序取第一个"双方输出已齐备且尚未研判"的配对
        section_pair = state["section_pair_store"].get_ready_pair()
        logger.info(f"【{display_agent_name('host')}】双Agent章节已齐备,开始研判 章节={section_pair.section_key}")
        # 让 LLM 对比 insight/media 两份章节正文，产出结构化裁决
        section_judgement = await self._section_judge.judge_section(section_pair)
        # 只放入临时候选字段，等待 apply_section_judgement 落库
        return {"section_judgement": section_judgement}

    async def apply_section_judgement(
            self,
            state: HostState
    ) -> dict[str, Any]:
        """将章节研判应用到 Host 状态并生成讨论事件"""
        section_judgement = state["section_judgement"]

        # 1. 在仓库中标记该章节已研判，避免重复处理
        state["section_pair_store"].mark_judged(section_judgement.section_key)

        # 2. 把本次研判追加到累计裁决列表（不改动已有历史）
        judgements = [*state["judgements"], section_judgement]
        # 3. 追加一条研判讨论事件，供前端实时展示
        discussion_events = [
            *state["discussion_events"],
            build_judgement_discussion_event(
                state["task_id"],
                section_judgement
            )
        ]
        logger.info(f"【{display_agent_name('host')}】章节研判完成 章节={section_judgement.section_key}")
        return {
            "section_pair_store": state["section_pair_store"],
            "judgements": judgements,
            "discussion_events": discussion_events
        }

    async def save_judgements(self, state: HostState) -> dict[str, Any]:
        """保存 Host 结构化研判"""
        # 1. 本次任务的 Host 输出目录（如 output/<task_id>/host）
        output_dir = get_report_dir(state["task_id"], "host")

        # 2. 将 Pydantic 裁决模型序列化为 JSON 数组；ensure_ascii=False 保留中文
        structured_content = json.dumps(
            [judgement.model_dump() for judgement in state["judgements"]],
            ensure_ascii=False,
            indent=2
        )
        # 3. 写入 judgements.json 并返回路径用于日志
        json_path = save_report(
            output_dir,
            "judgements.json",
            structured_content
        )
        logger.info(f"Host 结构化研判已保存 {json_path}")
        # 纯落盘操作，不修改图状态
        return {}
