import os
import time
import json
import shutil
from flask import Flask, request, jsonify
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai

app = Flask(__name__)

# Models configuration
GEMINI_MODELS = [
    {
        "name": "Gemini 2.5 Flash Preview 04-17 (Experimental)",
        "id": "gemini-1.5-flash-latest",
        "description": "Optimized for adaptive thinking and cost efficiency, it accepts audio, images, videos, and text as input and generates text.",
        "limits": {
            "requests_per_minute": 10,
            "tokens_per_minute": 250000,
            "requests_per_day": 500
        }
    },
    {
        "name": "Gemini 2.5 Pro Experimental 03-25 (Experimental)",
        "id": "gemini-1.5-pro-latest",
        "description": "The most advanced reasoning Gemini model, excelling in multimodal understanding, coding, and world knowledge. It supports audio, images, videos, and text inputs and provides text outputs.",
        "limits": {
            "requests_per_minute": 5,
            "tokens_per_minute": 250000,
            "tokens_per_day": 1000000,
            "requests_per_day": 25
        }
    },
    {
        "name": "Gemini 2.0 Flash",
        "id": "gemini-2.0-flash-001",
        "description": "A fast, next-generation multimodal model supporting audio, images, videos, and text inputs, with text, and experimental image outputs, and audio output coming soon. It's designed for diverse tasks and real-time streaming.",
        "limits": {
            "requests_per_minute": 15,
            "tokens_per_minute": 1000000,
            "requests_per_day": 1500
        }
    },
    {
        "name": "Gemini 2.0 Flash-Lite",
        "id": "gemini-2.0-flash-lite-001",
        "description": "A cost-effective version of Gemini 2.0 Flash, optimized for high throughput and low latency, supporting the same input types and providing text output.",
        "limits": {
            "requests_per_minute": 30,
            "tokens_per_minute": 1000000,
            "requests_per_day": 1500
        }
    },
    {
        "name": "Gemini 1.5 Flash",
        "id": "gemini-1.5-flash",
        "description": "Offers fast and versatile performance across various tasks, with audio, images, videos, and text input and text output, also featuring a 2M token context window.",
        "limits": {
            "requests_per_minute": 15,
            "tokens_per_minute": 250000,
            "requests_per_day": 500
        }
    },
]

# Email loader
def load_emails_from_temp(folder="temp"):
    emails = []
    if not os.path.exists(folder):
        print("[!] Temp folder not found.")
        return emails

    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    emails.append(data)
            except Exception as e:
                print(f"[!] Error reading {file}: {e}")
    print(f"[+] Loaded {len(emails)} emails from '{folder}'")
    return emails

# Flask route for listing models
@app.route('/models', methods=['GET'])
def list_models():
    return jsonify(GEMINI_MODELS)

# Flask route for selecting a model and asking questions
@app.route('/ask', methods=['POST'])
def ask_gemini():
    data = request.json

    # Get model ID and query from the request
    model_id = data.get('model_id')
    query = data.get('query')
    if not model_id or not query:
        return jsonify({"error": "model_id and query are required"}), 400

    # Load emails
    emails = load_emails_from_temp()
    if not emails:
        return jsonify({"error": "No emails loaded"}), 400

    # Configure the generative AI
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = GenerativeModel(model_id)

    # Generate the prompt
    prompt = f"Based on these emails:\n\n{json.dumps(emails)}\n\nAnswer this:\n{query}"

    try:
        # Get response from the model
        res = model.generate_content(prompt)
        return jsonify({"response": res.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route for cleanup
@app.route('/cleanup', methods=['POST'])
def cleanup_temp():
    temp_dir = "temp"
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({"message": "Temp folder deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
