from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import LoginSession


class IdleJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        session = LoginSession.objects.filter(pk=token.get("sid"), user=user, active=True).first()
        if (
            not session
            or session.last_seen + timedelta(seconds=settings.SESSION_COOKIE_AGE) <= timezone.now()
        ):
            raise AuthenticationFailed("Session expired. Sign in again.")
        LoginSession.objects.filter(pk=session.pk).update(last_seen=timezone.now())
        return user, token
