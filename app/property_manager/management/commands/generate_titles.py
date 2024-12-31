import os
import requests
import importlib.util
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Regenerate titles and generate descriptions for properties using the Gemini API."

    def handle(self, *args, **kwargs):
        # Import the parse_properties_from_sql function dynamically
        parse_properties_from_sql = self.import_parse_function()

        # Hardcoded Gemini API Key and URL
        api_key = 'AIzaSyD702s1yRxSnalEkUB9xULNqGpSYoFvDuw'
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Parse properties from the SQL file
        self.stdout.write("Parsing properties from the SQL file...")
        try:
            properties = parse_properties_from_sql()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("SQL file not found."))
            return

        if not properties:
            self.stdout.write(self.style.ERROR("No properties found to process."))
            return

        # Process each property
        self.stdout.write("Processing properties for titles and descriptions...")
        for property_data in properties:
            # Generate a new title
            title_prompt = f"Rewrite this property title to make it more engaging: {property_data['title']}"
            new_title = self.generate_text(title_prompt, api_key, api_url)

            # Generate a new description based on the new title
            description_prompt = f"Generate a detailed and concise description for this property titled '{new_title}':"
            new_description = self.generate_text(description_prompt, api_key, api_url)

            # Update the property data with the new title and description
            property_data['title'] = new_title
            property_data['description'] = new_description

            # Print updated property details
            self.stdout.write(f"ID: {property_data['id']} - New Title: {new_title}")
            self.stdout.write(f"ID: {property_data['id']} - New Description: {new_description}")

        self.stdout.write(self.style.SUCCESS("Successfully processed all properties."))

    def generate_text(self, prompt, api_key, api_url):
        """Function to call the Gemini API to generate text."""
        try:
            # Prepare the payload for the API request
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }

            # Make the POST request to the Gemini API
            response = requests.post(api_url, json=payload)

            # Handle the response
            if response.status_code == 200:
                result = response.json()
                rewritten_text = self.extract_rewritten_text(result)
                return rewritten_text if rewritten_text else "Error: No rewritten text found in response."
            else:
                return f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Request failed: {e}"

    def extract_rewritten_text(self, response_json):
        """Extract rewritten text from the Gemini API response."""
        try:
            # The structure may differ depending on the API's response
            candidates = response_json.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    # Extract the text content
                    raw_text = parts[0].get('text', '')
                    return raw_text.strip()
            return None
        except (KeyError, IndexError) as e:
            return None

    def import_parse_function(self):
        """Import the parse_properties_from_sql function dynamically."""
        parse_path = os.path.join(os.path.dirname(__file__), "/app/Data_Parsing/parse.py")
        spec = importlib.util.spec_from_file_location("parse", parse_path)
        parse_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parse_module)
        return parse_module.parse_properties_from_sql
