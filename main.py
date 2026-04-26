import os
import json
from flask import Flask, request, render_template_string, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# =========================
# VERTEX AI CONFIG
# =========================
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "youtube-ai-docker")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 🔥 tu modelo (el que ya te funciona)
model = GenerativeModel("gemini-2.5-pro")


# =========================
# PROMPT ULTRA CONTROLADO
# =========================
def build_prompt(topic: str):
    return f"""
Eres un sistema de generación de contenido viral de YouTube 2026.

OBLIGATORIO:
- Responde SOLO JSON válido
- Sin texto adicional
- Sin markdown
- Sin explicaciones

FORMATO EXACTO:

{{
  "title": "",
  "hook": "",
  "idea": "",
  "script": "",
  "thumbnail": "",
  "description": "",
  "hashtags": []
}}

REGLAS:
- CTR máximo
- Estilo viral (retención + storytelling)
- Hook potente en 15 segundos
- Optimizado para YouTube Shorts + long form

TEMA:
{topic}
"""


# =========================
# VALIDACIÓN JSON (CLAVE PRO)
# =========================
def safe_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


# =========================
# FRONT WEB
# =========================
HTML = """
<h1>🚀 AI YouTube Engine PRO (Phase 1)</h1>

<form method="post">
  <textarea name="topic" rows="6" cols="80" placeholder="Escribe tu idea..."></textarea><br><br>
  <button type="submit">Generar</button>
</form>

<hr>

<pre style="white-space: pre-wrap;">{{response}}</pre>
"""


# =========================
# CORE GENERATION
# =========================
def generate(topic: str):
    prompt = build_prompt(topic)

    result = model.generate_content(prompt)
    text = result.text

    parsed = safe_parse(text)

    # 🔁 REINTENTO SI FALLA JSON
    if parsed is None:
        retry_prompt = build_prompt(topic) + "\nIMPORTANTE: SOLO JSON VÁLIDO SIN ERRORES."
        retry = model.generate_content(retry_prompt)
        parsed = safe_parse(retry.text)

    return parsed or {
        "error": "No se pudo generar JSON válido",
        "raw": text
    }


# =========================
# WEB ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":
        topic = request.form.get("topic", "")
        response = json.dumps(generate(topic), indent=2, ensure_ascii=False)

    return render_template_string(HTML, response=response)


# =========================
# API (para futuro SaaS)
# =========================
@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        data = request.json
        topic = data.get("topic", "")

        result = generate(topic)

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
