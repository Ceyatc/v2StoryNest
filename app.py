import os
import openai
import streamlit as st
from PIL import Image
from io import BytesIO
from googletrans import Translator

# Load OpenAI API Key from Streamlit Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up Streamlit interface
st.title("StoryNest: AI-Personalized Children's Stories")

# Language Selection
st.sidebar.header("Settings")
language = st.sidebar.selectbox("Select Language:", ["English", "French", "Spanish", "German", "Dutch", "Italian"])

# Input Fields
st.header("Enter Story Details")
child_name = st.text_input("Child's Name:")
favorite_animal = st.text_input("Favorite Animal:")
theme = st.text_input("Story Theme (e.g., Adventure, Friendship, Magic):")
additional_notes = st.text_area("Additional Information (Optional):")
story_length = st.slider("Select Story Length:", min_value=100, max_value=1000, step=100)

# Generate Story
if st.button("Generate Story"):
    if not openai.api_key:
        st.error("OpenAI API Key not found. Please configure it in Streamlit Secrets.")
    elif not child_name or not favorite_animal or not theme:
        st.error("Please fill in all required fields.")
    else:
        # Story Prompt
        prompt = (
            f"Write a children's story about {child_name}, who loves {favorite_animal}, with a theme of {theme}. "
            f"Include details: {additional_notes}. Keep it creative and magical."
        )
        try:
            # Generate Story
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=story_length,
                temperature=0.7,
            )
            story = response["choices"][0]["message"]["content"]

            # Translate Story
            if language != "English":
                translator = Translator()
                translated_story = translator.translate(story, src="en", dest=language[:2].lower()).text
                st.subheader(f"Story in {language}")
                st.write(translated_story)
            else:
                st.subheader("Generated Story")
                st.write(story)

        except Exception as e:
            st.error(f"Error generating story: {str(e)}")

# Generate Illustration
if st.button("Generate Illustration"):
    try:
        illustration_prompt = f"A vibrant children's illustration for a story about {child_name} and a {favorite_animal} with a theme of {theme}. Style: magical, colorful, and cohesive."
        dalle_response = openai.Image.create(
            prompt=illustration_prompt,
            n=1,
            size="512x512",
        )
        image_url = dalle_response["data"][0]["url"]
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        st.image(img, caption="Generated Illustration", use_column_width=True)
    except Exception as e:
        st.error(f"Error generating illustration: {str(e)}")
