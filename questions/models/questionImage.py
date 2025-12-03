class QuestionImage(models.Model):
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Questão'
    )
    image_url = models.ImageField(
        upload_to='question_images/', verbose_name='Imagem')

    class Meta:
        verbose_name = 'Imagem da Questão'
        verbose_name_plural = 'Imagens das Questões'

    def __str__(self):
        return f'Imagem da Questão {self.question.id}'
