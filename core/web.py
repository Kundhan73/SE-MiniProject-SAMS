from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from core.errors import DomainError
from accounts.services import authenticate
from accounts.models import LoginSession
from rest_framework_simplejwt.tokens import RefreshToken


@ensure_csrf_cookie
def signin(request):
    if request.user.is_authenticated:
        return redirect("/")
    error = ""
    if request.method == "POST":
        try:
            user, tokens = authenticate(
                request.POST.get("institute_id"), request.POST.get("password")
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session["jwt_session_id"] = RefreshToken(tokens["refresh"])["sid"]
            return redirect("/")
        except DomainError as exc:
            error = exc.detail["message"]
    return render(request, "login.html", {"error": error})


@login_required(login_url="/login/")
@ensure_csrf_cookie
def dashboard(request):
    return render(request, "dashboard.html")


@require_POST
def signout(request):
    sid = request.session.get("jwt_session_id")
    if sid and request.user.is_authenticated:
        LoginSession.objects.filter(pk=sid, user=request.user).update(active=False)
    logout(request)
    return redirect("/login/")


@ensure_csrf_cookie
def reset_password(request):
    return render(request, "reset.html", {"token": request.GET.get("token", "")})
