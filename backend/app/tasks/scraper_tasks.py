from celery import shared_task
import requests
import uuid
from app.services.vector_db import insert_job
from app.services.embeddings import get_embedding

def normalize_job(raw_job: dict) -> dict:
    """Normalizes a scraped job into standard format."""
    return {
        "Title": raw_job.get("title", "Unknown Title"),
        "Company": raw_job.get("company", "Unknown Company"),
        "Location": raw_job.get("location", "Unknown Location"),
        "Remote": raw_job.get("remote", False),
        "Salary_Range": raw_job.get("salary", "Not Specified"),
        "Description": raw_job.get("description", ""),
        "Skills": raw_job.get("skills", [])
    }

@shared_task
def run_scrapers():
    """Background worker to fetch jobs daily."""
    print("Running nightly job scraper...")
    
    # Mock data source for now. In production, use Adzuna API, Selenium, etc.
    mock_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "remote": True,
            "salary": "$150k - $180k",
            "description": "Looking for an experienced Python developer with FastAPI and React skills.",
            "skills": ["Python", "FastAPI", "React", "Docker", "SQL"]
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Startup",
            "location": "San Francisco, CA",
            "remote": False,
            "salary": "$160k - $200k",
            "description": "Seeking an ML engineer with experience in LLMs and Vector Databases.",
            "skills": ["Python", "PyTorch", "NLP", "Pinecone", "HuggingFace"]
        }
    ]
    
    for raw_job in mock_jobs:
        normalized = normalize_job(raw_job)
        
        # Generate embedding from Description + Skills
        text_to_embed = f"{normalized['Title']} {normalized['Description']} {' '.join(normalized['Skills'])}"
        vector = get_embedding(text_to_embed)
        
        job_id = str(uuid.uuid4())
        insert_job(job_id, vector, normalized)
        
        print(f"Inserted job: {normalized['Title']} ({job_id})")
        
    # Phase 4.2: Automated Job Alerts could be triggered here
    # by fetching all users from the DB, finding matches for new jobs, and sending emails.
    
    print("Scraping finished.")
