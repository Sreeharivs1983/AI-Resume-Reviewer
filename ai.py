from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in the environment")

client = Groq(api_key=GROQ_API_KEY)

REQUIRED_RESPONSE_KEYS = {
    "resume_score": int,
    "strengths": list,
    "weaknesses": list,
    "missing_skills": list,
    "improvement_suggestions": list,
    "professional_summary": str,
    "final_verdict": str,
}


def parse_json_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(content[start:end + 1])
            except json.JSONDecodeError:
                pass
        raise


def validate_review_response(response):
    if not isinstance(response, dict):
        raise ValueError("AI response is not a valid JSON object")

    for key, expected_type in REQUIRED_RESPONSE_KEYS.items():
        if key not in response:
            raise ValueError(f"Missing required key '{key}' in AI response")

        value = response[key]
        if not isinstance(value, expected_type):
            if expected_type is int and isinstance(value, float) and value.is_integer():
                response[key] = int(value)
            else:
                raise ValueError(
                    f"Invalid type for '{key}'. Expected {expected_type.__name__}, got {type(value).__name__}"
                )

        if expected_type is list:
            if any(not isinstance(item, str) for item in value):
                raise ValueError(f"All items in '{key}' must be strings")

    score = response["resume_score"]
    if not isinstance(score, int):
        raise ValueError("resume_score must be an integer")
    if score < 0 or score > 100:
        raise ValueError("resume_score must be between 0 and 100")

    return response


def review_resume(resume_text, job_role):
    prompt = f"""
You are a senior ATS resume reviewer and technical hiring expert.
Analyze the resume below for the target job role and provide a concise, professional evaluation.

Target Job Role:
{job_role}

Resume:
{resume_text}

Return ONLY a valid JSON object with these keys:
- resume_score: integer from 0 to 100
- strengths: list of strings
- weaknesses: list of strings
- missing_skills: list of strings
- improvement_suggestions: list of strings
- professional_summary: string
- final_verdict: string

Do NOT return markdown, explanations, or text outside the JSON.
Do NOT wrap the JSON in code fences.
Use the exact keys shown above.
If a field cannot be determined, return an empty string or empty list.

Example format:
{{
    "resume_score": 85,
    "strengths": [
        "Strong Python experience",
        "Clear project outcomes"
    ],
    "weaknesses": [
        "Missing ATS keywords",
        "Formatting is inconsistent"
    ],
    "missing_skills": [
        "Docker",
        "Kubernetes"
    ],
    "improvement_suggestions": [
        "Add a concise summary statement",
        "Use bullet points for achievements"
    ],
    "professional_summary": "Experienced software engineer with strong backend and cloud skills...",
    "final_verdict": "Strong resume with minor ATS and formatting improvements."
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )
    except Exception as exc:
        raise RuntimeError("Failed to call Groq API") from exc

    try:
        content = response.choices[0].message.content
    except Exception as exc:
        raise RuntimeError("Unexpected response format from Groq API") from exc

    parsed_response = parse_json_content(content)
    return validate_review_response(parsed_response)
