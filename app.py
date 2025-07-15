from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import config

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
users_collection = db["users"]

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

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"success": False, "error": "Username already exists"}), 409

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user_id = users_collection.insert_one({
        "username": username,
        "password": hashed_password
    }).inserted_id

    print("✅ User created with ID:", user_id)

    return jsonify({"success": True, "message": "User created successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    stored_hash = user.get("password", "")

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    return jsonify({"success": True, "message": "Login successful"}), 200


if __name__ == "__main__":
    app.run(debug=True)
