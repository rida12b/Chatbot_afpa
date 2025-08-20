FROM python:3.10-slim

# Ajout de labels pour la documentation
LABEL maintainer="AFPA"
LABEL version="1.0"
LABEL description="Chatbot RAG AFPA basé sur LangChain"

# Définition du répertoire de travail
WORKDIR /app

# Configuration des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Installation des dépendances système avec nettoyage dans la même couche
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libreoffice \
    libgl1 \         
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création de la structure de répertoires
RUN mkdir -p data/vectors data/url models

# Copie et installation des dépendances Python (séparées pour optimiser le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie des fichiers de l'application
COPY src/ ./src/


# Création d'un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exposition du port
EXPOSE 7860

# Vérification de la santé de l'application
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Commande de démarrage
CMD ["python", "src/app.py"]
