import streamlit as st
from fpdf import FPDF
from utils import extract_text_from_pdf, extract_text_from_docx
from ai import review_resume

# Page configuration
st.set_page_config(
    page_title="AI Resume Reviewer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_score_status(score):
    if score >= 85:
        return (
            "🟢 Excellent",
            "The resume is highly aligned with the target role and demonstrates strong ATS compatibility.",
        )
    if score >= 70:
        return (
            "🟡 Good",
            "The resume is competitive but would benefit from targeted keyword and formatting improvements.",
        )
    return (
            "🔴 Needs Improvement",
            "The resume requires substantive revisions to improve keyword relevance and readability for ATS screening.",
    )


def build_download_report(review, job_role, filename):
    lines = [
        f"Resume Review Report\n",
        f"File: {filename}\n",
        f"Target Job Role: {job_role}\n",
        "\n",
        f"ATS Score: {review['resume_score']}/100\n",
        f"Recommendation: {get_score_status(review['resume_score'])[0]}\n",
        "\n",
        "Strengths:\n"
    ]

    for item in review['strengths']:
        lines.append(f"- {item}\n")

    lines.append("\nWeaknesses:\n")
    for item in review['weaknesses']:
        lines.append(f"- {item}\n")

    lines.append("\nMissing Technical Skills:\n")
    for item in review['missing_skills']:
        lines.append(f"- {item}\n")

    lines.append("\nImprovement Suggestions:\n")
    for item in review['improvement_suggestions']:
        lines.append(f"- {item}\n")

    lines.append("\nProfessional Summary:\n")
    lines.append(f"{review['professional_summary']}\n")

    lines.append("\nFinal Verdict:\n")
    lines.append(f"{review['final_verdict']}\n")

    return "".join(lines)


def build_pdf_report(review, job_role, filename):
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    def pdf_text(text):
        if text is None:
            return ""
        safe = str(text)
        safe = safe.replace("•", "-")
        safe = safe.replace("🟢", "").replace("🟡", "").replace("🔴", "")
        safe = safe.replace("✅", "").replace("⚠️", "").replace("🚀", "")
        safe = safe.replace("📝", "").replace("🎯", "")
        return safe.encode("latin-1", "replace").decode("latin-1")

    def write_heading(text):
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(page_width, 8, pdf_text(text))
        pdf.set_font("Helvetica", size=12)

    write_heading("Resume Review Report")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(f"Source file: {filename}"), align="L")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(f"Target role: {job_role}"), align="L")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(f"ATS Score: {review['resume_score']}/100"), align="L")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(f"Recommendation: {get_score_status(review['resume_score'])[0]}"), align="L")
    pdf.ln(4)

    write_heading("Strengths")
    for item in review['strengths']:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(page_width, 6, pdf_text(f"- {item}"), align="L")
    pdf.ln(2)

    write_heading("Opportunities")
    for item in review['weaknesses']:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(page_width, 6, pdf_text(f"- {item}"), align="L")
    pdf.ln(2)

    write_heading("Recommended Skills")
    for item in review['missing_skills']:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(page_width, 6, pdf_text(f"- {item}"), align="L")
    pdf.ln(2)

    write_heading("Improvement Plan")
    for idx, item in enumerate(review['improvement_suggestions'], start=1):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(page_width, 6, pdf_text(f"{idx}. {item}"), align="L")
    pdf.ln(2)

    write_heading("Executive Summary")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(review['professional_summary']), align="L")
    pdf.ln(2)

    write_heading("Final Verdict")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(page_width, 6, pdf_text(review['final_verdict']), align="L")

    pdf_output = pdf.output(dest="S")
    return bytes(pdf_output)
# ===========================
# Sidebar
# ===========================
with st.sidebar:

    st.title("📄 AI Resume Reviewer")

    st.markdown("---")

    st.subheader("📂 Supported Files")
    st.write("✅ PDF")
    st.write("✅ DOCX")

    st.markdown("---")

    st.subheader("📖 How to Use")

    st.markdown("""
1. Upload your resume.
2. Enter the target job role.
3. Click **🚀 Analyze Resume**.
4. Review the AI suggestions.
""")

    st.markdown("---")

    st.subheader("ℹ️ Tips")

    st.info("""
• Upload a clear and updated resume.

• Enter the exact job role.

• Use an ATS-friendly resume for better feedback.
""")

    st.markdown("---")

    st.caption("Version 1.0")

# ===========================
# Main Page
# ===========================

st.title("📄 AI Resume Reviewer")

st.caption(
    "Get AI-powered resume analysis, ATS suggestions, and skill recommendations."
)

st.divider()

with st.form("resume_review_form"):
    st.subheader("📂 Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF or DOCX)",
        type=["pdf", "docx"]
    )

    st.subheader("🎯 Target Job Role")
    job_role = st.text_input(
        "Enter the Target Job Role",
        placeholder="Example: Python Developer"
    )

    submitted = st.form_submit_button("🚀 Analyze Resume")

if submitted:

    # Validation
    if uploaded_file is None:
        st.warning("📂 Please upload your resume.")
        st.stop()

    if not job_role.strip():
        st.warning("🎯 Please enter the target job role.")
        st.stop()

    # Extract Resume Text
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)

    elif filename.endswith(".docx"):
        resume_text = extract_text_from_docx(uploaded_file)

    else:
        st.error("Unsupported file format.")
        st.stop()

    # AI Analysis
    with st.spinner("🤖 Analyzing your resume..."):

        try:
            review = review_resume(
                resume_text,
                job_role
            )

        except Exception as exc:
            st.error(f"Unable to review resume:\n\n{exc}")
            st.stop()

    st.success("✅ Analysis Complete!")

    # ===========================
    # Review Summary
    # ===========================

    score = review["resume_score"]
    status_label, status_summary = get_score_status(score)

    st.subheader("📊 ATS Review")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(label="Score", value=f"{score}/100")
        st.markdown(f"**Status:** {status_label}")

    with col2:
        st.info(status_summary)

    st.divider()

    # ===========================
    # Strengths / Opportunities
    # ===========================

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Strengths")
        st.markdown("\n".join([f"- {item}" for item in review["strengths"]]))

    with col2:
        st.subheader("⚠️ Opportunities")
        st.markdown("\n".join([f"- {item}" for item in review["weaknesses"]]))

    st.divider()

    # ===========================
    # Skills / Plan
    # ===========================

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💡 Recommended Skills")
        st.markdown("\n".join([f"- {item}" for item in review["missing_skills"]]))

    with col2:
        st.subheader("🚀 Improvement Plan")
        st.markdown("\n".join([f"{idx}. {item}" for idx, item in enumerate(review["improvement_suggestions"], start=1)]))

    st.divider()

    # ===========================
    # Executive Summary
    # ===========================

    st.subheader("📝 Executive Summary")
    st.write(review["professional_summary"])

    st.divider()

    # ===========================
    # Final Verdict
    # ===========================

    st.subheader("🎯 Final Verdict")
    st.info(review["final_verdict"])

    st.divider()

    # ===========================
    # Download Report
    # ===========================

    report_pdf = build_pdf_report(review, job_role, uploaded_file.name)

    st.download_button(
        label="📥 Download Review (PDF)",
        data=report_pdf,
        file_name="resume_review.pdf",
        mime="application/pdf"
    )
