import os
import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Import the counseling router
from routers import advisor

app = FastAPI(
    title="Erudite V2: Bangladesh Applicant Intelligence API",
    description="Unified, credit-safe admissions counseling and compliance audit engine for high-need applicants.",
    version="2.0.0"
)

# Configure CORS for Next.js frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the admissions advisor router
app.include_router(advisor.router, prefix="/advisor", tags=["Counseling"])

@app.get("/health")
async def health():
    """Service Health status endpoint."""
    return {
        "status": "ok",
        "app": "erudite-v2",
        "project": os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b"),
        "region": os.environ.get("REGION", "us-central1")
    }
