from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.database import get_db, User, Profile, SavedJob
from app.schemas.schemas import UserCreate, UserLogin, Token, MatchResponse, CVOptimizeRequest
from app.core.config import settings
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import uuid

from app.services.pdf_parser import extract_text_from_pdf
from app.services.llm import extract_cv_data_via_llm, optimize_cv
from app.services.embeddings import get_profile_embedding
from app.services.vector_db import insert_user_profile, search_jobs

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not pwd_context.verify(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
    # Phase 1: LLM Parsing
    cv_data = extract_cv_data_via_llm(raw_text)
    
    # Store in Relational DB
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        profile.parsed_data = cv_data
    else:
        profile = Profile(user_id=current_user.id, parsed_data=cv_data)
        db.add(profile)
    db.commit()
    
    # Generate Embedding and Store in Vector DB
    vector = get_profile_embedding(cv_data)
    insert_user_profile(str(current_user.id), vector, {"email": current_user.email, **cv_data})
    
    return {"message": "CV uploaded and parsed successfully", "data": cv_data}

@router.get("/get-matches")
def get_matches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile or not profile.parsed_data:
        raise HTTPException(status_code=400, detail="Please upload a CV first")
        
    user_skills = set([s.lower() for s in profile.parsed_data.get("Skills", [])])
    user_vector = get_profile_embedding(profile.parsed_data)
    
    # Query Vector DB
    matches = search_jobs(user_vector, limit=50)
    
    results = []
    for match in matches:
        job_data = match["job_data"]
        job_skills = set([s.lower() for s in job_data.get("Skills", [])])
        
        # Gap Analysis
        matched_skills = list(user_skills.intersection(job_skills))
        missing_skills = list(job_skills.difference(user_skills))
        
        results.append({
            "id": match["id"],
            "score": match["score"],
            "title": job_data.get("Title", "Unknown Title"),
            "company": job_data.get("Company", "Unknown Company"),
            "location": job_data.get("Location", "Unknown Location"),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        })
        
    return {"matches": results}

@router.post("/save-job/{job_id}")
def save_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id).first()
    if not saved:
        saved = SavedJob(user_id=current_user.id, job_id=job_id, status="saved")
        db.add(saved)
        db.commit()
    return {"message": "Job saved successfully"}

@router.post("/optimize-cv")
def api_optimize_cv(request: CVOptimizeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Upload CV first")
        
    # We would normally store the raw CV text, but here we can just pass the parsed JSON text representation 
    # as a placeholder since the prompt is expecting CV context.
    cv_text = str(profile.parsed_data)
    
    optimized = optimize_cv(cv_text, request.job_description)
    return {"optimized_experience": optimized}
