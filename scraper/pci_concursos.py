import re
from dataclasses import dataclass, field
from typing import Optional
from urllib import request


@dataclass
class Download:
    prova_url: Optional[str] = None
    gabarito_url: Optional[str] = None


@dataclass
class Prova:
    nome: str
    ano: str
    orgao: str
    instituicao: str
    nivel: str
    url: str
    download: Download = field(default_factory=Download)


@dataclass
class PciConcursos:
    timeout: Optional[float] = 10.0

    def fetch(self, url: str) -> str:
        with request.urlopen(url, timeout=self.timeout) as response:
            return response.read().decode(
                response.headers.get_content_charset() or "utf-8"
            )

    def extrair_exams(self, html: str) -> list[Prova]:
        provas = []
        pattern = r'<tr class="lk_link [ce]" data-url="([^"]+)">.*?<a[^>]*class="prova_download"[^>]*>.*?</i>([^<]+)</a></td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*><a[^>]*>([^<]+)</a></td>\s*<td[^>]*><a[^>]*>([^<]+)</a></td>\s*<td[^>]*>([^<]+)</td>'
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            provas.append(
                Prova(
                    url=match[0],
                    nome=match[1].strip(),
                    ano=match[2].strip(),
                    orgao=match[3].strip(),
                    instituicao=match[4].strip(),
                    nivel=match[5].strip(),
                )
            )
        return provas

    def extrair_downloads(self, html: str) -> Download:
        pdfs = re.findall(r'href="([^"]*\.pdf)"', html)
        prova_url = None
        gabarito_url = None
        for pdf in pdfs:
            if "gabarito" in pdf.lower():
                if not gabarito_url:
                    gabarito_url = pdf
            elif not prova_url:
                prova_url = pdf
        return Download(prova_url=prova_url, gabarito_url=gabarito_url)

    def completar_prova(self, prova: Prova) -> Prova:
        html = self.fetch(prova.url)
        prova.download = self.extrair_downloads(html)
        return prova
