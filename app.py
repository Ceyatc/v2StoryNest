import os
import openai
import streamlit as st
from googletrans import Translator
from PIL import Image
import requests
from io import BytesIO

# API-sleutel ophalen
openai.api_key = os.getenv("OPENAI_API_KEY")

# Functie voor het genereren van een samenhangend verhaal
def generate_story(child_name, favorite_animal, theme, length, language):
    length_map = {"Kort": 200, "Middel": 500, "Lang": 1000}
    max_tokens = length_map[length]

    prompt = (
        f"Write a coherent children's story with a clear beginning, middle, and end. "
        f"The story should be about {child_name}, who loves {favorite_animal}, "
        f"with a theme of {theme}. Ensure the story is engaging, logical, and has a meaningful conclusion."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    )
    story = response["choices"][0]["message"]["content"]

    # Verhaal vertalen naar de gekozen taal
    translator = Translator()
    translated_story = translator.translate(story, dest=language).text
    return translated_story

# Functie voor het genereren van samenhangende illustraties
def generate_illustration(paragraph, theme, style="children's cartoon"):
    dalle_prompt = (
        f"An illustration in {style} style. The theme is {theme}. "
        f"The content is: {paragraph}. Bright colors, consistent design, and suitable for children."
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
st.title("StoryNest: Create Personalized Children's Stories")
st.sidebar.title("Story Settings")

# Gebruikersinvoer
child_name = st.sidebar.text_input("Child's Name", "Ayyuce")
favorite_animal = st.sidebar.text_input("Favorite Animal", "Rabbit")
theme = st.sidebar.selectbox("Story Theme", ["Adventure", "Friendship", "Courage", "Winter"])
story_length = st.sidebar.selectbox("Story Length", ["Kort", "Middel", "Lang"])
language = st.sidebar.selectbox(
    "Choose Language",
    [
        "en",  # Engels
        "fr",  # Frans
        "nl",  # Nederlands
        "de",  # Duits
        "it",  # Italiaans
        "es",  # Spaans
        "tr",  # Turks
        "ja",  # Japans
        "ko",  # Koreaans
        "pt",  # Portugees
    ],
    format_func=lambda lang: {
        "en": "Engels",
        "fr": "Frans",
        "nl": "Nederlands",
        "de": "Duits",
        "it": "Italiaans",
        "es": "Spaans",
        "tr": "Turks",
        "ja": "Japans",
        "ko": "Koreaans",
        "pt": "Portugees",
    }[lang]
)

# Extra informatie
extra_info = st.sidebar.text_area(
    "Additional Information (Optional)",
    "Provide extra details to make the story unique (e.g., hobbies, places, friends)."
)

# Verhaal genereren
if st.sidebar.button("Generate Story"):
    with st.spinner("Generating your story and illustrations..."):
        story = generate_story(child_name, favorite_animal, theme, story_length, language)
        st.subheader("Your Story:")
        st.write(story)

        # Verdeel het verhaal in alinea's en genereer illustraties
        paragraphs = story.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                st.write(f"**Page {i+1}:** {paragraph.strip()}")
                illustration = generate_illustration(paragraph.strip(), theme)
                st.image(illustration, use_column_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Developed with ❤️ by [StoryNest](https://yourwebsite.com)"
)
