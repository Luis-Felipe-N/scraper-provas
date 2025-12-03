from typing import ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from scraper.serializers import BancaSerializer


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
