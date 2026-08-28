# AI Resume Reviewer

AI Resume Reviewer is a full-stack Generative AI application that analyzes resumes against a target job role and provides ATS-focused feedback.

## Features

- Upload PDF or DOCX resumes
- Enter a target job role
- AI-powered ATS score
- Resume strengths and weaknesses
- Missing skill recommendations
- Improvement suggestions
- Professional summary and final verdict
- Downloadable PDF report
- Responsive React UI

## Tech Stack

- React + Vite
- FastAPI
- Python
- GPT-OSS 120B
- FPDF2
- PDF/DOCX text extraction
- REST API

## Project Structure

```text
AI-Resume-Reviewer/
├── backend/
│   ├── ai.py
│   ├── main.py
│   ├── utils.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── tests/
├── .gitignore
└── README.md