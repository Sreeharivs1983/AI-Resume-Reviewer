from groq import Groq
from dotenv import load_dotenv
import os
import json
import streamlit as st

load_dotenv()


# ===========================
# Groq API Key
# ===========================

def get_groq_api_key():
    # Local development: .env
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return api_key

    # Streamlit Cloud: Secrets
    try:
        secrets = st.secrets
    except Exception:
        return None

    if isinstance(secrets, dict) and "GROQ_API_KEY" in secrets:
        return secrets["GROQ_API_KEY"]

    return None


# ===========================
# Groq Client
# ===========================

client = None


def get_client():
    global client

    if client is None:

        api_key = get_groq_api_key()

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file or Streamlit Cloud secrets."
            )

        client = Groq(api_key=api_key)

    return client


# ===========================
# Expected AI Response
# ===========================

REQUIRED_RESPONSE_KEYS = {
    "resume_score": int,
    "strengths": list,
    "weaknesses": list,
    "missing_skills": list,
    "improvement_suggestions": list,
    "professional_summary": str,
    "final_verdict": str,
}


# ===========================
# JSON Parsing
# ===========================

def parse_json_content(content):

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        # Fallback in case the model adds
        # extra text around the JSON.
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1 and start < end:

            try:
                return json.loads(content[start:end + 1])

            except json.JSONDecodeError:
                pass

        raise


# ===========================
# Response Validation
# ===========================

def validate_review_response(response):

    if not isinstance(response, dict):
        raise ValueError(
            "AI response is not a valid JSON object"
        )

    # Check required fields
    for key, expected_type in REQUIRED_RESPONSE_KEYS.items():

        if key not in response:
            raise ValueError(
                f"Missing required key '{key}' in AI response"
            )

        value = response[key]

        # Handle score such as 85.0
        if expected_type is int:

            if isinstance(value, float) and value.is_integer():
                response[key] = int(value)

            elif not isinstance(value, int):
                raise ValueError(
                    f"Invalid type for '{key}'. "
                    f"Expected integer, got {type(value).__name__}"
                )

        else:

            if not isinstance(value, expected_type):
                raise ValueError(
                    f"Invalid type for '{key}'. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        # Validate list contents
        if expected_type is list:

            if any(not isinstance(item, str) for item in value):
                raise ValueError(
                    f"All items in '{key}' must be strings"
                )

    # Validate score range
    score = response["resume_score"]

    if score < 0 or score > 100:
        raise ValueError(
            "resume_score must be between 0 and 100"
        )

    return response


# ===========================
# Resume Review
# ===========================

def review_resume(resume_text, job_role):

    prompt = f"""
You are a senior ATS resume reviewer and technical hiring expert.

Analyze the resume below for the target job role and provide a concise,
professional and realistic evaluation.

Target Job Role:
{job_role}

Resume:
{resume_text}

Evaluate the resume based on:

- Relevance to the target job role
- Technical skills
- Projects and experience
- ATS keyword relevance
- Resume clarity
- Formatting
- Professional presentation
- Skill gaps

Return ONLY a valid JSON object.

The JSON must contain exactly these fields:

- resume_score: integer from 0 to 100
- strengths: list of strings
- weaknesses: list of strings
- missing_skills: list of strings
- improvement_suggestions: list of strings
- professional_summary: string
- final_verdict: string

Rules:

1. resume_score must be an integer between 0 and 100.
2. strengths must contain concise observations about the resume.
3. weaknesses must contain genuine areas for improvement.
4. missing_skills should contain relevant skills missing for the target role.
5. improvement_suggestions should contain practical and actionable recommendations.
6. professional_summary should summarize the candidate professionally.
7. final_verdict should provide an overall assessment.
8. Do not invent experience, education, projects or skills that are not present.
9. Do not return Markdown.
10. Do not return code fences.
11. Do not return explanations outside the JSON object.
"""


    # ===========================
    # Call Groq
    # ===========================

    try:

        groq_client = get_client()

        response = groq_client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,

            # Ask the model to return valid JSON.
            response_format={
                "type": "json_object"
            }
        )

    except Exception as exc:

        # Keep the original error so debugging
        # is easier during development/deployment.
        raise RuntimeError(
            f"Failed to call Groq API: {exc}"
        ) from exc


    # ===========================
    # Get AI Response
    # ===========================

    try:

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Groq returned an empty response"
            )

    except Exception as exc:

        raise RuntimeError(
            f"Unexpected response format from Groq API: {exc}"
        ) from exc


    # ===========================
    # Parse JSON
    # ===========================

    try:

        parsed_response = parse_json_content(content)

    except Exception as exc:

        raise RuntimeError(
            f"AI returned invalid JSON: {exc}"
        ) from exc


    # ===========================
    # Validate Response
    # ===========================

    try:

        validated_response = validate_review_response(
            parsed_response
        )

    except Exception as exc:

        raise RuntimeError(
            f"AI response validation failed: {exc}"
        ) from exc


    return validated_response