import uuid
from django.contrib.gis.db import models  # For geospatial data support


class Property(models.Model):
    """
    Represents a property with its basic details.
    """
    id = models.CharField(max_length=255, primary_key=True)  # Matches your existing UUID primary key
    title = models.CharField(max_length=255, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    geom = models.PointField(null=True, blank=True, srid=4326)  # Spatial data for geolocation
    price = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    city_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # New field for the property description
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or "Untitled Property"


class PropertySummary(models.Model):
    """
    Stores a summary for each property.
    """
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='summary')
    summary = models.TextField()

    def __str__(self):
        return f"Summary for {self.property.title}"


class PropertyRating(models.Model):
    """
    Stores ratings and reviews for properties.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField()
    review = models.TextField()

    def __str__(self):
        return f"Rating for {self.property.title} ({self.rating})"
