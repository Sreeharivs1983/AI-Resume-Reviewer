import json
import logging
import os
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fpdf import FPDF

from backend.ai import review_resume, validate_review_response
from backend.utils import extract_text_from_pdf, extract_text_from_docx


# ===========================
# Logging Configuration
# ===========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ===========================
# Configuration
# ===========================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

MAX_RESUME_TEXT_LENGTH = 50_000  # Maximum extracted characters

MAX_JOB_ROLE_LENGTH = 150  # Maximum target role characters

MAX_REVIEW_PAYLOAD_LENGTH = 100_000  # Maximum review JSON characters


FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    ""
).strip()


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]


if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)


# ===========================
# FastAPI Application
# ===========================

app = FastAPI(
    title="AI Resume Reviewer API",
    description="Backend API for the AI Resume Reviewer",
    version="1.0.0"
)


# ===========================
# CORS Configuration
# ===========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Root
# ===========================

@app.get("/")
def root():
    return {
        "message": "AI Resume Reviewer API is running"
    }


# ===========================
# Health Check
# ===========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ===========================
# Resume Analysis
# ===========================

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_role: str = Form(...)
):

    # ---------------------------
    # Validate Job Role
    # ---------------------------

    job_role = job_role.strip()

    if not job_role:
        raise HTTPException(
            status_code=400,
            detail="Job role cannot be empty."
        )

    if len(job_role) > MAX_JOB_ROLE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Job role must be {MAX_JOB_ROLE_LENGTH} "
                "characters or fewer."
            )
        )

    # ---------------------------
    # Validate Filename
    # ---------------------------

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="No resume file was provided."
        )

    original_filename = resume.filename

    # Extract only the filename component.
    # This avoids treating any path information
    # supplied by the client as part of the filename.
    safe_filename = Path(original_filename).name

    filename = safe_filename.lower()

    # ---------------------------
    # Validate File Extension
    # ---------------------------

    if not filename.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    try:

        # ---------------------------
        # Validate File Size
        # ---------------------------

        total_size = 0
        chunk_size = 1024 * 1024  # 1 MB

        while True:

            chunk = await resume.read(chunk_size)

            if not chunk:
                break

            total_size += len(chunk)

            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="Resume file must be 10 MB or smaller."
                )

        # Reset file position so the parser
        # can read the file from the beginning.
        await resume.seek(0)

        # ---------------------------
        # Extract Resume Text
        # ---------------------------

        if filename.endswith(".pdf"):

            resume_text = extract_text_from_pdf(
                resume.file
            )

        else:

            resume_text = extract_text_from_docx(
                resume.file
            )

        # ---------------------------
        # Validate Extracted Text
        # ---------------------------

        if not resume_text or not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from the "
                    "uploaded resume."
                )
            )

        resume_text = resume_text.strip()

        # ---------------------------
        # Validate Resume Text Size
        # ---------------------------

        if len(resume_text) > MAX_RESUME_TEXT_LENGTH:

            raise HTTPException(
                status_code=400,
                detail=(
                    "The extracted resume content is too large "
                    "to analyze. Please upload a shorter resume."
                )
            )

        # ---------------------------
        # AI Resume Analysis
        # ---------------------------

        logger.info(
            "Starting resume analysis: filename=%s, role=%s, size=%d bytes",
            filename,
            job_role,
            total_size
        )

        review = review_resume(
            resume_text,
            job_role
        )

        logger.info(
            "Resume analysis completed successfully: filename=%s",
            filename
        )

        return review

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error while analyzing resume: %s",
            filename
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to analyze the resume right now. "
                "Please try again later."
            )
        )


# ===========================
# PDF Helper
# ===========================

