
from django.shortcuts import render

from .models import TouristSpot


def itinerary_page(request):
    spots = TouristSpot.objects.select_related(
        "category",
        "location"
    ).order_by("name")

    return render(
        request,
        "tourism/itinerary.html",
        {
            "spots": spots
        }
    )
