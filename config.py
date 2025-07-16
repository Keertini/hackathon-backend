import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from google import generativeai as genai
import cohere

# Load .env
load_dotenv()

# MongoDB credentials
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

if not MONGO_USERNAME or not MONGO_PASSWORD:
    raise ValueError("MONGO_USERNAME and MONGO_PASSWORD must be set in .env")

# MongoDB URI
MONGO_URI = (
    f"mongodb+srv://{MONGO_USERNAME}:{quote_plus(MONGO_PASSWORD)}"
    "@cluster0.n5rezic.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY must be set in .env")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Cohere API Key
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY must be set in .env")

# Create Cohere client instance
cohere_client = cohere.Client(COHERE_API_KEY)
