import time
import requests
import streamlit as st

def generate_illustration_with_leonardo(story_text):
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
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            # Check for the generation job ID
            if "sdGenerationJob" in response_data:
                generation_id = response_data["sdGenerationJob"]["generationId"]
                st.write(f"Image generation started. Generation ID: {generation_id}")
                
                # Poll for the result until it's ready (max 10 minutes for example)
                return poll_for_image(generation_id)
            else:
                st.error(f"Error: No image data returned: {response_data}")
                return None
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error making API request: {e}")
        return None

def poll_for_image(generation_id, max_retries=30, delay=10):
    """
    Polls the Leonardo API until the image is ready.
    """
    poll_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
    
    for i in range(max_retries):
        try:
            st.write(f"Polling for image... Attempt {i+1}/{max_retries}")
            response = requests.get(poll_url, headers={"Authorization": f"Bearer {leonardo_api_key}"})
            
            if response.status_code == 200:
                response_data = response.json()
                # Log the full response for debugging
                st.write(f"Response Data: {response_data}")
                
                # Check if the image URL is ready
                if "data" in response_data and len(response_data["data"]) > 0:
                    image_url = response_data["data"][0].get("url")
                    if image_url:
                        return image_url
                    else:
                        st.write("Error: Image URL not found in the response.")
                        return None
                else:
                    st.write("Image is still being processed...")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
            time.sleep(delay)  # Wait before polling again

        except Exception as e:
            st.error(f"Error polling for image: {e}")
            return None

    st.error("Timeout: Image generation took too long.")
    return None
