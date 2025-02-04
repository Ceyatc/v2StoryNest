import os
import openai
import replicate
import streamlit as st
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

# Configure API Keys
openai.api_key = OPENAI_API_KEY
replicate.api_key = REPLICATE_API_KEY

# Set up Streamlit UI
st.title("StoryNest - AI-Generated Children's Stories")
st.sidebar.header("Story Customization")

# Input fields for story customization
child_name = st.sidebar.text_input("Child's Name", "Emma")
favorite_animal = st.sidebar.text_input("Favorite Animal", "Rabbit")

# Select a theme, with an option for random
themes = ["Adventure", "Friendship", "Courage", "Magic", "Random"]
selected_theme = st.sidebar.selectbox("Choose a Theme", themes)

if selected_theme == "Random":
    import random
    selected_theme = random.choice(["Adventure", "Friendship", "Courage", "Magic"])

# Select story length (ENGLISH labels)
story_length = st.sidebar.radio("Story Length", ["Short", "Medium", "Long"])

# Language selection
languages = {
    "English": "en",
    "French": "fr",
    "Dutch": "nl",
    "German": "de",
    "Italian": "it",
    "Spanish": "es",
    "Turkish": "tr",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt"
}
selected_language = st.sidebar.selectbox("Choose Language", list(languages.keys()))

# Button to generate story
if st.sidebar.button("Generate Story"):

    # Story Prompt for OpenAI
    prompt = f"Write a children's story about {child_name}, who loves {favorite_animal}, with a theme of {selected_theme}. \
               Make sure the story has a clear beginning, middle, and logical ending."

    # Adjust length based on selection
    max_tokens = {"Short": 300, "Medium": 600, "Long": 1200}[story_length]

    # Generate story
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # More powerful & logical model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        story = response["choices"][0]["message"]["content"].strip()
    
        # Translate story if needed
        if selected_language != "English":
            story = GoogleTranslator(source="auto", target=languages[selected_language]).translate(story)

        # Display story
        st.subheader("Generated Story")
        st.write(story)

    except Exception as e:
        st.error(f"Failed to generate story. Error: {e}")

    # Image generation
    st.subheader("Story Illustrations")

    story_parts = story.split("\n\n")  # Split story into logical parts
    images = []

    for i, part in enumerate(story_parts):
        image_prompt = f"An illustrated children's book scene for the story: {part}. \
                         The style should be colorful, cartoon-like, and consistent with previous images. No text or numbers."

        try:
            image_url = replicate.run(
                "stability-ai/stable-diffusion-xl",
                input={"prompt": image_prompt, "width": 512, "height": 512, "num_inference_steps": 50}
            )
            if image_url:
                images.append(image_url)
                st.image(image_url, caption=f"Illustration {i+1}")
            else:
                st.warning(f"Failed to generate image for part {i+1}.")
        
        except Exception as e:
            st.error(f"Failed to generate image. Error: {e}")
