from rest_framework import authentication
from rest_framework import exceptions
from .models import AuthToken, UAdmin, AdminAuthToken
from rest_framework.authentication import get_authorization_header

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
        auth_header = get_authorization_header(request).decode('utf-8')
        if not auth_header or not auth_header.startswith('AdminToken '):
            return None
        key = auth_header.split(' ')[1]
        try:
            token = AdminAuthToken.objects.select_related('admin').get(key=key)
        except AdminAuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid admin token.')
        # Attach a flag to the user object to indicate admin
        admin = token.admin
        admin.is_superuser = True  # This can be checked in permissions if needed
        return (admin, token) 