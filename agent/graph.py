from langgraph.graph import StateGraph, END
from .state import MatchaState
from .nodes import (
    intent_classifier_node,
    user_profiler_node,
    skill_gap_node,
    resource_recommender_node,
    drift_detector_node,
    cv_reviewer_node,
    linkedin_reviewer_node
)

def route_after_intent(state: MatchaState) -> str:
    intent = state.get("detected_intent", "")
    drift = state.get("drift_detected", False)
    
    if drift:
        return "user_profiler"
    
    intent_map = {
        "CAREER_EXPLORATION": "user_profiler",
        "SKILL_INQUIRY": "skill_gap",
        "RESOURCE_REQUEST": "resource_recommender",
        "CONSTRAINT_UPDATE": "user_profiler",
        "PUSH_BACK": "skill_gap",
        "CONFIRMATION": "skill_gap",
        "CV_REVIEW": "cv_reviewer",
        "LINKEDIN_REVIEW": "linkedin_reviewer"
    }
    return intent_map.get(intent, "user_profiler")

def route_after_profile(state: MatchaState) -> str:
    if state.get("profile_complete", False):
        return "skill_gap"
    return "skill_gap"

def build_graph():
    graph = StateGraph(MatchaState)
    
    # Tambah nodes
    graph.add_node("drift_detector",       drift_detector_node)
    graph.add_node("intent_classifier",    intent_classifier_node)
    graph.add_node("user_profiler",        user_profiler_node)
    graph.add_node("skill_gap",            skill_gap_node)
    graph.add_node("resource_recommender", resource_recommender_node)
    graph.add_node("cv_reviewer", cv_reviewer_node)
    graph.add_node("linkedin_reviewer", linkedin_reviewer_node)

    # Entry point
    graph.set_entry_point("drift_detector")
    
    # Edges
    graph.add_edge("drift_detector", "intent_classifier")
    
    graph.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "user_profiler":        "user_profiler",
            "skill_gap":            "skill_gap",
            "resource_recommender": "resource_recommender",
            "cv_reviewer":          "cv_reviewer",
            "linkedin_reviewer":    "linkedin_reviewer"
        }
    )
    
    graph.add_conditional_edges(
        "user_profiler",
        route_after_profile,
        {"skill_gap": "skill_gap"}
    )
    
    graph.add_edge("skill_gap", END)
    graph.add_edge("resource_recommender", END)
    graph.add_edge("cv_reviewer", END)
    graph.add_edge("linkedin_reviewer", END)
    
    return graph.compile()

matcha_graph = build_graph()