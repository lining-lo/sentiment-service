from typing import Any

from langgraph.graph import END, START, StateGraph

from sentiment.engines.common.report_generation import ReportGenerationNode
from sentiment.engines.common.report_persistence import ReportPersistenceNode
from sentiment.engines.common.research_graph_runtime import (
    SECTION_SUMMARY_LOOP_MAPPING,
    ResearchRunContext,
    route_after_section_summary
)
from sentiment.engines.insight_agent.nodes.evidence_reranking_node import EvidenceRerankingNode
from sentiment.engines.insight_agent.nodes.evidence_retrieval_node import EvidenceRetrievalNode
from sentiment.engines.insight_agent.nodes.section_evidence_routing_node import SectionEvidenceRoutingNode
from sentiment.engines.insight_agent.nodes.section_preparation_node import SectionPreparationNode
from sentiment.engines.insight_agent.nodes.section_summary_node import SectionSummaryNode
from sentiment.engines.insight_agent.state import InsightState


def build_insight_graph(ctx: ResearchRunContext) -> Any:
    """构建并编译私域舆情智能体的 LangGraph 工作流"""

    graph = StateGraph(InsightState)  # type: ignore
    graph.add_node("retrieve_evidence", EvidenceRetrievalNode(ctx))
    graph.add_node("rerank_evidence", EvidenceRerankingNode(ctx))
    graph.add_node("route_section_evidence", SectionEvidenceRoutingNode(ctx))
    graph.add_node("prepare_sections", SectionPreparationNode(ctx))
    graph.add_node("summarize_sections", SectionSummaryNode(ctx))
    graph.add_node("generate_agent_report", ReportGenerationNode(ctx))
    graph.add_node("persist_agent_report", ReportPersistenceNode(ctx))

    graph.add_edge(START, "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "rerank_evidence")
    graph.add_edge("rerank_evidence", "route_section_evidence")
    graph.add_edge("route_section_evidence", "prepare_sections")
    graph.add_edge("prepare_sections", "summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING
    )
    graph.add_edge("generate_agent_report", "persist_agent_report")
    graph.add_edge("persist_agent_report", END)

    return graph.compile()
