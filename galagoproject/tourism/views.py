
import json
import os
import math

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import TouristSpot, Category, Visitor, Review
from .forms import VisitorReviewForm


# ==========================================
# HOME PAGE
# ==========================================

def home(request):
    spots = TouristSpot.objects.select_related(
        "category",
        "location"
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
        spots = spots.filter(
            category_id=int(category_id)
        )

    return render(
        request,
        "tourism/home.html",
        {
            "spots": spots,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
            "spot_count": TouristSpot.objects.count(),
        }
    )


# ==========================================
# OPEN-METEO WEATHER API
# ==========================================

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
        HTTPError,
        URLError,
        TimeoutError,
        ValueError,
        OSError,
    ):
        return None


# ==========================================
# TOURIST SPOT DETAIL PAGE
# ==========================================

def spot_detail(request, pk):

    spot = get_object_or_404(
        TouristSpot.objects.select_related(
            "category",
            "location"
        ),
        pk=pk,
    )

    # Handle visitor review submissions.
    if request.method == "POST":

        form = VisitorReviewForm(request.POST)

        if form.is_valid():

            visitor, created = Visitor.objects.get_or_create(
                email=form.cleaned_data["email"],
                defaults={
                    "name": form.cleaned_data["name"]
                }
            )

            Review.objects.create(
                tourist_spot=spot,
                visitor=visitor,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )

            # Remember successful submission for next page load.
            request.session["review_submitted_spot"] = spot.pk

            messages.success(
                request,
                "Thank you! Your review has been submitted."
            )

            return redirect(
                "spot_detail",
                pk=spot.pk
            )

    else:
        form = VisitorReviewForm()

    # Retrieve reviews.
    reviews = spot.review_set.select_related(
        "visitor"
    ).order_by("-created_at")

    # Calculate average rating.
    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    # Retrieve weather.
    weather = get_weather(
        float(spot.location.latitude),
        float(spot.location.longitude),
    )

    # Hide form only after a successful submission.
    review_submitted = (
        request.session.pop("review_submitted_spot", None)
        == spot.pk
    )

    return render(
        request,
        "tourism/spot_detail.html",
        {
            "spot": spot,
            "reviews": reviews,
            "average_rating": average_rating,
            "weather": weather,
            "review_form": form,
            "review_submitted": review_submitted,
        }
    )


# ==========================================
# OPENROUTESERVICE DIRECTIONS API
# ==========================================

@require_POST
def calculate_route(request, pk):

    spot = get_object_or_404(
        TouristSpot.objects.select_related("location"),
        pk=pk,
    )

    api_key = os.environ.get(
        "OPENROUTESERVICE_API_KEY",
        ""
    ).strip()

    if not api_key:
        return JsonResponse(
            {
                "error": (
                    "OpenRouteService API key is missing. "
                    "Check your .env file."
                )
            },
            status=503
        )

    try:
        body = json.loads(request.body)

        start_latitude = float(body["latitude"])
        start_longitude = float(body["longitude"])

        if not (
            math.isfinite(start_latitude)
            and math.isfinite(start_longitude)
        ):
            raise ValueError("Invalid coordinates")

        if not (-90 <= start_latitude <= 90):
            raise ValueError("Invalid latitude")

        if not (-180 <= start_longitude <= 180):
            raise ValueError("Invalid longitude")

    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError,
    ):
        return JsonResponse(
            {
                "error": (
                    "Invalid starting location. "
                    "Please select a point on the map."
                )
            },
            status=400
        )

    destination_latitude = float(
        spot.location.latitude
    )

    destination_longitude = float(
        spot.location.longitude
    )

    payload = {
        "coordinates": [
            [start_longitude, start_latitude],
            [destination_longitude, destination_latitude]
        ]
    }

    url = (
        "https://api.openrouteservice.org"
        "/v2/directions/driving-car/geojson"
    )

    api_request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/geo+json",
        },
        method="POST"
    )

    try:
        with urlopen(
            api_request,
            timeout=15
        ) as response:
            route_data = json.load(response)

        features = route_data.get("features", [])

        if not features:
            return JsonResponse(
                {
                    "error": (
                        "No driving route was found "
                        "between these locations."
                    )
                },
                status=404
            )

        feature = features[0]

        properties = feature.get("properties", {})
        summary = properties.get("summary", {})
        geometry = feature.get("geometry")

        if not geometry:
            return JsonResponse(
                {
                    "error": "Route geometry is unavailable."
                },
                status=502
            )

        distance_meters = summary.get("distance", 0)
        duration_seconds = summary.get("duration", 0)

        return JsonResponse(
            {
                "geometry": geometry,
                "distance_km": round(
                    distance_meters / 1000,
                    2
                ),
                "duration_minutes": round(
                    duration_seconds / 60
                ),
            }
        )

    except HTTPError as error:

        print(
            "OpenRouteService HTTP status:",
            error.code
        )

        error_response = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print(
            "OpenRouteService response:",
            error_response
        )

        if error.code in (401, 403):
            message = (
                "Route service authorization failed. "
                "Please check your API key."
            )
            status_code = 502

        elif error.code in (400, 404):
            message = (
                "No driving route is available "
                "between these locations. "
                "The destination may require "
                "boat travel or may not be "
                "connected to a road."
            )
            status_code = 404

        elif error.code == 429:
            message = (
                "Route service request limit reached. "
                "Please try again later."
            )
            status_code = 503

        else:
            message = (
                "Route service is temporarily unavailable."
            )
            status_code = 502

        return JsonResponse(
            {
                "error": message
            },
            status=status_code
        )

    except (
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:

        print(
            "OpenRouteService connection error:",
            type(error).__name__
        )

        return JsonResponse(
            {
                "error": (
                    "Unable to calculate the route. "
                    "Please try again later."
                )
            },
            status=502
        )
