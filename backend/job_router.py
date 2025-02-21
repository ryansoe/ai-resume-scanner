# backend/job_router.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import db
from user_router import get_current_user
import openai
import os
import json
from bson import ObjectId

job_router = APIRouter()

class JobCreate(BaseModel):
    title: str
    description: str

@job_router.post("/create-job")
def create_job(job: JobCreate, current_user: dict = Depends(get_current_user)):
    """
    Create a new job listing, link it to the current user,
    and auto-extract required skills from the description.
    Ensures 'required_skills' is a list of strings.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # 1. Extract skills from job description
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that extracts professional skills "
                        "from job descriptions. "
                        "Return ONLY a strict JSON array of strings with NO code fences, "
                        "e.g. [\"Python\", \"SQL\", \"React\"]."
                    )
                },
                {
                    "role": "user",
                    "content": job.description
                }
            ],
            temperature=0.0
        )
        raw_output = response.choices[0].message.content.strip()

        try:
            parsed_skills = json.loads(raw_output)
            if isinstance(parsed_skills, list):
                required_skills = parsed_skills
            else:
                # fallback if GPT returned something else
                required_skills = [raw_output]
        except json.JSONDecodeError:
            required_skills = [raw_output]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    # 2. Store the job
    job_doc = {
        "title": job.title,
        "description": job.description,
        "required_skills": required_skills,
        "user_id": str(current_user["_id"]),
        "username": current_user["username"]
    }
    result = db.jobs.insert_one(job_doc)

    return {
        "message": "Job created and skills extracted successfully",
        "job_id": str(result.inserted_id),
        "required_skills": required_skills
    }


@job_router.post("/match/{job_id}")
def match_resumes(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    For a given job, compare its required skills to all
    resumes belonging to the current user. Return a ranked list.
    """
    job = db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this job")

    job_skills = set(job.get("required_skills", []))

    user_resumes = list(db.resumes.find({"user_id": str(current_user["_id"])}))
    ranked_results = []
    for resume in user_resumes:
        resume_skills = set(resume.get("skills", []))
        if not resume_skills:
            overlap_score = 0
        else:
            intersection = job_skills.intersection(resume_skills)
            overlap_score = len(intersection) / len(job_skills) if len(job_skills) > 0 else 0

        ranked_results.append({
            "resume_id": str(resume["_id"]),
            "filename": resume.get("filename"),
            "overlap_score": overlap_score,
            "matched_skills": list(intersection)
        })

    ranked_results.sort(key=lambda x: x["overlap_score"], reverse=True)

    return {
        "job_id": job_id,
        "job_title": job["title"],
        "matches": ranked_results
    }