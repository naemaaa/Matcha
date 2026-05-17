from typing import TypedDict, List, Optional, Annotated
import operator

class UserProfile(TypedDict):
    current_role: Optional[str]
    target_role: Optional[str]
    current_skills: List[str]
    hours_per_week: Optional[int]
    budget_idr: Optional[int]
    timeline_months: Optional[int]

class MatchaState(TypedDict):
    # Conversation
    messages: Annotated[List[dict], operator.add]
    user_input: str

    #CV Review
    cv_text: Optional[str]

    #linkedin
    linkedin_text: Optional[str]

    # Intent
    detected_intent: Optional[str]
    intent_confidence: Optional[float]
    
    # Profile
    user_profile: Optional[UserProfile]
    profile_complete: bool
    
    # Analysis
    skill_gaps: Optional[List[str]]
    learning_path: Optional[str]
    recommended_resources: Optional[str]
    
    # Output
    agent_response: Optional[str]
    
    # Drift detection
    previous_intent_history: List[str]
    drift_detected: bool
