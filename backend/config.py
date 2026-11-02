from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Role-based model configuration (Groq fast triage + Gemini 3.5 Flash Lite clinical deliberation)
    model_router: str = "openai/gpt-oss-20b"
    model_safety: str = "openai/gpt-oss-20b"
    model_simple: str = "openai/gpt-oss-20b"
    model_model1: str = "gemini-3.5-flash-lite"
    model_model2: str = "gemini-3.5-flash-lite"
    model_model3: str = "gemini-3.5-flash-lite"
    model_vision: str = "gemini-3.5-flash-lite"

    max_tokens: int = 2048
    temperature: float = 0.3

    router_max_tokens: int = 96
    safety_max_tokens: int = 128
    extraction_max_tokens: int = 512
    simple_max_tokens: int = 512
    analysis_max_tokens: int = 1024
    evidence_max_tokens: int = 1024
    adjudication_max_tokens: int = 1536
    final_safety_max_tokens: int = 128
    context_char_limit: int = 2000
    evidence_char_limit: int = 3000
    adjudication_char_limit: int = 2500

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )


settings = Settings()
