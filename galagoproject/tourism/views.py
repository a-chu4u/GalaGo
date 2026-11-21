
import json
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg

from .models import TouristSpot, Category


def home(request):
    spots = TouristSpot.objects.select_related(
        "category", "location"
    ).order_by("-created_at")

    categories = Category.objects.all().order_by("name")

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    if query:
        spots = spots.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(location__name__icontains=query)
            | Q(location__address__icontains=query)
        )

    if category_id.isdigit():
        spots = spots.filter(category_id=int(category_id))

    return render(
        request,
        "tourism/home.html",
        {
            "spots": spots,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
            "spot_count": TouristSpot.objects.count(),
        },
    )


def get_weather(latitude, longitude):
    parameters = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "Asia/Manila",
    })

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + parameters
    )

    try:
        with urlopen(url, timeout=8) as response:
            data = json.load(response)

        current = data.get("current", {})

        if not current:
            return None

        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Heavy drizzle",
            61: "Light rain",
            63: "Rain",
            65: "Heavy rain",
            80: "Rain showers",
            81: "Rain showers",
            82: "Heavy showers",
            95: "Thunderstorm",
            96: "Thunderstorm",
            99: "Thunderstorm",
        }

        code = current.get("weather_code")

        return {
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "description": weather_codes.get(
                code,
                "Weather information"
            ),
            "updated_at": current.get("time"),
        }

    except (
        URLError,
        HTTPError,
        TimeoutError,
        ValueError,
        KeyError,
        OSError,
    ):
        return None


def spot_detail(request, pk):
    spot = get_object_or_404(
        TouristSpot.objects.select_related(
            "category", "location"
        ),
        pk=pk,
    )

    reviews = spot.review_set.select_related(
        "visitor"
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    weather = get_weather(
        float(spot.location.latitude),
        float(spot.location.longitude),
    )

    return render(
        request,
        "tourism/spot_detail.html",
        {
            "spot": spot,
            "reviews": reviews,
            "average_rating": average_rating,
            "weather": weather,
        },
    )
