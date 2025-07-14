from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import config  # Import your config

from google import generativeai as genai

# Flask app
app = Flask(__name__)
CORS(app, origins=[
    "https://hackathon-frontend-delta-six.vercel.app",
    "http://localhost:3000"
])

# MongoDB setup
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
collection = db["sample_table"]

@app.route("/")
def home():
    try:
        collections = db.list_collection_names()
        print("✅ MongoDB connected. Collections:", collections)
        return "MongoDB connection successful!"
    except Exception as e:
        print("❌ MongoDB connection error:", e)
        return "MongoDB connection failed."

@app.route("/api/gemini", methods=["POST"])
def call_gemini():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return jsonify({"response": response.text})


if __name__ == "__main__":
    app.run(debug=True)
