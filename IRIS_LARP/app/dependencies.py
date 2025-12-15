from typing import Generator, Annotated
from datetime import datetime, timedelta
import bcrypt
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import SessionLocal, User, UserRole
from .config import settings

# DB Dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_current_user_cookie(request: Request, db: Session = Depends(get_db)):
    # Query param takes priority (for tab-isolated sessions)
    token = request.query_params.get("token")
    if not token:
        # Fallback to cookie
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})
        
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})
    return user

async def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return current_user

async def get_current_root(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != UserRole.ADMIN or current_user.username != "root":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Root access required")
    return current_user
