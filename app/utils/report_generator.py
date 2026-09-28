"""
Report Generator Utility for CSV and Summary Export.
"""
import io
import pandas as pd
from typing import Any, Dict, List


class ReportGenerator:
    """Exports screening evaluations to CSV and structured formats."""

    @staticmethod
    def generate_csv_report(ranked_candidates: List[Dict[str, Any]]) -> str:
        """
        Converts a list of ranked candidate evaluation dictionaries into CSV format.
        """
        rows = []
        for cand in ranked_candidates:
            score_bd = cand.get("score_breakdown", {})
            cand_info = cand.get("candidate_info", {})
            skill_gap = cand.get("skill_gap_analysis", {})
            
            rows.append({
                "Rank": cand.get("rank"),
                "Candidate Name": cand.get("candidate_name"),
                "Match Score (%)": cand.get("composite_score"),
                "Fit Category": cand.get("fit_category"),
                "Email": cand.get("email"),
                "Phone": cand.get("phone"),
                "Experience (Yrs)": cand_info.get("experience_years"),
                "TF-IDF Similarity (%)": score_bd.get("tfidf_similarity"),
                "Skill Match (%)": score_bd.get("skill_match_percentage"),
                "Matched Skills": ", ".join(skill_gap.get("matched_skills", [])),
                "Missing Skills": ", ".join(skill_gap.get("missing_skills", [])),
                "AI Recommendation": " | ".join(cand.get("ai_insights", []))
            })

        df = pd.DataFrame(rows)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
