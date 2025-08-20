# Script de déploiement Docker pour le chatbot RAG AFPA
# Usage: .\docker-deploy.ps1 [build|start|stop|restart|logs|shell|status|help]

# Fonction d'aide
function Show-Help {
    Write-Host "Usage: $PSCommandPath [COMMAND]"
    Write-Host "Commands:"
    Write-Host "  build    - Construit l'image Docker"
    Write-Host "  start    - Démarre les conteneurs"
    Write-Host "  stop     - Arrête les conteneurs"
    Write-Host "  restart  - Redémarre les conteneurs"
    Write-Host "  logs     - Affiche les logs du conteneur"
    Write-Host "  shell    - Ouvre un shell dans le conteneur"
    Write-Host "  status   - Affiche le statut des conteneurs"
    Write-Host "  help     - Affiche cette aide"
}

# Vérification de Docker
function Check-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
    }
    catch {
        Write-Host "Docker n'est pas installé. Veuillez l'installer avant de continuer." -ForegroundColor Red
        exit 1
    }

    try {
        $null = Get-Command docker-compose -ErrorAction Stop
    }
    catch {
        Write-Host "Docker Compose n'est pas installé. Veuillez l'installer avant de continuer." -ForegroundColor Red
        exit 1
    }
}

# Construction de l'image
function Build-Image {
    Write-Host "Construction de l'image Docker..." -ForegroundColor Yellow
    docker-compose build
    Write-Host "Image construite avec succès !" -ForegroundColor Green
}

# Démarrage des conteneurs
function Start-Containers {
    Write-Host "Démarrage des conteneurs..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Conteneurs démarrés avec succès !" -ForegroundColor Green
    Write-Host "L'application est accessible à l'adresse: http://localhost:7860" -ForegroundColor Yellow
}

# Arrêt des conteneurs
function Stop-Containers {
    Write-Host "Arrêt des conteneurs..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "Conteneurs arrêtés avec succès !" -ForegroundColor Green
}

# Redémarrage des conteneurs
function Restart-Containers {
    Write-Host "Redémarrage des conteneurs..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "Conteneurs redémarrés avec succès !" -ForegroundColor Green
}

# Affichage des logs
function Show-Logs {
    Write-Host "Affichage des logs..." -ForegroundColor Yellow
    docker-compose logs
}

# Ouverture d'un shell dans le conteneur
function Open-Shell {
    Write-Host "Ouverture d'un shell dans le conteneur..." -ForegroundColor Yellow
    docker-compose exec chatbot /bin/bash
}

# Affichage du statut des conteneurs
function Show-Status {
    Write-Host "Statut des conteneurs:" -ForegroundColor Yellow
    docker-compose ps
}

# Vérification de Docker
Check-Docker

# Traitement des commandes
$command = $args[0]

switch ($command) {
    "build" { Build-Image }
    "start" { Start-Containers }
    "stop" { Stop-Containers }
    "restart" { Restart-Containers }
    "logs" { Show-Logs }
    "shell" { Open-Shell }
    "status" { Show-Status }
    "help" { Show-Help }
    default {
        if ($command) {
            Write-Host "Commande non reconnue: $command" -ForegroundColor Red
        }
        Show-Help
    }
} 