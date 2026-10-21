import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ScamShield AI Enterprise"
    PROJECT_DESCRIPTION: str = "Enterprise AI Scam Call & Message Threat Intelligence Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MySQL Database Configuration
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "scamshield_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

    # ML Model Config
    MODEL_DIR: Path = BASE_DIR / "app" / "ml" / "saved_models"
    MODEL_FILENAME: str = "scam_classifier_pipeline.joblib"
    AUTO_RETRAIN_ON_STARTUP: bool = False
    
    # Thresholds
    SAFE_THRESHOLD: float = 30.0        # < 30 is Safe
    SUSPICIOUS_THRESHOLD: float = 65.0  # 30-65 Suspicious, > 65 High Risk Scam
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
os.makedirs(settings.MODEL_DIR, exist_ok=True)
