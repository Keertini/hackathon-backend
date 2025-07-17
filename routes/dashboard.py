from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

dashboard_bp = Blueprint("dashboard", __name__)
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]

users_col = db["users"]
tasks_col = db["tasks"]
user_tasks_col = db["user_tasks"]

@dashboard_bp.route("/dashboard/<user_id>", methods=["GET"])
def get_assigned_tasks(user_id):
    try:
        user_obj_id = ObjectId(user_id)
        user = users_col.find_one({"_id": user_obj_id})
        if not user:
            print("User not found:", user_id)
            return jsonify({"success": False, "error": "User not found"}), 404

        assignments = list(user_tasks_col.find({"user_id": user_obj_id}))
        print("Assignments:", assignments)

        task_ids = [a["task_id"] for a in assignments]
        tasks = list(tasks_col.find({"task_id": {"$in": task_ids}}))
        print("Tasks:", tasks)

        task_map = {t["task_id"]: t for t in tasks}

        combined = []
        for a in assignments:
            task_info = task_map.get(a["task_id"])
            if task_info:
                combined.append({
                    "task_id": task_info["task_id"],
                    "task": task_info["task"],
                    "time": task_info.get("time", "N/A"),
                    "status": a["status"]
                })

        print("Combined tasks:", combined)
        return jsonify({"success": True, "tasks": combined})
    except Exception as e:
        print("❌ Error in get_assigned_tasks:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

@dashboard_bp.route("/dashboard/<user_id>/<task_id>", methods=["PUT"])
def update_task_status(user_id, task_id):
    try:
        new_status = request.json.get("status")
        if not new_status:
            return jsonify({"success": False, "error": "Missing status"}), 400

        result = user_tasks_col.update_one(
            {"user_id": ObjectId(user_id), "task_id": task_id},
            {"$set": {"status": new_status}}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Assignment not found"}), 404

        return jsonify({"success": True})
    except Exception as e:
        print("❌ Error updating status:", e)
        return jsonify({"success": False, "error": "Server error"}), 500
