import os
from fastapi import FastAPI
from dotenv import load_dotenv
from db import db
from resume_router import resume_router
from user_router import user_router

load_dotenv()  # Take environment variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()

app.include_router(resume_router, prefix="/resumes", tags=["resumes"])
app.include_router(user_router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Screener!"}

@app.get("/test-db")
def test_db():
    # Attempt to insert or fetch something from the database
    db.test_collection.insert_one({"status": "connected"})
    return {"message": "Database connection is working!"}
