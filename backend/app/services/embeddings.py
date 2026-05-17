from sentence_transformers import SentenceTransformer

# Load open-source embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for a given text."""
    # Convert numpy array to list of floats
    return model.encode(text).tolist()

def get_profile_embedding(profile_data: dict) -> list[float]:
    """Generate an embedding for a user profile based on extracted JSON data."""
    skills = " ".join(profile_data.get("Skills", []))
    job_titles = " ".join(profile_data.get("Job_Titles", []))
    text_to_embed = f"{skills} {job_titles} {profile_data.get('Education_Level', '')}"
    return get_embedding(text_to_embed)
