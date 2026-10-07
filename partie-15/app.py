import os
from pathlib import Path

from flask import Flask

app = Flask(__name__)

# message par défaut si on ne passe pas APP_MESSAGE au docker run
DEFAULT_MESSAGE = Path("message.txt").read_text(encoding="utf-8").strip()


@app.route("/")
def home():
    message = os.getenv("APP_MESSAGE", DEFAULT_MESSAGE)
    return f"<h1>{message}</h1>"


# utilisé par le HEALTHCHECK du Dockerfile
@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
