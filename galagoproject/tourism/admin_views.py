
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

from .models import (
    Category,
    Location,
    TouristSpot,
    Visitor,
    Review,
    Favorite,
    Itinerary,
)


# ==========================================
# ADMIN PERMISSION CHECK
# ==========================================

def is_admin(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.is_superuser
    )


# ==========================================
# ADMIN LOGIN
# ==========================================

@never_cache
def admin_login(request):

    # Already logged-in administrators
    # go directly to the dashboard.
    if is_admin(request.user):
        return redirect("admin_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username", ""
        ).strip()

        password = request.POST.get(
            "password", ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and is_admin(user):

            login(request, user)

            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid administrator credentials."
        )

    return render(
        request,
        "tourism/admin_login.html"
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@user_passes_test(
    is_admin,
    login_url="admin_login"
)
@never_cache
def admin_dashboard(request):

    context = {
        "category_count": Category.objects.count(),
        "location_count": Location.objects.count(),
        "spot_count": TouristSpot.objects.count(),
        "visitor_count": Visitor.objects.count(),
        "review_count": Review.objects.count(),
        "favorite_count": Favorite.objects.count(),
        "itinerary_count": Itinerary.objects.count(),
    }

    return render(
        request,
        "tourism/admin_dashboard.html",
        context
    )


# ==========================================
# ADMIN LOGOUT
# ==========================================

@require_POST
@never_cache
def admin_logout(request):

    logout(request)

    return redirect("admin_login")
