import requests
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Regenerate titles and descriptions for properties using the Gemini API."

    def handle(self, *args, **kwargs):
        # Hardcoded Gemini API Key and URL
        api_key = 'AIzaSyD702s1yRxSnalEkUB9xULNqGpSYoFvDuw'
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Sample prompt for testing
        prompt = "Rewrite this property title to make it more engaging: Beautiful 2-bedroom apartment"

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
            response = requests.post(api_url, json=payload)

            # Handle the response
            if response.status_code == 200:
                result = response.json()
                print("API Response:", result)
                # Try to extract and parse the rewritten text from the response
                rewritten_text = self.extract_rewritten_text(result)
                if rewritten_text:
                    print("Rewritten Text:")
                    for idx, option in enumerate(rewritten_text, start=1):
                        print(f"Option {idx}: {option}")
                else:
                    print("Error: No rewritten text found in response.")
            else:
                print(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def extract_rewritten_text(self, response_json):
        """Extract rewritten text from the Gemini API response and return a list of options."""
        try:
            # The structure may differ depending on the API's response
            candidates = response_json.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    # Extract the text content of each option
                    raw_text = parts[0].get('text', '')
                    # Split the options based on the * delimiter
                    options = self.parse_options(raw_text)
                    return options
            return None
        except (KeyError, IndexError) as e:
            return None

    def parse_options(self, raw_text):
        """Parse the raw text into a list of readable and concise options."""
        # Split the options by '*', which is how they are separated in the API response
        options = raw_text.split('\n\n* ')
        options = [option.strip('* ').strip() for option in options if option]
        return options
