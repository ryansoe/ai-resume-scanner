# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db import db
from resume_router import resume_router
from user_router import user_router
from job_router import job_router

load_dotenv()  # Take environment variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-resume-scanner-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/resumes", tags=["resumes"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(job_router, prefix="/jobs", tags=["jobs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Screener!"}

@app.get("/test-db")
def test_db():
    # Attempt to insert or fetch something from the database
    db.test_collection.insert_one({"status": "connected"})
    return {"message": "Database connection is working!"}
