from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'image', 'gender', 'country', 'plan', 'profile_done', 'current_feel', 'checking_time','avarage' ,'notifications', 'current_stack','last_stack_date' ,'total_checking')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        if 'name' not in validated_data or not validated_data['name']:
            validated_data['name'] = "New User"
            
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            image=validated_data.get('image'),
            gender=validated_data.get('gender'),
            country=validated_data.get('country', '')
        )
        return user

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'gender', 'country', 'image','checking_time')
