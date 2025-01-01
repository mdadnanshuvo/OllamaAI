import pytest
from unittest.mock import patch, MagicMock
from property_manager.models import Property, PropertySummary, PropertyRating
from property_manager.management.commands.generate_data import Command

@pytest.fixture
def command():
    """Fixture for the Command class instance."""
    return Command()

@pytest.fixture
def mock_parse_data():
    """Fixture to mock parsed data from the SQL file."""
    return [
        {
            'id': '1',
            'title': None,
            'rating': 4.5,
            'location': 'Test Location',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'geom': 'POINT(-74.0060 40.7128)',
            'price': '100.00',
            'image_url': 'http://example.com/image.jpg',
            'city_id': '123',
            'description': None,
            'reviews': None,
        }
    ]

@pytest.mark.django_db
@patch('property_manager.management.commands.generate_data.Command.generate_text_with_retry')
@patch('property_manager.management.commands.generate_data.Command.import_parse_function')
def test_handle(mock_import_parse_function, mock_generate_text_with_retry, command, mock_parse_data):
    """Test the handle method."""
    # Mock the parse function to return mock data
    mock_import_parse_function.return_value = lambda: mock_parse_data

    # Mock the Gemini API calls to return test strings
    mock_generate_text_with_retry.side_effect = lambda *args, **kwargs: "Generated text"

    # Call the handle method
    command.handle()

    # Assert the property was created
    property_instance = Property.objects.get(id='1')
    assert property_instance.title == "Generated text"
    assert property_instance.rating == 4.5
    assert property_instance.location == "Test Location"
    assert property_instance.description == "Generated text"

    # Assert that the summary was created
    summary_instance = PropertySummary.objects.get(property=property_instance)
    assert summary_instance.summary == "Generated text"

    # Assert that the rating and review were created
    rating_instance = PropertyRating.objects.get(property=property_instance)
    assert rating_instance.review == "Generated text"
    assert rating_instance.rating == 4.5

@pytest.mark.django_db
@patch('property_manager.management.commands.generate_data.Command.generate_text_with_retry')
def test_generate_review_based_on_rating(mock_generate_text_with_retry, command):
    """Test review generation based on rating."""
    mock_generate_text_with_retry.return_value = "Generated Review"
    review = command.generate_review_based_on_rating(4.5, "Test Title", "api_key", "api_url")
    assert review == "Generated Review"
    mock_generate_text_with_retry.assert_called_once()

@pytest.mark.django_db
def test_update_or_create_property_rating(command):
    """Test updating or creating property ratings."""
    property_instance = Property.objects.create(id="1", title="Test Property")
    command.update_or_create_property_rating(property_instance, "Test Review", 4.5)

    # Assert the rating and review are created
    rating_instance = PropertyRating.objects.get(property=property_instance)
    assert rating_instance.review == "Test Review"
    assert rating_instance.rating == 4.5

    # Update the review and rating
    command.update_or_create_property_rating(property_instance, "Updated Review", 5.0)
    updated_rating_instance = PropertyRating.objects.get(property=property_instance)
    assert updated_rating_instance.review == "Updated Review"
    assert updated_rating_instance.rating == 5.0

@pytest.mark.django_db
def test_import_parse_function(command):
    """Test importing the parse function dynamically."""
    with patch('importlib.util.spec_from_file_location') as mock_spec:
        mock_spec.return_value = MagicMock()
        mock_parse = MagicMock()
        mock_parse.parse_properties_from_sql.return_value = []
        mock_spec.loader.exec_module.return_value = mock_parse

        parse_function = command.import_parse_function()
        assert callable(parse_function)

@patch('property_manager.management.commands.generate_data.requests.post')
def test_generate_text_with_retry(mock_post, command):
    """Test text generation with retries."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Generated Text"}]}}]
    }

    result = command.generate_text_with_retry("Test Prompt", "api_key", "api_url")
    assert result == "Generated Text"

@patch('property_manager.management.commands.generate_data.requests.post')
def test_generate_text_with_retry_rate_limit(mock_post, command):
    """Test text generation handling rate limit."""
    mock_post.side_effect = [
        MagicMock(status_code=429),  # First call exceeds rate limit
        MagicMock(status_code=200, json=lambda: {
            "candidates": [{"content": {"parts": [{"text": "Generated Text"}]}}]
        }),  # Second call succeeds
    ]

    result = command.generate_text_with_retry("Test Prompt", "api_key", "api_url")
    assert result == "Generated Text"
    assert mock_post.call_count == 2  # Ensure it retried once

def test_extract_rewritten_text(command):
    """Test extraction of rewritten text from API response."""
    response_json = {
        "candidates": [{"content": {"parts": [{"text": "Extracted Text"}]}}]
    }
    result = command.extract_rewritten_text(response_json)
    assert result == "Extracted Text"

    # Test with malformed JSON
    response_json = {"candidates": []}
    result = command.extract_rewritten_text(response_json)
    assert result is None

    response_json = {}
    result = command.extract_rewritten_text(response_json)
    assert result is None
