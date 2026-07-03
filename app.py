# app.py

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# -------- Import Project Modules --------
from modules.text_extractor import extract_text
from modules.skill_detector import detect_skills
from modules.job_matcher import match_score
from modules.ai_suggestions import generate_suggestions


# ----------------------------------------
# Initialize FastAPI
# ----------------------------------------
app = FastAPI(title="AI Resume Analyzer")

# Optional: allow browser-based requests during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------
# Add Middleware to Prevent Caching
# ----------------------------------------
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ----------------------------------------
# Templates & Static Files
# ----------------------------------------
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ----------------------------------------
# Upload Folder Setup
# ----------------------------------------
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def parse_job_description(job_description: str):
    """Parse the job description into a cleaned list of skills."""
    if not job_description:
        return []

    normalized = job_description.replace("\n", " ").replace("\r", " ")
    normalized = normalized.replace(";", ",")

    if "," in normalized:
        items = [item.strip() for item in normalized.split(",") if item.strip()]
    else:
        items = [item.strip() for item in normalized.split() if item.strip()]

    seen = set()
    parsed = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            parsed.append(item)

    return parsed


# ----------------------------------------
# Route 1: Home Page
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ----------------------------------------
# Route 2: Analyze Resume
# ----------------------------------------
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_cv(
    request: Request,
    cv_file: UploadFile = File(...),
    job_description: str = Form(...)
):

    # -------- File Validation --------
    allowed_extensions = [".pdf", ".docx"]
    file_ext = os.path.splitext(cv_file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return HTMLResponse("<h3>Only PDF or DOCX files are allowed.</h3>")


    # -------- Save Uploaded File --------
    file_location = os.path.join(UPLOAD_FOLDER, cv_file.filename)

    with open(file_location, "wb") as f:
        shutil.copyfileobj(cv_file.file, f)


    # -------- Extract Resume Text --------
    try:
        text = extract_text(file_location)

    except Exception as e:
        return HTMLResponse(f"<h2>Error extracting text: {str(e)}</h2>")


    # -------- Detect Skills from Resume --------
    skills = detect_skills(text)

    # Store original resume text for suggestions
    resume_text = text

    # -------- Process Job Description --------
    job_skills = parse_job_description(job_description)

    # -------- Calculate Match Score --------
    score, matched_skills, missing_skills, breakdown = match_score(skills, job_skills)


    # -------- Generate AI Suggestions --------
    suggestions = generate_suggestions(resume_text, missing_skills)


    # -------- Return Result Page --------
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "skills": skills,
            "score": score,
            "missing_skills": missing_skills,
            "matched_skills": matched_skills,
            "breakdown": breakdown,
            "suggestions": suggestions,
            "filename": cv_file.filename,
            "job_description": job_description
        }
    )


# ----------------------------------------
# Health Check API
# ----------------------------------------
@app.get("/health")
def health_check():
    return {"status": "AI Resume Analyzer is running"}