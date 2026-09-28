"""
FastAPI Application Entry Point for Intelligent Resume Screening System.
"""
import json
import os
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from app.core.config import SKILL_TAXONOMY
from app.models.schemas import (
    CandidateEvaluationResult,
    JobDescriptionRequest,
    ScreeningResponse,
    SingleScreeningRequest
)
from app.nlp.extractor import EntityExtractor
from app.nlp.matcher import ResumeMatcher
from app.utils.file_parser import FileParser
from app.utils.report_generator import ReportGenerator

app = FastAPI(
    title="Intelligent Resume Screening System – AI/ML & NLP",
    description="Automated AI Resume Analyzer, Skill Gap Detector, and Candidate Matcher built with Python, Scikit-learn, NLP, and FastAPI.",
    version="1.0.0"
)

# Mount static files for dashboard frontend UI
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

matcher = ResumeMatcher()


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the web dashboard UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Intelligent Resume Screening System API is running.</h1><p>Visit /docs for API Swagger documentation.</p>"


@app.get("/api/health")
async def health_check():
    return {"status": "online", "system": "Intelligent Resume Screening AI Engine"}


@app.get("/api/skill-taxonomy")
async def get_skill_taxonomy():
    """Returns master skill taxonomy by category."""
    return SKILL_TAXONOMY


@app.get("/api/sample-data")
async def get_sample_data():
    """Returns sample resumes and job descriptions for quick dashboard testing."""
    samples_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    resumes_dir = os.path.join(samples_dir, "sample_resumes")
    jds_dir = os.path.join(samples_dir, "sample_job_descriptions")

    resumes = []
    if os.path.exists(resumes_dir):
        for f in os.listdir(resumes_dir):
            if f.endswith('.txt'):
                file_path = os.path.join(resumes_dir, f)
                with open(file_path, "r", encoding="utf-8") as fp:
                    resumes.append({
                        "filename": f,
                        "title": f.replace('resume_', '').replace('.txt', '').replace('_', ' ').title(),
                        "content": fp.read()
                    })

    job_descriptions = []
    if os.path.exists(jds_dir):
        for f in os.listdir(jds_dir):
            if f.endswith('.json'):
                file_path = os.path.join(jds_dir, f)
                with open(file_path, "r", encoding="utf-8") as fp:
                    job_descriptions.append(json.load(fp))

    return {
        "sample_resumes": resumes,
        "sample_job_descriptions": job_descriptions
    }


@app.post("/api/screen-single", response_model=CandidateEvaluationResult)
async def screen_single_resume(payload: SingleScreeningRequest):
    """Screens a single resume text against a Job Description."""
    try:
        eval_result = matcher.evaluate_candidate(
            resume_id="single_eval",
            resume_text=payload.resume_text,
            job_title=payload.job_description.title,
            jd_text=payload.job_description.description,
            required_skills=payload.job_description.required_skills,
            required_experience=payload.job_description.required_experience or 0.0
        )
        eval_result["rank"] = 1
        return eval_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening error: {str(e)}")


@app.post("/api/screen-bulk", response_model=ScreeningResponse)
async def screen_bulk_resumes(
    job_title: str = Form(...),
    job_description: str = Form(...),
    required_skills: Optional[str] = Form(None),  # Comma separated skills
    required_experience: Optional[float] = Form(0.0),
    resumes: List[UploadFile] = File(...)
):
    """
    Accepts multiple uploaded resume files (.pdf, .txt, .docx), screens each against
    the job description, and returns a ranked list of evaluated candidates.
    """
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume files uploaded.")

    parsed_required_skills = []
    if required_skills:
        parsed_required_skills = [s.strip().lower() for s in required_skills.split(',') if s.strip()]

    evaluations = []
    for idx, file in enumerate(resumes):
        try:
            content_bytes = await file.read()
            text = FileParser.parse_file(file.filename, content_bytes)
            if not text:
                continue

            eval_res = matcher.evaluate_candidate(
                resume_id=f"res_{idx}_{file.filename}",
                resume_text=text,
                job_title=job_title,
                jd_text=job_description,
                required_skills=parsed_required_skills,
                required_experience=required_experience or 0.0
            )
            evaluations.append(eval_res)
        except Exception as e:
            print(f"Error parsing file {file.filename}: {e}")

    ranked = matcher.rank_candidates(evaluations)

    return {
        "job_title": job_title,
        "total_candidates_screened": len(ranked),
        "ranked_candidates": ranked
    }


@app.post("/api/parse-resume")
async def parse_resume_file(file: UploadFile = File(...)):
    """Extracts raw entities, contact information, skills, and experience from a resume file."""
    try:
        content_bytes = await file.read()
        text = FileParser.parse_file(file.filename, content_bytes)
        
        email = EntityExtractor.extract_email(text)
        phone = EntityExtractor.extract_phone(text)
        links = EntityExtractor.extract_links(text)
        name = EntityExtractor.extract_candidate_name(text)
        skills = EntityExtractor.extract_skills(text)
        experience = EntityExtractor.estimate_experience_years(text)
        education = EntityExtractor.extract_education(text)

        return {
            "filename": file.filename,
            "candidate_name": name,
            "email": email,
            "phone": phone,
            "links": links,
            "experience_years": experience,
            "education": education,
            "skills": skills,
            "raw_text_preview": text[:500] + "..." if len(text) > 500 else text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@app.post("/api/export-csv")
async def export_csv(payload: List[dict]):
    """Generates a downloadable CSV report from screening results."""
    try:
        csv_data = ReportGenerator.generate_csv_report(payload)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=candidate_screening_report.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Export error: {str(e)}")
