from django.db import models


class Alternative(models.Model):
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='alternative_set',
        verbose_name='Questão'
    )
    label = models.CharField(max_length=1, verbose_name='Letra')
    text = models.TextField(verbose_name='Texto da Alternativa')
    is_correct = models.BooleanField(default=False, verbose_name='Correta')

    class Meta:
        verbose_name = 'Alternativa'
        verbose_name_plural = 'Alternativas'
        ordering = ['label']

    def __str__(self):
        return f'Alternativa {self.label} da Questão {self.question.id}'
