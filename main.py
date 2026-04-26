import os
from flask import Flask, request, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# 🔥 CONFIG VERTEX AI (PROYECTO ÚNICO)
PROJECT_ID = "youtube-ai-docker"
LOCATION = "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

# ✅ MODELO ESTABLE (NO USAR gemini-3-pro)
model = GenerativeModel(
    "projects/youtube-ai-docker/locations/us-central1/publishers/google/models/gemini-1.5-pro"
)

# 🧠 UI SIMPLE
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube AI Agent</title>
</head>
<body>
    <h1>🔥 YouTube AI Agent</h1>

    <form method="post">
        <textarea name="prompt" rows="10" cols="80" placeholder="Escribe tu idea aquí..."></textarea><br><br>
        <button type="submit">Generar</button>
    </form>

    <hr>

    <h2>Respuesta:</h2>
    <pre style="white-space: pre-wrap;">{{response}}</pre>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    try:
        if request.method == "POST":
            prompt = request.form.get("prompt", "")

            full_prompt = f"""
Eres un experto en viralidad de YouTube en 2026.

Devuelve en formato claro:

1. Título CTR máximo (muy viral)
2. Hook de 15 segundos
3. Idea del vídeo
4. Descripción de miniatura

Tema:
{prompt}
"""

            result = model.generate_content(full_prompt)
            response = result.text

    except Exception as e:
        # 🔥 EVITA CRASH TOTAL EN CLOUD RUN
        response = f"Error interno: {str(e)}"

    return render_template_string(HTML, response=response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
