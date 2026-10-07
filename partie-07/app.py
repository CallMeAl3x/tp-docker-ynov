from pathlib import Path

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    message = Path("message.txt").read_text(encoding="utf-8").strip()
    return f"<h1>{message}</h1>"


if __name__ == "__main__":
    # 0.0.0.0 sinon on ne peut pas joindre l'appli depuis l'extérieur du conteneur
    app.run(host="0.0.0.0", port=5000)
