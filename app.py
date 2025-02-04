
import streamlit as st
import openai
import requests
import os
import time
from googletrans import Translator

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

def translate_text(text, target_language):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        st.error(f"Error during translation: {e}")
        return text  # Fallback if translation fails

# Story Generator
def generate_story(name, favorite_animal, theme, length):
    prompts = {
        "Short": 300,
        "Medium": 600,
        "Long": 1200
    }
    
    prompt = (
        f"Write a well-structured children's story about {name}, who loves {favorite_animal}, with the theme of {theme}. "
        "The story should be engaging, creative, and must have a clear beginning, middle, and ending."
    )
    
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=prompts[length],
            temperature=0.8
        )
        story = response.choices[0].text.strip()
        return story
    except Exception as e:
        st.error(f"Error generating story: {e}")
        return ""

# Illustration Generator using Leonardo API
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
                
                # Poll for the result until it's ready (max 5 minutes for example)
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

# Streamlit UI
st.title("StoryNest - AI Story & Illustration Generator")

# User Input
name = st.text_input("Enter child's name:", "Aiden")
favorite_animal = st.text_input("Enter child's favorite animal:", "Rabbit")
theme = st.selectbox("Choose a theme:", themes)
story_length = st.selectbox("Choose story length:", ["Short", "Medium", "Long"])
language = st.selectbox("Select story language:", ["English", "French", "Dutch", "German", "Italian", "Spanish", "Turkish", "Japanese", "Korean", "Portuguese"])

if st.button("Generate Story & Illustrations"):
    st.subheader("Generated Story:")
    
    story = generate_story(name, favorite_animal, theme, story_length)
    if story:
        translated_story = translate_text(story, language)
        st.write(translated_story)

        st.subheader("Illustrations:")
        paragraphs = translated_story.split("\n")

        for paragraph in paragraphs:
            if paragraph.strip():
                image_url = generate_illustration_with_leonardo(paragraph)
                if image_url:
                    st.image(image_url, use_column_width=True)
                else:
                    st.write("Image generation failed for this scene.")
    else:
        st.error("Story generation failed.")

st.write("© StoryNest - AI-Powered Personalized Storytelling")
