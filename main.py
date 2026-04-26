import os
from flask import Flask, request, jsonify, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# =========================
# CONFIG VERTEX AI
# =========================
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "youtube-ai-docker")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 🔥 TU MODELO (el que te funciona)
MODEL_NAME = "gemini-2.5-pro"

model = GenerativeModel(MODEL_NAME)


# =========================
# PROMPT ENGINE PRO
# =========================
def build_prompt(topic: str):
    return f"""
Eres un experto mundial en viralidad de YouTube en 2026.

Devuelve SOLO JSON válido con esta estructura:

{{
  "title": "",
  "hook": "",
  "idea": "",
  "thumbnail": "",
  "description": "",
  "hashtags": []
}}

REGLAS:
- Máximo CTR posible
- Estilo MrBeast + storytelling + psicología viral
- Optimizado para retención >70%
- Sin explicaciones, SOLO JSON

Tema:
{topic}
"""


# =========================
# FRONTEND SIMPLE
# =========================
HTML = """
<h1>🚀 AI YouTube Engine PRO</h1>

<form method="post">
  <textarea name="topic" rows="6" cols="80" placeholder="Escribe tu idea..."></textarea><br><br>
  <button type="submit">Generar</button>
</form>

<hr>

<pre style="white-space: pre-wrap;">{{response}}</pre>
"""


# =========================
# ROUTE WEB
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    try:
        if request.method == "POST":
            topic = request.form.get("topic")

            prompt = build_prompt(topic)

            result = model.generate_content(prompt)

            response = result.text

    except Exception as e:
        response = f"❌ ERROR: {str(e)}"

    return render_template_string(HTML, response=response)


# =========================
# API MODE (para apps futuras)
# =========================
@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        data = request.json
        topic = data.get("topic", "")

        prompt = build_prompt(topic)

        result = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "data": result.text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
