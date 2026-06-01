from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mistral_api_key: str = ""
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    playwright_headless: bool = True
    playwright_scrape_timeout_ms: int = 45000

    langsmith_tracing: str = "false"
    langsmith_endpoint: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = ""
    # Optional SMTP settings for bug reporting
    bug_report_recipient: str = ""
    smtp_server: str = ""
    smtp_port: int = 0
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings():
    return Settings()
