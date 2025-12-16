"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "social_support"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db: str = "social_support"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Ollama Settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    
    # Langfuse Settings (Optional - for observability/monitoring)
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Application Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # File Upload Settings
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env (for backward compatibility)


settings = Settings()

