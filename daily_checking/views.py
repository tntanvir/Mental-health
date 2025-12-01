from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import DailyChecking
from .serializers import DailyCheckingSerializer
from backend_interface import generate_journal_prompts
from django.utils import timezone
import json

class DailyCheckingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        checkings = DailyChecking.objects.filter(user=request.user).order_by('-created_at')
        serializer = DailyCheckingSerializer(checkings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DailyCheckingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.save()
            user = request.user
            data.user = user
            data.save()
            user.current_feel = data.feeling
            user.total_checking += 1
            from datetime import timedelta
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)

            if user.last_stack_date:
                if user.last_stack_date == yesterday:
                    user.current_stack += 1
                    user.last_stack_date = today
                elif user.last_stack_date < yesterday:
                    user.current_stack = 1
                    user.last_stack_date = today
                # If last_stack_date == today, do nothing
            else:
                user.current_stack = 1
                user.last_stack_date = today
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DailyCheckingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return DailyChecking.objects.get(pk=pk, user=user)
        except DailyChecking.DoesNotExist:
            return None

    def get(self, request, pk):
        checking = self.get_object(pk, request.user)
        if not checking:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DailyCheckingSerializer(checking)
        return Response(serializer.data)

    def put(self, request, pk):
        checking = self.get_object(pk, request.user)
        if not checking:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DailyCheckingSerializer(checking, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        checking = self.get_object(pk, request.user)
        if not checking:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        checking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class QuestionSuggestionView(APIView):

    def post(self, request):
        data = request.data.get('feelings')
        if data:
            ai = generate_journal_prompts(data)
            data = json.loads(ai)
            return Response(data, status=status.HTTP_200_OK)
        return Response({'error': 'No feelings provided'}, status=status.HTTP_400_BAD_REQUEST)