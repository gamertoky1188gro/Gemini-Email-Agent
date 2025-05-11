import os
import time
import json
import shutil
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai

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
    {
        "name": "Gemini 1.5 Flash-8B",
        "id": "gemini-1.5-flash-8b",
        "description": "Designed for high-volume and lower-intelligence tasks, it supports multimodal inputs and text output.",
        "limits": {
            "requests_per_minute": 15,
            "tokens_per_minute": 250000,
            "requests_per_day": 500
        }
    },
    {
        "name": "Gemma 3",
        "id": "gemma-3",
        "description": "A small-sized, lightweight open model for text generation and image understanding.",
        "limits": {
            "requests_per_minute": 30,
            "tokens_per_minute": 15000,
            "requests_per_day": 14400
        }
    },
    {
        "name": "Gemini Embedding Experimental 03-07",
        "id": "embedding-001",
        "description": "Creates text embeddings to measure the relatedness of text strings.",
        "limits": {
            "requests_per_minute": 5,
            "requests_per_day": 100
        }
    }
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

# Gemini agent functions
def select_model():
    print("[?] Select a Gemini model:")
    for i, model in enumerate(GEMINI_MODELS, 1):
        print(f" {i}. {model['name']}")
        print(f"    {model['description']}")
        print(f"    Limits: {json.dumps(model['limits'])}\n")

    while True:
        try:
            choice = int(input("> "))
            if 1 <= choice <= len(GEMINI_MODELS):
                return GEMINI_MODELS[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(GEMINI_MODELS)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def ask_loop(model_id, all_emails):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = GenerativeModel(model_id)
    history = []

    print("\n[+] Ask about your emails. Type 'exit()' to quit.\n")
    while True:
        query = input("You: ")
        if query.strip() == "exit()":
            break
        prompt = f"Based on these emails:\n\n{json.dumps(all_emails)}\n\nAnswer this:\n{query}"
        try:
            res = model.generate_content(prompt)
            print("AI:", res.text.strip())
        except Exception as e:
            print("[!] Error with Gemini:", e)
        time.sleep(0.5)

def cleanup_prompt(temp_dir="temp"):
    choice = input("\nDo you want to delete the temp folder? (y/n): ").strip().lower()
    if choice == "y":
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("[+] Temp folder deleted.")
    else:
        print("[+] Temp folder preserved.")

# Main program
def main():
    print("== Gemini Email Agent ==")
    model_info = select_model()
    print(f"\n[+] Selected model: {model_info['name']}")

    emails = load_emails_from_temp()
    if not emails:
        print("[!] No emails loaded. Exiting.")
        return

    ask_loop(model_info['id'], emails)
    cleanup_prompt()

if __name__ == "__main__":
    main()
