"""
Entity and Feature Extraction Engine.
Extracts contact info, skills, education, and years of experience from resume text.
"""
import re
from datetime import datetime
from typing import Dict, List, Set, Tuple

from app.core.config import ALL_SKILLS, SKILL_TAXONOMY
from app.nlp.preprocessor import TextPreprocessor


class EntityExtractor:
    """Extracts structured entities from parsed resume text."""

    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email address using regex pattern."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract phone number using international/US format regex."""
        pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_links(text: str) -> Dict[str, str]:
        """Extract LinkedIn and GitHub profile links."""
        links = {"linkedin": "", "github": "", "portfolio": ""}
        
        linkedin_pattern = r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+)'
        github_pattern = r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+)'
        
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        
        if linkedin_match:
            links["linkedin"] = linkedin_match.group(0)
        if github_match:
            links["github"] = github_match.group(0)
            
        return links

    @staticmethod
    def extract_candidate_name(text: str) -> str:
        """
        Extract candidate name from header or top lines of resume text.
        Applies heuristic search on non-empty first 5 lines.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:5]:
            # Skip emails, phone numbers, or section headers
            if '@' in line or re.search(r'\d{5,}', line):
                continue
            if any(kw in line.lower() for kw in ["resume", "curriculum vitae", "cv", "page"]):
                continue
            # A candidate name usually has 2-4 words and no special punctuation
            cleaned_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            words = cleaned_line.split()
            if 1 <= len(words) <= 4 and all(w.istitle() or w.isupper() for w in words):
                return " ".join(words)
        return "Candidate"

    @staticmethod
    def extract_skills(text: str) -> Dict[str, List[str]]:
        """
        Extracts skills from text by matching against master skill taxonomy.
        Returns both categorized skills and a flat list of extracted skills.
        """
        text_lower = text.lower()
        extracted_by_category: Dict[str, List[str]] = {}
        all_found: Set[str] = set()

        for category, skills in SKILL_TAXONOMY.items():
            category_found = []
            for skill in skills:
                # Skill matching with boundary checks to prevent false substrings
                # e.g., 'c' matching 'cats', or 'r' matching 'work'
                escaped_skill = re.escape(skill)
                pattern = r'(?:^|[\s,.\/()\[\]:\-])' + escaped_skill + r'(?:$|[\s,.\/()\[\]:\-])'
                
                if re.search(pattern, text_lower):
                    category_found.append(skill)
                    all_found.add(skill)
                    
            if category_found:
                extracted_by_category[category] = sorted(category_found)

        return {
            "categorized": extracted_by_category,
            "flat_list": sorted(list(all_found))
        }

    @staticmethod
    def estimate_experience_years(text: str) -> float:
        """
        Estimates candidate total years of experience by searching for explicit text statement
        (e.g., '5+ years of experience') or date ranges (e.g. 2018 - 2023, 2021 - Present).
        """
        text_lower = text.lower()
        
        # Method 1: Direct statement (e.g. "5+ years", "3.5 years of experience")
        direct_match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*years?(?:\s+of)?\s+experience', text_lower)
        if direct_match:
            try:
                return float(direct_match.group(1))
            except ValueError:
                pass
                
        # Method 2: Extract date ranges like 2018 - 2022 or Jan 2020 - Present
        current_year = datetime.now().year
        year_ranges = re.findall(r'(20\d{2}|19\d{2})\s*(?:-|to|–|—)\s*(20\d{2}|19\d{2}|present|current|now)', text_lower)
        
        total_months = 0
        for start_str, end_str in year_ranges:
            start_yr = int(start_str)
            if end_str in ['present', 'current', 'now']:
                end_yr = current_year
            else:
                end_yr = int(end_str)
                
            diff = max(0, end_yr - start_yr)
            # Cap realistic single role at 15 years unless specified
            if 0 <= diff <= 25:
                total_months += diff * 12

        if total_months > 0:
            # Add partial estimate or return computed years
            return round(min(total_months / 12.0, 30.0), 1)
            
        return 1.0  # Default baseline estimate if unspecified

    @staticmethod
    def extract_education(text: str) -> List[str]:
        """Extract degree levels and majors from resume text."""
        degrees = []
        degree_patterns = [
            r'\b(?:b\.?s\.?|b\.?tech\.?|bachelor(?:[\'\u2019]s)?(?:\s+of\s+[a-zA-Z\s]+)?)\b',
            r'\b(?:m\.?s\.?|m\.?tech\.?|master(?:[\'\u2019]s)?(?:\s+of\s+[a-zA-Z\s]+)?)\b',
            r'\b(?:ph\.?d\.?|doctorate|doctor of philosophy)\b',
            r'\b(?:b\.?a\.?|m\.?a\.?|b\.?c\.?a\.?|m\.?c\.?a\.?|b\.?b\.?a\.?|m\.?b\.?a\.?)\b'
        ]
        
        text_lower = text.lower()
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                degrees.append(m.upper())
                
        return sorted(list(set(degrees)))
