from django.urls import path
from .views import DailyCheckingListCreateView, DailyCheckingDetailView,QuestionSuggestionView

urlpatterns = [
    path('daily-checking/', DailyCheckingListCreateView.as_view(), name='daily_checking_list_create'),
    path('daily-checking/<int:pk>/', DailyCheckingDetailView.as_view(), name='daily_checking_detail'),
    path('ai_questions',QuestionSuggestionView.as_view(), name='question_suggestion')
]
