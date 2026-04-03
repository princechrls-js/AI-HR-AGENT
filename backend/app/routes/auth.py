from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import auth_service
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
async def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if exists in local DB
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    try:
        auth_resp = await auth_service.sign_up_user(user_in.email, user_in.password, user_in.name, user_in.role.value)
        # Handle both AuthResponse (has .user) and pure User returns
        created_user = getattr(auth_resp, "user", auth_resp)
        if not created_user:
             raise HTTPException(status_code=400, detail="Supabase signup failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Save to local public metadata table (for roles/profile)
    # Note: We don't store the password_hash here because Supabase Auth handles it.
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash="[STORED_IN_SUPABASE_AUTH]",
        role=user_in.role.value
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user in database: {str(e)}")
        
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        auth_resp = await auth_service.sign_in_user(form_data.username, form_data.password)
        if not auth_resp.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Retrieve the user from the local DB to avoid extra round-trips from frontend
        db_user = db.query(User).filter(User.email == form_data.username).first()
        if db_user:
            user_payload = {
                "id": db_user.id,
                "email": db_user.email,
                "name": db_user.name,
                "role": db_user.role.value if hasattr(db_user.role, 'value') else db_user.role,
                "title": db_user.title,
                "company_name": db_user.company_name,
                "bio": db_user.bio,
                "avatar_url": db_user.avatar_url,
                "bg_url": db_user.bg_url
            }
        else:
            user_payload = auth_resp.user
            
        return {
            "access_token": auth_resp.session.access_token,
            "token_type": "bearer",
            "expires_in": auth_resp.session.expires_in,
            "refresh_token": auth_resp.session.refresh_token,
            "user": user_payload
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

from app.schemas.user import UserUpdate

@router.put("/profile", response_model=UserResponse)
def update_profile(updates: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user

from fastapi import UploadFile, File
import uuid
import os
from app.services.file_storage_service import file_storage_service

@router.post("/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    folder: str = "profiles",
    current_user: User = Depends(get_current_user)
):
    try:
        filename = f"{current_user.id}_{uuid.uuid4()}_{file.filename}"
        url = await file_storage_service.save_image(file, filename, folder)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.services.resume_parser_service import resume_parser_service
import tempfile

@router.post("/upload-resume")
async def upload_master_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Save to a temporary file on disk so resume_parser_service can read it
        suffix = os.path.splitext(file.filename)[1].lower() if file.filename else ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extract text using our PyMuPDF parser (expects a file path, synchronous)
        parsed_text = resume_parser_service.extract_text(tmp_path)

        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        if not parsed_text or len(parsed_text) < 30:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from resume. Please upload a text-based PDF.")

        # Reset file cursor so Supabase can read it
        await file.seek(0)

        # Upload the PDF to Supabase Storage
        filename = f"{current_user.id}_{uuid.uuid4()}_{file.filename}"
        url = await file_storage_service.save_resume(file, filename)

        # Save both URL and parsed text to User model
        user = db.query(User).filter(User.id == current_user.id).first()
        user.resume_url = url
        user.parsed_resume_text = parsed_text

        db.commit()
        db.refresh(user)

        return {"url": url, "message": "Resume uploaded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}")
