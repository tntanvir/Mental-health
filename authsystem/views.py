from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .serializers import UserRegistrationSerializer, UserSerializer, UserProfileUpdateSerializer

from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

class UserProfileUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            # profile_done is updated in User.save()
            
            # Return full user data
            user_serializer = UserSerializer(user)
            return Response({
                'message': 'Profile updated successfully',
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and Send OTP
            otp = user.generate_otp()
            
            subject = 'Verify your account'
            html_message = render_to_string('authsystem/otp_email.html', {'otp': otp})
            plain_message = strip_tags(html_message)
            from_email = 'noreply@mentalhealth.com'
            to = user.email

            send_mail(
                subject,
                plain_message,
                from_email,
                [to],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({"message": "OTP sent to email. Please verify."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({'error': 'Please provide email and OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if user.is_otp_valid(otp):
            user.is_active = True
            user.otp = None # Clear OTP after successful verification
            user.save()
            
            # Login the user
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'message': 'Verification successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tokenr  = request.data.get('token')
        if tokenr:
            try:
                token = RefreshToken(tokenr)
                token.blacklist()
                logout(request)
                return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                 return Response({'error': 'Account is inactive. Please verify OTP.'}, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_serializer.data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomSocialLoginView(SocialLoginView):
    def get_response(self):
        # This method is called by SocialLoginView after successful login
        # We override it to return our custom response format
        user = self.user
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

class GoogleLogin(CustomSocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

class AppleLogin(CustomSocialLoginView):
    adapter_class = AppleOAuth2Adapter
    client_class = OAuth2Client

class AccountInactiveView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response({"error": "Account is inactive. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)

class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response( user_serializer.data, status=status.HTTP_200_OK)
    