from rest_framework.throttling import ScopedRateThrottle
from django.core.cache import cache


class ResendVerificationThrottle(ScopedRateThrottle):
    scope = 'resend_verification'
    
    def get_cache_key(self, request, view):
        email = request.data.get('email', '').strip().lower()
        if email:
            return f'throttle_resend_{email}'
        return None
    def allow_request(self, request, view):
        if self.get_cache_key(request, view):
            return True
        return super().allow_request(request, view)