
import requests
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Generates content or rewrites text using Google Gemini API'

    def add_arguments(self, parser):
        parser.add_argument('text', type=str, help="Text to be rewritten or generated.")

    def handle(self, *args, **kwargs):
        text_to_rewrite = kwargs['text']

        # Fetch API Key from environment variables (from Docker environment, not .env file)
        api_key = os.getenv('API_KEY')  # Accessing the API key from the environment variable

        if not api_key:
            self.stdout.write(self.style.ERROR("Error: API_KEY not found in the environment."))
            return

        # URL for the API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyD702s1yRxSnalEkUB9xULNqGpSYoFvDuw"

        # Prepare the payload for the API request
        payload = {
            "contents": [{
                "parts": [{
                    "text": text_to_rewrite
                }]
            }]
        }

        try:
            # Make the POST request to the API
            response = requests.post(url, json=payload)

            # Handle the response
            if response.status_code == 200:
                result = response.json()

                # Check if response contains the rewritten text
                rewritten_text = self.extract_rewritten_text(result)

                if rewritten_text:
                    self.stdout.write(self.style.SUCCESS(f"Rewritten Text: {rewritten_text}"))
                else:
                    self.stdout.write(self.style.ERROR("Error: No text found in the response."))
            else:
                self.stdout.write(self.style.ERROR(f"API Error: {response.status_code} - {response.text}"))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Request failed: {e}"))

    def extract_rewritten_text(self, response_json):
        """Extract rewritten text from the API response"""
        try:
            return response_json.get('content', {}).get('parts', [{}])[0].get('text', '')
        except (KeyError, IndexError) as e:
            self.stdout.write(self.style.ERROR(f"Error parsing the response: {e}"))
            return None
