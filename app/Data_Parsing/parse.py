import re

def parse_properties_from_sql():
    """
    Parses the SQL file to extract data from the `public.properties` table.

    Returns:
        list: A list of dictionaries representing the rows in the `public.properties` table.
    """
    # Hardcoded SQL file path
    sql_file_path = "/app/Data_Parsing/tripcom_backup_20241230123803.sql"  # Updated to absolute path for clarity

    try:
        # Read the SQL file content
        with open(sql_file_path, "r") as file:
            sql_content = file.read()

        # Extract the COPY data for 'public.properties'
        match = re.search(r"COPY public\.properties \((.*?)\) FROM stdin;\n(.*?)\\\.", sql_content, re.DOTALL)
        if not match:
            print("No data found for 'public.properties'.")
            return []

        # Extract column names and data rows
        column_names = match.group(1).strip().split(", ")
        data_rows = match.group(2).strip().split("\n")

        # Parse the rows into dictionaries
        parsed_data = []
        for row in data_rows:
            values = row.split("\t")  # Tab-delimited values
            parsed_data.append(dict(zip(column_names, values)))

        return parsed_data

    except FileNotFoundError:
        print(f"Error: The file '{sql_file_path}' does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred while parsing the SQL file: {e}")
        return []

# Usage example
if __name__ == "__main__":
    parsed_properties = parse_properties_from_sql()

    # Display a few parsed rows for inspection
    if parsed_properties:
        for i, property_data in enumerate(parsed_properties[:5]):
            print(f"Row {i + 1}: {property_data}")
    else:
        print("No data was parsed.")
