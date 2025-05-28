import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Available Gemini Models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"- {m.name} (supported for generateContent)")
    else:
        print(f"- {m.name} (NOT supported for generateContent)")