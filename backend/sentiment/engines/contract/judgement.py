"""主持人结构化裁决契约:Host 与 Report 引擎共享的裁决模型与 Markdown 渲染"""

from pydantic import BaseModel, Field


class SectionJudgement(BaseModel):
    """主持人对单个章节的结构化裁决"""

    # 章节标识：与 SECTION_DEFINITIONS 中的 key 对应，用于把裁决归位到对应章节
    section_key: str
    # 双方（正方/反方或不同信源）达成一致的观点；缺省为空列表
    aligned_points: list[str] = Field(default_factory=list)
    # 双方存在争议的分歧点；缺省为空列表
    conflicts: list[str] = Field(default_factory=list)
    # 对证据充分性、可信度及信息缺口的评估文本
    evidence_review: str
    # 主持人的最终研判结论，渲染时作为整段裁决的开头
    host_judgement: str

    @property
    def content(self) -> str:
        """渲染讨论区展示用的 Markdown 文本"""
        return render_judgement_markdown(self)


def render_judgement_markdown(judgement: SectionJudgement) -> str:
    """将结构化裁决渲染为 Markdown,标题层级按嵌入上下文调整"""
    # 统一使用三级标题，表示这是嵌入在某个章节讨论区内部的小节
    heading_level = "#" * 3
    # 依次拼接四个部分：研判结论、一致观点、关键分歧、证据情况
    blocks = [
        # 结论段落本身不加标题；为空时给出占位文案，避免渲染出空块
        judgement.host_judgement or "暂无研判",
        f"{heading_level} 双方一致观点\n"
        f"{format_markdown_list(judgement.aligned_points)}",
        f"{heading_level} 关键分歧\n"
        f"{format_markdown_list(judgement.conflicts)}",
        f"{heading_level} 证据情况与信息缺口\n"
        f"{judgement.evidence_review or '暂无补充'}"
    ]
    # 各块之间用空行分隔，保证 Markdown 段落/标题正确渲染
    return "\n\n".join(blocks)


def format_markdown_list(items: list[str]) -> str:
    """渲染无序列表"""
    # 每一项渲染成 "- xxx"；列表为空时返回占位项，避免出现空列表
    return "\n".join(f"- {item}" for item in items) or "- 暂无"
