import pytest
from unittest.mock import patch, mock_open
from Data_Parsing.parse import parse_properties_from_sql


def generate_mock_data(columns, rows):
    """
    Dynamically generate mock SQL COPY data.
    
    Args:
        columns (list): A list of column names.
        rows (list of lists): A list of rows, where each row is a list of values.

    Returns:
        str: A formatted SQL COPY command with the provided columns and rows.
    """
    column_part = ", ".join(columns)
    row_part = "\n".join(["\t".join(map(str, row)) for row in rows])
    return f"COPY public.properties ({column_part}) FROM stdin;\n{row_part}\n\\."


def generate_expected_output(columns, rows):
    """
    Dynamically generate expected parsed output based on columns and rows.
    
    Args:
        columns (list): A list of column names.
        rows (list of lists): A list of rows, where each row is a list of values.

    Returns:
        list of dicts: A list of dictionaries representing parsed rows.
    """
    output = []
    for row in rows:
        # Pad the row with None to match the column count
        adjusted_row = row + [None] * (len(columns) - len(row))
        # Trim the row if it exceeds the column count
        adjusted_row = adjusted_row[:len(columns)]
        output.append(dict(zip(columns, adjusted_row)))
    return output


@pytest.mark.parametrize("columns,rows", [
    # Test valid COPY data with all columns and rows matching
    (
        ["id", "title", "rating", "location"],
        [
            ["1", "Test Title 1", "4.5", "Test Location 1"],
            ["2", "Test Title 2", "4.0", "Test Location 2"]
        ]
    ),
    # Test valid COPY data with rows missing some fields
    (
        ["id", "title", "rating", "location"],
        [
            ["1", "Test Title 1", "4.5", "Test Location 1"],
            ["2", "Test Title 2", "4.0"]
        ]
    ),
    # Test valid COPY data with more fields in rows than columns
    (
        ["id", "title", "rating"],
        [
            ["1", "Test Title 1", "4.5", "Extra Field"],
            ["2", "Test Title 2", "4.0", "Another Extra"]
        ]
    ),
    # Test empty COPY data
    (
        ["id", "title", "rating", "location"],
        []
    )
])
def test_parse_properties_from_sql_dynamic(columns, rows):
    """
    Parametrized test case for dynamic handling of columns and rows.
    """
    mock_data = generate_mock_data(columns, rows)
    expected = generate_expected_output(columns, rows)

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
