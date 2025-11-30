import asyncio

import aiohttp

from src.config import EXAM_SOURCES
from src.scrapers import PciConcursosScraper
from src.services import PdfExtractor


async def main() -> None:
    scraper = PciConcursosScraper()
    extractor = PdfExtractor()

    for source in EXAM_SOURCES[:1]:
        print(f"Processing source: {source.name}")

        async with aiohttp.ClientSession(timeout=scraper.timeout) as session:
            async for exam in scraper.scrape_all(source.base_url):
                await scraper.enrich_exam(session, exam)

                if exam.download.answer_key_url:
                    print(f"\n📝 {exam.name} ({exam.year})")
                    print(f"   Gabarito URL: {exam.download.answer_key_url}")

                    print("\nExtracting answer keys...")
                    answer_keys = await extractor.extract_answer_keys_from_url(
                        session, exam.download.answer_key_url
                    )

                    print(f"Found {len(answer_keys)} answer key(s):\n")

                    for ak in answer_keys:
                        print(f"Exam: {ak.exam_name}")
                        print(f"Tipo: {ak.tipo}")
                        print(f"Total Questions: {len(ak.answers)}")
                        print("Answers (first 20):")
                        for q_num in sorted(ak.answers.keys())[:20]:
                            print(f"  {q_num}: {ak.answers[q_num]}", end="")
                        print("\n" + "-" * 50)

                    break
            break


if __name__ == "__main__":
    asyncio.run(main())
