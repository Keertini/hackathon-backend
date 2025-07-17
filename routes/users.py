from flask import Blueprint, request, jsonify
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
users_collection = db["users"]

users_bp = Blueprint("users", __name__)

@users_bp.route("/signup", methods=["POST"])
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


@users_bp.route("/login", methods=["POST"])
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

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user_id": str(user["_id"]),
        "username": user["username"]
    }), 200
