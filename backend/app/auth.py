from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from app.database import get_db
from app import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# ─── SCHEMAS ─────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


# ─── PASSWORD ───────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ─── TOKEN ──────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─── ROUTES ─────────────────────────

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # check username
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # check email
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)  # ✅ FIXED
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, db_user.hashed_password):  # ✅ FIXED
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }