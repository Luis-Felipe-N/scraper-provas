from django.db import models


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
        'questions.Question', related_name='exams', blank=True)

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
