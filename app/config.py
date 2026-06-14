import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Vercel and other serverless platforms have a read-only filesystem except /tmp
_ON_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
_DEFAULT_DB = (
    "sqlite+aiosqlite:////tmp/musicmakerlm.db"
    if _ON_SERVERLESS
    else "sqlite+aiosqlite:///./musicmakerlm.db"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    llm_provider: str = "local"
    audio_provider: str = "local"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    soundfont_path: str = "soundfonts/GeneralUser.sf2"
    database_url: str = _DEFAULT_DB
    debug: bool = False
    secret_key: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
