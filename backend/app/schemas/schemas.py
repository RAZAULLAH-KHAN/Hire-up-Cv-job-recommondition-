from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MatchResponse(BaseModel):
    id: str
    score: float
    title: str
    company: str
    location: str
    matched_skills: List[str]
    missing_skills: List[str]

class CVOptimizeRequest(BaseModel):
    job_description: str
