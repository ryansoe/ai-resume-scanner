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
from user_router import get_current_user
import json
from extract_skills import extract_skills_from_text

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
    uploaded_resumes = []

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are allowed. File '{file.filename}' is {file.content_type}."
            )

        file_bytes = await file.read()
        try:
            # Extract PDF text
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""

            # Insert the doc
            resume_data = {
                "filename": file.filename,
                "content_type": file.content_type,
                "resume_text": extracted_text,
                "user_id": str(current_user["_id"]),
                "username": current_user["username"],
            }
            result = db.resumes.insert_one(resume_data)
            resume_id = result.inserted_id

            # REUSE the existing helper function
            extracted_skills = extract_skills_from_text(extracted_text)

            # Update the doc
            db.resumes.update_one(
                {"_id": resume_id},
                {"$set": {"skills": extracted_skills}}
            )

            uploaded_resumes.append({
                "filename": file.filename,
                "resume_id": str(resume_id),
                "extracted_skills": extracted_skills
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

@resume_router.delete("/delete/{resume_id}")
def delete_resume(
    resume_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a resume by ID, only if it belongs to the current user.
    """
    resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.get("user_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this resume")

    db.resumes.delete_one({"_id": ObjectId(resume_id)})
    return {"message": "Resume deleted successfully"}

# @resume_router.post("/extract-skills/bulk")
# def extract_skills_bulk(current_user: dict = Depends(get_current_user)):
#     """
#     Extract skills for all resumes belonging to the current user (bulk).
#     Ensures the final 'skills' field is a list of strings (all lowercase).
#     """
#     user_resumes = list(db.resumes.find({"user_id": str(current_user["_id"])}))
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     if not openai.api_key:
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured")

#     updated_count = 0

#     for res in user_resumes:
#         resume_text = res.get("resume_text", "")
#         if not resume_text.strip():
#             continue

#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": (
#                             "You are an AI assistant that extracts professional skills "
#                             "from the following resume text. "
#                             "Return ONLY a strict JSON array of strings with NO code fences, "
#                             "e.g. [\"Python\", \"SQL\", \"React\"]."
#                         )
#                     },
#                     {
#                         "role": "user",
#                         "content": resume_text
#                     }
#                 ],
#                 temperature=0.0
#             )
#             raw_output = response.choices[0].message.content.strip()

#             try:
#                 extracted_skills = json.loads(raw_output)
#                 if not isinstance(extracted_skills, list):
#                     # If GPT returned a single string, store it as a list
#                     extracted_skills = [raw_output.lower()]
#                 else:
#                     # Lowercase each skill
#                     extracted_skills = [skill.lower() for skill in extracted_skills]
#             except json.JSONDecodeError:
#                 # If we can't parse JSON, fallback to the raw string
#                 extracted_skills = [raw_output.lower()]

#             db.resumes.update_one(
#                 {"_id": res["_id"]},
#                 {"$set": {"skills": extracted_skills}}
#             )
#             updated_count += 1

#         except Exception as e:
#             print(f"Error processing resume {res['_id']}: {e}")

#     return {"message": "Bulk skill extraction completed", "updated_resumes": updated_count}

# @resume_router.post("/extract-skills/{resume_id}")
# def extract_skills(
#     resume_id: str = Path(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Extract skills from a single resume using OpenAI GPT.
#     Ensures the final 'skills' field is a list of strings (all lowercase).
#     """
#     resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
#     if not resume:
#         raise HTTPException(status_code=404, detail="Resume not found")
#     if resume.get("user_id") != str(current_user["_id"]):
#         raise HTTPException(status_code=403, detail="Not authorized to access this resume")

#     resume_text = resume.get("resume_text", "")
#     if not resume_text.strip():
#         raise HTTPException(status_code=400, detail="Resume text is empty or missing")

#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     if not openai.api_key:
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured")

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an AI assistant that extracts professional skills "
#                         "from the following resume text. "
#                         "Return ONLY a strict JSON array of strings with NO code fences, "
#                         "e.g. [\"Python\", \"SQL\", \"React\"]."
#                     )
#                 },
#                 {
#                     "role": "user",
#                     "content": resume_text
#                 }
#             ],
#             temperature=0.0
#         )
#         raw_output = response.choices[0].message.content.strip()

#         try:
#             extracted_skills = json.loads(raw_output)
#             if not isinstance(extracted_skills, list):
#                 extracted_skills = [raw_output.lower()]
#             else:
#                 extracted_skills = [skill.lower() for skill in extracted_skills]
#         except json.JSONDecodeError:
#             extracted_skills = [raw_output.lower()]

#         db.resumes.update_one(
#             {"_id": ObjectId(resume_id)},
#             {"$set": {"skills": extracted_skills}}
#         )

#         return {
#             "message": "Skills extracted successfully",
#             "resume_id": resume_id,
#             "skills": extracted_skills
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))