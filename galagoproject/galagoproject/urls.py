
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from tourism import views
from tourism import api_views
from tourism import admin_views
from tourism import itinerary_views
from tourism import auth_views


router = DefaultRouter()

router.register("categories", api_views.CategoryViewSet)
router.register("locations", api_views.LocationViewSet)
router.register("spots", api_views.TouristSpotViewSet)
router.register("visitors", api_views.VisitorViewSet)
router.register("reviews", api_views.ReviewViewSet)
router.register("favorites", api_views.FavoriteViewSet)
router.register("itineraries", api_views.ItineraryViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    path(
        "favorites/",
        login_required(views.home, login_url="login"),
        name="favorites"
    ),

    path(
        "itinerary/",
        itinerary_views.itinerary_page,
        name="itinerary"
    ),

    path(
        "itinerary/data/",
        itinerary_views.itinerary_api,
        name="itinerary_api"
    ),

    path(
        "itinerary/data/<int:pk>/",
        itinerary_views.itinerary_item_api,
        name="itinerary_item_api"
    ),

    path(
        "spots/<int:pk>/",
        views.spot_detail,
        name="spot_detail"
    ),

    path(
        "spots/<int:pk>/route/",
        views.calculate_route,
        name="calculate_route"
    ),

    path(
        "register/",
        auth_views.register_view,
        name="register"
    ),

    path(
        "login/",
        auth_views.login_view,
        name="login"
    ),

    path(
        "logout/",
        auth_views.logout_view,
        name="logout"
    ),

    path(
        "admin-login/",
        admin_views.admin_login,
        name="admin_login"
    ),

    path(
        "dashboard/",
        admin_views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "admin-logout/",
        admin_views.admin_logout,
        name="admin_logout"
    ),

    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
