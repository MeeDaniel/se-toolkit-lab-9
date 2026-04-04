from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MISTRAL_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://api.mistral.ai/v1"
    QWEN_MODEL: str = "mistral-small-latest"
    NANOBOT_ACCESS_KEY: str = "changeme_nanobot_key_123"
    NANOBOT_SYSTEM_PROMPT: str = "You are a helpful assistant for Innopolis tour guides."
    BACKEND_URL: str = "http://backend:8000"
    MCP_CONFIG_PATH: str = "/app/mcp"
    
    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4317"
    OTEL_SERVICE_NAME: str = "tourstats-nanobot"
    
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
