"""
Builds the Phase 2 LangGraph graph:

  synthesize -> assemble -> validate --fails, retries left--> synthesize
                                      --passes or out of retries--> END
"""

from langgraph.graph import END, StateGraph

from src.synthesis.nodes import MAX_RETRIES, assemble_node, synthesize_node, validate_node
from src.synthesis.state import SynthesisState


def _should_retry(state: SynthesisState) -> str:
    if state.get("validation_errors") and state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"
    return "done"


def build_synthesis_graph():
    graph = StateGraph(SynthesisState)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("assemble", assemble_node)
    graph.add_node("validate", validate_node)

    graph.set_entry_point("synthesize")
    graph.add_edge("synthesize", "assemble")
    graph.add_edge("assemble", "validate")
    graph.add_conditional_edges("validate", _should_retry, {"retry": "synthesize", "done": END})

    return graph.compile()
