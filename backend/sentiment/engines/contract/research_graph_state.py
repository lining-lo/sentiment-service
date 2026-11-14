"""Insight 与 Media 研究图共享的状态契约"""
from typing import Generic, TypeVar
from typing_extensions import TypedDict


class SectionState(TypedDict, total=False):
    """完成规划后在研究图中持续传递的章节状态"""

    section_key: str  # 章节eky
    title: str  # 章节的标题
    body: str  # 章节的内容


SectionStateT = TypeVar("SectionStateT", bound=SectionState)


class ResearchGraphState(TypedDict, Generic[SectionStateT], total=False):
    """
    研究图全流程共享的运行标识、章节与报告状态
    Generic[SectionStateT]：
    ①：类定义时的继承列表
    ②：当前类是一个泛型容器，内部结构依赖于 SectionStateT
    type[SectionStateT]：
    ①：函数参数、返回值或变量的类型标注
    ②：这个值是一个符合 SectionStateT 约束的类本身
    """
    sections: list[SectionStateT]  # 章节列表 本质结构：list[{"section_key": ..., "title": ..., "body": ...}]
    cursor: int  # 章节处理游标
    final_report: str  # 最终报告
