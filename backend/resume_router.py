# backend/resume_router.py

import openai
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from bson import ObjectId
import io
import os
from db import db
from user_router import get_current_user  # The dependency we created

resume_router = APIRouter()

@resume_router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate File Type eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTczOTk1MDQ5OX0.a2v8RQ6_oTUhSqrn2cHA2tFvo8gNthjfLoIP-JsjZzQ
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # 2. Read File Bytes
    file_bytes = await file.read()

    try:
        # 3. Extract text with PyPDF2
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() or ""

        # 4. Store Resume Text & Metadata in MongoDB
        # Link to the user by their username or user ID
        resume_data = {
            "filename": file.filename,
            "content_type": file.content_type,
            "resume_text": extracted_text,
            "user_id": str(current_user["_id"]),   # store user ID
            "username": current_user["username"], # or store username
        }
        result = db.resumes.insert_one(resume_data)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Resume uploaded and processed successfully",
                "resume_id": str(result.inserted_id),
                "linked_to_user": current_user["username"]
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

@resume_router.post("/upload-multiple")
async def upload_multiple_resumes(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Accept multiple PDF files and link them to the current user.
    """
    uploaded_resumes = []

    for file in files:
        # 1. Validate File Type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. File '{file.filename}' is {file.content_type}.")

        # 2. Read File Bytes
        file_bytes = await file.read()
        try:
            # 3. Extract text with PyPDF2
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""

            # 4. Store Resume Text & Metadata in MongoDB
            resume_data = {
                "filename": file.filename,
                "content_type": file.content_type,
                "resume_text": extracted_text,
                "user_id": str(current_user["_id"]),
                "username": current_user["username"],
            }
            result = db.resumes.insert_one(resume_data)
            uploaded_resumes.append({
                "filename": file.filename,
                "resume_id": str(result.inserted_id)
            })

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDF '{file.filename}': {e}"
            )

    return {
        "message": "Files uploaded and processed successfully",
        "resumes": uploaded_resumes,
        "linked_to_user": current_user["username"]
    }

@resume_router.get("/my-resumes")
def get_my_resumes(current_user: dict = Depends(get_current_user)):
    """
    Fetch all resumes belonging to the current user.
    """
    user_id = str(current_user["_id"])
    
    # Query the resumes collection for docs where user_id = current user's ID
    user_resumes = list(db.resumes.find({"user_id": user_id}))
    
    # Convert ObjectId to string for JSON serialization
    for r in user_resumes:
        r["_id"] = str(r["_id"])
    
    return {"username": current_user["username"], "resumes": user_resumes}

@resume_router.post("/extract-skills/{resume_id}")
def extract_skills(
    resume_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Extract skills from the specified resume using OpenAI GPT."""

    # 1. Fetch the resume by ID, ensure it belongs to the current user
    resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    resume_text = resume.get("resume_text", "")
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty or missing")

    # 2. Call the OpenAI API to extract skills
    openai.api_key = openai.api_key or os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        # -- Option A: Using ChatCompletion (GPT-3.5/4) --
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts professional skills from resumes."},
                {"role": "user", "content": f"Resume text:\n{resume_text}\n\nExtract the skills as a list of strings."},
            ],
            temperature=0.0
        )
        raw_output = response["choices"][0]["message"]["content"].strip()



        # -- Option B: Using Completion (older models) --
        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=f"Extract professional skills from the following resume text:\n{resume_text}\n\nReturn them as a JSON list.",
        #     temperature=0.0,
        #     max_tokens=200
        # )
        # raw_output = response.choices[0].text.strip()

        # 3. Parse the response content (JSON or text)
        # Assume the model returns something like: ["Python", "SQL", "Machine Learning"]
        # If not strictly JSON, we can parse or do a second pass to parse JSON
        # For safety, let's attempt to parse JSON if possible:
        import json
        try:
            extracted_skills = json.loads(raw_output)
            # ensure it's a list
            if not isinstance(extracted_skills, list):
                # if not a list, handle gracefully
                extracted_skills = [raw_output]
        except json.JSONDecodeError:
            # fallback: store raw string
            extracted_skills = [raw_output]

        # 4. Update the resume document with extracted skills
        db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {"skills": extracted_skills}}
        )

        return {
            "message": "Skills extracted successfully",
            "resume_id": resume_id,
            "skills": extracted_skills
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @resume_router.post("/extract-skills/bulk")
# def extract_skills_bulk(current_user: dict = Depends(get_current_user)):
#     """
#     Extract skills from all of the current user's resumes.
#     """
#     user_resumes = list(db.resumes.find({"user_id": str(current_user["_id"])}))
#     updated_count = 0

#     for res in user_resumes:
#         resume_text = res.get("resume_text", "")
#         if not resume_text.strip():
#             continue

#         # (Same logic: call OpenAI, parse output, update DB)
#         # ...
#         updated_count += 1

#     return {"message": "Bulk skill extraction completed", "updated_resumes": updated_count}

