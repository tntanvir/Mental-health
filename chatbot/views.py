from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage, ChatSession
from .serializers import ChatMessageSerializer, ChatSessionSerializer
import sys
import os
import json

# Ensure we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend_interface import process_chat_message

class ChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        title = request.data.get('title', 'New Chat')
        session = ChatSession.objects.create(user=request.user, title=title)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return ChatSession.objects.get(pk=pk, user=user)
        except ChatSession.DoesNotExist:
            return None

    def get(self, request, pk):
        session = self.get_object(pk, request.user)
        if not session:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        session = self.get_object(pk, request.user)
        if not session:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        user_input = request.data.get('message')
        if not user_input:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Build history from this session
        previous_messages = session.messages.order_by('created_at')
        history = []
        for msg in previous_messages:
            history.append({"role": "user", "content": msg.user_input})
            history.append({"role": "assistant", "content": msg.bot_response})

        # Get location
        location = request.data.get('location')
        if not location and hasattr(request.user, 'country'):
            location = request.user.country

        # Process message
        try:
            bot_response = process_chat_message(user_input, history=history, location=location)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save to DB
        chat_message = ChatMessage.objects.create(
            session=session,
            user_input=user_input,
            bot_response=bot_response
        )
        
        # Update session timestamp
        session.save() # Updates updated_at

        serializer = ChatMessageSerializer(chat_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
