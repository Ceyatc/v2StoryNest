import streamlit as st
import openai
import random
from googletrans import Translator
import os
import requests

# Load API keys securely from Streamlit Cloud Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
leonardo_api_key = os.getenv("LEONARDO_API_KEY")

# Ensure API keys exist
if not openai.api_key or not leonardo_api_key:
    st.error("API keys are missing. Set them in Streamlit Secrets or .env file.")
    st.stop()

# Story Themes
themes = ["Adventure", "Friendship", "Magic", "Mystery", "Courage", "Exploration"]

# Translation Function
translator = Translator()

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
        try:
            response_data = response.json()
            # Ensure that the 'data' key exists and contains the list with an image URL
            if "data" in response_data and len(response_data["data"]) > 0:
                image_url = response_data["data"][0].get("url")
                if image_url:
                    return image_url
                else:
                    st.write("Error: Image URL not found in the response.")
                    return None
            else:
                st.write("Error: No data returned in the response.")
                st.write(f"Response: {response_data}")
                return None
        except Exception as e:
            st.write(f"Error parsing response: {str(e)}")
            st.write(f"Response: {response.text}")
            return None
    else:
        # Log the error if the request fails
        st.write(f"Error {response.status_code}: {response.text}")
        return None
