import io
import re
from dataclasses import dataclass, field

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
class AnswerKey:
    exam_name: str
    tipo: str
    answers: dict[int, str]


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
            end = matches[i + 1].start() if i + \
                1 < len(matches) else min(start + 3000, len(text))
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

    def extract_answer_keys(self, text: str) -> list[AnswerKey]:
        text = re.sub(r"pcimarkpci\s*\w+", "", text)
        text = re.sub(r"\s+", " ", text)

        answer_keys = []
        pattern = r"([A-Za-zÀ-ÿº\s]+(?:Militar|Bombeiro|Polícia|Civil|Perito|Tenente|Soldado|Oficial|Agente)[^–\-]*)[–\-]\s*Tipo\s*(\d+)"
        blocks = list(re.finditer(pattern, text, re.IGNORECASE))

        for i, match in enumerate(blocks):
            exam_name = match.group(1).strip()
            exam_name = re.sub(r"^(GABARITO\s*(DEFINITIVO|PRELIMINAR|OFICIAL)?\s*)", "", exam_name, flags=re.IGNORECASE).strip()
            exam_name = re.sub(r"^\d*º?\s*", "", exam_name).strip()
            tipo = match.group(2).strip()

            start = match.end()
            end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
            block_text = text[start:end]

            numbers = re.findall(r"\b(\d{1,3})\b", block_text)
            letters = re.findall(r"\b([A-E])\b", block_text)

            answers = {}
            expected_questions = []
            for num in numbers:
                n = int(num)
                if 1 <= n <= 200:
                    expected_questions.append(n)

            expected_questions = sorted(set(expected_questions))

            if len(letters) >= len(expected_questions):
                for idx, q_num in enumerate(expected_questions):
                    if idx < len(letters):
                        answers[q_num] = letters[idx]

            if answers:
                answer_keys.append(
                    AnswerKey(
                        exam_name=exam_name,
                        tipo=tipo,
                        answers=answers,
                    )
                )

        return answer_keys

    async def extract_answer_keys_from_url(
        self, session: aiohttp.ClientSession, url: str
    ) -> list[AnswerKey]:
        pdf_content = await self.extract_from_url(session, url)
        return self.extract_answer_keys(pdf_content.text)
