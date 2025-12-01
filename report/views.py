from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from daily_checking.models import DailyChecking
from collections import defaultdict
import datetime

class MonthlyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get month and year from query params, default to current
        now = timezone.now()
        user =request.user
        try:
            month = int(request.query_params.get('month', now.month))
            year = int(request.query_params.get('year', now.year))
        except ValueError:
            return Response({"error": "Invalid month or year"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter checkings for the user and specific month
        checkings = DailyChecking.objects.filter(
            user=request.user,
            created_at__year=year,
            created_at__month=month
        )

        # Initialize report structure
        report = {
            "month": month,
            "year": year,
            "weeks": {
                "week_1": {"points": 0, "feelings": defaultdict(int)},
                "week_2": {"points": 0, "feelings": defaultdict(int)},
                "week_3": {"points": 0, "feelings": defaultdict(int)},
                "week_4": {"points": 0, "feelings": defaultdict(int)},
            },
            'other':{
                "stack": user.current_stack,
                "avarage":user.total_checking / 10,
                "checking":user.total_checking
            }
        }

        for checking in checkings:
            day = checking.created_at.day
            points = checking.index if checking.index is not None else 0
            feeling = checking.feeling

            if 1 <= day <= 7:
                week_key = "week_1"
            elif 8 <= day <= 14:
                week_key = "week_2"
            elif 15 <= day <= 21:
                week_key = "week_3"
            else:
                week_key = "week_4"

            report["weeks"][week_key]["points"] += points
            report["weeks"][week_key]["feelings"][feeling] += 1

        # Convert defaultdict to dict for JSON serialization
        for week in report["weeks"]:
            report["weeks"][week]["feelings"] = dict(report["weeks"][week]["feelings"])

        return Response(report)