def pdf_text(text):
    """
    Convert text to characters supported by
    the default FPDF Helvetica font.
    """

    if text is None:
        return ""

    safe = str(text)

    replacements = {
        "•": "-",
        "🟢": "",
        "🟡": "",
        "🔴": "",
        "✅": "",
        "⚠️": "",
        "🚀": "",
        "📝": "",
        "🎯": "",
        "💡": "",
        "📄": "",
    }

    for old, new in replacements.items():
        safe = safe.replace(old, new)

    return (
        safe
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


# ===========================
# PDF Report
# ===========================

def build_pdf_report(review, job_role, filename):

    pdf = FPDF(
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        size=12
    )

    page_width = (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )

    def write_heading(text):

        pdf.set_font(
            "Helvetica",
            style="B",
            size=12
        )

        pdf.set_x(pdf.l_margin)

        pdf.multi_cell(
            page_width,
            8,
            pdf_text(text)
        )

        pdf.set_font(
            "Helvetica",
            size=12
        )

    # ===========================
    # Header
    # ===========================

    write_heading(
        "AI Resume Review Report"
    )

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        page_width,
        6,
        pdf_text(
            f"Source file: {filename}"
        )
    )

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        page_width,
        6,
        pdf_text(
            f"Target role: {job_role}"
        )
    )

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        page_width,
        6,
        pdf_text(
            f"ATS Score: {review['resume_score']}/100"
        )
    )

    pdf.ln(4)

    # ===========================
    # Strengths
    # ===========================

    write_heading("Strengths")

    for item in review["strengths"]:

        pdf.set_x(pdf.l_margin)

        pdf.multi_cell(
            page_width,
            6,
            pdf_text(f"- {item}")
        )

    pdf.ln(2)

    # ===========================
    # Opportunities
    # ===========================

    write_heading("Opportunities")

    for item in review["weaknesses"]:

        pdf.set_x(pdf.l_margin)

        pdf.multi_cell(
            page_width,
            6,
            pdf_text(f"- {item}")
        )

    pdf.ln(2)

    # ===========================
    # Recommended Skills
    # ===========================

    write_heading("Recommended Skills")

    for item in review["missing_skills"]:

        pdf.set_x(pdf.l_margin)

        pdf.multi_cell(
            page_width,
            6,
            pdf_text(f"- {item}")
        )

    pdf.ln(2)

    # ===========================
    # Improvement Plan
    # ===========================

    write_heading("Improvement Plan")

    for index, item in enumerate(
        review["improvement_suggestions"],
        start=1
    ):

        pdf.set_x(pdf.l_margin)

        pdf.multi_cell(
            page_width,
            6,
            pdf_text(
                f"{index}. {item}"
            )
        )

    pdf.ln(2)

    # ===========================
    # Executive Summary
    # ===========================

    write_heading(
        "Executive Summary"
    )

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        page_width,
        6,
        pdf_text(
            review["professional_summary"]
        )
    )

    pdf.ln(2)

    # ===========================
    # Final Verdict
    # ===========================

    write_heading(
        "Final Verdict"
    )

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        page_width,
        6,
        pdf_text(
            review["final_verdict"]
        )
    )

    # ===========================
    # Return PDF bytes
    # ===========================

    pdf_output = pdf.output()

    return bytes(pdf_output)


# ===========================
# PDF Download Endpoint
# ===========================

@app.post("/report")
async def generate_report(
    job_role: str = Form(...),
    filename: str = Form(...),
    review: str = Form(...)
):

    try:

        # ---------------------------
        # Validate Job Role
        # ---------------------------

        job_role = job_role.strip()

        if not job_role:
            raise HTTPException(
                status_code=400,
                detail="Job role cannot be empty."
            )

        if len(job_role) > MAX_JOB_ROLE_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Job role must be {MAX_JOB_ROLE_LENGTH} "
                    "characters or fewer."
                )
            )

        # ---------------------------
        # Validate Filename
        # ---------------------------

        if not filename.strip():
            raise HTTPException(
                status_code=400,
                detail="Filename cannot be empty."
            )

        safe_filename = Path(filename).name

        if not safe_filename.lower().endswith(
            (".pdf", ".docx")
        ):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX filenames are supported."
            )

        # ---------------------------
        # Validate Review Payload Size
        # ---------------------------

        if len(review) > MAX_REVIEW_PAYLOAD_LENGTH:
            raise HTTPException(
                status_code=400,
                detail="Review data is too large."
            )

        # ---------------------------
        # Parse Review JSON
        # ---------------------------

        try:

            review_data = json.loads(review)

        except json.JSONDecodeError:

            raise HTTPException(
                status_code=400,
                detail="Invalid review data."
            )

        # ---------------------------
        # Validate Review Data
        # ---------------------------

        review_data = validate_review_response(
            review_data
        )

        # ---------------------------
        # Generate PDF
        # ---------------------------

        pdf_bytes = build_pdf_report(
            review_data,
            job_role,
            safe_filename
        )

        logger.info(
            "PDF report generated successfully: filename=%s",
            safe_filename
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=resume_review.pdf"
            }
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error while generating PDF report."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate the PDF report right now. "
                "Please try again later."
            )
        )