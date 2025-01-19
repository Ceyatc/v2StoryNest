import openai
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Laad de .env-variabelen
load_dotenv()

# Haal de OpenAI API-sleutel op
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY niet gevonden. Controleer je .env-bestand.")

# Instellen van de OpenAI API-sleutel
openai.api_key = openai_api_key

app = Flask(__name__)

@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()

    child_name = data.get("child_name", "Unknown")
    favorite_animal = data.get("favorite_animal", "animal")
    theme = data.get("theme", "adventure")

    prompt = f"Write a children's story about {child_name}, who loves {favorite_animal}, with a theme of {theme}."

    try:
        # Vraag een verhaal op van OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a children's story writer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.8
        )
        story = response['choices'][0]['message']['content']
        return jsonify({"story": story})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
