from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session
import httpx

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR.lstrip('/')}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Supabase uses its own JWT secret (usually the same as SERVICE_ROLE or a separate JWT SECRET)
        # However, it's easier to verify via the Supabase API if we want to be safe,
        # or just decode it if we have the secret.
        # For simplicity in this demo, we'll use the Supabase Project URL to verify if needed, 
        # or decode with the provided JWT secret (often Anon Key secret or a custom one).
        
        from app.core.database import supabase
        
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise credentials_exception
            
        user_email = user_response.user.email
        user_metadata = getattr(user_response.user, "user_metadata", {}) or {}
        
    except Exception:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        # Auto-sync missing user from Supabase to local DB
        new_user = User(
            name=user_metadata.get("full_name", user_email),
            email=user_email,
            password_hash="[STORED_IN_SUPABASE_AUTH]",
            role=user_metadata.get("role", "candidate")
        )
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            user = new_user
        except Exception:
            db.rollback()
            raise credentials_exception
            
    return user

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR.lstrip('/')}/auth/login", auto_error=False)

async def get_current_user_optional(token: str = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        from app.core.database import supabase
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            return None
        user_email = user_response.user.email
    except Exception:
        return None
        
    user = db.query(User).filter(User.email == user_email).first()
    return user
