from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 YouTube AI System Online"

@app.route("/generate")
def generate():
    return """
🔥 IDEA VIRAL:
Cómo ganar dinero con IA sin programar en 2026

🎯 TÍTULO CTR:
Gana DINERO con IA en 2026 SIN Programar (Método Viral)

⚡ HOOK:
La mayoría usará IA mal… mientras unos pocos la convierten en una máquina de dinero.

🖼 MINIATURA:
Persona sorprendida + dinero + robot IA + texto: “SIN PROGRAMAR”
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
