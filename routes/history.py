from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

history_bp = Blueprint("history", __name__)

client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
history_collection = db["history"]

@history_bp.route("/history/<username>", methods=["GET"])
def get_history(username):
    try:
        history_items = list(history_collection.find({"username": username}).sort("created_at", -1))
        for item in history_items:
            item["_id"] = str(item["_id"])
        return jsonify({"success": True, "history": history_items})
    except Exception as e:
        print("Error fetching history:", e)
        return jsonify({"success": False, "error": "Could not fetch history"}), 500

@history_bp.route("/save_history", methods=["POST", "OPTIONS"])
def save_history():
    if request.method == "OPTIONS":
        return "", 200
    try:
        data = request.json
        username = data.get("username")
        prompt = data.get("prompt")
        response = data.get("response")
        language = data.get("language", "en-US")

        if not username or not prompt or not response:
            return jsonify({"success": False, "error": "Missing fields"}), 400

        history_collection.insert_one({
            "username": username,
            "prompt": prompt,
            "response": response,
            "language": language,
            "created_at": datetime.utcnow()
        })

        return jsonify({"success": True}), 201
    except Exception as e:
        print("Error saving history:", e)
        return jsonify({"success": False, "error": "Could not save history"}), 500
