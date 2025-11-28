from abc import ABC, abstractmethod
import asyncio
from collections.abc import AsyncIterator
from typing import Optional

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.models import Exam


class BaseScraper(ABC):
    def __init__(
        self,
        timeout: float = settings.timeout,
        user_agent: str = settings.user_agent,
        max_concurrent: int = settings.max_concurrent_requests,
    ):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.user_agent = user_agent
        self.max_concurrent = max_concurrent
        self._semaphore: Optional[asyncio.Semaphore] = None

    @retry(
        stop=stop_after_attempt(settings.retry_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
        before_sleep=lambda retry_state: print(
            f"Retry {retry_state.attempt_number} for {retry_state.args[1] if len(retry_state.args) > 1 else 'unknown URL'}"
        ),
    )
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)

        async with self._semaphore:
            headers = {"User-Agent": self.user_agent}
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()

    @abstractmethod
    def parse_exam_list(self, html: str) -> list[Exam]:
        pass

    @abstractmethod
    def parse_download_page(self, html: str) -> tuple[Optional[str], Optional[str]]:
        pass

    @abstractmethod
    async def scrape_all(self, base_url: str) -> AsyncIterator[Exam]:
        pass

    async def enrich_exam(self, session: aiohttp.ClientSession, exam: Exam) -> Exam:
        try:
            html = await self.fetch(session, exam.page_url)
            exam_url, answer_key_url = self.parse_download_page(html)
            exam.download.exam_url = exam_url
            exam.download.answer_key_url = answer_key_url
        except Exception as e:
            print(f"Failed to enrich exam {exam.name}: {e}")
        return exam
