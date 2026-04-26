from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        return f"""
        <h1>Respuesta del agente:</h1>
        <p>{prompt}</p>
        <br><a href="/">Volver</a>
        """
    
    return """
    <h1>YouTube AI Agent</h1>
    <form method="post">
        <textarea name="prompt" rows="8" cols="80" placeholder="Escribe tu prompt aquí"></textarea><br><br>
        <button type="submit">Enviar</button>
    </form>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
