FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY message.txt .

# on crée un utilisateur sans shell et on lui donne /app
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

# à partir d'ici tout tourne en appuser, plus en root
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
