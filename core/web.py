from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from core.errors import DomainError
from accounts.services import authenticate


@ensure_csrf_cookie
def signin(request):
    if request.user.is_authenticated:
        return redirect("/")
    error = ""
    if request.method == "POST":
        try:
            user, _ = authenticate(request.POST.get("institute_id"), request.POST.get("password"))
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
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
    logout(request)
    return redirect("/login/")


@ensure_csrf_cookie
def reset_password(request):
    return render(request, "reset.html", {"token": request.GET.get("token", "")})
