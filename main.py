from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from importlib_resources import contents
from pydantic import BaseModel
from typing import Optional
import uvicorn
import io
import json

from agent.graph import matcha_graph
from agent.memory import init_db, save_session, load_session
from utils.helpers import extract_cv_text

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    user_input: str
    agent_state: Optional[dict] = None

class JobRequest(BaseModel):
    session_id: str
    job_description: str
    agent_state: Optional[dict] = None

class ReviewRequest(BaseModel):
    session_id: str
    document_type: str  # 'cv' or 'linkedin'
    agent_state: Optional[dict] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    saved = load_session(request.session_id)
    
    current_state = {
        "messages": [],
        "profile_complete": False,
        "drift_detected": False,
        "previous_intent_history": [],
        "cv_text": None,
        "linkedin_text": None,
        **saved,
        **(request.agent_state or {}),
        "user_input": request.user_input,
    }
    
    result = matcha_graph.invoke(current_state)
    save_session(request.session_id, result)
    
    return {
        "response": result.get("agent_response", "Maaf, terjadi error."),
        "agent_state": result
    }

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    file_type: str = Form(...)
):
    contents = await file.read()
    file_like = io.BytesIO(contents)
    file_like.filename = file.filename
    extracted_text = extract_cv_text(file_like)
    
    saved = load_session(session_id)
    if file_type == "cv":
        saved["cv_text"] = extracted_text
        saved["cv_uploaded"] = True
    else:
        saved["linkedin_text"] = extracted_text
        saved["linkedin_uploaded"] = True
    save_session(session_id, saved)
    
    return {"extracted_text": extracted_text, "status": "success"}

@app.post("/review-document")
async def review_document(request: ReviewRequest):
    """
    Analyze CV or LinkedIn dan extract profil, skills, etc.
    """
    saved = load_session(request.session_id)
    document_text = saved.get("cv_text") if request.document_type == "cv" else saved.get("linkedin_text")
    
    if not document_text:
        return {"error": f"No {request.document_type} document found"}
    
    review_prompt = f"""
Analyze this {request.document_type.upper()} and extract:
1. Current role/position
2. Years of experience
3. Top 5 skills/competencies
4. Education background
5. Career goals (if mentioned)

{request.document_type.upper()} Content:
{document_text}

Return as JSON:
{{
    "current_role": "string",
    "experience_years": number,
    "skills": ["skill1", "skill2", ...],
    "education": "string",
    "career_goals": "string or null"
}}
"""
    
    current_state = {
        "messages": [],
        "profile_complete": False,
        "drift_detected": False,
        "previous_intent_history": [],
        **saved,
        **(request.agent_state or {}),
        "user_input": f"tolong review {request.document_type} saya dan ekstrak info penting",
    }
    
    # Jalankan graph untuk review
    result = matcha_graph.invoke(current_state)
    
    # Extract structured data dari review response
    review_response = result.get("agent_response", "")
    extracted_data = {"skills": [], "current_role": None, "experience_years": None}
    
    # Simple extraction dari response
    try:
        # Try to parse if it contains JSON
        import re
        json_match = re.search(r'\{.*\}', review_response, re.DOTALL)
        if json_match:
            extracted_data = json.loads(json_match.group())
    except:
        # Fallback: extract skills mention
        if "skill" in review_response.lower():
            lines = review_response.split('\n')
            for line in lines:
                if any(skill_word in line.lower() for skill_word in ['skill', 'keahlian', 'competency', '•', '-']):
                    extracted_data["skills"].append(line.strip().lstrip('•-').strip())
    
    # Update state dengan extracted info
    if extracted_data.get("current_role"):
        if not result.get("user_profile"):
            result["user_profile"] = {}
        result["user_profile"]["current_role"] = extracted_data["current_role"]
    
    if extracted_data.get("skills"):
        result["extracted_skills"] = extracted_data["skills"]
        if not result.get("user_profile"):
            result["user_profile"] = {}
        result["user_profile"]["skills"] = extracted_data["skills"]
    
    if request.document_type == "cv":
        result["cv_reviewed"] = True
        result["cv_review"] = review_response
    else:
        result["linkedin_reviewed"] = True
        result["linkedin_review"] = review_response
    
    save_session(request.session_id, result)
    
    return {
        "response": review_response,
        "agent_state": result,
        "extracted_data": extracted_data
    }

@app.post("/analyze-job")
async def analyze_job(request: JobRequest):
    saved = load_session(request.session_id)
    
    current_state = {
        "messages": [],
        "profile_complete": False,
        "drift_detected": False,
        "previous_intent_history": [],
        "cv_text": None,
        "linkedin_text": None,
        **saved,
        **(request.agent_state or {}),
        "user_input": f"tolong analisis job description ini: {request.job_description}",
        "job_description": request.job_description,
    }
    
    result = matcha_graph.invoke(current_state)
    save_session(request.session_id, result)
    
    return {
        "response": result.get("agent_response", "Maaf, terjadi error."),
        "agent_state": result
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)