from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.core.config import settings
import uuid

# Initialize Qdrant client
qdrant_client = QdrantClient(url=settings.QDRANT_URL)

JOBS_COLLECTION = "jobs"
USERS_COLLECTION = "users"

# Ensure collections exist
def init_qdrant():
    collections = qdrant_client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if JOBS_COLLECTION not in collection_names:
        qdrant_client.create_collection(
            collection_name=JOBS_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE) # all-MiniLM-L6-v2 output size is 384
        )
        
    if USERS_COLLECTION not in collection_names:
        qdrant_client.create_collection(
            collection_name=USERS_COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

# Initialize on startup
try:
    init_qdrant()
except Exception as e:
    print(f"Warning: Could not connect to Qdrant during startup: {e}")

def insert_job(job_id: str, vector: list[float], payload: dict):
    """Insert or update a job in the vector database."""
    qdrant_client.upsert(
        collection_name=JOBS_COLLECTION,
        points=[
            PointStruct(
                id=job_id,
                vector=vector,
                payload=payload
            )
        ]
    )

def insert_user_profile(user_id: str, vector: list[float], payload: dict):
    """Insert or update a user profile in the vector database."""
    qdrant_client.upsert(
        collection_name=USERS_COLLECTION,
        points=[
            PointStruct(
                id=user_id,
                vector=vector,
                payload=payload
            )
        ]
    )

def search_jobs(user_vector: list[float], limit: int = 50) -> list[dict]:
    """Search for the top matching jobs given a user profile vector."""
    results = qdrant_client.search(
        collection_name=JOBS_COLLECTION,
        query_vector=user_vector,
        limit=limit
    )
    # Format results
    matches = []
    for hit in results:
        matches.append({
            "id": hit.id,
            "score": hit.score,
            "job_data": hit.payload
        })
    return matches
