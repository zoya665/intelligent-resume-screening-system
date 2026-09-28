"""
File Parser Utility for Reading Resume Documents (.pdf, .txt, .docx).
"""
import io
import os
from typing import Union
import pypdf


class FileParser:
    """Extracts raw text content from uploaded resume documents."""

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF file byte contents."""
        text_content = []
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
            return "\n".join(text_content).strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        """Extract text from plain text file content."""
        try:
            return file_bytes.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise ValueError(f"Failed to decode text document: {str(e)}")

    @classmethod
    def parse_file(cls, filename: str, file_bytes: bytes) -> str:
        """
        Parses uploaded file byte stream according to file extension.
        Supports .pdf, .txt, and markdown files.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return cls.parse_pdf(file_bytes)
        elif ext in ['.txt', '.md', '.rtf']:
            return cls.parse_txt(file_bytes)
        elif ext == '.docx':
            # Basic fallback text extraction for docx XML structure if python-docx not available
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                return "\n".join([para.text for para in doc.paragraphs if para.text]).strip()
            except ImportError:
                # Simple fallback: extract ASCII printable text strings from byte stream
                clean_str = "".join([chr(b) if 32 <= b <= 126 or b in [10, 13] else ' ' for b in file_bytes])
                return clean_str.strip()
        else:
            # Attempt plain text decoding as fallback
            return cls.parse_txt(file_bytes)
