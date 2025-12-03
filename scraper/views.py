import asyncio
from typing import ClassVar

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import scrape_banca_task
from .serializers import BancaSerializer, ScrapeRequestSerializer, ScrapeResultSerializer


class BancaListView(APIView):
    """
    View para listar todas as bancas disponíveis para scraping.
    """
    AVAILABLE_BANCAS: ClassVar[list[dict]] = [
        {'id': 'fgv', 'name': 'FGV'},
        {'id': 'cebraspe', 'name': 'CEBRASPE'},
        {'id': 'fcc', 'name': 'FCC'},
        {'id': 'vunesp', 'name': 'VUNESP'},
        {'id': 'ibfc', 'name': 'IBFC'},
        {'id': 'cesgranrio', 'name': 'CESGRANRIO'},
        {'id': 'consulplan', 'name': 'CONSULPLAN'},
        {'id': 'fundatec', 'name': 'FUNDATEC'},
        {'id': 'fundep', 'name': 'FUNDEP'},
        {'id': 'idecan', 'name': 'IDECAN'},
        {'id': 'aocp', 'name': 'AOCP'},
        {'id': 'quadrix', 'name': 'QUADRIX'},
    ]

    @extend_schema(
        summary="Listar bancas disponíveis",
        description="Retorna a lista de bancas disponíveis para realizar o scraping.",
        tags=["Scraper"],
        responses={200: BancaSerializer(many=True)},
    )
    def get(self, request):
        """Retorna a lista de bancas disponíveis para scraping."""
        serializer = BancaSerializer(self.AVAILABLE_BANCAS, many=True)
        return Response({'bancas': serializer.data})

    @classmethod
    def get_valid_bancas(cls) -> list[str]:
        """Retorna lista de IDs de bancas válidas."""
        return [b['id'].upper() for b in cls.AVAILABLE_BANCAS]


class ScrapeBancaView(APIView):
    """
    View para executar o scraping de provas de uma banca específica.
    """

    @extend_schema(
        summary="Executar scraping de provas",
        description=(
            "Executa o scraping de provas de uma banca específica. "
            "O processo extrai as questões e gabaritos das provas encontradas."
        ),
        tags=["Scraper"],
        request=ScrapeRequestSerializer,
        responses={
            200: ScrapeResultSerializer,
            400: {"description": "Parâmetros inválidos"},
        },
    )
    def post(self, request):
        """
        Executa o scraping de provas de uma banca.

        Parâmetros:
            - banca: ID da banca (obrigatório)
            - max_exams: Número máximo de provas a processar (padrão: 10)
        """
        serializer = ScrapeRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        banca = serializer.validated_data['banca'].upper()
        max_exams = serializer.validated_data.get('max_exams', 10)

        valid_bancas = BancaListView.get_valid_bancas()
        if banca not in valid_bancas:
            return Response(
                {
                    'error': 'Banca inválida',
                    'detail': f'Bancas válidas: {", ".join(valid_bancas)}',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Executa o scraping
        result = asyncio.run(scrape_banca_task(banca, max_exams))

        result_serializer = ScrapeResultSerializer(result)
        return Response(result_serializer.data)


class ScrapeStatusView(APIView):
    """
    View para verificar o status do último scraping executado.
    """

    # Status compartilhado (em produção, usar Redis ou banco de dados)
    _last_result: ClassVar[dict | None] = None

    @extend_schema(
        summary="Status do scraping",
        description="Retorna o status do último scraping executado.",
        tags=["Scraper"],
        responses={200: ScrapeResultSerializer},
    )
    def get(self, request):
        """Retorna o status do último scraping executado."""
        if self._last_result is None:
            return Response(
                {'message': 'Nenhum scraping foi executado ainda.'},
                status=status.HTTP_204_NO_CONTENT,
            )

        serializer = ScrapeResultSerializer(self._last_result)
        return Response(serializer.data)
