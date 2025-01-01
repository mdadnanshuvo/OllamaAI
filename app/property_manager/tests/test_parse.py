import pytest
from unittest.mock import patch, mock_open
from Data_Parsing.parse import parse_properties_from_sql


@pytest.mark.parametrize("mock_data,expected", [
    # Test valid COPY data with multiple rows
    (
        "COPY public.properties (id, title, rating, location) FROM stdin;\n"
        "1\tTest Title 1\t4.5\tTest Location 1\n"
        "2\tTest Title 2\t4.0\tTest Location 2\n\\.",
        [
            {"id": "1", "title": "Test Title 1", "rating": "4.5", "location": "Test Location 1"},
            {"id": "2", "title": "Test Title 2", "rating": "4.0", "location": "Test Location 2"}
        ]
    ),
    # Test valid COPY data with a single row
    (
        "COPY public.properties (id, title, rating, location) FROM stdin;\n"
        "1\tTest Title\t4.5\tTest Location\n\\.",
        [{"id": "1", "title": "Test Title", "rating": "4.5", "location": "Test Location"}]
    ),
    # Test empty COPY data
    (
        "COPY public.properties (id, title, rating, location) FROM stdin;\n\\.",
        []
    ),
    # Test malformed COPY data (mismatched columns)
    (
        "COPY public.properties (id, title, rating, location) FROM stdin;\n"
        "1\tTest Title\t4.5\n\\.",
        []
    ),
    # Test missing COPY data
    (
        "CREATE TABLE public.properties (id SERIAL PRIMARY KEY);\n",
        []
    ),
    # Test completely empty file
    ("", [])
])
def test_parse_properties_from_sql(mock_data, expected):
    """
    Parametrized test case to handle various scenarios for parse_properties_from_sql.
    """
    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("os.path.exists", return_value=True):
            result = parse_properties_from_sql()
            assert result == expected


def test_parse_file_not_found():
    """
    Test case for FileNotFoundError.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = parse_properties_from_sql()
        assert result == []


def test_parse_unexpected_error():
    """
    Test case for handling unexpected errors during parsing.
    """
    with patch("builtins.open", side_effect=Exception("Unexpected Error")):
        result = parse_properties_from_sql()
        assert result == []


def test_parse_no_data_section():
    """
    Test case for SQL file missing the COPY section entirely.
    """
    mock_data = (
        "CREATE TABLE public.properties (\n"
        "id SERIAL PRIMARY KEY, title VARCHAR(255)\n"
        ");"
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("os.path.exists", return_value=True):
            result = parse_properties_from_sql()
            assert result == []


def test_parse_partial_data():
    """
    Test case for partially valid data in the COPY section.
    """
    mock_data = (
        "COPY public.properties (id, title, rating, location) FROM stdin;\n"
        "1\tTest Title 1\t4.5\tTest Location 1\n"
        "2\t\t\t\n\\."  # Second row has missing data
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("os.path.exists", return_value=True):
            result = parse_properties_from_sql()
            assert result == [
                {"id": "1", "title": "Test Title 1", "rating": "4.5", "location": "Test Location 1"}
            ]  # Only the first row is valid


def test_parse_file_with_extra_whitespace():
    """
    Test case for handling files with extra whitespace or empty lines.
    """
    mock_data = (
        "\n\n"
        "COPY public.properties (id, title, rating, location) FROM stdin;\n"
        "1\tTest Title\t4.5\tTest Location\n\n\\.\n\n"
    )
    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("os.path.exists", return_value=True):
            result = parse_properties_from_sql()
            assert result == [
                {"id": "1", "title": "Test Title", "rating": "4.5", "location": "Test Location"}
            ]
