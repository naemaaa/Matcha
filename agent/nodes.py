import json
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from .state import MatchaState

load_dotenv()
from prompts import (
    INTENT_CLASSIFIER_PROMPT,
    USER_PROFILER_PROMPT,
    SKILL_GAP_PROMPT,
    RESOURCE_RECOMMENDER_PROMPT,
    CV_REVIEWER_PROMPT,
)
from langchain_groq import ChatGroq


def _get_groq_llm(temperature: float = 0.1) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is required to run the Matcha agent. "
            "Set it in your environment or in the .env file."
        )
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=temperature,
    )

def intent_classifier_node(state: MatchaState) -> dict:
    prompt = INTENT_CLASSIFIER_PROMPT.format(
        user_input=state["user_input"]
    )
    response = _get_groq_llm(0.1).invoke([HumanMessage(content=prompt)])
    try:
        # Bersihkan response kalau ada markdown code block
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        return {
            "detected_intent": result.get("intent", "CAREER_EXPLORATION"),
            "intent_confidence": result.get("confidence", 0.5),
            "previous_intent_history": state.get("previous_intent_history", []) + [result.get("intent", "CAREER_EXPLORATION")]
        }
    except:
        return {
            "detected_intent": "CAREER_EXPLORATION",
            "intent_confidence": 0.5,
            "previous_intent_history": state.get("previous_intent_history", []) + ["CAREER_EXPLORATION"]
        }

def user_profiler_node(state: MatchaState) -> dict:
    history_text = "\n".join([
        f"{m['role'].upper()}: {m['content']}"
        for m in state.get("messages", [])[-10:]
    ])
    prompt = USER_PROFILER_PROMPT.format(
        chat_history=history_text,
        user_input=state["user_input"],
        detected_intent=state.get("detected_intent", "")
    )
    response = _get_groq_llm(0.1).invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        profile = json.loads(content.strip())
        old_profile = state.get("user_profile") or {}
        merged = {**old_profile, **{k: v for k, v in profile.items() if v is not None}}
        is_complete = bool(merged.get("target_role") and merged.get("current_role") is not None)
        return {"user_profile": merged, "profile_complete": is_complete}
    except:
        return {}

def skill_gap_node(state: MatchaState) -> dict:
    profile = state.get("user_profile") or {}
    prompt = SKILL_GAP_PROMPT.format(
        user_profile=json.dumps(profile, ensure_ascii=False),
        detected_intent=state.get("detected_intent", "")
    )
    response = _get_groq_llm(0.7).invoke([HumanMessage(content=prompt)])
    return {
        "agent_response": response.content,
        "skill_gaps": response.content  # simpan juga ke skill_gaps
    }


def resource_recommender_node(state: MatchaState) -> dict:
    profile = state.get("user_profile") or {}
    
    # Load data kursus dari JSON
    try:
        with open("data/course_catalog.json", encoding="utf-8") as f:
            courses = json.load(f)
        courses_text = json.dumps(courses[:20], ensure_ascii=False)
    except:
        courses_text = "Data kursus tidak tersedia"
    
    prompt = RESOURCE_RECOMMENDER_PROMPT.format(
        courses_data=courses_text,
        skill_gaps=state.get("skill_gaps", ""),
        budget=profile.get("budget_idr", 0)
    )
    response = _get_groq_llm(0.7).invoke([HumanMessage(content=prompt)])
    return {"agent_response": response.content}

def drift_detector_node(state: MatchaState) -> dict:
    history = state.get("previous_intent_history", [])
    if len(history) < 3:
        return {"drift_detected": False}
    recent = set(history[-3:])
    drift = len(recent) >= 3
    return {"drift_detected": drift}


def cv_reviewer_node(state: MatchaState) -> dict:
    cv_text = state.get("cv_text", "")
    if not cv_text:
        return {"agent_response": "Belum ada CV yang diupload. Silakan upload CV kamu terlebih dahulu."}
    
    profile = state.get("user_profile") or {}
    
    prompt = CV_REVIEWER_PROMPT.format(
        cv_text=cv_text,
        target_role=profile.get("target_role", "belum ditentukan"),
        skill_gaps=state.get("skill_gaps", "belum dianalisis")
    )
    response = _get_groq_llm(0.7).invoke([HumanMessage(content=prompt)])
    return {"agent_response": response.content}

def linkedin_reviewer_node(state: MatchaState) -> dict:
    linkedin_text = state.get("linkedin_text", "")
    if not linkedin_text:
        return {"agent_response": "Belum ada profil LinkedIn yang diupload. Silakan upload PDF LinkedIn kamu terlebih dahulu."}
    
    profile = state.get("user_profile") or {}
    
    from prompts import LINKEDIN_REVIEWER_PROMPT
    prompt = LINKEDIN_REVIEWER_PROMPT.format(
        linkedin_text=linkedin_text,
        target_role=profile.get("target_role", "belum ditentukan"),
        skill_gaps=state.get("skill_gaps", "belum dianalisis")
    )
    response = _get_groq_llm(0.7).invoke([HumanMessage(content=prompt)])
    return {"agent_response": response.content}