from scraper.pci_concursos import PciConcursos

BANCAS = {
    "FGV": "https://www.pciconcursos.com.br/provas/fgv",
}


if __name__ == "__main__":
    scraper = PciConcursos()

    for banca, url in BANCAS.items():
        print(f"\n📂 Processando banca: {banca}")
        provas = scraper.extrair_todas_provas(url)

        print(f"Total de provas encontradas: {len(provas)}")
        for prova in provas[:3]:
            scraper.completar_prova(prova)
            print(f"\n  📝 {prova.nome} ({prova.ano})")
            print(f"     Prova: {prova.download.prova_url}")
            print(f"     Gabarito: {prova.download.gabarito_url}")
