import asyncio
from typing import ClassVar

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import scrape_banca_task
from .serializers import BancaSerializer, ScrapeRequestSerializer, ScrapeResultSerializer


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
