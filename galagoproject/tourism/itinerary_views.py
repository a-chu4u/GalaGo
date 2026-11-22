
import json

from datetime import date, time
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Itinerary, TouristSpot


def serialize_plan(plan):
    return {
        "id": str(plan.pk),
        "spotId": str(plan.tourist_spot_id),
        "visitDate": plan.visit_date.isoformat(),
        "visitTime": (
            plan.visit_time.strftime("%H:%M")
            if plan.visit_time else ""
        ),
        "durationHours": (
            str(
                Decimal(plan.duration_minutes) / Decimal("60")
            )
            if plan.duration_minutes is not None else ""
        ),
        "estimatedCost": (
            str(plan.estimated_cost)
            if plan.estimated_cost is not None else ""
        ),
        "notes": plan.notes,
    }


def invalid(message):
    return None, JsonResponse(
        {"error": message},
        status=400
    )


def read_plan_data(request):
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return invalid("Invalid request data.")

    if not isinstance(data, dict):
        return invalid("Invalid request data.")

    spot_id = str(data.get("spotId", ""))

    if not spot_id.isdigit():
        return invalid("Please select a destination.")

    spot = TouristSpot.objects.filter(
        pk=int(spot_id)
    ).first()

    if spot is None:
        return invalid("Destination not found.")

    raw_date = data.get("visitDate", "")

    if not isinstance(raw_date, str):
        return invalid("Please select a valid visit date.")

    try:
        visit_date = date.fromisoformat(raw_date)
    except ValueError:
        return invalid("Please select a valid visit date.")

    raw_time = data.get("visitTime", "")

    if not isinstance(raw_time, str):
        return invalid("Invalid visit time.")

    visit_time = None

    if raw_time:
        try:
            visit_time = time.fromisoformat(raw_time)

            if (
                visit_time.tzinfo is not None
                or visit_time.second
                or visit_time.microsecond
            ):
                raise ValueError
        except ValueError:
            return invalid("Please enter a valid visit time.")

    raw_hours = data.get("durationHours", "")
    duration_minutes = None

    if raw_hours != "" and raw_hours is not None:
        if isinstance(raw_hours, bool):
            return invalid("Enter a valid duration in hours.")

        try:
            hours = Decimal(str(raw_hours))
        except (InvalidOperation, ValueError):
            return invalid("Enter a valid duration in hours.")

        if (
            not hours.is_finite()
            or hours <= 0
            or hours > 168
        ):
            return invalid(
                "Duration must be greater than 0 "
                "and no more than 168 hours."
            )

        minutes = hours * 60

        if minutes != minutes.to_integral_value():
            return invalid(
                "Duration must represent whole minutes."
            )

        duration_minutes = int(minutes)

    raw_cost = data.get("estimatedCost", "")
    estimated_cost = None

    if raw_cost != "" and raw_cost is not None:
        if isinstance(raw_cost, bool):
            return invalid("Enter a valid estimated cost.")

        try:
            estimated_cost = Decimal(str(raw_cost))
        except (InvalidOperation, ValueError):
            return invalid("Enter a valid estimated cost.")

        if (
            not estimated_cost.is_finite()
            or estimated_cost < 0
            or estimated_cost > Decimal("99999999.99")
        ):
            return invalid(
                "Estimated cost must be between "
                "₱0 and ₱99,999,999.99."
            )

        if estimated_cost.as_tuple().exponent < -2:
            return invalid(
                "Estimated cost may have at most two decimal places."
            )

    notes = data.get("notes", "")

    if not isinstance(notes, str) or len(notes) > 2000:
        return invalid(
            "Notes must be 2000 characters or fewer."
        )

    return {
        "tourist_spot": spot,
        "visit_date": visit_date,
        "visit_time": visit_time,
        "duration_minutes": duration_minutes,
        "estimated_cost": estimated_cost,
        "notes": notes.strip(),
    }, None


@login_required(login_url="login")
@ensure_csrf_cookie
def itinerary_page(request):
    spots = TouristSpot.objects.select_related(
        "category",
        "location"
    ).order_by("name")

    return render(
        request,
        "tourism/itinerary.html",
        {"spots": spots}
    )


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def itinerary_api(request):
    if request.method == "GET":
        plans = Itinerary.objects.filter(
            user=request.user
        ).order_by(
            "visit_date",
            "visit_time",
            "pk"
        )

        return JsonResponse({
            "plans": [
                serialize_plan(plan)
                for plan in plans
            ]
        })

    data, error = read_plan_data(request)

    if error is not None:
        return error

    plan = Itinerary.objects.create(
        user=request.user,
        **data
    )

    return JsonResponse(
        {"plan": serialize_plan(plan)},
        status=201
    )


@login_required(login_url="login")
@require_http_methods(["PUT", "DELETE"])
def itinerary_item_api(request, pk):
    plan = get_object_or_404(
        Itinerary,
        pk=pk,
        user=request.user
    )

    if request.method == "DELETE":
        plan.delete()

        return JsonResponse({"success": True})

    data, error = read_plan_data(request)

    if error is not None:
        return error

    for field, value in data.items():
        setattr(plan, field, value)

    plan.save()

    return JsonResponse({
        "plan": serialize_plan(plan)
    })
