from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet, ExamViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'exams', ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),
]
