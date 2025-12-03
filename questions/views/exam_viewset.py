from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from questions.models import Exam
from questions.serializers import ExamSerializer, ExamDetailSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar provas",
        description="Retorna uma lista paginada de provas com filtros opcionais.",
        tags=["Provas"],
    ),
    retrieve=extend_schema(
        summary="Obter prova",
        description="Retorna os detalhes completos de uma prova específica, incluindo suas questões.",
        tags=["Provas"],
    ),
)
class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualização de provas de concursos.

    Permite listar, filtrar e buscar provas por diversos critérios.
    """
    queryset = Exam.objects.prefetch_related('questions').all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        'banca': ['exact', 'icontains'],
        'year': ['exact', 'gte', 'lte'],
        'level': ['exact', 'icontains'],
        'organization': ['exact', 'icontains'],
    }
    search_fields = ['name', 'organization', 'institution']
    ordering_fields = ['year', 'banca', 'name', 'created_at']
    ordering = ['-year', 'banca']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamDetailSerializer
        return ExamSerializer

    @extend_schema(
        summary="Estatísticas de provas",
        description="Retorna estatísticas gerais sobre as provas cadastradas.",
        tags=["Provas"],
    )
    @action(detail=False, methods=['get'], url_path='estatisticas')
    def statistics(self, request):
        """Retorna estatísticas sobre as provas cadastradas."""
        total = Exam.objects.count()

        by_banca = (
            Exam.objects
            .values('banca')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        by_year = (
            Exam.objects
            .values('year')
            .annotate(count=Count('id'))
            .order_by('-year')[:10]
        )

        return Response({
            'total': total,
            'por_banca': list(by_banca),
            'por_ano': list(by_year),
        })
