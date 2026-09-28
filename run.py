"""
Application Server Launcher script.
Runs the FastAPI application on http://127.0.0.1:8000 using Uvicorn.
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Intelligent Resume Screening System...")
    print("📍 Dashboard URL: http://127.0.0.1:8000")
    print("📍 OpenAPI Docs:  http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
