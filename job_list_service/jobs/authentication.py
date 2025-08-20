from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests
import logging

logger = logging.getLogger(__name__)  # Logging for debugging

class AuthenticatedUser:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.is_authenticated = True

    def __str__(self):
        return self.email or "AuthenticatedUser"

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("Authorization header missing")
            raise AuthenticationFailed('Authorization header missing')

        try:
            res = requests.get(
                #"http://account_service:8000/api/auth/me/",  # Docker service name
                "http://https://jobjourney.ddns.net/auth/api/auth/me/",
                headers={'Authorization': auth_header},
                timeout=3
            )
            res.raise_for_status()
            user_data = res.json().get('data')
            if not user_data:
                logger.warning(f"No user data returned for token: {auth_header}")
                raise AuthenticationFailed('User data not found in auth service response')

            logger.info(f"User authenticated successfully: {user_data.get('email')}")
            return (AuthenticatedUser(user_data), None)

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error from auth service: {http_err}")
            raise AuthenticationFailed(f'HTTP error from auth service: {http_err}')
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Auth service unreachable: {req_err}")
            raise AuthenticationFailed(f'Auth service unreachable: {req_err}')

