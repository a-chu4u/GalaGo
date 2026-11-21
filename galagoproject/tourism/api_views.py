
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import (
    Category,
    Location,
    TouristSpot,
    Visitor,
    Review,
    Favorite,
    Itinerary,
)

from .serializers import (
    CategorySerializer,
    LocationSerializer,
    TouristSpotSerializer,
    VisitorSerializer,
    ReviewSerializer,
    FavoriteSerializer,
    ItinerarySerializer,
)


class AdminWriteViewSet(viewsets.ModelViewSet):
    """
    CRUD API for authenticated Django staff.

    Visitors can read public destination information
    through the public viewsets below.
    """

    permission_classes = [IsAdminUser]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdminUser]


class TouristSpotViewSet(viewsets.ModelViewSet):
    queryset = TouristSpot.objects.all()
    serializer_class = TouristSpotSerializer
    permission_classes = [IsAdminUser]


class VisitorViewSet(AdminWriteViewSet):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer


class ReviewViewSet(AdminWriteViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class FavoriteViewSet(AdminWriteViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ItineraryViewSet(AdminWriteViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
