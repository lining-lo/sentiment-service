from typing import Any

from langgraph.graph import END, START, StateGraph

from sentiment.engines.common.report_generation import ReportGenerationNode
from sentiment.engines.common.report_persistence import ReportPersistenceNode
from sentiment.engines.common.research_graph_runtime import (
    SECTION_SUMMARY_LOOP_MAPPING,
    ResearchRunContext,
    route_after_section_summary
)
from sentiment.engines.media_agent.nodes import (
    SearchNode,
    SearchPlanningNode,
    SectionSummaryNode
)
from sentiment.engines.media_agent.state import MediaState


def build_graph(ctx: ResearchRunContext) -> Any:
    """编排规划、检索、摘要、排版与落盘节点"""
    graph = StateGraph(MediaState)  # type: ignore
    graph.add_node("plan_search", SearchPlanningNode(ctx))  # type: ignore
    graph.add_node("search", SearchNode(ctx))  # type: ignore
    graph.add_node("summarize_sections", SectionSummaryNode(ctx))  # type: ignore
    graph.add_node("generate_agent_report", ReportGenerationNode(ctx))  # type: ignore
    graph.add_node("persist_agent_report", ReportPersistenceNode(ctx))  # type: ignore
    graph.add_edge(START, "plan_search")
    graph.add_edge("plan_search", "search")
    graph.add_edge("search", "summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING
    )
    graph.add_edge("generate_agent_report", "persist_agent_report")
    graph.add_edge("persist_agent_report", END)
    return graph.compile()
