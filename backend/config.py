"""
Configuration management for the application.
Loads environment variables and provides typed settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Loan Underwriting AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    MONGODB_DB_NAME: str = Field(default="loan_underwriting_db")
    
    # JWT
    JWT_SECRET_KEY: str = Field(default="change-this-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Groq LLM
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    
    # File Upload
    UPLOAD_DIR: str = "./backend/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    
    # ML Model
    MODEL_PATH: str = "./backend/ml/artifacts/model.pkl"
    SCALER_PATH: str = "./backend/ml/artifacts/scaler.pkl"
    FEATURE_NAMES_PATH: str = "./backend/ml/artifacts/feature_names.json"
    
    # RAG
    POLICY_PATH: str = "./backend/policies/underwriting_policy.txt"
    EMBEDDINGS_PATH: str = "./data/embeddings/policy_embeddings.pkl"
    FAISS_INDEX_PATH: str = "./data/embeddings/faiss_index.bin"
    
    # Tesseract OCR
    TESSERACT_CMD: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    OCR_LANG: str = "eng"
    
    # Business Rules
    MIN_AGE: int = 21
    MAX_AGE: int = 65
    MIN_INCOME: float = 15000.0
    MAX_LOAN_AMOUNT: float = 5000000.0
    MAX_FOIR: float = 0.5
    MIN_BUREAU_SCORE: int = 650
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    LOG_FILE: str = "./logs/app.log"

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create global settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.UPLOAD_DIR,
        os.path.dirname(settings.LOG_FILE) if settings.LOG_FILE else None,
        os.path.dirname(settings.MODEL_PATH) if settings.MODEL_PATH else None,
        os.path.dirname(settings.EMBEDDINGS_PATH) if settings.EMBEDDINGS_PATH else None,
        "./data/synthetic",
        "./data/embeddings",
    ]
    
    for directory in directories:
        if directory:
            os.makedirs(directory, exist_ok=True)


ensure_directories()