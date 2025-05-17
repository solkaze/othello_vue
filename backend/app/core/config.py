"""
app/core/config.py
"""
try:
    from pydantic_settings import BaseSettings  # pydantic v2 系
except ImportError:
    # もし v1 系を使う場合のフォールバック
    from pydantic import BaseSettings

class Settings(BaseSettings):
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()