# Image de base Python 3.9 slim
FROM python:3.9-slim

# Éviter les fichiers .pyc et buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Créer les dossiers utilisés par l'application
RUN mkdir -p uploads static/detections

# Exposer le port
EXPOSE 5000

# Variables d'environnement par défaut
ENV PORT=5000
ENV FLASK_DEBUG=False
ENV MODEL_PATH=/app/model/modele_plantes.pt

# Démarrer l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]