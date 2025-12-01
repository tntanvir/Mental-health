from django.contrib import admin
from .models import DailyChecking

@admin.register(DailyChecking)
class DailyCheckingAdmin(admin.ModelAdmin):
    list_display = ('user', 'feeling', 'created_at')
    list_filter = ('feeling', 'created_at')
    search_fields = ('user__email', 'question', 'answer')
