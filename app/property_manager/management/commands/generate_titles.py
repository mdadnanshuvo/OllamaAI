import os
import requests
import importlib.util
from django.core.management.base import BaseCommand
from property_manager.models import Property, PropertySummary, PropertyRating 

class Command(BaseCommand):
    help = "Regenerate titles, descriptions, summaries, and reviews for properties using the Gemini API. Automatically generate missing data."

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
        self.stdout.write("Processing properties for titles, descriptions, summaries, and reviews...")
        for property_data in properties:
            # Regenerate missing or empty fields
            if not property_data.get('title'):
                property_data['title'] = self.generate_text(
                    "Generate a title for a property with no title.", api_key, api_url
                )

            if not property_data.get('description'):
                description_prompt = f"Generate a detailed and concise description for the property titled '{property_data['title']}':"
                property_data['description'] = self.generate_text(description_prompt, api_key, api_url)

            # Generate summary for PropertySummary table
            summary_prompt = f"Generate a short and engaging summary for the property titled '{property_data['title']}':"
            new_summary = self.generate_text(summary_prompt, api_key, api_url)

            # Generate reviews and ratings for PropertyRating table
            review_prompt = f"Generate a positive review and a rating (out of 5) for the property titled '{property_data['title']}':"
            review_and_rating = self.generate_text(review_prompt, api_key, api_url)

            # Parse the review and rating (assuming the response contains "Review: ... Rating: ...")
            review, rating = self.parse_review_and_rating(review_and_rating)

            # Save to the database
            property_instance, created = Property.objects.update_or_create(
                id=property_data['id'],
                defaults={
                    'title': property_data['title'],
                    'rating': rating if rating else property_data.get('rating'),
                    'location': property_data.get('location'),
                    'latitude': property_data.get('latitude'),
                    'longitude': property_data.get('longitude'),
                    'price': property_data.get('price'),
                    'image_url': property_data.get('image_url'),
                    'city_id': property_data.get('city_id'),
                    'description': property_data['description'],
                },
            )

            # Save or update PropertySummary
            PropertySummary.objects.update_or_create(
                property=property_instance,
                defaults={'summary': new_summary},
            )

            # Save or update PropertyRating
            PropertyRating.objects.create(
                property=property_instance,
                rating=rating,
                review=review,
            )

            # Log the results
            self.stdout.write(f"ID: {property_instance.id} - New Title: {property_data['title']}")
            self.stdout.write(f"ID: {property_instance.id} - New Description: {property_data['description']}")
            self.stdout.write(f"ID: {property_instance.id} - New Summary: {new_summary}")
            self.stdout.write(f"ID: {property_instance.id} - New Review: {review} (Rating: {rating})")

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
            candidates = response_json.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    raw_text = parts[0].get('text', '')
                    return raw_text.strip()
            return None
        except (KeyError, IndexError) as e:
            return None

    def parse_review_and_rating(self, review_and_rating_text):
        """Parse the review and rating from the response."""
        try:
            # Assuming the format: "Review: ... Rating: ..."
            if "Review:" in review_and_rating_text and "Rating:" in review_and_rating_text:
                review = review_and_rating_text.split("Review:")[1].split("Rating:")[0].strip()
                rating = float(review_and_rating_text.split("Rating:")[1].strip())
                return review, rating
            return "No review available", 0.0
        except Exception as e:
            return "Error parsing review", 0.0

    def import_parse_function(self):
        """Import the parse_properties_from_sql function dynamically."""
        parse_path = os.path.join(os.path.dirname(__file__), "/app/Data_Parsing/parse.py")
        spec = importlib.util.spec_from_file_location("parse", parse_path)
        parse_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parse_module)
        return parse_module.parse_properties_from_sql
