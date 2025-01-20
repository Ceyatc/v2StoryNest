import os
import openai
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Haal API-sleutels op vanuit Streamlit Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

# Functie voor het genereren van een verhaal
def generate_story(child_name, favorite_animal, theme, length):
    length_map = {"Kort": 200, "Middel": 500, "Lang": 1000}
    max_tokens = length_map[length]
    prompt = (
        f"Write a children's story about {child_name}, who loves {favorite_animal}, "
        f"with a theme of {theme}. Make it a {length.lower()} story suitable for children."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    )
    story = response["choices"][0]["message"]["content"]
    return story

# Functie voor het genereren van illustraties
def generate_illustration(prompt):
    dalle_prompt = (
        f"A children's cartoon-style illustration of {prompt}. "
        "Bright colors, consistent style, suitable for a children's book."
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

# Extra informatie
extra_info = st.sidebar.text_area(
    "Additional Information (Optional)",
    "Provide extra details to make the story unique (e.g., hobbies, places, friends)."
)

# Verhaal genereren
if st.sidebar.button("Generate Story"):
    with st.spinner("Generating your story and illustrations..."):
        story = generate_story(child_name, favorite_animal, theme, story_length)
        st.subheader("Your Story:")
        st.write(story)

        # Verdeel het verhaal in alinea's en genereer illustraties
        paragraphs = story.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                st.write(f"**Page {i+1}:** {paragraph.strip()}")
                illustration = generate_illustration(paragraph.strip())
                st.image(illustration, use_column_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Developed with ❤️ by [StoryNest](https://yourwebsite.com)"
)
