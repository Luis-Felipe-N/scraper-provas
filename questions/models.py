from django.db import models


class Question(models.Model):
    class Banca(models.TextChoices):
        FGV = 'FGV', 'FGV'
        CEBRASPE = 'CEBRASPE', 'CEBRASPE'
        FCC = 'FCC', 'FCC'
        VUNESP = 'VUNESP', 'VUNESP'
        IBFC = 'IBFC', 'IBFC'
        CESGRANRIO = 'CESGRANRIO', 'CESGRANRIO'
        CONSULPLAN = 'CONSULPLAN', 'CONSULPLAN'
        FUNDATEC = 'FUNDATEC', 'FUNDATEC'
        OTHER = 'OTHER', 'Outra'

    number = models.PositiveIntegerField(verbose_name='Número')
    text = models.TextField(verbose_name='Enunciado')
    alternatives = models.JSONField(default=dict, verbose_name='Alternativas')
    correct_answer = models.CharField(
        max_length=1, verbose_name='Resposta Correta')
    comment = models.TextField(
        blank=True, null=True, verbose_name='Comentário')

    banca = models.CharField(
        max_length=100,
        choices=Banca.choices,
        db_index=True,
        verbose_name='Banca'
    )
    year = models.PositiveIntegerField(db_index=True, verbose_name='Ano')
    organization = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Órgão'
    )
    position = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Cargo'
    )
    subject = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name='Disciplina'
    )
    topic = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Assunto'
    )

    exam_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name='URL da Prova')
    source_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name='URL de Origem')

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['-year', 'banca', 'number']

    def __str__(self):
        return f'{self.banca} {self.year} - Q{self.number}'


class Exam(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome')
    year = models.PositiveIntegerField(db_index=True, verbose_name='Ano')
    banca = models.CharField(
        max_length=100, db_index=True, verbose_name='Banca')
    organization = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Órgão')
    institution = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Instituição')
    level = models.CharField(max_length=100, blank=True,
                             null=True, verbose_name='Nível')

    page_url = models.URLField(max_length=500, verbose_name='URL da Página')
    exam_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name='URL da Prova')
    answer_key_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name='URL do Gabarito')

    questions = models.ManyToManyField(
        Question, related_name='exams', blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Prova'
        verbose_name_plural = 'Provas'
        ordering = ['-year', 'banca']

    def __str__(self):
        return f'{self.name} - {self.banca} ({self.year})'
