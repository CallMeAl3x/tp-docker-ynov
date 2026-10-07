# 1re étape : on installe juste les dépendances dans /install
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --target=/install -r requirements.txt


# 2e étape : l'image finale, on ne récupère que ce qui a été installé
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local/lib/python3.12/site-packages
COPY app.py .
COPY message.txt .

EXPOSE 5000

CMD ["python", "app.py"]
