from fastapi import UploadFile
from app.core.config import settings
from app.core.database import supabase_admin as supabase
import io

class FileStorageService:
    def __init__(self):
        self.supabase = supabase
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET

    async def save_resume(self, file: UploadFile, filename: str) -> str:
        # Read file content
        content = await file.read()
        
        # Upload to Supabase Storage
        path = f"resumes/{filename}"
        self.supabase.storage.from_(self.bucket_name).upload(
            path=path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        res = self.supabase.storage.from_(self.bucket_name).get_public_url(path)
        
        # In some versions of supabase-py, get_public_url returns a string, 
        # in others it returns an object with a field.
        if isinstance(res, str):
            return res
        elif hasattr(res, "public_url"):
            return res.public_url
        elif isinstance(res, dict) and "public_url" in res:
            return res["public_url"]
        
        return str(res)

    async def save_image(self, file: UploadFile, filename: str, folder: str = "profiles") -> str:
        content = await file.read()
        path = f"{folder}/{filename}"
        self.supabase.storage.from_(self.bucket_name).upload(
            path=path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        res = self.supabase.storage.from_(self.bucket_name).get_public_url(path)
        if isinstance(res, str): return res
        elif hasattr(res, "public_url"): return res.public_url
        elif isinstance(res, dict) and "public_url" in res: return res["public_url"]
        return str(res)

    def delete_file(self, file_path: str):
        # Extract filename from URL or path
        filename = file_path.split("/")[-1]
        path = f"resumes/{filename}"
        self.supabase.storage.from_(self.bucket_name).remove([path])

file_storage_service = FileStorageService()
