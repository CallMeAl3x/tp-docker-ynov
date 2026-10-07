FROM python:3.12-slim

WORKDIR /app

# requirements.txt tout seul d'abord : tant qu'il ne bouge pas,
# le pip install reste en cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# le code en dernier, c'est ce qui change le plus souvent
COPY app.py .
COPY message.txt .

EXPOSE 5000

CMD ["python", "app.py"]
