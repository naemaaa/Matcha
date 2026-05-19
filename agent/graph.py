from langgraph.graph import StateGraph, END

from .state import MatchaState
from .nodes import (
    intent_classifier_node,
    user_profiler_node,
    skill_gap_analyzer_node,
    cv_reviewer_node,
    linkedin_reviewer_node,
    general_responder_node,
)


# ─────────────────────────────────────────────
# Router: tentukan node berikutnya setelah profiler
# ─────────────────────────────────────────────

def route_after_profiler(state: MatchaState) -> str:
    """
    Routing logic setelah User Profiler selesai.
    Keputusan berdasarkan detected_intent.
    """
    intent = state.get("detected_intent", "CAREER_EXPLORATION")

    routing_map = {
        "CAREER_EXPLORATION": "skill_gap_analyzer",
        "SKILL_INQUIRY":      "skill_gap_analyzer",
        "RESOURCE_REQUEST":   "skill_gap_analyzer",
        "CV_REVIEW":          "cv_reviewer",
        "LINKEDIN_REVIEW":    "linkedin_reviewer",
        "PUSH_BACK":          "general_responder",
        "CONFIRMATION":       "general_responder",
        "CONSTRAINT_UPDATE":  "general_responder",
    }

    return routing_map.get(intent, "skill_gap_analyzer")


# ─────────────────────────────────────────────
# Build Graph
# ─────────────────────────────────────────────

def build_matcha_graph():
    graph = StateGraph(MatchaState)

    # Daftarkan semua node
    graph.add_node("intent_classifier",  intent_classifier_node)
    graph.add_node("user_profiler",      user_profiler_node)
    graph.add_node("skill_gap_analyzer", skill_gap_analyzer_node)
    graph.add_node("cv_reviewer",        cv_reviewer_node)
    graph.add_node("linkedin_reviewer",  linkedin_reviewer_node)
    graph.add_node("general_responder",  general_responder_node)

    # Entry point
    graph.set_entry_point("intent_classifier")

    # Edge: intent_classifier → user_profiler (selalu)
    graph.add_edge("intent_classifier", "user_profiler")

    # Edge: user_profiler → routing berdasarkan intent
    graph.add_conditional_edges(
        "user_profiler",
        route_after_profiler,
        {
            "skill_gap_analyzer": "skill_gap_analyzer",
            "cv_reviewer":        "cv_reviewer",
            "linkedin_reviewer":  "linkedin_reviewer",
            "general_responder":  "general_responder",
        },
    )

    # Semua node akhir → END
    graph.add_edge("skill_gap_analyzer", END)
    graph.add_edge("cv_reviewer",        END)
    graph.add_edge("linkedin_reviewer",  END)
    graph.add_edge("general_responder",  END)

    return graph.compile()


# Instance siap pakai — diimport di app.py
matcha_graph = build_matcha_graph()