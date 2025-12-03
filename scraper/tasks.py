import asyncio
import aiohttp
from questions.models import Question, Exam
from src.scrapers import PciConcursosScraper
from src.services import PdfExtractor


async def scrape_banca_task(banca: str, max_exams: int = 10) -> dict:
    scraper = PciConcursosScraper()
    extractor = PdfExtractor()

    base_url = f"https://www.pciconcursos.com.br/provas/{banca.lower()}"

    result = {
        'banca': banca,
        'total_exams': 0,
        'total_questions': 0,
        'errors': [],
    }

    try:
        async with aiohttp.ClientSession(timeout=scraper.timeout) as session:
            exam_count = 0

            async for exam_data in scraper.scrape_all(base_url):
                print(f"Processing exam: {exam_data.name}")
                if exam_count >= max_exams:
                    break

                try:
                    await scraper.enrich_exam(session, exam_data)

                    if not exam_data.download.exam_url and not exam_data.download.answer_key_url:
                        exam_count += 1
                        continue

                    try:
                        year = int(exam_data.year) if exam_data.year else 2024
                    except (ValueError, TypeError):
                        year = 2024

                    # [CORREÇÃO] Uso de aget_or_create (nativo Django 5)
                    exam_obj, created = await Exam.objects.aget_or_create(
                        page_url=exam_data.page_url,
                        defaults={
                            'name': exam_data.name,
                            'year': year,
                            'banca': banca.upper(),
                            'organization': exam_data.organization,
                            'institution': exam_data.institution,
                            'level': exam_data.level,
                            'exam_url': exam_data.download.exam_url,
                            'answer_key_url': exam_data.download.answer_key_url,
                        }
                    )

                    result['total_exams'] += 1

                    if exam_data.download.exam_url and exam_data.download.answer_key_url:
                        try:
                            pdf_content = await extractor.extract_from_url(
                                session, exam_data.download.exam_url
                            )
                            questions_data = extractor.extract_questions(
                                pdf_content.text)

                            answer_keys = await extractor.extract_answer_keys_from_url(
                                session, exam_data.download.answer_key_url
                            )

                            answer_map = answer_keys[0].answers if answer_keys else {
                            }

                            for q_data in questions_data:
                                q_num = q_data['number']
                                correct_answer = answer_map.get(q_num, '')

                                if not correct_answer:
                                    continue

                                # [CORREÇÃO] aget_or_create para questões
                                question, q_created = await Question.objects.aget_or_create(
                                    banca=banca.upper(),
                                    year=year,
                                    number=q_num,
                                    source_url=exam_data.page_url,
                                    defaults={
                                        'text': q_data['text'],
                                        'alternatives': {},
                                        'correct_answer': correct_answer,
                                        'organization': exam_data.organization,
                                        'position': exam_data.name,
                                        'exam_url': exam_data.download.exam_url,
                                    }
                                )

                                if q_created:
                                    # [CORREÇÃO] aadd para relacionamento ManyToMany
                                    await exam_obj.questions.aadd(question)
                                    result['total_questions'] += 1

                        except Exception as e:
                            result['errors'].append(
                                f"Erro na extração de {exam_data.name}: {e}")

                except Exception as e:
                    result['errors'].append(
                        f"Erro ao processar prova {exam_data.name}: {e}")

                exam_count += 1
                await asyncio.sleep(0.5)

    except Exception as e:
        result['errors'].append(f"Erro fatal no scraping: {str(e)}")

    return result
