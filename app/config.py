"""
Central configuration for the AIVOA Customer Complaint Management System backend.
All secrets/config are read from environment variables (see .env.example).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    database_url: str = "sqlite:///./ccms.db"  # swap for postgres/mysql URL in prod

    # --- Groq LLM config ---
    groq_api_key: str = ""
    groq_extraction_model: str = "gemma2-9b-it"
    groq_reasoning_model: str = "llama-3.3-70b-versatile"

    # --- App ---
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
