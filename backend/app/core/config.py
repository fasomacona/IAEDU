from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    use_mock_hints: bool = False

    sandbox_timeout_seconds: int = 5
    sandbox_max_output_chars: int = 8000

    database_url: str = "sqlite+aiosqlite:///./codementor.db"
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
