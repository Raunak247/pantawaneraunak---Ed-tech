import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API keys
    admin_api_key: str = os.environ.get("ADMIN_API_KEY", "default-admin-key-change-me")
    ai_api_key: str = os.environ.get("AI_API_KEY", "default-ai-key-change-me")
    
    # db
    use_in_memory: bool = os.environ.get("USE_IN_MEMORY", "true").lower() == "true"
    
    # Firebase
    firebase_credentials_path: str = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
    firebase_project_id: str = os.environ.get("FIREBASE_PROJECT_ID", "")
    
    # Fallback database
    fallback_questions_path: str = os.environ.get("FALLBACK_QUESTIONS_PATH", "sample_questions.json")
    
    # Application
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()