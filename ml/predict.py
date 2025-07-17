from flask import Blueprint, jsonify
from ml.model import load_model
import random

predict_bp = Blueprint("predict", __name__)
model = load_model()

@predict_bp.route("/predict", methods=["POST"])
def predict_task_time():
    try:
        # Step 1: Randomly generate realistic values
        engine_hours = round(random.uniform(10, 200), 2)
        fuel_used = round(random.uniform(5, 100), 2)
        load_cycles = random.randint(10, 100)
        temperature = random.randint(15, 45)
        wind_speed = random.randint(0, 25)
        humidity = random.randint(20, 90)

        # Step 2: Prepare features
        features = [engine_hours, fuel_used, load_cycles, temperature, wind_speed, humidity]
        prediction = model.predict([features])[0]

        # Step 3: Return both inputs and prediction
        return jsonify({
            "predicted_task_time": round(prediction, 2),
            "input": {
                "engine_hours": engine_hours,
                "fuel_used": fuel_used,
                "load_cycles": load_cycles,
                "temperature": temperature,
                "wind_speed": wind_speed,
                "humidity": humidity
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
