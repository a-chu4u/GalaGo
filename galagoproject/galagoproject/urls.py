
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from tourism import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path(
        "spots/<int:pk>/",
        views.spot_detail,
        name="spot_detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
