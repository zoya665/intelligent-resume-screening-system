"""
Pydantic API Schemas for Requests and Responses.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobDescriptionRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Senior Data Scientist / AI Engineer"})
    description: str = Field(..., json_schema_extra={"example": "Looking for a Python AI engineer with experience in Machine Learning, NLP, Scikit-learn, and FastAPI."})
    required_skills: Optional[List[str]] = Field(default=[], json_schema_extra={"example": ["python", "scikit-learn", "nlp", "fastapi"]})
    required_experience: Optional[float] = Field(default=3.0, json_schema_extra={"example": 3.0})


class SingleScreeningRequest(BaseModel):
    resume_text: str
    job_description: JobDescriptionRequest


class CandidateScoreBreakdown(BaseModel):
    tfidf_similarity: float
    skill_match_percentage: float
    experience_score: float
    education_score: float


class CandidateInfo(BaseModel):
    experience_years: float
    education: List[str]
    categorized_skills: Dict[str, List[str]]
    total_skills_count: int


class SkillGapAnalysis(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    skill_match_percentage: float


class CandidateEvaluationResult(BaseModel):
    rank: Optional[int] = None
    resume_id: str
    candidate_name: str
    email: str
    phone: str
    links: Dict[str, str]
    job_title: str
    composite_score: float
    fit_category: str
    badge_color: str
    score_breakdown: CandidateScoreBreakdown
    candidate_info: CandidateInfo
    skill_gap_analysis: SkillGapAnalysis
    ai_insights: List[str]


class ScreeningResponse(BaseModel):
    job_title: str
    total_candidates_screened: int
    ranked_candidates: List[CandidateEvaluationResult]
