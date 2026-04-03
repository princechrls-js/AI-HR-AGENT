import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXHIRE Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # AI Config
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5")
    
    # Paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/resumes")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "faiss_store/jobs.index")
    FAISS_METADATA_PATH: str = os.getenv("FAISS_METADATA_PATH", "faiss_store/jobs_metadata.pkl")

    class Config:
        case_sensitive = True

settings = Settings()
