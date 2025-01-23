import os
import openai
import streamlit as st
from googletrans import Translator
from PIL import Image
import requests
from io import BytesIO
import random

# OpenAI API-sleutel ophalen
openai.api_key = os.getenv("OPENAI_API_KEY")

# Functie om een willekeurig thema te kiezen
def get_random_theme():
    themes = ["Adventure", "Friendship", "Courage", "Winter", "Magic", "Exploration", "Nature", "Family", "Kindness"]
    return random.choice(themes)

# Functie om een logisch verhaal te genereren
def generate_story(child_name, favorite_animal, theme, length, language):
    length_map = {"Short": 300, "Medium": 800, "Long": 1500}
    max_tokens = length_map[length]

    prompt = (
        f"Write a children's story about {child_name}, who loves {favorite_animal}. The story should follow a theme of {theme}, "
        f"and include a clear beginning, middle, and a meaningful, happy ending. Make the story engaging, imaginative, and age-appropriate."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    )
    story = response["choices"][0]["message"]["content"]

    # Verhaal vertalen
    translator = Translator()
    translated_story = translator.translate(story, dest=language).text
    return translated_story

# Functie om samenhangende illustraties te genereren
def generate_illustration(paragraph, theme, style="storybook cartoon style for children"):
    dalle_prompt = (
        f"A cohesive, high-quality, text-free illustration in {style}. It should use consistent colors, characters, and style. "
        f"The illustration should reflect the following scene: '{paragraph}' and align with the theme '{theme}'. No text, numbers, or symbols should appear."
    )
    response = openai.Image.create(
        prompt=dalle_prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))
    return img

# Streamlit UI
st.title("StoryNest: Personalized Children's Stories with Illustrations")
st.sidebar.title("Story Settings")

# Gebruikersinvoer
child_name = st.sidebar.text_input("Child's Name", "Ayyuce")
favorite_animal = st.sidebar.text_input("Favorite Animal", "Rabbit")
theme_options = ["Adventure", "Friendship", "Courage", "Winter", "Magic", "Exploration", "Random"]
selected_theme = st.sidebar.selectbox("Story Theme", theme_options)

# Willekeurig thema kiezen indien geselecteerd
if selected_theme == "Random":
    selected_theme = get_random_theme()

story_length = st.sidebar.selectbox("Story Length", ["Short", "Medium", "Long"])
language = st.sidebar.selectbox(
    "Choose Language",
    [
        "en",  # English
        "fr",  # French
        "nl",  # Dutch
        "de",  # German
        "it",  # Italian
        "es",  # Spanish
        "tr",  # Turkish
        "ja",  # Japanese
        "ko",  # Korean
        "pt",  # Portuguese,
    ],
    format_func=lambda lang: {
        "en": "English",
        "fr": "Français",
        "nl": "Nederlands",
        "de": "Deutsch",
        "it": "Italiano",
        "es": "Español",
        "tr": "Türkçe",
        "ja": "日本語",
        "ko": "한국어",
        "pt": "Português",
    }[lang]
)

# Extra informatie
extra_info = st.sidebar.text_area(
    "Additional Information (Optional)",
    "Add any specific details to make the story more personalized (e.g., hobbies, places, friends)."
)

# Verhaal en illustraties genereren
if st.sidebar.button("Generate Story and Illustrations"):
    with st.spinner("Generating story and illustrations..."):
        # Verhaal genereren
        story = generate_story(child_name, favorite_animal, selected_theme, story_length, language)
        st.subheader("Your Story:")
        st.write(story)

        # Illustraties genereren per alinea
        paragraphs = story.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                st.write(f"**Page {i+1}:** {paragraph.strip()}")
                illustration = generate_illustration(paragraph.strip(), selected_theme)
                st.image(illustration, use_column_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Developed with ❤️ by [StoryNest](https://yourwebsite.com)"
)
