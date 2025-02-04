import openai
import requests
import streamlit as st
import json
import os

# Laden van API Keys vanuit Streamlit Secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
leonardo_api_key = os.getenv("LEONARDO_API_KEY")

# Functie om een verhaal te genereren met een logische opbouw
def generate_story(character_name, favorite_animal, theme, length, language):
    prompts = {
        "Adventure": f"A thrilling adventure about {character_name} and their beloved {favorite_animal}.",
        "Fantasy": f"A magical journey where {character_name} discovers a hidden world with {favorite_animal}.",
        "Mystery": f"A suspenseful tale where {character_name} solves a mystery with {favorite_animal}.",
        "Friendship": f"A heartwarming story about {character_name} and {favorite_animal} learning the value of friendship.",
    }
    
    prompt = prompts.get(theme, "A unique children's story.")

    # Story length settings
    story_lengths = {"Short": 400, "Medium": 800, "Long": 1500}
    max_tokens = story_lengths.get(length, 800)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Write a children's story with a clear beginning, middle, and end."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

# Functie om een illustratie te genereren met Leonardo AI
def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {leonardo_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "model": "stable-diffusion-xl",
        "num_images": 1,
        "aspect_ratio": "16:9",
        "negative_prompt": "text, watermark, logo, blurry, distorted"
    }

    response = requests.post("https://cloud.leonardo.ai/api/generate", headers=headers, json=payload)
    if response.status_code == 200:
        image_data = response.json()
        image_url = image_data["images"][0]["url"]
        return image_url
    else:
        return None

# Streamlit Webinterface
st.title("StoryNest - AI Generated Children's Stories & Illustrations")

# Gebruikersinput
character_name = st.text_input("Enter the child's name:")
favorite_animal = st.text_input("Enter the child's favorite animal:")
story_length = st.selectbox("Select story length:", ["Short", "Medium", "Long"])
story_theme = st.selectbox("Select story theme:", ["Adventure", "Fantasy", "Mystery", "Friendship"])
story_language = st.selectbox("Select language:", ["English", "French", "Dutch", "German", "Italian", "Spanish", "Turkish", "Japanese", "Korean", "Portuguese"])

if st.button("Generate Story & Illustrations"):
    if character_name and favorite_animal:
        story = generate_story(character_name, favorite_animal, story_theme, story_length, story_language)
        st.subheader("Generated Story")
        st.write(story)

        # Illustraties per alinea genereren
        st.subheader("Illustrations")
        story_sentences = story.split(". ")
        for i, sentence in enumerate(story_sentences[:5]):
            image_url = generate_image(f"{sentence}, child illustration, cartoon style")
            if image_url:
                st.image(image_url, caption=f"Illustration {i+1}", use_column_width=True)
            else:
                st.write("Failed to generate image.")

    else:
        st.warning("Please fill in all fields.")
