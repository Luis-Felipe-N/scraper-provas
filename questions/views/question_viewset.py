from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from questions.models import Question
from questions.serializers import QuestionSerializer, QuestionListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar questões",
        description="Retorna uma lista paginada de questões com filtros opcionais.",
        tags=["Questões"],
    ),
    retrieve=extend_schema(
        summary="Obter questão",
        description="Retorna os detalhes completos de uma questão específica.",
        tags=["Questões"],
    ),
)
class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualização de questões de concursos.

    Permite listar, filtrar e buscar questões por diversos critérios.
    """
    queryset = Question.objects.select_related().all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        'banca': ['exact', 'icontains'],
        'year': ['exact', 'gte', 'lte'],
        'subject': ['exact', 'icontains'],
        'organization': ['exact', 'icontains'],
    }
    search_fields = ['text', 'organization', 'position', 'topic']
    ordering_fields = ['year', 'banca', 'number', 'created_at']
    ordering = ['-year', 'number']

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionSerializer

    @extend_schema(
        summary="Listar bancas disponíveis",
        description="Retorna todas as bancas que possuem questões cadastradas.",
        tags=["Questões"],
        responses={200: {"type": "array", "items": {"type": "string"}}},
    )
    @action(detail=False, methods=['get'], url_path='bancas')
    def list_bancas(self, request):
        """Lista todas as bancas com questões cadastradas."""
        bancas = (
            Question.objects
            .values_list('banca', flat=True)
            .distinct()
            .order_by('banca')
        )
        return Response(list(bancas))

    @extend_schema(
        summary="Listar anos disponíveis",
        description="Retorna todos os anos que possuem questões cadastradas.",
        tags=["Questões"],
        responses={200: {"type": "array", "items": {"type": "integer"}}},
    )
    @action(detail=False, methods=['get'], url_path='anos')
    def list_years(self, request):
        """Lista todos os anos com questões cadastradas."""
        years = (
            Question.objects
            .values_list('year', flat=True)
            .distinct()
            .order_by('-year')
        )
        return Response(list(years))

    @extend_schema(
        summary="Listar disciplinas disponíveis",
        description="Retorna todas as disciplinas que possuem questões cadastradas.",
        tags=["Questões"],
        responses={200: {"type": "array", "items": {"type": "string"}}},
    )
    @action(detail=False, methods=['get'], url_path='disciplinas')
    def list_subjects(self, request):
        """Lista todas as disciplinas com questões cadastradas."""
        subjects = (
            Question.objects
            .exclude(subject__isnull=True)
            .exclude(subject='')
            .values_list('subject', flat=True)
            .distinct()
            .order_by('subject')
        )
        return Response(list(subjects))

    @extend_schema(
        summary="Obter questões aleatórias",
        description="Retorna questões aleatórias com filtros opcionais.",
        tags=["Questões"],
        parameters=[
            OpenApiParameter(name='count', type=int,
                             description='Quantidade de questões (padrão: 10)'),
            OpenApiParameter(name='banca', type=str,
                             description='Filtrar por banca'),
            OpenApiParameter(name='subject', type=str,
                             description='Filtrar por disciplina'),
            OpenApiParameter(name='year', type=int,
                             description='Filtrar por ano'),
        ],
    )
    @action(detail=False, methods=['get'], url_path='aleatorias')
    def random_questions(self, request):
        """Retorna questões aleatórias com filtros opcionais."""
        count = min(int(request.query_params.get('count', 10)), 50)
        banca = request.query_params.get('banca')
        subject = request.query_params.get('subject')
        year = request.query_params.get('year')

        queryset = self.get_queryset()

        if banca:
            queryset = queryset.filter(banca__iexact=banca)
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        if year:
            queryset = queryset.filter(year=year)

        questions = queryset.order_by('?')[:count]
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Estatísticas de questões",
        description="Retorna estatísticas gerais sobre as questões cadastradas.",
        tags=["Questões"],
    )
    @action(detail=False, methods=['get'], url_path='estatisticas')
    def statistics(self, request):
        """Retorna estatísticas sobre as questões cadastradas."""
        total = Question.objects.count()

        by_banca = (
            Question.objects
            .values('banca')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        by_year = (
            Question.objects
            .values('year')
            .annotate(count=Count('id'))
            .order_by('-year')[:10]
        )

        return Response({
            'total': total,
            'por_banca': list(by_banca),
            'por_ano': list(by_year),
        })
