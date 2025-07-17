from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

security_bp = Blueprint("security", __name__)
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
security_collection = db["security"]

@security_bp.route("/security/update", methods=["POST"])
def update_seatbelt_status():
    data = request.json
    username = data.get("username")
    machine_id = data.get("machine_id")
    seatbelt = data.get("seatbelt")  # boolean
    alert_triggered = data.get("safety_alert_triggered", False)

    if not username or not machine_id:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    security_collection.update_one(
        {"username": username, "machine_id": machine_id},
        {
            "$set": {
                "seatbelt": seatbelt,
                "safety_alert_triggered": alert_triggered,
                "last_updated": datetime.utcnow()
            }
        },
        upsert=True
    )

    return jsonify({"success": True}), 200
