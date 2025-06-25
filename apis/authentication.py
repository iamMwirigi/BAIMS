from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import AuthToken, AdminAuthToken, BaAuthToken, User, UAdmin, Ba

class TokenAuthentication(BaseAuthentication):
    """
    Custom authentication for User tokens.
    Expects Authorization header: "Token <token_key>"
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token_type, token_key = auth_header.split()
            if token_type.lower() != 'token':
                return None
        except ValueError:
            return None

        try:
            token = AuthToken.objects.select_related('user').get(key=token_key)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User account inactive.')

        return (token.user, token)

class AdminTokenAuthentication(BaseAuthentication):
    """
    Custom authentication for UAdmin tokens.
    Expects Authorization header: "Admin_Token <token_key>"
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token_type, token_key = auth_header.split()
            if token_type.lower() != 'admin_token':
                return None
        except ValueError:
            return None

        try:
            token = AdminAuthToken.objects.select_related('admin').get(key=token_key)
        except AdminAuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid admin token.')

        # Add any active status check for UAdmin if applicable
        # if not token.admin.is_active:
        #     raise AuthenticationFailed('Admin account inactive.')

        return (token.admin, token)

class BaTokenAuthentication(BaseAuthentication):
    """
    Custom authentication for BA tokens.
    Expects Authorization header: "Ba_Token <token_key>"
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token_type, token_key = auth_header.split()
            if token_type.lower() != 'ba_token':
                return None
        except ValueError:
            return None

        try:
            token = BaAuthToken.objects.select_related('ba').get(key=token_key)
        except BaAuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid BA token.')

        # Add any active status check for Ba if applicable
        # if not token.ba.is_active:
        #     raise AuthenticationFailed('BA account inactive.')

        return (token.ba, token)