from rest_framework import serializers

from .models import Question, Exam


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'number', 'text', 'alternatives', 'correct_answer',
            'comment', 'banca', 'year', 'organization', 'position',
            'subject', 'topic', 'exam_url', 'source_url', 'created_at'
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'number', 'banca', 'year', 'organization',
            'position', 'subject', 'created_at'
        ]


class ExamSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'year', 'banca', 'organization', 'institution',
            'level', 'page_url', 'exam_url', 'answer_key_url',
            'questions_count', 'created_at'
        ]

    def get_questions_count(self, obj):
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'year', 'banca', 'organization', 'institution',
            'level', 'page_url', 'exam_url', 'answer_key_url',
            'questions', 'created_at', 'updated_at'
        ]
