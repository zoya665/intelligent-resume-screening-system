"""
Configuration and Taxonomy Rules for the Intelligent Resume Screening System.
"""
from typing import Dict, List

# Master Skill Dictionary categorized by technical domains
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "golang",
        "rust", "ruby", "php", "scala", "kotlin", "swift", "r", "sql", "bash", "shell"
    ],
    "AI / ML / Data Science": [
        "machine learning", "deep learning", "natural language processing", "nlp",
        "computer vision", "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "xgboost",
        "lightgbm", "catboost", "spacy", "nltk", "transformers", "huggingface",
        "bert", "gpt", "llm", "large language models", "opencv", "neural networks",
        "cnn", "rnn", "lstm", "data analysis", "data mining", "feature engineering",
        "vector databases", "faiss", "pinecone", "chromadb", "langchain", "llama-index"
    ],
    "Web & Backend Development": [
        "fastapi", "flask", "django", "express", "express.js", "nodejs", "node.js",
        "react", "react.js", "vue", "vue.js", "angular", "next.js", "nuxt",
        "html", "html5", "css", "css3", "tailwind", "bootstrap", "rest api",
        "restful api", "graphql", "microservices", "websockets", "gRPC", "celery"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud platform",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "ci/cd", "nginx", "apache", "linux",
        "unix", "prometheus", "grafana", "helm", "serverless", "lambda"
    ],
    "Databases & Big Data": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "elasticsearch", "cassandra", "dynamodb", "snowflake", "bigquery",
        "apache spark", "spark", "hadoop", "kafka", "airflow", "dbt", "hive"
    ],
    "Tools & Frameworks": [
        "git", "github", "gitlab", "jira", "confluence", "postman", "swagger",
        "jupyter", "jupyter notebook", "vscode", "pycharm", "docker compose"
    ],
    "Soft Skills & Methodology": [
        "agile", "scrum", "leadership", "communication", "problem solving",
        "critical thinking", "teamwork", "project management", "time management",
        "mentorship", "cross-functional collaboration"
    ]
}

# Flattened set of all known skills for quick lookup
ALL_SKILLS = set()
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        ALL_SKILLS.add(skill.lower())

# Resume Section Header keywords for parsing
SECTION_MARKERS = {
    "summary": ["summary", "profile", "objective", "about me", "professional summary", "overview"],
    "experience": ["experience", "work history", "employment history", "professional experience", "work experience", "career summary"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "expertise", "skills & tools"],
    "education": ["education", "academic background", "qualification", "academic qualifications", "degrees"],
    "projects": ["projects", "key projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "licenses", "courses", "certificates", "credentials"]
}

# Default scoring weights for match calculation
DEFAULT_WEIGHTS = {
    "tfidf_similarity": 0.35,     # Global TF-IDF + Cosine semantic overlap
    "skill_overlap": 0.40,        # Exact & Categorized Skill overlap against JD requirements
    "experience_match": 0.15,     # Target years of experience vs candidate experience
    "education_domain": 0.10      # Relevance of education background / degree level
}
