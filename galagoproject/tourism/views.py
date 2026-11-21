
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

    return render(
        request,
        "tourism/spot_detail.html",
        {
            "spot": spot,
            "reviews": reviews,
            "average_rating": average_rating,
        },
    )
