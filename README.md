# Scraper de Provas de Concursos

Scraper assíncrono para extração de provas e gabaritos de concursos públicos do site PCI Concursos.

## 📋 Funcionalidades

- **Scraping assíncrono** com `aiohttp` para alta performance
- **Extração de PDFs** de provas e gabaritos
- **Parsing de gabaritos** com múltiplos formatos suportados
- **Retry automático** com backoff exponencial usando `tenacity`
- **Rate limiting** para evitar bloqueios
- **Suporte a múltiplas bancas**: FGV, CEBRASPE, FCC, VUNESP, IBFC, CESGRANRIO, e mais

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- pip ou poetry

### Configuração

1. Clone o repositório:

```bash
git clone https://github.com/Luis-Felipe-N/scraper-provas.git
cd scraper-provas
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (opcional):

```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

## ⚙️ Configuração

O scraper pode ser configurado através de variáveis de ambiente ou arquivo `.env`:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SCRAPER_TIMEOUT` | Timeout das requisições (segundos) | `10.0` |
| `SCRAPER_DELAY_BETWEEN_REQUESTS` | Delay entre requisições (segundos) | `0.5` |
| `SCRAPER_MAX_CONCURRENT_REQUESTS` | Máximo de requisições simultâneas | `10` |
| `SCRAPER_RETRY_ATTEMPTS` | Número de tentativas em caso de erro | `3` |
| `SCRAPER_LOG_LEVEL` | Nível de log (DEBUG, INFO, WARNING, ERROR) | `INFO` |

## 📖 Uso

### Uso Básico

```python
import asyncio
import aiohttp
from src.scrapers import PciConcursosScraper
from src.services import PdfExtractor

async def main():
    scraper = PciConcursosScraper()
    extractor = PdfExtractor()
    
    base_url = "https://www.pciconcursos.com.br/provas/fgv"
    
    async with aiohttp.ClientSession(timeout=scraper.timeout) as session:
        async for exam in scraper.scrape_all(base_url):
            # Enriquecer com URLs de download
            await scraper.enrich_exam(session, exam)
            
            print(f"Prova: {exam.name}")
            print(f"Ano: {exam.year}")
            print(f"Órgão: {exam.organization}")
            print(f"PDF da Prova: {exam.download.exam_url}")
            print(f"PDF do Gabarito: {exam.download.answer_key_url}")
            
            # Extrair gabarito
            if exam.download.answer_key_url:
                answer_keys = await extractor.extract_answer_keys_from_url(
                    session, exam.download.answer_key_url
                )
                
                for ak in answer_keys:
                    print(f"Gabarito: {ak.exam_name}")
                    print(f"Respostas: {ak.answers}")

asyncio.run(main())
```

### Executar o Script Principal

```bash
python scraper_main.py
```

### Extrair Texto de PDF

```python
from src.services import PdfExtractor

extractor = PdfExtractor()

# Extrair de arquivo local
with open("prova.pdf", "rb") as f:
    content = extractor.extract_text(f.read())
    print(content.text)
    print(f"Páginas: {content.num_pages}")

# Extrair questões
questions = extractor.extract_questions(content.text)
for q in questions:
    print(f"Questão {q['number']}: {q['text'][:100]}...")
```

## 🏗️ Estrutura do Projeto

```
scraper-provas/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configurações e constantes
│   ├── models/
│   │   ├── __init__.py
│   │   └── exam.py         # Modelos de dados (Exam, Download)
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py         # Classe base abstrata
│   │   └── pci_concursos.py # Implementação para PCI Concursos
│   └── services/
│       ├── __init__.py
│       └── pdf_extractor.py # Extração de PDFs
├── scraper_main.py         # Script de exemplo
├── requirements.txt
├── .env.example
└── README.md
```

## 📦 Módulos

### `src.scrapers`

- **`BaseScraper`**: Classe base abstrata com retry automático e rate limiting
- **`PciConcursosScraper`**: Implementação específica para o site PCI Concursos

### `src.services`

- **`PdfExtractor`**: Extração de texto, imagens e gabaritos de PDFs
  - `extract_text()`: Extrai texto do PDF
  - `extract_questions()`: Identifica e extrai questões
  - `extract_answer_keys()`: Extrai gabaritos com suporte a múltiplos formatos

### `src.models`

- **`Exam`**: Representa uma prova de concurso
- **`Download`**: URLs de download da prova e gabarito

## 🎯 Bancas Suportadas

| Banca | Status |
|-------|--------|
| FGV | ✅ Testado |
| CEBRASPE | ✅ Testado |
| FCC | ✅ Testado |
| VUNESP | ✅ Testado |
| IBFC | ✅ Testado |
| CESGRANRIO | ✅ Testado |
| CONSULPLAN | ✅ Testado |
| FUNDATEC | ✅ Testado |
| FUNDEP | ✅ Suportado |
| IDECAN | ✅ Suportado |
| AOCP | ✅ Suportado |
| QUADRIX | ✅ Suportado |

## 🔧 Desenvolvimento

### Adicionar Nova Banca

1. Crie uma nova classe em `src/scrapers/`:

```python
from src.scrapers.base import BaseScraper

class NovaBancaScraper(BaseScraper):
    def parse_exam_list(self, html: str) -> list[Exam]:
        # Implementar parsing da lista de provas
        pass
    
    def parse_download_page(self, html: str) -> tuple[str | None, str | None]:
        # Implementar parsing da página de download
        pass
    
    async def scrape_all(self, base_url: str) -> AsyncIterator[Exam]:
        # Implementar scraping completo
        pass
```

2. Registre no `__init__.py`

### Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=src
```

## 📝 Licença

Este projeto é apenas para fins educacionais. Respeite os termos de uso dos sites que você está acessando.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## ⚠️ Aviso Legal

Este scraper deve ser usado de forma responsável e ética. Certifique-se de:

- Respeitar os termos de uso do site
- Não sobrecarregar os servidores
- Usar delays apropriados entre requisições
- Não redistribuir conteúdo protegido por direitos autorais
