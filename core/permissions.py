from core.errors import DomainError


def require_role(user, *roles):
    if user.role not in roles:
        raise DomainError("FORBIDDEN", "Your role cannot perform this action.", 403)
