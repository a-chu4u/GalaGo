
from django.contrib import admin

from .models import (
    Category,
    Location,
    TouristSpot,
    Visitor,
    Review,
    Favorite,
    Itinerary,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "latitude", "longitude")
    search_fields = ("name", "address")


@admin.register(TouristSpot)
class TouristSpotAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "location", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name", "email")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "tourist_spot", "visitor", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "visitor", "tourist_spot")


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ("id", "visitor", "tourist_spot", "visit_date")
    list_filter = ("visit_date",)
