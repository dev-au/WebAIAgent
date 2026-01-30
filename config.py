import os

from dotenv import load_dotenv

from google import genai

load_dotenv()

__GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

CLIENT = genai.Client(api_key=__GEMINI_API_KEY)
