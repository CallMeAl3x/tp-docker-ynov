# Version volontairement mal optimisée :
# le COPY . . passe avant le pip install, donc dès qu'on touche
# à message.txt (ou n'importe quel fichier), Flask est réinstallé.
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
