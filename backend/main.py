from fastapi import FastAPI, UploadFile, File, Form
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import shutil
import os
import asyncio
from agents.resume_processor import process_resume
from agents.jd_parser import process_jd
from agents.ats_scorer import getATS_scorerAgent
from agents.improvment_agent import getImprovementAgent
from utils.ats_response_parser import parse_ats_response, extract_score_data
from database.connection import insert_resume_from_json, insert_job, insert_score
from models.openrouter import getOpenRouterModel
from models.groq_openai import GetGroqModelClient

app = FastAPI(title="ATS Resume Scorer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm=GetGroqModelClient()
model = getOpenRouterModel()
ats_agent = getATS_scorerAgent(model)
improvement_agent = getImprovementAgent(model)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "ATS API Running"}

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, resume.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        resume_data = process_resume(llm,file_path)
        if hasattr(resume_data, "model_dump"):
            resume_data = resume_data.model_dump()

        jd_data=process_jd(llm,jd_text)
        if hasattr(jd_data, "model_dump"):
            jd_data = jd_data.model_dump()

        scoring_input = json.dumps({
            "resume_details": resume_data,
            "jd_details": jd_data
        }, indent=2)

        ats_response = await ats_agent.run(task=scoring_input)

        ats_result = None
        for msg in reversed(ats_response.messages):
            if msg.source == "ATS_Scorer":
                ats_result = msg.content
                break
        ats_score_json=parse_ats_response(ats_result)
        extracted__Score = extract_score_data(ats_score_json)

        improvement_response = await improvement_agent.run(task=ats_result)

        improvements = None
        for msg in reversed(improvement_response.messages):
            if msg.source == "ImprovementAgent":
                improvements = msg.content
                break

        resume_id = insert_resume_from_json(resume_data)
        jd_id = insert_job(jd_data)

        insert_score(
            extracted__Score,
            resume_id,
            jd_id,
            improvements
        )

        return {
            "resume": resume_data,
            "jd": jd_data,
            "score": ats_result,
            "improvements": improvements
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    
    
