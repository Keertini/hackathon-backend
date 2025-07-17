from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import config

incident_bp = Blueprint("incident", __name__)
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]

incident_col = db["incidents"]

@incident_bp.route("/incidents", methods=["POST"])
def submit_incident():
    try:
        data = request.json
        user_id = data.get("userId")
        text = data.get("text")

        if not user_id or not text:
            return jsonify({"success": False, "error": "Missing user ID or content"}), 400

        incident = {
            "user_id": ObjectId(user_id),
            "text": text,
            "created_at": datetime.utcnow()
        }

        result = incident_col.insert_one(incident)
        incident["_id"] = str(result.inserted_id)
        incident["user_id"] = str(user_id)
        incident["created_at"] = incident["created_at"].isoformat()

        return jsonify({"success": True, "incident": incident}), 201

    except Exception as e:
        print("❌ Error submitting incident:", e)
        return jsonify({"success": False, "error": "Server error"}), 500


@incident_bp.route("/incidents/<user_id>", methods=["GET"])
def get_incidents(user_id):
    try:
        user_obj_id = ObjectId(user_id)
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid user ID format"}), 400

    try:
        incidents = list(incident_col.find({"user_id": user_obj_id}).sort("created_at", -1))
        for i in incidents:
            i["_id"] = str(i["_id"])
            i["user_id"] = str(i["user_id"])
            i["created_at"] = i["created_at"].isoformat()

        return jsonify({"success": True, "incidents": incidents}), 200

    except Exception as e:
        print("❌ Error loading incidents:", e)
        return jsonify({"success": False, "error": "Server error"}), 500
