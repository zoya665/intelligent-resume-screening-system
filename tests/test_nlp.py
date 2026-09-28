"""
Unit tests for NLP preprocessing, feature extraction, and TF-IDF similarity matcher.
"""
import pytest
from app.nlp.preprocessor import TextPreprocessor
from app.nlp.extractor import EntityExtractor
from app.nlp.matcher import ResumeMatcher


def test_clean_text():
    raw_text = "John Doe • Python Dev!  Visit http://example.com or email test@example.com."
    cleaned = TextPreprocessor.clean_text(raw_text)
    assert "http" not in cleaned
    assert "Python Dev" in cleaned


def test_entity_extraction():
    sample_text = """
    John Doe
    Email: john.doe@ai.org | Phone: +1 555-019-2834
    LinkedIn: https://linkedin.com/in/johndoe-ai

    SUMMARY
    Senior AI / ML Engineer with 4 years of experience in Python, Scikit-learn, NLP, and FastAPI.
    Degree: Bachelor of Science in Computer Science.
    """
    email = EntityExtractor.extract_email(sample_text)
    phone = EntityExtractor.extract_phone(sample_text)
    links = EntityExtractor.extract_links(sample_text)
    skills = EntityExtractor.extract_skills(sample_text)
    exp = EntityExtractor.estimate_experience_years(sample_text)

    assert email == "john.doe@ai.org"
    assert "linkedin" in links["linkedin"]
    assert "python" in skills["flat_list"]
    assert "scikit-learn" in skills["flat_list"]
    assert exp == 4.0


def test_resume_matcher_similarity():
    matcher = ResumeMatcher()
    resume_text = "Python developer with machine learning, scikit-learn, pandas, numpy, and fastAPI experience."
    jd_text = "Looking for a Python AI engineer with machine learning, scikit-learn, and FastAPI skills."

    similarity = matcher.compute_tfidf_similarity(resume_text, jd_text)
    assert similarity > 20.0

    eval_result = matcher.evaluate_candidate(
        resume_id="test_1",
        resume_text=resume_text,
        job_title="AI Engineer",
        jd_text=jd_text,
        required_skills=["python", "scikit-learn", "fastapi"],
        required_experience=2.0
    )

    assert eval_result["composite_score"] > 50.0
    assert eval_result["fit_category"] in ["Strong Match", "Moderate Match", "Potential Match"]
