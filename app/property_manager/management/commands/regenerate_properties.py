import os
import time
import importlib.util
from django.core.management.base import BaseCommand
import requests

# Import parse_properties_from_sql dynamically
def import_parse_function():
    parse_path = os.path.join(os.path.dirname(__file__), "/app/Data_Parsing/parse.py")
    spec = importlib.util.spec_from_file_location("parse", parse_path)
    parse_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parse_module)
    return parse_module.parse_properties_from_sql

# Import call_tinyllama dynamically (we will keep this for consistency, though we won't use it)
def import_generate_function():
    generate_path = os.path.join(os.path.dirname(__file__), "/app/Integrate_Ollama/generate.py")
    spec = importlib.util.spec_from_file_location("generate", generate_path)
    generate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generate_module)
    return generate_module.call_tinyllama

# Helper function to generate text with delay using Gemini API
def generate_text_with_delay(prompt, delay, description=False):
    time.sleep(delay)  # Introduce a delay between API calls

    # Hardcoded Gemini API Key
    api_key = "AIzaSyD702s1yRxSnalEkUB9xULNqGpSYoFvDuw"  # Hardcoded API key
    
    # URL for the Gemini API request
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # Prepare the payload for the API request
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        # Make the POST request to the Gemini API
        response = requests.post(api_url, json=payload, params={"key": api_key})

        # Handle the response
        if response.status_code == 200:
            result = response.json()
            rewritten_text = extract_rewritten_text(result)

            if rewritten_text:
                return rewritten_text
            else:
                if description:
                    return "Error: Unable to generate description from Gemini"
                return "Error: Unable to generate title from Gemini"
        else:
            return f"API Error: {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def extract_rewritten_text(response_json):
    """Extract rewritten text from the Gemini API response"""
    try:
        return response_json.get('content', {}).get('parts', [{}])[0].get('text', '')
    except (KeyError, IndexError) as e:
        return None

# Management Command Class
class Command(BaseCommand):
    help = "Re-generate titles and generate descriptions for properties with delays using Gemini API."

    def handle(self, *args, **kwargs):
        # Import functions dynamically
        parse_properties_from_sql = import_parse_function()

        # Define delay (no need to set API URL and key here)
        delay = 5  # Delay in seconds between API calls

        # Parse properties from the SQL file
        self.stdout.write("Parsing properties from the SQL file...")
        try:
            properties = parse_properties_from_sql()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("SQL file not found"))
            return

        if not properties:
            self.stdout.write(self.style.ERROR("No properties found to process."))
            return

        # Process titles first
        self.stdout.write("Processing titles for properties...")
        for property_data in properties:
            title_prompt = f"Rewrite this property title to make it more engaging: {property_data['title']}"
            new_title = generate_text_with_delay(title_prompt, delay)
            property_data['title'] = new_title

            # Print updated title (no DB push, just logging)
            self.stdout.write(f"ID: {property_data['id']} - New Title: {new_title}")

        # Process descriptions next
        self.stdout.write("Processing descriptions for properties...")
        for property_data in properties:
            description_prompt = f"Generate a detailed description for this property titled '{property_data['title']}':"
            new_description = generate_text_with_delay(description_prompt, delay, description=True)
            property_data['description'] = new_description

            # Print updated description (no DB push, just logging)
            self.stdout.write(f"ID: {property_data['id']} - Description: {new_description}")

        self.stdout.write(self.style.SUCCESS("Successfully processed all properties with delays using Gemini API."))
