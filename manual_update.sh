#!/bin/bash

# Nom du conteneur et de l'image
CONTAINER_NAME="le69iste"
IMAGE_NAME="le69iste"

# Fichier de configuration des variables d'environnement
ENV_FILE=".env"

# Fonction pour afficher les messages de log avec timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Arrêter et supprimer le conteneur s'il existe déjà
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    log "Arrêt du conteneur $CONTAINER_NAME"
    docker stop $CONTAINER_NAME
fi

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    log "Suppression du conteneur $CONTAINER_NAME"
    docker rm $CONTAINER_NAME
fi

# Mettre à jour le code depuis le dépôt GitHub
log "Mise à jour du code depuis GitHub"
git pull || { log "Échec de la mise à jour du code depuis GitHub"; exit 1; }

# Construire la nouvelle image Docker
log "Construction de la nouvelle image Docker"
docker build -t $IMAGE_NAME . || { log "Échec de la construction de l'image Docker"; exit 1; }

# Lancer le nouveau conteneur Docker
log "Lancement du nouveau conteneur Docker"
docker run -d --name $CONTAINER_NAME --env-file $ENV_FILE $IMAGE_NAME || { log "Échec du lancement du conteneur Docker"; exit 1; }

log "Mise à jour et redémarrage du conteneur $CONTAINER_NAME complétés avec succès"