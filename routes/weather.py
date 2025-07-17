# backend/routes/weather.py

from flask import Blueprint, jsonify, request
import requests
import config

weather_bp = Blueprint("weather", __name__)

OPENWEATHER_API_KEY = config.OPENWEATHER_API_KEY

@weather_bp.route("/weather", methods=["GET"])
def get_weather():
    try:
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        city = request.args.get("city", "Chennai")

        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Weather data fetch failed", "details": data}), 500

        temperature = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]
        weather_desc = data["weather"][0]["description"]

        insight = "✅ Clear weather"
        if "rain" in weather_desc or "storm" in weather_desc:
            insight = "🚨 Rainy or stormy weather"
        elif "cloud" in weather_desc:
            insight = "☁️ Cloudy conditions"
        elif temperature > 40:
            insight = "⛔ Too hot"

        return jsonify({
            "temperature": temperature,
            "wind_speed": wind_speed,
            "description": weather_desc,
            "insight": insight
        })

    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500

@weather_bp.route("/weather/forecast", methods=["GET"])
def get_forecast():
    try:
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Latitude and Longitude required"}), 400

        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Forecast fetch failed", "details": data}), 500

        # Pick one forecast per day at noon
        daily_forecast = {}
        for entry in data["list"]:
            dt_txt = entry["dt_txt"]
            date = dt_txt.split(" ")[0]
            if "12:00:00" in dt_txt:
                daily_forecast[date] = {
                    "temperature": entry["main"]["temp"],
                    "wind_speed": entry["wind"]["speed"],
                    "description": entry["weather"][0]["description"],
                }

        return jsonify(daily_forecast)

    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500