
from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7
    )

    def __str__(self):
        return self.name


class TouristSpot(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT
    )

    image = models.ImageField(
        upload_to="tourist_spots/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Visitor(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    tourist_spot = models.ForeignKey(
        TouristSpot,
        on_delete=models.CASCADE
    )

    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        choices=[
            (i, str(i))
            for i in range(1, 6)
        ]
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.visitor.name} - "
            f"{self.tourist_spot.name}"
        )


class Favorite(models.Model):
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE
    )

    tourist_spot = models.ForeignKey(
        TouristSpot,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "visitor",
                    "tourist_spot"
                ],
                name="unique_visitor_favorite"
            )
        ]

    def __str__(self):
        return (
            f"{self.visitor.name} - "
            f"{self.tourist_spot.name}"
        )


class Itinerary(models.Model):
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="travel_plans"
    )

    tourist_spot = models.ForeignKey(
        TouristSpot,
        on_delete=models.CASCADE
    )

    visit_date = models.DateField()

    visit_time = models.TimeField(
        null=True,
        blank=True
    )

    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        if self.user_id:
            owner = self.user.username
        elif self.visitor_id:
            owner = self.visitor.name
        else:
            owner = "Unknown"

        return (
            f"{owner} - "
            f"{self.tourist_spot.name}"
        )
