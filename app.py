import requests
import streamlit as st

def generate_illustration_with_leonardo(story_text):
    # Format the prompt to guide the image generation
    prompt = f"A professional, child-friendly cartoon-style illustration for the following story scene:\n\n{story_text}"

    # Endpoint for Leonardo's image generation API
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    # Set the headers with your Leonardo API key
    headers = {
        "Authorization": f"Bearer {leonardo_api_key}",
        "Content-Type": "application/json"
    }
    
    # Request payload with parameters expected by the API
    data = {
        "prompt": prompt,   # The prompt describing the image
        "width": 512,       # Image width (modify as needed)
        "height": 512,      # Image height (modify as needed)
        "num_images": 1     # Number of images you want to generate (optional)
    }
    
    # Make the API call to Leonardo's image generation endpoint
    response = requests.post(url, headers=headers, json=data)

    # Check for success (HTTP status code 200)
    if response.status_code == 200:
        # Extract the image URL from the response
        response_data = response.json()
        image_url = response_data.get("data", [])[0].get("url")  # Assuming "url" is the key for the generated image URL
        
        if image_url:
            return image_url
        else:
            st.write("Error: Image URL not found in the response.")
            return None
    else:
        # Log the error if the request fails
        st.write(f"Error {response.status_code}: {response.text}")
        return None

