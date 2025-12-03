import asyncio
from typing import ClassVar
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from scraper.serializers import BancaSerializer, ScrapeRequestSerializer, ScrapeResultSerializer
from scraper.tasks import scrape_banca_task


class ScrapeBancaView(APIView):
    """
    View para executar o scraping de provas de uma banca específica.
    """
    @extend_schema(
        summary="Executar scraping de provas",
        tags=["Scraper"],
        request=ScrapeRequestSerializer,
        responses={200: ScrapeResultSerializer, 400: {"description": "Erro"}}
    )
    def post(self, request):
        serializer = ScrapeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        banca = serializer.validated_data['banca'].upper()
        max_exams = serializer.validated_data.get('max_exams', 10)

        try:
            result = asyncio.run(scrape_banca_task(banca, max_exams))

            ScrapeStatusView._last_result = result

            return Response(ScrapeResultSerializer(result).data)

        except Exception as e:
            return Response(
                {'error': f'Erro na execução: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
