"""
Builds the Phase 3 mentorship graph:

  coordinator --Send fan-out--> specialist(s) --> synthesizer --> grounding_check
                                                                      │
                                        fails, retries left ---------┤
                                                                      ↓
                                             passes / out of retries -> END
"""

from langgraph.graph import END, StateGraph

from src.mentorship.nodes import (
    MAX_RETRIES,
    coordinator_node,
    grounding_check_node,
    route_to_specialists,
    should_retry,
    specialist_node,
    synthesizer_node,
)
from src.mentorship.state import MentorshipState
from src.profile_schema import StartupProfile


def build_mentorship_graph():
    graph = StateGraph(MentorshipState)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("specialist", specialist_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("grounding_check", grounding_check_node)

    graph.set_entry_point("coordinator")
    graph.add_conditional_edges("coordinator", route_to_specialists, ["specialist"])
    graph.add_edge("specialist", "synthesizer")
    graph.add_edge("synthesizer", "grounding_check")
    graph.add_conditional_edges("grounding_check", should_retry, {"retry": "synthesizer", "done": END})

    return graph.compile()


def answer_question(profile: StartupProfile, question: str) -> dict:
    graph = build_mentorship_graph()
    result = graph.invoke(
        {
            "profile": profile,
            "question": question,
            "specialists_to_run": [],
            "specialist_responses": {},
            "draft_reply": None,
            "grounding_issues": [],
            "retry_count": 0,
        }
    )
    return {
        "reply": result["draft_reply"],
        "specialists_used": list(result["specialist_responses"].keys()),
        "remaining_grounding_issues": result["grounding_issues"],
    }
