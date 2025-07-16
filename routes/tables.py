from flask import Blueprint, jsonify
from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
collection = db["sample_table"]

tables_bp = Blueprint("tables", __name__)

@tables_bp.route("/table-data", methods=["GET"])
def get_table_data():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
