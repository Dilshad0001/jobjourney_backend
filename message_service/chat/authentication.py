
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
import requests

class AuthenticatedUser:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.is_authenticated = True  # 👈 THIS is key!

    def __str__(self):
        return self.email or "AuthenticatedUser"

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed('Authorization header missing')

        try:
            res = requests.get(
                "http://51.21.215.128/auth/api/auth/me/",
                headers={'Authorization': auth_header},
                timeout=3
            )
            if res.status_code != 200:
                raise AuthenticationFailed(f'Invalid tokensss, status={res.status_code}, token={auth_header}')
            user_data = res.json()
            actual_user_data = user_data.get('data')

            return (AuthenticatedUser(actual_user_data), None)
        except requests.exceptions.RequestException:
            raise AuthenticationFailed('Auth service unreachable')
