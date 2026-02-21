from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Video Clipper API"
    environment: str = "dev"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/clipper"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    s3_bucket: str = "video-uploads"
    max_upload_mb: int = 2048

    # plan rules
    guest_clip_limit: int = 2
    free_clip_limit: int = 5
    paid_monthly_limit: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
