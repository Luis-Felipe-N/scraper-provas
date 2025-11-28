import io
from dataclasses import dataclass, field
from typing import Optional

import aiohttp
from PIL import Image
from pypdf import PdfReader


@dataclass
class PdfImage:
    page: int
    index: int
    width: int
    height: int
    data: bytes
    format: str


@dataclass
class PdfContent:
    text: str
    num_pages: int
    metadata: dict
    images: list[PdfImage] = field(default_factory=list)


class PdfExtractor:
    def __init__(self, user_agent: str = "Mozilla/5.0"):
        self.user_agent = user_agent

    async def fetch_pdf(self, session: aiohttp.ClientSession, url: str) -> bytes:
        headers = {"User-Agent": self.user_agent}
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.read()

    def extract_text(self, pdf_bytes: bytes, extract_images: bool = False) -> PdfContent:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text_parts = []
        images = []

        for page_num, page in enumerate(reader.pages):
            text_parts.append(page.extract_text() or "")

            if extract_images:
                for img_index, image in enumerate(page.images):
                    try:
                        img_data = image.data
                        img = Image.open(io.BytesIO(img_data))
                        images.append(
                            PdfImage(
                                page=page_num + 1,
                                index=img_index,
                                width=img.width,
                                height=img.height,
                                data=img_data,
                                format=img.format or "unknown",
                            )
                        )
                    except Exception:
                        continue

        metadata = {}
        if reader.metadata:
            metadata = {
                "title": reader.metadata.title,
                "author": reader.metadata.author,
                "subject": reader.metadata.subject,
                "creator": reader.metadata.creator,
            }

        return PdfContent(
            text="\n\n".join(text_parts),
            num_pages=len(reader.pages),
            metadata=metadata,
            images=images,
        )

    async def extract_from_url(
        self, session: aiohttp.ClientSession, url: str, extract_images: bool = False
    ) -> PdfContent:
        pdf_bytes = await self.fetch_pdf(session, url)
        return self.extract_text(pdf_bytes, extract_images)

    def extract_questions(self, text: str) -> list[dict]:
        import re

        questions = []
        pattern = r"(?:^|\n)\s*(\d{1,3})\s*\n"
        matches = list(re.finditer(pattern, text))

        if not matches:
            pattern = r"(?:QUESTÃO|Questão|QUEST[ÃA]O)\s*[:\-]?\s*(\d+)"
            matches = list(re.finditer(pattern, text))

        seen_numbers = set()
        for i, match in enumerate(matches):
            num = int(match.group(1))
            if num in seen_numbers or num > 200:
                continue
            seen_numbers.add(num)

            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else min(start + 3000, len(text))
            question_text = text[start:end].strip()

            if len(question_text) < 50:
                continue

            questions.append(
                {
                    "number": num,
                    "text": question_text[:3000],
                }
            )

        questions.sort(key=lambda q: q["number"])
        return questions
