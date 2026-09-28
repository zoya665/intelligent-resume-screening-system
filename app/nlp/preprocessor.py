"""
NLP Preprocessor Module for Resume and Job Description Text.
Handles text cleaning, tokenization, stopword removal, lemmatization, and section extraction.
"""
import re
import string
from typing import Dict, List, Set
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from app.core.config import SECTION_MARKERS

# Ensure NLTK packages are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Initialize NLP tools with fallback
try:
    STOP_WORDS = set(stopwords.words('english'))
except Exception:
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "until", "while",
        "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
        "during", "before", "after", "above", "below", "to", "from", "up", "down", "in",
        "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now",
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "this", "that"
    }

lemmatizer = WordNetLemmatizer()


class TextPreprocessor:
    """Provides methods for cleaning, normalizing, and structuring document text."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans raw text by removing URLs, emails, bullet symbols, special characters,
        and extra whitespace while retaining technical punctuation like c++, c#, .js, .py.
        """
        if not text:
            return ""
        
        # Replace newlines and tabs with space
        cleaned = text.replace("\r", "\n")
        
        # Remove URLs
        cleaned = re.sub(r'http\S+|www\.\S+', ' ', cleaned)
        
        # Replace bullet points and weird symbols
        cleaned = re.sub(r'[\u2022\u2023\u25b6\u25c0\u25ba\u25c4\u25cf\u25cb\u25e6\u25a0\u25a1\uf0a7\u2013\u2014]', ' ', cleaned)
        cleaned = re.sub(r'[-–—•*]', ' ', cleaned)
        
        # Normalize non-ASCII characters
        cleaned = re.sub(r'[^\x00-\x7F]+', ' ', cleaned)
        
        # Collapse multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    @staticmethod
    def preprocess_tokens(text: str, remove_stop: bool = True, lemmatize: bool = True) -> List[str]:
        """
        Tokenizes text, converts to lowercase, removes stop words, and applies lemmatization.
        Preserves special technical tokens like 'c++', 'c#', '.net'.
        """
        cleaned = TextPreprocessor.clean_text(text).lower()
        
        # Tokenize using word boundary/regex to retain special tech names
        tokens = re.findall(r'[a-z0-9+#.]+', cleaned)
        
        processed_tokens = []
        for token in tokens:
            # Strip trailing dots unless it's like .net or node.js
            if token.endswith('.') and not (token.startswith('.') or token.count('.') > 1):
                token = token[:-1]
                
            if not token or len(token) < 2 and token not in ['r', 'c']:
                continue
                
            if remove_stop and token in STOP_WORDS:
                continue
                
            if lemmatize and token.isalpha():
                try:
                    token = lemmatizer.lemmatize(token)
                except Exception:
                    pass
                    
            processed_tokens.append(token)
            
        return processed_tokens

    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """
        Parses resume text into logical sections based on common headings.
        Returns a dictionary mapping section names to their textual content.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        sections: Dict[str, List[str]] = {key: [] for key in SECTION_MARKERS.keys()}
        sections["header"] = []
        
        current_section = "header"
        
        for line in lines:
            line_lower = line.lower().strip(':').strip('-').strip()
            
            # Check if this line is a section header
            matched_section = None
            if len(line_lower.split()) <= 4:  # Section titles are usually short
                for sec_name, keywords in SECTION_MARKERS.items():
                    if any(kw == line_lower or f"{kw}:" in line_lower for kw in keywords):
                        matched_section = sec_name
                        break
                        
            if matched_section:
                current_section = matched_section
            else:
                sections[current_section].append(line)
                
        # Join lines for each section
        return {sec: "\n".join(content) for sec, content in sections.items()}
