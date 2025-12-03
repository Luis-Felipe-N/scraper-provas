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

    model_config = {"env_prefix": "SCRAPER_", "env_file": ".env", "extra": "ignore"}


class ExamSource:
    def __init__(self, name: str, base_url: str, source_type: str = "banca"):
        self.name = name
        self.base_url = base_url
        self.source_type = source_type


EXAM_BANCAS: list[ExamSource] = [
    ExamSource("FGV", "https://www.pciconcursos.com.br/provas/fgv"),
    ExamSource("CEBRASPE", "https://www.pciconcursos.com.br/provas/cebraspe"),
    ExamSource("FCC", "https://www.pciconcursos.com.br/provas/fcc"),
    ExamSource("VUNESP", "https://www.pciconcursos.com.br/provas/vunesp"),
    ExamSource("IBFC", "https://www.pciconcursos.com.br/provas/ibfc"),
    ExamSource("CESGRANRIO", "https://www.pciconcursos.com.br/provas/cesgranrio"),
    ExamSource("FUNDEP", "https://www.pciconcursos.com.br/provas/fundep"),
    ExamSource("IDECAN", "https://www.pciconcursos.com.br/provas/idecan"),
    ExamSource("FUNDATEC", "https://www.pciconcursos.com.br/provas/fundatec"),
    ExamSource("AOCP", "https://www.pciconcursos.com.br/provas/aocp"),
    ExamSource("CONSULPLAN", "https://www.pciconcursos.com.br/provas/consulplan"),
    ExamSource("INSTITUTO AOCP",
               "https://www.pciconcursos.com.br/provas/instituto-aocp"),
    ExamSource("QUADRIX", "https://www.pciconcursos.com.br/provas/quadrix"),
    ExamSource("OBJETIVA", "https://www.pciconcursos.com.br/provas/objetiva"),
    ExamSource("FUNCAB", "https://www.pciconcursos.com.br/provas/funcab"),
]

EXAM_CATEGORIES: list[ExamSource] = [
    ExamSource(
        "Enfermeiro", "https://www.pciconcursos.com.br/provas/enfermeiro", "cargo"),
    ExamSource("Médico", "https://www.pciconcursos.com.br/provas/medico", "cargo"),
    ExamSource(
        "Professor", "https://www.pciconcursos.com.br/provas/professor", "cargo"),
    ExamSource(
        "Contador", "https://www.pciconcursos.com.br/provas/contador", "cargo"),
    ExamSource(
        "Advogado", "https://www.pciconcursos.com.br/provas/advogado", "cargo"),
    ExamSource("Analista de Sistemas",
               "https://www.pciconcursos.com.br/provas/analista-de-sistemas", "cargo"),
    ExamSource("Agente de Polícia",
               "https://www.pciconcursos.com.br/provas/agente-de-policia", "cargo"),
    ExamSource("Delegado de Polícia",
               "https://www.pciconcursos.com.br/provas/delegado-de-policia", "cargo"),
    ExamSource("Escriturário",
               "https://www.pciconcursos.com.br/provas/escriturario", "cargo"),
    ExamSource("Técnico de Enfermagem",
               "https://www.pciconcursos.com.br/provas/tecnico-de-enfermagem", "cargo"),
    ExamSource("Auditor Fiscal",
               "https://www.pciconcursos.com.br/provas/auditor-fiscal", "cargo"),
    ExamSource("Analista Judiciário",
               "https://www.pciconcursos.com.br/provas/analista-judiciario", "cargo"),
    ExamSource("Oficial de Justiça",
               "https://www.pciconcursos.com.br/provas/oficial-de-justica", "cargo"),
    ExamSource("Engenheiro Civil",
               "https://www.pciconcursos.com.br/provas/engenheiro-civil", "cargo"),
    ExamSource("Assistente Social",
               "https://www.pciconcursos.com.br/provas/assistente-social", "cargo"),
    ExamSource(
        "Psicólogo", "https://www.pciconcursos.com.br/provas/psicologo", "cargo"),
    ExamSource("Nutricionista",
               "https://www.pciconcursos.com.br/provas/nutricionista", "cargo"),
    ExamSource("Farmacêutico",
               "https://www.pciconcursos.com.br/provas/farmaceutico", "cargo"),
    ExamSource("Fisioterapeuta",
               "https://www.pciconcursos.com.br/provas/fisioterapeuta", "cargo"),
    ExamSource(
        "Dentista", "https://www.pciconcursos.com.br/provas/dentista", "cargo"),
]

EXAM_SOURCES: list[ExamSource] = EXAM_BANCAS


settings = Settings()
logger = setup_logging(settings.log_level)
