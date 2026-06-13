from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "local"
    audio_provider: str = "local"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    soundfont_path: str = "soundfonts/GeneralUser.sf2"
    database_url: str = "sqlite+aiosqlite:///./musicmakerlm.db"
    debug: bool = False
    secret_key: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
