# AI Resume Reviewer

AI Resume Reviewer is a simple Streamlit application that analyzes uploaded resumes and provides ATS-friendly feedback for a target job role using an LLM.

## Features

- Upload resume files in `PDF` or `DOCX` format
- Enter a target job role for personalized review
- Receive:
  - ATS score
  - Resume strengths
  - Resume weaknesses
  - Missing technical skills
  - Improvement suggestions
  - Professional summary
  - Final verdict
  - Download the review as a PDF file

## Requirements

- Python 3.10+
- `streamlit`
- `pdfplumber`
- `python-docx`
- `fpdf2`
- `groq`
- `python-dotenv`

## Setup

1. Clone the repository or open the project folder.
2. Create and activate a Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your GROQ API key:

```env
GROQ_API_KEY=your_api_key_here
```

## Running the app

Start the Streamlit app from the project directory:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## Live Demo

- https://ai-resume-reviewer-sreeharivs.streamlit.app/

## Usage

1. Upload a resume file in PDF or DOCX format.
2. Enter the target job role (for example: `Python Developer`).
3. Click **Analyze Resume**.
4. Review the results provided by the app.
5. Download the completed review as a PDF file.

## File Support

- `PDF`
- `DOCX`

## Notes

- The app relies on the Groq `llama-3.3-70b-versatile` model to generate resume review output.
- The AI response is expected to be valid JSON in a specific structure.
- If the app fails, verify that `GROQ_API_KEY` is set and that all dependencies are installed.

## Project Files

- `app.py` - Streamlit UI and application workflow
- `ai.py` - AI prompt logic and Groq API call
- `utils.py` - Resume text extraction utilities
- `README.md` - Project documentation
- `requirements.txt` - Python dependency list
