import uuid
import os
import time
import requests
import importlib.util
from django.core.management.base import BaseCommand
from property_manager.models import Property, PropertySummary, PropertyRating
from django.db.models import Count

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
            # Regenerate missing or empty fields using Gemini API if necessary
            title = property_data.get('title')
            description = property_data.get('description')
            summary = property_data.get('summary')
            review = property_data.get('reviews')
            rating = property_data.get('rating')  # Rating is fetched from the SQL data

            # Handle missing fields and regenerate them
            if not title:
                title = self.generate_text_with_retry(
                    "Generate a professional, eye-catching, appealing title for a luxury hotel property.",
                    api_key, api_url
                )
            
            if not description:
                description = self.generate_text_with_retry(
                    f"Generate a concise and professional description for a luxury hotel titled '{title}':",
                    api_key, api_url
                )

            if not summary:
                summary = self.generate_text_with_retry(
                    f"Generate a concise, engaging summary for the luxury hotel titled '{title}':",
                    api_key, api_url
                )

            # Generate review based on rating
            if not review or not rating:
                review = self.generate_review_based_on_rating(rating, title, api_key, api_url)
                rating = rating or 5.0  # Default rating if it's still missing
            else:
                review = review or "A wonderful stay with exceptional service. Highly recommended!"
                rating = rating or 5.0

            # Only proceed if all critical fields are non-empty
            if title and description and summary and review and rating:
                # Save the data into the Property table
                property_instance, created = Property.objects.update_or_create(
                    id=property_data['id'],  # Assuming your 'id' is unique and comes from SQL data
                    defaults={
                        'title': title,
                        'rating': rating,
                        'location': property_data.get('location'),
                        'latitude': property_data.get('latitude'),
                        'longitude': property_data.get('longitude'),
                        'price': property_data.get('price'),
                        'image_url': property_data.get('image_url'),
                        'city_id': property_data.get('city_id'),
                        'description': description,
                        'geom': property_data.get('geom')  # Ensure that geom is passed if geospatial data is needed
                    },
                )

                # Save or update PropertySummary
                PropertySummary.objects.update_or_create(
                    property=property_instance,
                    defaults={'summary': summary},
                )

                # Handling PropertyRating to avoid MultipleObjectsReturned
                self.update_or_create_property_rating(property_instance, review, rating)

                # Log the results
                self.stdout.write(f"ID: {property_instance.id} - New Title: {title}")
                self.stdout.write(f"ID: {property_instance.id} - New Description: {description}")
                self.stdout.write(f"ID: {property_instance.id} - New Summary: {summary}")
                self.stdout.write(f"ID: {property_instance.id} - New Review: {review} (Rating: {rating})")
            else:
                # If any critical field is missing, log and skip the property
                self.stdout.write(self.style.ERROR(f"Skipped property ID {property_data['id']} due to missing fields."))
        
        self.stdout.write(self.style.SUCCESS("Successfully processed all properties."))

    def generate_text_with_retry(self, prompt, api_key, api_url, max_retries=5, backoff_factor=2):
        """Function to call the Gemini API with retry logic."""
        retries = 0
        while retries < max_retries:
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
                elif response.status_code == 429:
                    # Handle rate limit exceeded: Retry after waiting
                    retries += 1
                    wait_time = backoff_factor ** retries  # Exponential backoff
                    print(f"Rate limit exceeded, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)  # Wait before retrying
                else:
                    return f"Error: {response.status_code} - {response.text}"

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                break

        return "Error: Unable to generate text after multiple retries."

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

    def generate_review_based_on_rating(self, rating, title, api_key, api_url):
        """Generate a unique and eye-catching review based on the rating using Gemini API."""
        rating = float(rating)  # Ensure rating is a float
        if rating >= 4.5:
            prompt = f"Generate a highly positive, unique, and eye-catching review for a luxury hotel titled '{title}' with a rating of {rating}. It should sound like a human review."
        elif rating >= 3.5:
            prompt = f"Generate a positive, unique, and eye-catching review for a luxury hotel titled '{title}' with a rating of {rating}. It should sound like a human review."
        elif rating >= 2.5:
            prompt = f"Generate a neutral, professional review for a luxury hotel titled '{title}' with a rating of {rating}. It should sound like a human review."
        else:
            prompt = f"Generate a constructive, human-sounding review for a luxury hotel titled '{title}' with a rating of {rating}. It should be professional and insightful."

        # Call Gemini API to generate review based on the rating
        review = self.generate_text_with_retry(prompt, api_key, api_url)
        return review

    def update_or_create_property_rating(self, property_instance, review, rating):
        """Handle creating or updating PropertyRating."""
        # First, try to find any existing rating for the property
        existing_rating = PropertyRating.objects.filter(property=property_instance).first()
        if existing_rating:
            # Update existing rating if found
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.save()
        else:
            # Create new rating if no existing rating found
            PropertyRating.objects.create(
                property=property_instance,
                rating=rating,
                review=review,
            )

    def import_parse_function(self):
        """Import the parse_properties_from_sql function dynamically."""
        parse_path = os.path.join(os.path.dirname(__file__), "/app/Data_Parsing/parse.py")
        spec = importlib.util.spec_from_file_location("parse", parse_path)
        parse_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parse_module)
        return parse_module.parse_properties_from_sql
