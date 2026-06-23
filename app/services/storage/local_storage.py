# Storage service skeleton
import os
import shutil

class LocalStorageService:
    def __init__(self, upload_dir: str = "/tmp/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_file(self, file_content: bytes, filename: str, job_id: str) -> str:
        job_dir = os.path.join(self.upload_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        file_path = os.path.join(job_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
