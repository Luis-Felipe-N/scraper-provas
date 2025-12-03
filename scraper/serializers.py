from rest_framework import serializers


class BancaSerializer(serializers.Serializer):
    """Serializer para representar uma banca."""
    id = serializers.CharField(help_text="Identificador único da banca")
    name = serializers.CharField(help_text="Nome da banca")


class ScrapeRequestSerializer(serializers.Serializer):
    """Serializer para requisição de scraping."""
    banca = serializers.CharField(
        required=True,
        help_text="ID da banca (ex: FGV, CEBRASPE, FCC)",
    )
    max_exams = serializers.IntegerField(
        required=False,
        default=10,
        min_value=1,
        max_value=100,
        help_text="Número máximo de provas a processar (padrão: 10)",
    )


class ScrapeResultSerializer(serializers.Serializer):
    """Serializer para resultado do scraping."""
    banca = serializers.CharField(help_text="Banca processada")
    total_exams = serializers.IntegerField(
        help_text="Total de provas processadas")
    total_questions = serializers.IntegerField(
        help_text="Total de questões extraídas")
    errors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de erros encontrados durante o processo",
    )
