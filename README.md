# AI Resume Reviewer

An AI-powered resume analysis application that evaluates resumes against a target job role and provides ATS-focused feedback, skill-gap analysis, and improvement recommendations.

## 🚀 Live Demo

👉 https://ai-resume-reviewer-sreehari-vs.vercel.app

## ✨ Features

- Upload resumes in PDF or DOCX format
- Enter a target job role
- AI-powered ATS compatibility score
- Resume strengths and weaknesses
- Missing skills identification
- Personalized improvement suggestions
- Professional summary
- Final assessment
- Download analysis as a PDF report

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI & Processing
- Groq API
- GPT-OSS
- PDFPlumber
- python-docx
- FPDF2

## 📁 Project Structure

```text
AI-Resume-Reviewer/
│
├── backend/
│   ├── main.py
│   ├── ai.py
│   ├── utils.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md

```


## How It Works

```text
Resume + Target Role
        ↓
React Frontend
        ↓
FastAPI Backend
        ↓
Resume Text Extraction
        ↓
GPT-OSS 120B
        ↓
Structured AI Review
        ↓
ATS Score + Recommendations
        ↓
PDF Report
```

## Developer

**Sreehari V S**

LinkedIn: [https://www.linkedin.com/in/sreehari--vs](https://www.linkedin.com/in/sreehari--vs)

GitHub: [https://github.com/Sreeharivs1983](https://github.com/Sreeharivs1983)

## License

This project is developed for educational and portfolio purposes.
