# extract_skills.py

import os
import json
import openai
from fastapi import HTTPException

def extract_skills_from_text(resume_text: str) -> list:
    """
    Reusable helper function that:
    1) Calls OpenAI ChatCompletion to parse skills from resume_text.
    2) Returns a list of all-lowercase strings.
    If no text is provided, returns an empty list.
    """
    if not resume_text.strip():
        # If there's no text, just return empty
        return []

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that extracts professional skills "
                        "from the following text. "
                        "Return ONLY a strict JSON array of strings with NO code fences, "
                        "e.g. [\"python\", \"sql\", \"react\"]."
                    )
                },
                {
                    "role": "user",
                    "content": resume_text
                }
            ],
            temperature=0.0
        )
        raw_output = response.choices[0].message.content.strip()

        # Attempt to parse JSON
        try:
            parsed = json.loads(raw_output)
            if not isinstance(parsed, list):
                return [raw_output.lower()]
            return [skill.lower() for skill in parsed]
        except json.JSONDecodeError:
            # If parse fails, fallback to single string
            return [raw_output.lower()]

    except Exception as e:
        # Re-raise or log as needed
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")