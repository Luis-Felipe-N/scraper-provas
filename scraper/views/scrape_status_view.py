from typing import ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from scraper.serializers import ScrapeResultSerializer


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
