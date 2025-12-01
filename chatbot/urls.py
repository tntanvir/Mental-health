from django.urls import path
from .views import ChatSessionView, ChatSessionDetailView, ChatView

urlpatterns = [
    path('sessions/', ChatSessionView.as_view(), name='chat_session_list_create'),
    path('sessions/<int:pk>/', ChatSessionDetailView.as_view(), name='chat_session_detail'),
    path('sessions/<int:session_id>/message/', ChatView.as_view(), name='chat_message_create'),
]
