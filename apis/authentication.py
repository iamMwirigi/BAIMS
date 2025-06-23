from rest_framework import authentication
from rest_framework import exceptions
from .models import AuthToken, UAdmin, AdminAuthToken

class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Token '):
            return None

        key = auth_header.split(' ')[1]

        # Find the token in the database
        try:
            token = AuthToken.objects.select_related('user').get(key=key)
        except AuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (token.user, token) 

class AdminTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('AdminToken '):
            return None

        key = auth_header.split(' ')[1]

        # Find the token in the database
        try:
            token = AdminAuthToken.objects.select_related('admin').get(key=key)
        except AdminAuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid admin token.')

        return (token.admin, token) 