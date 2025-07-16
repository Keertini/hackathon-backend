from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import config

# Route Blueprints
from routes.users import users_bp
from routes.llms import llm_bp
from routes.tables import tables_bp 

app = Flask(__name__)
CORS(app, origins=[
    "https://hackathon-frontend-delta-six.vercel.app",
    "http://localhost:3000"
])

# MongoDB setup
client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]

# Register Blueprints
app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(llm_bp, url_prefix="/api")
app.register_blueprint(tables_bp, url_prefix="/api")  # Optional

@app.route("/")
def home():
    try:
        collections = db.list_collection_names()
        print("✅ MongoDB connected. Collections:", collections)
        return "MongoDB connection successful!"
    except Exception as e:
        print("❌ MongoDB connection error:", e)
        return "MongoDB connection failed."

if __name__ == "__main__":
    app.run(debug=True)
