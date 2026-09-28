# Intelligent Resume Screening System – AI/ML & NLP 🚀

An end-to-end AI-powered resume screening, skill gap detection, and candidate ranking system built using **Python**, **Natural Language Processing (NLP)**, **Scikit-learn**, **Pandas**, **NumPy**, and **FastAPI**.

---

## 🌟 Key Features

1. **Text Preprocessing & NLP Pipeline**:
   - Automated text cleaning (removal of noise, URLs, bullet formatting, non-ASCII characters).
   - Tokenization, Stop-word removal, and Lemmatization using `NLTK`.
   - Structural section parsing (Summary, Experience, Education, Skills, Projects).

2. **Entity & Feature Extraction**:
   - Contact info extraction (Candidate Name, Email, Phone Number, LinkedIn, GitHub).
   - Categorized Skill Mining using a taxonomy covering AI/ML, Web Dev, Cloud & DevOps, Databases, Tools, and Soft Skills.
   - Candidate Experience Estimation & Degree Parsing (BS, MS, PhD).

3. **Multi-Factor AI Similarity & Ranking Engine**:
   - **TF-IDF Vectorization & Cosine Similarity**: Captures semantic overlap between candidate resume and Job Description across unigrams, bigrams, and trigrams.
   - **Skill Gap Analysis**: Pinpoints exactly which required technical skills are matched vs missing.
   - **Experience & Seniority Score**: Evaluates candidate career length against target role requirements.
   - **Composite Fit Category**: Assigns candidate match percentages and fit badges (*Strong Match*, *Moderate Match*, *Potential Match*, *Low Match*).

4. **Interactive Modern Web Dashboard**:
   - Real-time batch resume screening (.pdf, .txt, .docx files).
   - Candidate Ranking Board with score breakdowns and skill tags.
   - AI Insights & Recommendations for every applicant.
   - Single Resume Entity Extractor UI.
   - Multi-dimensional Chart.js Analytics & Score Radar.
   - CSV Candidate Evaluation Export.

5. **REST API & Developer Swagger UI**:
   - Fully documented OpenAPI endpoints built with FastAPI & Pydantic.

---

## 🛠️ Architecture & Tech Stack

- **Backend Framework**: Python, FastAPI, Uvicorn
- **AI/ML & Math**: Scikit-learn (`TfidfVectorizer`, `cosine_similarity`), NumPy, Pandas
- **NLP & Document Parsing**: NLTK, PyPDF, Regular Expressions
- **Frontend Dashboard**: HTML5, Tailwind CSS, JavaScript (ES6+), Chart.js, FontAwesome

---

## 🚀 Quick Start

### 1. Installation

Clone or navigate into the project workspace:

```bash
pip install -r requirements.txt
```

### 2. Run the Server

Start the application using the launcher script:

```bash
python run.py
```

Or run via Uvicorn:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Open Web Dashboard & API Docs

- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive Web Dashboard UI |
| `GET` | `/api/health` | System health check status |
| `GET` | `/api/sample-data` | Retrieves pre-packaged demo resumes & job descriptions |
| `GET` | `/api/skill-taxonomy` | Returns master categorized skill dictionary |
| `POST` | `/api/screen-single` | Evaluates a single resume text against a Job Description |
| `POST` | `/api/screen-bulk` | Uploads multiple PDF/DOCX/TXT files & screens against a JD |
| `POST` | `/api/parse-resume` | Extracts contact info, skills, and experience from a resume file |
| `POST` | `/api/export-csv` | Exports candidate screening scoreboard to downloadable CSV |

---

## 🧪 Running Unit Tests

Run the test suite to verify NLP algorithms and API endpoints:

```bash
pytest
```

---

## 📄 License

MIT License. Designed for Intelligent AI/ML & NLP Resume Screening applications.
