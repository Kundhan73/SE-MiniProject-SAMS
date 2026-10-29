import hashlib
import logging
import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from core.errors import DomainError
from .models import User, LoginSession, ResetToken

logger = logging.getLogger(__name__)


# Counters commit before an authentication error is raised.
def authenticate(institute_id, password):
    if not institute_id or not password:
        raise DomainError("REQUIRED_FIELDS", "Institute ID and password are required.")
    with transaction.atomic():
        user = User.objects.select_for_update().filter(username=institute_id).first()
        if user and user.locked_until and user.locked_until > timezone.now():
            raise DomainError("ACCOUNT_LOCKED", "Account locked for 15 minutes.", 423)
        if user and user.locked_until:
            user.failed_attempts = 0
            user.locked_until = None
        valid = bool(user and user.check_password(password) and user.is_active)
        if user and not valid:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = timezone.now() + timedelta(minutes=15)
                logger.warning("Account lockout user_id=%s", user.pk)
            user.save(update_fields=["failed_attempts", "locked_until"])
        elif user:
            user.failed_attempts = 0
            user.locked_until = None
            user.save(update_fields=["failed_attempts", "locked_until"])
        else:
            User().set_password(password)  # Match password hashing work for unknown accounts.
    if not valid:
        raise DomainError("INVALID_CREDENTIALS", "Invalid ID or password.", 401)
    login_session = LoginSession.objects.create(user=user)
    token = RefreshToken.for_user(user)
    token["sid"] = str(login_session.pk)
    return user, {
        "access": str(token.access_token),
        "refresh": str(token),
        "role": user.role,
        "name": user.get_full_name() or user.username,
    }


def request_reset(email):
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user:
        raw = secrets.token_urlsafe(32)
        ResetToken.objects.create(
            user=user,
            digest=hashlib.sha256(raw.encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=30),
        )
        from notifications.tasks import send_reset

        send_reset.delay(user.email, f"{settings.PUBLIC_URL}/reset/?token={raw}")
    return {"message": "If the account exists, a link has been sent."}


@transaction.atomic
def confirm_reset(token, new_password):
    item = (
        ResetToken.objects.select_for_update()
        .filter(digest=hashlib.sha256(token.encode()).hexdigest())
        .first()
    )
    if not item or item.used or item.expires_at <= timezone.now():
        raise DomainError("TOKEN_EXPIRED_OR_USED", "Reset link expired or already used.", 410)
    validate_password(new_password, item.user)
    item.user.set_password(new_password)
    item.user.failed_attempts = 0
    item.user.locked_until = None
    item.user.save()
    item.used = True
    item.save(update_fields=["used"])
    LoginSession.objects.filter(user=item.user).update(active=False)
