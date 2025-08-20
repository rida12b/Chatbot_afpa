#!/bin/bash

# Script de déploiement Docker pour le chatbot RAG AFPA
# Usage: ./docker-deploy.sh [build|start|stop|restart|logs|shell]

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo -e "${YELLOW}Usage: $0 [COMMAND]${NC}"
    echo -e "Commands:"
    echo -e "  ${GREEN}build${NC}    - Construit l'image Docker"
    echo -e "  ${GREEN}start${NC}    - Démarre les conteneurs"
    echo -e "  ${GREEN}stop${NC}     - Arrête les conteneurs"
    echo -e "  ${GREEN}restart${NC}  - Redémarre les conteneurs"
    echo -e "  ${GREEN}logs${NC}     - Affiche les logs du conteneur"
    echo -e "  ${GREEN}shell${NC}    - Ouvre un shell dans le conteneur"
    echo -e "  ${GREEN}status${NC}   - Affiche le statut des conteneurs"
    echo -e "  ${GREEN}help${NC}     - Affiche cette aide"
}

# Vérification de Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
        exit 1
    fi
}

# Construction de l'image
build_image() {
    echo -e "${YELLOW}Construction de l'image Docker...${NC}"
    docker-compose build
    echo -e "${GREEN}Image construite avec succès !${NC}"
}

# Démarrage des conteneurs
start_containers() {
    echo -e "${YELLOW}Démarrage des conteneurs...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Conteneurs démarrés avec succès !${NC}"
    echo -e "${YELLOW}L'application est accessible à l'adresse: ${GREEN}http://localhost:7860${NC}"
}

# Arrêt des conteneurs
stop_containers() {
    echo -e "${YELLOW}Arrêt des conteneurs...${NC}"
    docker-compose down
    echo -e "${GREEN}Conteneurs arrêtés avec succès !${NC}"
}

# Redémarrage des conteneurs
restart_containers() {
    echo -e "${YELLOW}Redémarrage des conteneurs...${NC}"
    docker-compose restart
    echo -e "${GREEN}Conteneurs redémarrés avec succès !${NC}"
}

# Affichage des logs
show_logs() {
    echo -e "${YELLOW}Affichage des logs...${NC}"
    docker-compose logs -f
}

# Ouverture d'un shell dans le conteneur
open_shell() {
    echo -e "${YELLOW}Ouverture d'un shell dans le conteneur...${NC}"
    docker-compose exec chatbot /bin/bash
}

# Affichage du statut des conteneurs
show_status() {
    echo -e "${YELLOW}Statut des conteneurs:${NC}"
    docker-compose ps
}

# Vérification de Docker
check_docker

# Traitement des commandes
case "$1" in
    build)
        build_image
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    status)
        show_status
        ;;
    help|*)
        show_help
        ;;
esac

exit 0 