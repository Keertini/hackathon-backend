from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

user_tasks_bp = Blueprint("user_tasks", __name__)

client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
tasks_col = db["tasks"]
user_tasks_col = db["user_tasks"]
users_col = db["users"]

# Seed tasks and assign them to each user
def seed_tasks_and_assign():
    default_tasks = [
        {"task_id": "T001", "task": "Refuel Machine", "time": "01:00 PM"},
        {"task_id": "T002", "task": "Clean debris from Zone 2", "time": "02:30 PM"},
        {"task_id": "T003", "task": "Pre-Start Checklist", "time": "08:00 AM"},
    ]

    if tasks_col.count_documents({}) == 0:
        tasks_col.insert_many(default_tasks)

    all_tasks = list(tasks_col.find({}))
    all_users = list(users_col.find({}))

    for user in all_users:
        for task in all_tasks:
            existing = user_tasks_col.find_one({
                "user_id": user["_id"],
                "task_id": task["task_id"]
            })

            if not existing:
                user_tasks_col.insert_one({
                    "user_id": user["_id"],
                    "task_id": task["task_id"],
                    "status": "Pending"
                })

# 👇 Call once on startup
seed_tasks_and_assign()

# 🔍 GET tasks for user by ObjectId (pass as string)
@user_tasks_bp.route("/user_tasks/<user_id>", methods=["GET"])
def get_tasks_for_user(user_id):
    try:
        user_obj_id = ObjectId(user_id)
        user_tasks = list(user_tasks_col.find({"user_id": user_obj_id}))
        task_ids = [ut["task_id"] for ut in user_tasks]
        tasks = {t["task_id"]: t for t in tasks_col.find({"task_id": {"$in": task_ids}})}

        result = []
        for ut in user_tasks:
            task = tasks.get(ut["task_id"])
            if task:
                result.append({
                    "task_id": ut["task_id"],
                    "task": task["task"],
                    "time": task["time"],
                    "status": ut["status"]
                })

        return jsonify({"success": True, "tasks": result})
    except Exception as e:
        print("Error fetching user tasks:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# 📝 Update task status for a specific user
@user_tasks_bp.route("/user_tasks/<user_id>/<task_id>", methods=["PUT"])
def update_user_task(user_id, task_id):
    try:
        new_status = request.json.get("status")
        result = user_tasks_col.update_one(
            {"user_id": ObjectId(user_id), "task_id": task_id},
            {"$set": {"status": new_status}}
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Task not found for user"}), 404

        return jsonify({"success": True})
    except Exception as e:
        print("Error updating task:", e)
        return jsonify({"success": False, "error": str(e)}), 500
