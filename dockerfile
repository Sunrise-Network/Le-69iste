# Utiliser une image de base Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port (optionnel, si vous avez un serveur web intégré)
# EXPOSE 8000

# Définir la commande de démarrage
CMD ["python", "bot.py"]