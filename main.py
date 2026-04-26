import os
from flask import Flask, request, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# 🔥 Inicializar Vertex AI (Google Gemini)
vertexai.init(project="youtube-ai-docker", location="us-central1")

model = GenerativeModel("gemini-3-pro")

HTML = """
<h1>YouTube AI Agent 🚀</h1>
<form method="post">
  <textarea name="prompt" rows="8" cols="80" placeholder="Escribe tu idea..."></textarea><br><br>
  <button type="submit">Generar</button>
</form>

<hr>
<h2>Respuesta:</h2>
<p>{{response}}</p>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":
        prompt = request.form.get("prompt")

        full_prompt = f"""
Eres un experto en viralidad de YouTube en 2026.
Devuelve:

1. Título CTR máximo
2. Hook de 15 segundos
3. Idea del vídeo
4. Miniatura descripción

Tema: {prompt}
"""

        result = model.generate_content(full_prompt)
        response = result.text

    return render_template_string(HTML, response=response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
