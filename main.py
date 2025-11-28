import asyncio

import aiohttp

from src.config import EXAM_SOURCES
from src.scrapers import PciConcursosScraper
from src.services import PdfExtractor


async def main() -> None:
    scraper = PciConcursosScraper()
    pdf_extractor = PdfExtractor()

    for source in EXAM_SOURCES[:1]:
        print(f"Processing source: {source.name}")

        async with aiohttp.ClientSession(timeout=scraper.timeout) as session:
            async for exam in scraper.scrape_all(source.base_url):
                await scraper.enrich_exam(session, exam)

                print(f"\n📝 {exam.name} ({exam.year}) - {exam.organization}")
                print(f"   Exam URL: {exam.download.exam_url}")

                if exam.download.exam_url:
                    print("\n📄 Extracting PDF content...")
                    content = await pdf_extractor.extract_from_url(
                        session, exam.download.exam_url, extract_images=True
                    )
                    print(f"   Pages: {content.num_pages}")
                    print(f"   Images: {len(content.images)}")
                    print(f"   Text preview: {content.text}...")

                    if content.images:
                        print("\n   🖼️  Images found:")
                        for img in content.images[:5]:
                            print(
                                f"      Page {img.page}: {img.width}x{img.height} ({img.format})")

                    questions = pdf_extractor.extract_questions(content.text)
                    print(f"\n   📋 Questions found: {len(questions)}")
                    print("   First 3 questions:")
                    for q in questions[:3]:
                        print(f"      Q{q['number']}: {q['text'][:100]}...")
                    print("   Last 3 questions:")
                    for q in questions[-3:]:
                        print(f"      Q{q['number']}: {q['text'][:150]}...")

                break


if __name__ == "__main__":
    asyncio.run(main())
