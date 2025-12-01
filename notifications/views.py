
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer
# from .pagination import NotificationPagination
# from villas.views import StandardResultsSetPagination


class NotificationList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user

        # ===== Single Notification Read =====
        if pk:
            try:
                notification = Notification.objects.get(user=user, id=pk)
            except Notification.DoesNotExist:
                return Response({"error": "Notification not found"}, status=404)

            notification.is_read = True
            notification.save()

            return Response({
                "notification": NotificationSerializer(notification).data,
                "message": "Notification marked as read"
            }, status=status.HTTP_200_OK)

        # ===== All Notifications with Pagination =====
        notifications = Notification.objects.filter(user=user).order_by('-id')

        # paginator = StandardResultsSetPagination()
        # paginated_qs = paginator.paginate_queryset(notifications, request)

        response_data = {
            "unseen_count": notifications.filter(is_read=False).count(),
            "notifications": NotificationSerializer(notifications, many=True).data
        }

        # return paginator.get_paginated_response(response_data)
        return Response(response_data, status=status.HTTP_200_OK)
