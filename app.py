from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import config

from routes.users import users_bp
from routes.llms import llm_bp
from routes.tables import tables_bp
from routes.history import history_bp
from routes.weather import weather_bp

app = Flask(__name__)

CORS(
    app,
    origins=[
        "https://hackathon-frontend-delta-six.vercel.app",
        "http://localhost:3000"
    ],
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

client = MongoClient(config.MONGO_URI)
db = client["caterpillar"]
app.config["history"] = db

app.register_blueprint(users_bp, url_prefix="/api")
app.register_blueprint(llm_bp, url_prefix="/api")
app.register_blueprint(tables_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")
app.register_blueprint(weather_bp, url_prefix="/api")

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
