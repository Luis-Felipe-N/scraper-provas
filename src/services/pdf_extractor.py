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
        text = re.sub(r"pcimarkpci\s*\S+", "", text)
        text = re.sub(r"www\.pciconcursos\.com\.br", "", text)
        text = re.sub(r"Página\s*\d+\s*de\s*\d+", "", text)
        text = re.sub(r"([A-ZÀ-Ÿ])\n([A-ZÀ-Ÿ])", r"\1\2", text)

        answer_keys = []

        cargo_patterns = [
            (r"M(\d+)\s*[-–]\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿº\s\-–]+?)(?:\n|PROVA)", "m_pattern"),
            (r"([A-ZÀ-Ÿ][A-Za-zÀ-ÿº\s\-–]+(?:Militar|Bombeiro|Polícia|Civil|Perito|Tenente|Soldado|Oficial|Agente|Contador|Analista|Técnico|Escriturário|Assistente|Auxiliar|Administrador|Engenheiro|Advogado|Médico|Enfermeiro|Professor|Fiscal|Auditor|Delegado|Escrivão|Inspetor|Motorista|Operador|Secretário|Gestor|Coordenador|Supervisor|Gerente|Diretor)[A-Za-zÀ-ÿº\s\-–]*)[–\-]\s*Tipo\s*(\d+)", "tipo"),
            (r"(?:GABARITO\s*(?:OFICIAL|DEFINITIVO|PRELIMINAR)?)\s*\n?\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿº\s\-–]+?)\s+Prova\s*[-–]?\s*([A-Z0-9]+)", "prova"),
            (r"\n\s*([A-ZÀ-Ÿ][A-ZÀ-Ÿ\s\-–]+(?:ÁRIO|ISTA|OR|ENTE|IVO|ICO|IRO|ADO|IDO|OSO|ÃO|EIRO|ADOR)[A-ZÀ-Ÿ\s\-–]*)\s*\n\s*(?=\d+\s*[-–:]?\s*[A-E])", "uppercase"),
        ]

        for pattern, pattern_type in cargo_patterns:
            blocks = list(re.finditer(
                pattern, text, re.IGNORECASE | re.MULTILINE))

            for i, match in enumerate(blocks):
                if pattern_type == "m_pattern":
                    tipo = match.group(1).strip()
                    exam_name = match.group(2).strip()
                else:
                    exam_name = match.group(1).strip()
                    tipo = match.group(2).strip(
                    ) if match.lastindex >= 2 else "1"

                exam_name = re.sub(r"^(GABARITO\s*(DEFINITIVO|PRELIMINAR|OFICIAL)?\s*)",
                                   "", exam_name, flags=re.IGNORECASE).strip()
                exam_name = re.sub(r"^\d*º?\s*", "", exam_name).strip()
                exam_name = re.sub(r"\s+", " ", exam_name).strip()

                if len(exam_name) < 4 or exam_name.upper() in ("PROVA", "GABARITO", "TIPO"):
                    continue

                start = match.end()
                next_match_start = blocks[i + 1].start() if i + \
                    1 < len(blocks) else len(text)
                end = next_match_start

                block_text = text[start:end]

                answers = self._extract_answers_from_block(block_text)

                if answers and len(answers) >= 5:
                    existing = next(
                        (ak for ak in answer_keys if ak.exam_name == exam_name and ak.tipo == tipo), None)
                    if not existing:
                        answer_keys.append(
                            AnswerKey(exam_name=exam_name, tipo=tipo, answers=answers))

            if answer_keys:
                break

        if not answer_keys:
            answers = self._extract_answers_from_block(text)
            if answers and len(answers) >= 5:
                exam_name = self._extract_exam_name_from_text(text)
                answer_keys.append(
                    AnswerKey(exam_name=exam_name, tipo="1", answers=answers))

        return answer_keys

    def _extract_exam_name_from_text(self, text: str) -> str:
        patterns = [
            r"(?:GABARITO\s*(?:OFICIAL|DEFINITIVO|PRELIMINAR)?)\s*\n?\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿº\s\-–]{5,50})",
            r"([A-Z][A-Z\s\-–]+(?:ÁRIO|ISTA|OR|ENTE|IVO|ICO|IRO|ADO|IDO|OSO)[A-Z\s\-–]*)",
            r"CARGO:\s*([A-Za-zÀ-ÿº\s\-–]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                name = re.sub(r"\s+", " ", name)
                if len(name) >= 5:
                    return name
        return "Unknown"

    def _extract_answers_from_block(self, block_text: str) -> dict[int, str]:
        answers = {}

        table_pattern = r"(\d+(?:\s+\d+){4,})\s*\n\s*([A-EX](?:\s+[A-EX]){4,})"
        for match in re.finditer(table_pattern, block_text, re.IGNORECASE):
            nums = [int(n) for n in match.group(1).split()]
            letters = match.group(2).upper().split()
            for num, letter in zip(nums, letters):
                if 1 <= num <= 200 and letter in "ABCDEX":
                    answers[num] = letter

        if answers:
            return answers

        patterns = [
            r"(\d{1,3})\s*[-–:]\s*([A-EX])",
            r"(\d{1,3})\s*[\.]\s*([A-EX])",
            r"\b(\d{1,3})\s+([A-EX])\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, block_text, re.IGNORECASE)
            for num_str, letter in matches:
                num = int(num_str)
                if 1 <= num <= 200 and letter.upper() in "ABCDEX":
                    if num not in answers:
                        answers[num] = letter.upper()

        return answers

    async def extract_answer_keys_from_url(
        self, session: aiohttp.ClientSession, url: str
    ) -> list[AnswerKey]:
        pdf_content = await self.extract_from_url(session, url)
        return self.extract_answer_keys(pdf_content.text)
