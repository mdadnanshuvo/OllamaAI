import pytest
from django.contrib.gis.geos import Point
from property_manager.models import Property, PropertySummary, PropertyRating

@pytest.mark.django_db
def test_property_model():
    property_obj = Property.objects.create(
        id="test-id",
        title="Test Property",
        rating=4.5,
        location="Test Location",
        latitude=12.34,
        longitude=56.78,
        geom=Point(12.34, 56.78),
        price="100",
        image_url="http://example.com/image.jpg",
        city_id="123",
        description="Test Description"
    )

    assert property_obj.title == "Test Property"
    assert property_obj.rating == 4.5
    assert property_obj.geom.x == 12.34
    assert property_obj.geom.y == 56.78

@pytest.mark.django_db
def test_property_summary_model():
    property_obj = Property.objects.create(id="test-id", title="Test Property")
    summary_obj = PropertySummary.objects.create(property=property_obj, summary="Test Summary")

    assert summary_obj.property.title == "Test Property"
    assert summary_obj.summary == "Test Summary"

@pytest.mark.django_db
def test_property_rating_model():
    property_obj = Property.objects.create(id="test-id", title="Test Property")
    rating_obj = PropertyRating.objects.create(property=property_obj, rating=4.5, review="Great property!")

    assert rating_obj.property.title == "Test Property"
    assert rating_obj.rating == 4.5
    assert rating_obj.review == "Great property!"
