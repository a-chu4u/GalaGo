
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from tourism import views
from tourism import api_views
from tourism import admin_views
from tourism import itinerary_views


router = DefaultRouter()

router.register(
    r"categories",
    api_views.CategoryViewSet
)

router.register(
    r"locations",
    api_views.LocationViewSet
)

router.register(
    r"spots",
    api_views.TouristSpotViewSet
)

router.register(
    r"visitors",
    api_views.VisitorViewSet
)

router.register(
    r"reviews",
    api_views.ReviewViewSet
)

router.register(
    r"favorites",
    api_views.FavoriteViewSet
)

router.register(
    r"itineraries",
    api_views.ItineraryViewSet
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "favorites/",
        views.home,
        name="favorites"
    ),

    path(
        "itinerary/",
        itinerary_views.itinerary_page,
        name="itinerary"
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

    path(
        "api/",
        include(router.urls)
    ),

    path(
        "api-auth/",
        include("rest_framework.urls")
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
