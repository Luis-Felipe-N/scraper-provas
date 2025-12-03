from django.contrib import admin

from .models import Question, Exam


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'banca', 'year',
                    'organization', 'subject', 'correct_answer', 'created_at']
    list_filter = ['banca', 'year', 'subject', 'organization']
    search_fields = ['text', 'organization', 'position', 'topic']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'banca', 'year',
                    'organization', 'level', 'created_at']
    list_filter = ['banca', 'year', 'level']
    search_fields = ['name', 'organization', 'institution']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['questions']
