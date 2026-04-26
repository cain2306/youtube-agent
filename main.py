import os
import json
import time
import uuid
import re
from flask import Flask, request, render_template_string, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# =========================
# VERTEX AI
# =========================
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "youtube-ai-docker")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("gemini-2.5-pro")


# =========================
# STORAGE CONFIG
# =========================
DATA_DIR = "data/videos"
os.makedirs(DATA_DIR, exist_ok=True)


# =========================
# AUTO SAVE FUNCTION
# =========================
def save_result(topic, data):
    video_id = str(uuid.uuid4())

    file_path = os.path.join(DATA_DIR, f"video_{video_id}.json")

    payload = {
        "id": video_id,
        "topic": topic,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[YT-ENGINE] Saved: {file_path}")

    return file_path


# =========================
# PROMPT ENGINE
# =========================
def build_prompt(topic: str):
    return f"""
Eres un experto en YouTube 2026.

Devuelve SOLO JSON válido SIN markdown, SIN texto extra.

FORMATO EXACTO:

{{
  "video_idea": "",
  "title_primary": "",
  "title_secondary": "",
  "description_seo": "",
  "tags": [],
  "hashtags": [],
  "thumbnail_description": "",
  "hook": "",
  "full_script_15_20min": [
    {{
      "part": "Intro",
      "duration": "0-1:30",
      "content": ""
    }},
    {{
      "part": "Setup",
      "duration": "1:30-5:00",
      "content": ""
    }},
    {{
      "part": "Development",
      "duration": "5:00-12:00",
      "content": ""
    }},
    {{
      "part": "Climax",
      "duration": "12:00-17:00",
      "content": ""
    }},
    {{
      "part": "Ending",
      "duration": "17:00-20:00",
      "content": ""
    }}
  ],
  "retention_strategy": {{
    "open_loops": [],
    "engagement_tricks": []
  }}
}}

TEMA:
{topic}
"""


# =========================
# SAFE JSON PARSER (ROBUST FINAL FIXED)
# =========================
def safe_json(text):
    try:
        if not text:
            return None

        text = text.strip()

        # quitar markdown si aparece
        if "```" in text:
            parts = text.split("```")
            for p in parts:
                if "{" in p:
                    text = p
                    break

        # extraer SOLO JSON real (evita texto basura antes/después)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

        return json.loads(text)

    except Exception as e:
        print(f"[YT-ENGINE] JSON parse error: {e}")
        return None


# =========================
# GENERATION CORE (STABLE FINAL)
# =========================
def generate(topic):
    prompt = build_prompt(topic)

    print(f"[YT-ENGINE] Topic: {topic}")

    try:
        result = model.generate_content(prompt)
        text = getattr(result, "text", "") or ""
    except Exception as e:
        return {"error": f"vertex_ai_failed: {str(e)}"}

    parsed = safe_json(text)

    # retry automático si falla JSON
    if parsed is None:
        print("[YT-ENGINE] Retry JSON generation...")

        try:
            result = model.generate_content(
                prompt + "\nIMPORTANTE: SOLO JSON válido, sin ``` ni texto adicional."
            )
            text_retry = getattr(result, "text", "") or ""
            parsed = safe_json(text_retry)
        except Exception as e:
            print(f"[YT-ENGINE] Retry failed: {e}")
            parsed = None

    if parsed is None:
        parsed = {
            "error": "invalid json",
            "raw": text
        }

    file_path = save_result(topic, parsed)

    return {
        "saved_to": file_path,
        "result": parsed
    }


# =========================
# FRONTEND
# =========================
HTML = """
<h1>🚀 AI YouTube Engine PRO (FINAL STABLE)</h1>

<form method="post">
  <textarea name="topic" rows="6" cols="80" placeholder="Ej: ganar dinero con IA"></textarea><br><br>
  <button type="submit">Generar y Guardar</button>
</form>

<hr>

<pre style="white-space: pre-wrap;">{{response}}</pre>
"""


# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":
        topic = request.form.get("topic", "")
        response = json.dumps(generate(topic), indent=2, ensure_ascii=False)

    return render_template_string(HTML, response=response)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.json
    topic = data.get("topic", "")

    return jsonify(generate(topic))


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
