"""Конфигурация проекта."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # AI Service
    ai_host: str = "localhost"
    ai_port: int = 11434
    ai_model: str = "deepseek-r1:7b"
    ai_max_tokens: int = 2048
    ai_temperature: float = 0.1
    ai_cache_dir: str = "models/ai_server/cache"
    ai_confidence_threshold: float = 0.85
    
    # App
    app_name: str = "ASUTP-DSS-Local"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Storage
    sqlite_path: str = "data/asutp.db"
    documents_dir: str = "data/raw"
    models_dir: str = "models"
    cache_dir: str = "data/cache"
    
    # ML
    ml_device: str = "cuda"
    ml_batch_size: int = 32
    ml_num_workers: int = 4
    
    # UI
    streamlit_port: int = 8501
    api_port: int = 8000


settings = Settings()
