"""
AI/ML Similarity Matching and Candidate Ranking Engine.
Uses TF-IDF Vectorization, Cosine Similarity, Skill Gap Analysis, and Multi-factor Scoring.
"""
from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import DEFAULT_WEIGHTS
from app.nlp.extractor import EntityExtractor
from app.nlp.preprocessor import TextPreprocessor


class ResumeMatcher:
    """Intelligent Screening Engine matching resumes against Job Descriptions."""

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def compute_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Computes TF-IDF vector cosine similarity between clean resume text and job description text.
        Uses unigrams, bigrams, and trigrams to capture phrase semantics.
        """
        clean_resume = TextPreprocessor.clean_text(resume_text)
        clean_jd = TextPreprocessor.clean_text(jd_text)

        if not clean_resume or not clean_jd:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                sublinear_tf=True,
                stop_words='english'
            )
            tfidf_matrix = vectorizer.fit_transform([clean_jd, clean_resume])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.round(similarity * 100, 2))
        except Exception:
            return 0.0

    def analyze_skills_gap(
        self, candidate_skills: List[str], jd_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Analyzes skill alignment between candidate skills and job description required skills.
        Identifies matched skills, missing essential skills, and extra candidate skills.
        """
        cand_set = {s.lower() for s in candidate_skills}
        jd_set = {s.lower() for s in jd_skills}

        if not jd_set:
            return {
                "matched_skills": candidate_skills,
                "missing_skills": [],
                "extra_skills": [],
                "skill_match_percentage": 100.0 if cand_set else 0.0
            }

        matched = sorted(list(cand_set.intersection(jd_set)))
        missing = sorted(list(jd_set.difference(cand_set)))
        extra = sorted(list(cand_set.difference(jd_set)))

        match_pct = round((len(matched) / len(jd_set)) * 100, 2)

        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "extra_skills": extra,
            "skill_match_percentage": match_pct
        }

    def compute_experience_score(
        self, candidate_exp_years: float, required_exp_years: float
    ) -> float:
        """
        Calculates experience score based on candidate experience vs required job experience.
        Full score awarded if candidate meets or exceeds requirement.
        """
        if required_exp_years <= 0:
            return 100.0

        if candidate_exp_years >= required_exp_years:
            # Full points + bonus cap up to 100
            return 100.0
        else:
            # Proportional score
            ratio = candidate_exp_years / required_exp_years
            return round(ratio * 100, 2)

    def evaluate_candidate(
        self,
        resume_id: str,
        resume_text: str,
        job_title: str,
        jd_text: str,
        required_skills: List[str] = None,
        required_experience: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-factor evaluation of a single candidate against a Job Description.
        """
        # 1. Parse entities from Resume
        contact_email = EntityExtractor.extract_email(resume_text)
        contact_phone = EntityExtractor.extract_phone(resume_text)
        social_links = EntityExtractor.extract_links(resume_text)
        candidate_name = EntityExtractor.extract_candidate_name(resume_text)
        extracted_skills_dict = EntityExtractor.extract_skills(resume_text)
        candidate_skills = extracted_skills_dict["flat_list"]
        candidate_exp_years = EntityExtractor.estimate_experience_years(resume_text)
        education_list = EntityExtractor.extract_education(resume_text)

        # 2. Extract JD skills if not explicitly provided
        if not required_skills:
            jd_skills_dict = EntityExtractor.extract_skills(jd_text)
            required_skills = jd_skills_dict["flat_list"]

        # 3. Compute Individual Scores
        tfidf_score = self.compute_tfidf_similarity(resume_text, jd_text)
        skill_gap = self.analyze_skills_gap(candidate_skills, required_skills)
        skill_score = skill_gap["skill_match_percentage"]
        exp_score = self.compute_experience_score(candidate_exp_years, required_experience)
        
        # Education baseline score
        edu_score = 100.0 if education_list else 70.0

        # 4. Calculate Final Composite Score
        composite_score = (
            (tfidf_score * self.weights["tfidf_similarity"]) +
            (skill_score * self.weights["skill_overlap"]) +
            (exp_score * self.weights["experience_match"]) +
            (edu_score * self.weights["education_domain"])
        )
        composite_score = float(np.round(composite_score, 2))

        # 5. Qualification Category Determination
        if composite_score >= 80.0:
            fit_category = "Strong Match"
            badge_color = "green"
        elif composite_score >= 65.0:
            fit_category = "Moderate Match"
            badge_color = "blue"
        elif composite_score >= 50.0:
            fit_category = "Potential Match"
            badge_color = "yellow"
        else:
            fit_category = "Low Match"
            badge_color = "red"

        # 6. Generate Actionable AI Recommendations
        recommendations = []
        if skill_gap["missing_skills"]:
            top_missing = ", ".join(skill_gap["missing_skills"][:4])
            recommendations.append(f"Missing key required skills: {top_missing}")
        else:
            recommendations.append("Matches all key technical skills listed in Job Description.")

        if candidate_exp_years >= required_experience:
            recommendations.append(f"Meets or exceeds experience requirement ({candidate_exp_years} yrs vs {required_experience} yrs required).")
        else:
            recommendations.append(f"Below required experience target ({candidate_exp_years} yrs vs {required_experience} yrs required).")

        if skill_score > 75:
            recommendations.append("High domain skill alignment detected.")

        return {
            "resume_id": resume_id,
            "candidate_name": candidate_name,
            "email": contact_email,
            "phone": contact_phone,
            "links": social_links,
            "job_title": job_title,
            "composite_score": composite_score,
            "fit_category": fit_category,
            "badge_color": badge_color,
            "score_breakdown": {
                "tfidf_similarity": tfidf_score,
                "skill_match_percentage": skill_score,
                "experience_score": exp_score,
                "education_score": edu_score
            },
            "candidate_info": {
                "experience_years": candidate_exp_years,
                "education": education_list,
                "categorized_skills": extracted_skills_dict["categorized"],
                "total_skills_count": len(candidate_skills)
            },
            "skill_gap_analysis": skill_gap,
            "ai_insights": recommendations
        }

    def rank_candidates(self, evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks evaluated candidates in descending order of their composite match score.
        Assigns rank position integers (1, 2, 3...).
        """
        sorted_candidates = sorted(evaluations, key=lambda x: x["composite_score"], reverse=True)
        for rank, candidate in enumerate(sorted_candidates, start=1):
            candidate["rank"] = rank
        return sorted_candidates
