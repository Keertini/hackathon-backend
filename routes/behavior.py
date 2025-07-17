from flask import Blueprint, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import config

behavior_bp = Blueprint("behavior", __name__)
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
telemetry_col = db["task_history"]

@behavior_bp.route("/behavior/<machine_id>", methods=["GET"])
def analyze_behavior(machine_id):
    try:
        # Fetch latest 100 records for the machine
        records = list(telemetry_col.find({"machine_id": machine_id}).sort("timestamp", -1).limit(100))

        if not records:
            return jsonify({"success": False, "error": "No telemetry data found"}), 404

        alerts = []

        # Sort by time ascending
        records.reverse()

        # EXCESSIVE IDLING: no change in load_cycles for > 5 mins
        idle_start = None
        for i in range(1, len(records)):
            prev, curr = records[i - 1], records[i]
            t1 = datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(curr["timestamp"].replace("Z", "+00:00"))
            if curr["load_cycles"] == prev["load_cycles"]:
                if idle_start is None:
                    idle_start = t1
                if (t2 - idle_start) > timedelta(minutes=5):
                    alerts.append("🟡 Excessive idling detected (>5 minutes)")
                    break
            else:
                idle_start = None

        # HARSH OPERATION: load_cycles jump > threshold
        for i in range(1, len(records)):
            delta = records[i]["load_cycles"] - records[i - 1]["load_cycles"]
            if delta > 10:
                alerts.append("🔴 Harsh operation detected (spike in load cycles)")
                break

        # OVERUSE: task_time > 8 hours/day
        total_task_time = sum([r.get("task_time", 0) for r in records])
        avg_task_time = total_task_time / len(records)
        if avg_task_time > 8:
            alerts.append("🟠 Machine overused (avg task time > 8 hrs/day)")

        # WEATHER-RELATED (optional)
        for r in records:
            if r["temperature"] > 45 or r["wind_speed"] > 30:
                alerts.append("⚠️ Unsafe weather conditions detected")
                break

        return jsonify({
            "success": True,
            "machine_id": machine_id,
            "alerts": list(set(alerts)),  # remove duplicates
            "record_count": len(records)
        })

    except Exception as e:
        print("❌ Behavior analysis error:", e)
        return jsonify({"success": False, "error": "Server error"}), 500
