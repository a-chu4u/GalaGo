
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
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
    created_at = models.DateTimeField(auto_now_add=True)

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
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor.name} - {self.tourist_spot.name}"


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
                fields=["visitor", "tourist_spot"],
                name="unique_visitor_favorite"
            )
        ]

    def __str__(self):
        return f"{self.visitor.name} - {self.tourist_spot.name}"


class Itinerary(models.Model):
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE
    )
    tourist_spot = models.ForeignKey(
        TouristSpot,
        on_delete=models.CASCADE
    )
    visit_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.visitor.name} - {self.tourist_spot.name}"
