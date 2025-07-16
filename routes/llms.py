from flask import Blueprint, request, jsonify, send_file
from google import generativeai as genai
from utils.tts import generate_tts_audio
import cohere
import config

llm_bp = Blueprint("llm", __name__)

@llm_bp.route("/gemini", methods=["POST"])
def call_gemini():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return jsonify({"response": response.text})

@llm_bp.route("/cohere", methods=["POST"])
def call_cohere():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    co = cohere.Client(config.COHERE_API_KEY)
    response = co.chat(model="command-nightly", message=prompt)
    return jsonify({"response": response.text.strip()})

@llm_bp.route("/tts")
def tts():
    text = request.args.get("text")
    lang = request.args.get("lang", "en")

    if not text:
        return {"error": "No text provided"}, 400

    try:
        buf = generate_tts_audio(text, lang)
        return send_file(buf, mimetype="audio/mpeg")
    except Exception as e:
        print("TTS Error:", e)
        return {"error": str(e)}, 500
