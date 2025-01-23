import openai
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# Laad de API-sleutels uit .env-bestand
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

openai.api_key = OPENAI_API_KEY

# Functie om een verhaal te genereren
def generate_story(child_name, favorite_animal, theme, story_length, language):
    prompt = f"""
    Write a children's story in {language} about {child_name}, who loves {favorite_animal}.
    The theme is {theme}, and the story should be {story_length}. Ensure the story has a clear ending and is engaging for children.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a children's story writer."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        story = response['choices'][0]['message']['content'].strip()
        return story
    except Exception as e:
        return f"Error generating story: {e}"

# Functie om illustraties te genereren
def generate_illustration(paragraph, theme, style="storybook cartoon style for children"):
    prompt = (
        f"Create a consistent and cohesive children's storybook illustration in '{style}'. "
        f"The image should reflect: '{paragraph}'. "
        f"Ensure the image aligns with the theme '{theme}', has consistent characters, colors, and no text, numbers, or symbols."
    )
    try:
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {REPLICATE_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "version": "latest",
            "input": {
                "prompt": prompt,
                "image_dimensions": "512x512",
                "negative_prompt": "text, watermark, logo, numbers, letters",
            },
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        prediction = response.json()
        image_url = prediction["output"][0]
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        return image
    except Exception as e:
        print(f"Error generating illustration: {e}")
        return None

# Streamlit-app
st.title("StoryNest: Create Personalized Children's Stories with Illustrations")

# Invoeropties
st.sidebar.header("Story Settings")
child_name = st.sidebar.text_input("Child's Name", value="Ayyuce")
favorite_animal = st.sidebar.text_input("Favorite Animal", value="Rabbit")
theme = st.sidebar.selectbox("Select Theme", ["Adventure", "Friendship", "Courage", "Winter", "Magical"])
story_length = st.sidebar.selectbox("Story Length", ["Short", "Medium", "Long"])
language = st.sidebar.selectbox(
    "Select Language",
    ["English", "French", "Dutch", "German", "Italian", "Spanish", "Turkish", "Japanese", "Korean", "Portuguese"]
)

# Verhaal en illustraties genereren
if st.sidebar.button("Generate Story and Illustrations"):
    with st.spinner("Generating story and illustrations..."):
        # Verhaal genereren
        story = generate_story(child_name, favorite_animal, theme, story_length, language)
        st.subheader("Generated Story:")
        st.write(story)

        # Illustraties genereren per alinea
        st.subheader("Illustrations:")
        paragraphs = story.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                st.write(f"**Page {i+1}:** {paragraph.strip()}")
                illustration = generate_illustration(paragraph.strip(), theme)
                if illustration:
                    st.image(illustration, use_column_width=True)
                else:
                    st.write("Illustration could not be generated for this page.")

st.sidebar.info("Powered by OpenAI and Replicate")
