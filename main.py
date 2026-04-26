import os
import json
import time
import uuid
import sqlite3
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
# DATABASE (SAAS CORE)
# =========================
os.makedirs("data", exist_ok=True)
DB_PATH = "data/saas.db"

# CORRECCIÓN: Inicializamos la BD al arrancar, pero no dejamos la conexión abierta globalmente.
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
          id TEXT PRIMARY KEY,
          user_id TEXT,
          topic TEXT,
          title TEXT,
          hook TEXT,
          script TEXT,
          viral_score REAL,
          ctr REAL,
          status TEXT,
          created_at TEXT
        )
        """)
        conn.commit()

init_db()

# CORRECCIÓN: Función para obtener una conexión limpia por cada petición web
def get_db_connection():
    return sqlite3.connect(DB_PATH)


# =========================
# USER SYSTEM SIMPLE
# =========================
def get_user():
    return "demo_user"


# =========================
# MULTI AGENT SYSTEM
# =========================
# CORRECCIÓN: Se inyectaron las variables dentro de los f-strings
def agent_idea(topic):
    prompt = f"Genera UNA idea viral de YouTube sobre: {}"
    return model.generate_content(prompt).text


def agent_title(idea):
    prompt = f"Genera un título CTR alto para esta idea: {}"
    return model.generate_content(prompt).text


def agent_script(idea):
    prompt = f"Escribe guion de 15-20 min para: {}"
    return model.generate_content(prompt).text


def agent_seo(title):
    prompt = f"Genera SEO, tags y hashtags para: {}"
    return model.generate_content(prompt).text


# =========================
# SAVE SYSTEM
# =========================
def save_video(user_id, topic, title, hook, script, viral_score):
    video_id = str(uuid.uuid4())
    ctr = round(viral_score * 0.8, 2)
    status = "VIRAL" if viral_score > 80 else "GOOD" if viral_score > 50 else "TEST"

    # CORRECCIÓN: Uso de conexión local para evitar bloqueos (database is locked)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            user_id,
            topic,
            title,
            hook,
            script,
            viral_score,
            ctr,
            status,
            time.strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

    return video_id


# =========================
# GENERATION ENGINE (FASE 5)
# =========================
def generate(topic):
    # CORRECCIÓN: Manejo de errores en caso de que Vertex AI falle
    try:
        user_id = get_user()

        idea = agent_idea(topic)
        title = agent_title(idea)
        script = agent_script(idea)
        seo = agent_seo(title)

        viral_score = min(95, max(40, len(idea) % 100)) # simulación inteligente

        video_id = save_video(user_id, topic, title, idea, script, viral_score)

        return {
            "id": video_id,
            "idea": idea,
            "title": title,
            "script": script,
            "seo": seo,
            "viral_score": viral_score
        }
    except Exception as e:
        return {"error": f"Ocurrió un error al generar con IA: {str(e)}"}


# =========================
# DASHBOARD DATA
# =========================
def dashboard():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, topic, title, viral_score, status, created_at
        FROM videos
        ORDER BY viral_score DESC
        LIMIT 20
        """)
        rows = cursor.fetchall()

        return [
            {
                "id": r[0],
                "topic": r[1],
                "title": r[2],
                "viral_score": r[3],
                "status": r[4],
                "created_at": r[5]
            }
            for r in rows
        ]


# =========================
# FRONTEND SAAS
# =========================
# CORRECCIÓN: Se cambiaron los {} vacíos por variables de Jinja2 {{ variable }}
HTML = """
<h1>🚀 YouTube AI SAAS (FASE 5)</h1>

<form method="post">
 <textarea name="topic" rows="4" cols="70" required placeholder="Escribe el tema de tu video aquí..."></textarea><br><br>
 <button type="submit">Generar sistema completo</button>
</form>

<h2>📊 Dashboard</h2>
<pre>{{ dash }}</pre>

<hr>

<h2>🧠 Última generación</h2>
<pre>{{ response }}</pre>
"""


# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""

    if request.method == "POST":
        topic = request.form.get("topic", "")
        if topic:
            response = json.dumps(generate(topic), indent=2, ensure_ascii=False)

    dash = json.dumps(dashboard(), indent=2, ensure_ascii=False)

    return render_template_string(HTML, response=response, dash=dash)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.json
    return jsonify(generate(data.get("topic", "")))


@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(dashboard())


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
