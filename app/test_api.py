import requests

def test_gemini_api():
    # Hardcoded Gemini API Key and URL
    api_key = 'AIzaSyD702s1yRxSnalEkUB9xULNqGpSYoFvDuw'
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

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
        response = requests.post(url, json=payload)

        # Handle the response
        if response.status_code == 200:
            result = response.json()
            print("API Response:", result)
            # Try to extract rewritten text from the response
            rewritten_text = extract_rewritten_text(result)
            if rewritten_text:
                print("Rewritten Text:", rewritten_text)
            else:
                print("Error: No rewritten text found in response.")
        else:
            print(f"API Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def extract_rewritten_text(response_json):
    """Extract rewritten text from the Gemini API response"""
    try:
        return response_json.get('content', {}).get('parts', [{}])[0].get('text', '')
    except (KeyError, IndexError) as e:
        return None

if __name__ == "__main__":
    test_gemini_api()
