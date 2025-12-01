from rest_framework import serializers
from .models import DailyChecking

class DailyCheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyChecking
        fields = ('id', 'feeling','index', 'question', 'answer', 'created_at')
        read_only_fields = ('id','index', 'created_at')

    def create(self, validated_data):
        # Automatically associate the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
