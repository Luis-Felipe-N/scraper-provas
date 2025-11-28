import asyncio
from collections.abc import AsyncIterator
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from src.config import settings
from src.models import Exam
from src.scrapers.base import BaseScraper


class PciConcursosScraper(BaseScraper):
    def parse_exam_list(self, html: str) -> list[Exam]:
        soup = BeautifulSoup(html, "html.parser")
        exams = []

        for row in soup.select("tr.lk_link[data-url]"):
            try:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                name_link = row.select_one("a.prova_download")
                name = name_link.get_text(strip=True) if name_link else ""

                exams.append(
                    Exam(
                        page_url=row["data-url"],
                        name=name,
                        year=cols[1].get_text(strip=True),
                        organization=cols[2].get_text(strip=True),
                        institution=cols[3].get_text(strip=True),
                        level=cols[4].get_text(strip=True),
                    )
                )
            except (KeyError, IndexError) as e:
                print(f"Failed to parse row: {e}")
                continue

        return exams

    def parse_download_page(self, html: str) -> tuple[Optional[str], Optional[str]]:
        soup = BeautifulSoup(html, "html.parser")
        exam_url = None
        answer_key_url = None

        for link in soup.select('a[href$=".pdf"]'):
            href = link.get("href", "")
            if "gabarito" in href.lower():
                if not answer_key_url:
                    answer_key_url = href
            elif not exam_url:
                exam_url = href

        return exam_url, answer_key_url

    async def scrape_all(self, base_url: str) -> AsyncIterator[Exam]:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            page = 1
            while True:
                url = base_url if page == 1 else f"{base_url}/{page}"
                print(f"Fetching page {page}: {url}")

                try:
                    html = await self.fetch(session, url)
                    exams = self.parse_exam_list(html)

                    if not exams:
                        print(f"No more exams found at page {page}")
                        break

                    for exam in exams:
                        yield exam

                    page += 1
                    await asyncio.sleep(settings.delay_between_requests)

                except Exception as e:
                    print(f"Failed to fetch page {page}: {e}")
                    break
