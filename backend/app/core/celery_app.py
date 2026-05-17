from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Example schedule for scraping jobs nightly
celery_app.conf.beat_schedule = {
    'scrape-jobs-every-night': {
        'task': 'app.tasks.scraper_tasks.run_scrapers',
        'schedule': 86400.0, # Every day
    },
}
