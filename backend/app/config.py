from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://tourstats:changeme_password_123@db:5432/tourstats_db"
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus"
    BACKEND_SECRET: str = "changeme_backend_secret_123"
    NANOBOT_WS_URL: str = "ws://nanobot:8000/ws"
    DEBUG: bool = False
    
    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4317"
    OTEL_SERVICE_NAME: str = "tourstats-backend"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
