from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

class BlacklistJWTCookieAuthentication(JWTCookieAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token['jti']
        if BlacklistedToken.objects.filter(token__jti=jti).exists():
            raise InvalidToken('Token is blacklisted')
        return token
