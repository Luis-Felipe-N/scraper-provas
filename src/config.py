import logging
from pydantic_settings import BaseSettings
from pydantic import Field


def setup_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("scraper")


class Settings(BaseSettings):
    timeout: float = Field(
        default=10.0, description="Request timeout in seconds")
    user_agent: str = Field(
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        description="User agent for HTTP requests",
    )
    download_dir: str = Field(
        default="downloads", description="Directory for downloads")
    delay_between_requests: float = Field(
        default=0.5, description="Delay between requests in seconds"
    )
    max_concurrent_requests: int = Field(
        default=10, description="Maximum concurrent HTTP requests"
    )
    retry_attempts: int = Field(
        default=3, description="Number of retry attempts")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = {"env_prefix": "SCRAPER_", "env_file": ".env"}


class ExamSource:
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url


EXAM_SOURCES: list[ExamSource] = [
    ExamSource(name="FGV", base_url="https://www.pciconcursos.com.br/provas/fgv"),
    ExamSource(
        name="CEBRASPE", base_url="https://www.pciconcursos.com.br/provas/cebraspe"
    ),
    ExamSource(name="FCC", base_url="https://www.pciconcursos.com.br/provas/fcc"),
]


settings = Settings()
logger = setup_logging(settings.log_level)
