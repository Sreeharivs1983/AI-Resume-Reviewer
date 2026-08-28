import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [resume, setResume] = useState(null);
  const [jobRole, setJobRole] = useState("");
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);

  const analysisSteps = [
    "Reading resume content",
    "Evaluating ATS compatibility",
    "Comparing skills with target role",
    "Preparing recommendations",
  ];

  useEffect(() => {
    if (!loading) {
      setLoadingStep(0);
      return;
    }

    const interval = setInterval(() => {
      setLoadingStep((current) => {
        if (current < analysisSteps.length - 1) {
          return current + 1;
        }

        return current;
      });
    }, 1400);

    return () => clearInterval(interval);
  }, [loading, analysisSteps.length]);

  const analyzeResume = async () => {
    if (!resume) {
      setError("Please upload your resume.");
      return;
    }

    if (!jobRole.trim()) {
      setError("Please enter the target job role.");
      return;
    }

    setLoading(true);
    setLoadingStep(0);
    setError("");
    setReview(null);

    const formData = new FormData();

    formData.append("resume", resume);
    formData.append("job_role", jobRole);

    try {
      const response = await fetch(
  `${API_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to analyze resume."
        );
      }

      setLoadingStep(analysisSteps.length - 1);
      setReview(data);
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong while analyzing the resume."
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!review || !resume) {
      return;
    }

    setDownloading(true);
    setError("");

    const formData = new FormData();

    formData.append("job_role", jobRole);
    formData.append("filename", resume.name);
    formData.append(
      "review",
      JSON.stringify(review)
    );

    try {
      const response = await fetch(
  `${API_URL}/report`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        let message = "Failed to generate PDF report.";

        try {
          const data = await response.json();
          message = data.detail || message;
        } catch {
          // Keep default message when response is not JSON.
        }

        throw new Error(message);
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;
      link.download = "resume_review.pdf";

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err.message || "Failed to generate PDF report."
      );
    } finally {
      setDownloading(false);
    }
  };

  const handleResumeChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setResume(selectedFile);
    setError("");
    setReview(null);
  };

  const removeResume = () => {
    setResume(null);
    setReview(null);
    setError("");
  };

  const handleRoleExample = (role) => {
    setJobRole(role);
    setError("");
  };

  const getScoreStatus = (score) => {
    if (score >= 85) {
      return {
        label: "Excellent",
        className: "excellent",
      };
    }

    if (score >= 70) {
      return {
        label: "Good",
        className: "good",
      };
    }

    return {
      label: "Needs Improvement",
      className: "needs-improvement",
    };
  };

  const getScoreDescription = (score) => {
    if (score >= 85) {
      return "Your resume is strongly aligned with the target role.";
    }

    if (score >= 70) {
      return "Your resume has a solid foundation with room for improvement.";
    }

    return "Your resume could benefit from targeted improvements for this role.";
  };

  const getScoreDashArray = (score) => {
    const circumference = 2 * Math.PI * 52;

    return `${(score / 100) * circumference} ${circumference}`;
  };

  const scoreStatus = review
    ? getScoreStatus(review.resume_score)
    : null;

  return (
    <div className="app">

      {/* ===========================
          Navbar
      =========================== */}

      <header className="navbar">
        <div className="nav-inner">

          <div className="brand">

            <div className="brand-icon">
              ✦
            </div>

            <div>
              <div className="brand-name">
                AI Resume Reviewer
              </div>

              <div className="brand-tagline">
                Intelligent Resume Analysis
              </div>
            </div>

          </div>

          <div className="nav-badge">
            AI-Powered ATS Review
          </div>

        </div>
      </header>


      <main>

        {/* ===========================
            Hero
        =========================== */}

        <section className="hero">

          <div className="hero-badge">
            <span className="status-dot"></span>
            AI-powered resume intelligence
          </div>

          <h1>
            Make your resume
            <span>get noticed.</span>
          </h1>

          <p className="hero-description">
            Get a professional AI-powered review of your resume,
            tailored to the job you want. Discover strengths,
            skill gaps, ATS opportunities, and practical ways
            to improve your chances.
          </p>

          <div className="hero-points">

            <div>
              <span>✓</span>
              ATS-focused analysis
            </div>

            <div>
              <span>✓</span>
              Role-specific insights
            </div>

            <div>
              <span>✓</span>
              Actionable recommendations
            </div>

          </div>

        </section>


        {/* ===========================
            Workspace
        =========================== */}

        {!loading && !review && (
          <section className="workspace">

            <div className="workspace-header">

              <div>

                <span className="section-number">
                  01
                </span>

                <div>
                  <h2>
                    Start your review
                  </h2>

                  <p>
                    Upload your resume and tell us what role you're targeting.
                  </p>
                </div>

              </div>

            </div>


            <div className="input-grid">

              {/* Resume Upload */}

              <div className="input-card">

                <div className="input-card-header">

                  <div className="input-icon">
                    ↑
                  </div>

                  <div>
                    <h3>
                      Resume
                    </h3>

                    <p>
                      PDF or DOCX · Max 10 MB
                    </p>
                  </div>

                </div>


                {!resume ? (

                  <label className="drop-zone">

                    <input
                      type="file"
                      accept=".pdf,.docx"
                      onChange={handleResumeChange}
                    />

                    <div className="upload-symbol">
                      ↑
                    </div>

                    <strong>
                      Click to upload your resume
                    </strong>

                    <span>
                      PDF or DOCX files supported
                    </span>

                  </label>

                ) : (

                  <div className="selected-file">

                    <div className="file-symbol">
                      {resume.name
                        .toLowerCase()
                        .endsWith(".pdf")
                        ? "PDF"
                        : "DOCX"}
                    </div>

                    <div className="file-details">

                      <strong title={resume.name}>
                        {resume.name}
                      </strong>

                      <span>
                        {(resume.size / 1024 / 1024).toFixed(2)} MB
                      </span>

                    </div>

                    <button
                      type="button"
                      className="remove-file"
                      onClick={removeResume}
                      aria-label="Remove resume"
                    >
                      ×
                    </button>

                  </div>

                )}

              </div>


              {/* Job Role */}

              <div className="input-card">

                <div className="input-card-header">

                  <div className="input-icon">
                    ◎
                  </div>

                  <div>
                    <h3>
                      Target role
                    </h3>

                    <p>
                      Tell the AI what position you're applying for
                    </p>
                  </div>

                </div>


                <div className="role-input-wrapper">

                  <span className="input-hint">
                    Target job role
                  </span>

                  <input
                    type="text"
                    value={jobRole}
                    onChange={(event) => {
                      setJobRole(event.target.value);
                      setError("");
                    }}
                    placeholder="e.g. Generative AI Developer"
                  />

                </div>


                <div className="role-examples">

                  <span>
                    Try:
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      handleRoleExample("Python Developer")
                    }
                  >
                    Python Developer
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleRoleExample("React Developer")
                    }
                  >
                    React Developer
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleRoleExample("Generative AI Developer")
                    }
                  >
                    Generative AI
                  </button>

                </div>

              </div>

            </div>


            {/* Error */}

            {error && (

              <div className="error-message">

                <span>
                  !
                </span>

                <p>
                  {error}
                </p>

              </div>

            )}


            {/* Analyze */}

            <button
              className="analyze-button"
              onClick={analyzeResume}
              disabled={loading}
            >

              <span>
                Analyze my resume
              </span>

              <span className="button-arrow">
                →
              </span>

            </button>


            <div className="privacy-note">

              <span>
                🔒
              </span>

              Your resume is processed securely for this analysis.

            </div>

          </section>
        )}


        {/* ===========================
            Loading State
        =========================== */}

        {loading && (

          <section className="analysis-loading">

            <div className="loading-container">

              <div className="loading-orbit">

                <div></div>

              </div>


              <div className="loading-badge">
                AI ANALYSIS IN PROGRESS
              </div>


              <h2>
                Analyzing your resume
              </h2>

              <p>
                Our AI is evaluating your resume against the target role.
              </p>


              <div className="loading-progress">

                <div
                  className="loading-progress-bar"
                  style={{
                    width: `${Math.max(
                      15,
                      ((loadingStep + 1) /
                        analysisSteps.length) *
                        100
                    )}%`,
                  }}
                ></div>

              </div>


              <div className="loading-step-list">

                {analysisSteps.map(
                  (step, index) => {

                    const isComplete =
                      index < loadingStep;

                    const isActive =
                      index === loadingStep;

                    return (
                      <div
                        key={step}
                        className={`loading-step ${
                          isComplete
                            ? "complete"
                            : ""
                        } ${
                          isActive
                            ? "active"
                            : ""
                        }`}
                      >

                        <span className="loading-step-icon">

                          {isComplete
                            ? "✓"
                            : isActive
                            ? ""
                            : index + 1}

                        </span>

                        <span>
                          {step}
                        </span>

                        {isActive && (
                          <span className="step-pulse">
                            ...
                          </span>
                        )}

                      </div>
                    );
                  }
                )}

              </div>

            </div>

          </section>
        )}


        {/* ===========================
            Results
        =========================== */}

        {review && !loading && (

          <section className="results">

            <div className="results-heading">

              <div>

                <span className="section-number">
                  02
                </span>

                <div>

                  <h2>
                    Resume review
                  </h2>

                  <p>
                    AI-generated insights for your target role.
                  </p>

                </div>

              </div>


              <div className="review-complete">
                ✓ Review complete
              </div>

            </div>


            {/* ===========================
                ATS Score
            =========================== */}

            <div
              className={`score-panel ${scoreStatus.className}`}
            >

              <div className="score-circle">

                <svg
                  className="score-ring"
                  viewBox="0 0 120 120"
                  aria-label={`ATS score ${review.resume_score} out of 100`}
                >

                  <circle
                    className="score-track"
                    cx="60"
                    cy="60"
                    r="52"
                  />

                  <circle
                    className="score-progress"
                    cx="60"
                    cy="60"
                    r="52"
                    strokeDasharray={getScoreDashArray(
                      review.resume_score
                    )}
                  />

                </svg>

                <div className="score-value">

                  <strong>
                    {review.resume_score}
                  </strong>

                  <span>
                    / 100
                  </span>

                </div>

              </div>


              <div className="score-content">

                <span className="score-label">
                  ATS compatibility score
                </span>

                <h3 className={scoreStatus.className}>
                  {scoreStatus.label}
                </h3>

                <p>
                  {getScoreDescription(
                    review.resume_score
                  )}
                </p>

              </div>


              <div className="score-meta">

                <div className="score-meta-item">

                  <span>
                    TARGET ROLE
                  </span>

                  <strong title={jobRole}>
                    {jobRole}
                  </strong>

                </div>


                <div className="score-meta-item">

                  <span>
                    RESUME
                  </span>

                  <strong title={resume?.name}>
                    {resume?.name}
                  </strong>

                </div>

              </div>

            </div>


            {/* Result Cards */}

            <div className="result-grid">

              {/* Strengths */}

              <div className="result-card strengths-card">

                <div className="result-card-heading">

                  <div className="result-icon">
                    ✓
                  </div>

                  <div>

                    <span>
                      What works well
                    </span>

                    <h3>
                      Strengths
                    </h3>

                  </div>

                </div>


                <ul>

                  {review.strengths.map(
                    (item, index) => (
                      <li key={index}>

                        <span>
                          ✓
                        </span>

                        <div>
                          {item}
                        </div>

                      </li>
                    )
                  )}

                </ul>

              </div>


              {/* Opportunities */}

              <div className="result-card opportunities-card">

                <div className="result-card-heading">

                  <div className="result-icon">
                    !
                  </div>

                  <div>

                    <span>
                      Areas to improve
                    </span>

                    <h3>
                      Opportunities
                    </h3>

                  </div>

                </div>


                <ul>

                  {review.weaknesses.map(
                    (item, index) => (
                      <li key={index}>

                        <span>
                          !
                        </span>

                        <div>
                          {item}
                        </div>

                      </li>
                    )
                  )}

                </ul>

              </div>


              {/* Skills */}

              <div className="result-card skills-card">

                <div className="result-card-heading">

                  <div className="result-icon">
                    +
                  </div>

                  <div>

                    <span>
                      Close your skill gaps
                    </span>

                    <h3>
                      Recommended Skills
                    </h3>

                  </div>

                </div>


                <ul>

                  {review.missing_skills.map(
                    (item, index) => (
                      <li key={index}>

                        <span>
                          +
                        </span>

                        <div>
                          {item}
                        </div>

                      </li>
                    )
                  )}

                </ul>

              </div>


              {/* Improvement */}

              <div className="result-card improvement-card">

                <div className="result-card-heading">

                  <div className="result-icon">
                    →
                  </div>

                  <div>

                    <span>
                      Recommended next steps
                    </span>

                    <h3>
                      Improvement Plan
                    </h3>

                  </div>

                </div>


                <ol>

                  {review.improvement_suggestions.map(
                    (item, index) => (
                      <li key={index}>

                        <span>
                          {index + 1}
                        </span>

                        <div>
                          {item}
                        </div>

                      </li>
                    )
                  )}

                </ol>

              </div>

            </div>


            {/* Executive Summary */}

            <div className="summary-card">

              <div className="summary-label">

                <span>
                  AI
                </span>

                Executive Summary

              </div>


              <p>
                {review.professional_summary}
              </p>

            </div>


            {/* Verdict */}

            <div className="verdict-card">

              <div className="verdict-icon">
                ◎
              </div>

              <div>

                <span>
                  Final assessment
                </span>

                <h3>
                  Final Verdict
                </h3>

                <p>
                  {review.final_verdict}
                </p>

              </div>

            </div>


            {/* Download */}

            <div className="download-section">

              <div>

                <h3>
                  Take your review with you
                </h3>

                <p>
                  Download a professional PDF report of this analysis.
                </p>

              </div>


              <button
                className="download-button"
                onClick={downloadReport}
                disabled={downloading}
              >

                <span>
                  {downloading
                    ? "Generating..."
                    : "Download report"}
                </span>

                <span>
                  ↓
                </span>

              </button>

            </div>

          </section>
        )}

      </main>


      {/* ===========================
          Footer
      =========================== */}

      <footer className="footer">

        <div className="footer-inner">

          <div className="footer-brand">

            <span>
              ✦
            </span>

            AI Resume Reviewer

          </div>

          <p>
            Turn your resume into a stronger application.
          </p>

          <div className="footer-tech">
            React · FastAPI · GPT-OSS
          </div>

        </div>


        {/* Developer Credit */}

        <div className="footer-developer">

          <span>
            Developed by <strong>Sreehari V S</strong>
          </span>

          <span className="footer-links-separator">
            ·
          </span>

          <a
            href="https://www.linkedin.com/in/sreehari--vs"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Sreehari V S LinkedIn profile"
          >
            LinkedIn
          </a>

          <span className="footer-links-separator">
            ·
          </span>

          <a
            href="https://github.com/Sreeharivs1983"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Sreehari V S GitHub profile"
          >
            GitHub
          </a>

        </div>

      </footer>

    </div>
  );
}

export default App;