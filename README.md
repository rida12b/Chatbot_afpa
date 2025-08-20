# Chatbot RAG de l'AFPA : Documentation Technique Complète

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python) ![Flask](https://img.shields.io/badge/Flask-black?logo=flask) ![Docker](https://img.shields.io/badge/Docker-blue?logo=docker) ![Azure](https://img.shields.io/badge/Azure-blue?logo=microsoftazure) ![CI Status](https://img.shields.io/badge/CI-Passing-brightgreen?logo=githubactions)

## Table des Matières

1.  [Présentation du Projet](#1-presentation-du-projet)
2.  [Fonctionnalités Clés](#2-fonctionnalites-cles)
3.  [Architecture du Système](#3-architecture-du-systeme)
    *   [Phase 1 : Indexation (Offline)](#phase-1-indexation-offline)
    *   [Phase 2 : Requête (Online)](#phase-2-requete-online)
4.  [Structure du Projet](#4-structure-du-projet)
5.  [Installation et Configuration](#5-installation-et-configuration)
    *   [Prérequis](#prerequis)
    *   [Étape 1 : Configuration de l'Environnement](#etape-1-configuration-de-lenvironnement)
    *   [Étape 2 : Installation des Dépendances](#etape-2-installation-des-dependances)
6.  [Guide d'Utilisation](#6-guide-dutilisation)
    *   [Étape 0 : Récupération des Données Sources (Prérequis)](#etape-0-recuperation-des-donnees-sources-prerequis)
    *   [Étape 1 : Ingestion des Données](#etape-1-ingestion-des-donnees)
    *   [Étape 2 : Lancement de l'Application](#etape-2-lancement-de-lapplication)
7.  [Tests Automatisés](#7-tests-automatises)
8.  [Déploiement](#8-deploiement)
    *   [8.1. Checklist de Sécurité](#81-checklist-de-securite)
    *   [8.2. Déploiement avec Docker (Local)](#82-deploiement-avec-docker-local)
    *   [8.3. Déploiement sur Azure (Production)](#83-deploiement-sur-azure-production)
9.  [Maintenance et Mises à Jour](#9-maintenance-et-mises-a-jour)
    *   [Mise à Jour de la Base de Connaissances](#mise-a-jour-de-la-base-de-connaissances)
    *   [Consultation des Logs](#consultation-des-logs)
10. [Intégration Continue (CI/CD)](#10-integration-continue-cicd)

## 1. Présentation du Projet

Ce projet est un assistant conversationnel intelligent (chatbot) basé sur une architecture **RAG (Retrieval-Augmented Generation)**. Sa mission est de fournir des réponses précises et contextuelles aux questions des collaborateurs de l'AFPA en s'appuyant exclusivement sur une base de documents d'entreprise validés.

Il est conçu pour être **déployable en local** pour le développement et **prêt pour la production** sur une infrastructure cloud comme Azure, grâce à une configuration flexible et une conteneurisation Docker.

## 2. Fonctionnalités Clés

*   **Ingestion de Données Polyvalente** : Capacité à traiter de multiples formats de fichiers (PDF, PPTX, DOCX, etc.) depuis des sources locales ou un stockage cloud (Azure Blob Storage).
*   **Recherche Hybride Avancée** : Combine la **recherche sémantique** (vectorielle) pour comprendre l'intention et la **recherche par mots-clés** pour la précision, garantissant une pertinence maximale des résultats.
*   **Architecture Unifiée et Performante** : Utilise une base de données vectorielle unique qui lie le contenu, les métadonnées et les URLs des documents dès l'indexation, simplifiant la logique et accélérant les temps de réponse.
*   **Sécurité et Authentification** : Système de connexion robuste avec gestion des rôles (Utilisateur, Administrateur) et protection des routes.
*   **Prêt pour la Production** : Déploiement simplifié via Docker, gestion centralisée de la configuration (`.env`), logging structuré et tests automatisés.
*   **CI/CD Intégrée** : Un workflow GitHub Actions est inclus pour exécuter automatiquement les tests à chaque modification du code, garantissant la stabilité du projet.

## 3. Architecture du Système

L'architecture est divisée en deux phases distinctes pour optimiser la performance et la maintenabilité.

### Phase 1 : Indexation (Offline)

Ce processus transforme les documents bruts en une base de connaissances interrogeable. Il est exécuté par le script `src/create_unified_vectordb.py`.

1.  **Source des Données** : Le script lit les documents soit depuis le dossier local `data/documents/`, soit depuis un conteneur Azure Blob Storage, en fonction de la variable `DATA_SOURCE` dans le fichier `.env`.
2.  **Extraction de Texte** : Le contenu textuel de chaque document est extrait (la logique est dans `src/ingestion.py`).
3.  **Chunking** : Le texte est divisé en petits morceaux de texte (chunks) pertinents.
4.  **Enrichissement des Métadonnées** : Chaque chunk est associé à des métadonnées (titre du document source, catégorie, et URL si disponible).
5.  **Vectorisation (Embedding)** : Les chunks sont transformés en vecteurs numériques via un modèle Sentence-Transformer.
6.  **Stockage** : Les vecteurs sont stockés dans un index **FAISS** pour une recherche ultra-rapide. Les chunks et métadonnées sont sauvegardés dans des fichiers `.json` et `.pkl`.

**Artefacts produits dans le dossier `models/` :** `unified_index.bin`, `unified_chunks.json`, `unified_metadata.pkl`.

### Phase 2 : Requête (Online)

Ce processus se déroule en temps réel lorsqu'un utilisateur interagit avec l'application. Il est géré par `src/app_unified.py`.

1.  **Requête Utilisateur** : L'utilisateur envoie une question via l'interface web Flask.
2.  **Recherche Hybride** : La question est utilisée pour interroger la base de connaissances :
    *   Une recherche vectorielle est effectuée sur l'index FAISS pour trouver les chunks sémantiquement similaires.
    *   Une recherche par mots-clés est effectuée pour trouver les correspondances exactes.
    *   Les résultats sont fusionnés et reclassés pour une pertinence optimale.
3.  **Génération du Contexte** : Les chunks les plus pertinents et leurs métadonnées sont assemblés pour former un contexte.
4.  **Appel au LLM** : Le contexte et la question initiale sont envoyés à **Azure OpenAI**.
5.  **Génération de la Réponse** : Le LLM synthétise une réponse structurée en HTML en se basant *uniquement* sur le contexte fourni.
6.  **Affichage** : La réponse HTML est transmise à l'interface utilisateur et affichée dans le navigateur.

## 4. Structure du Projet

```
chatbot_rag_project/
│
├── .github/workflows/      # Workflows d'intégration continue (CI/CD)
│   └── ci.yml              # Exécute les tests automatiquement
│
├── data/                   # Données non versionnées (utilisées en local)
│   └── documents/          # (À créer) Placer ici les documents sources
│
├── models/                 # Base de connaissances générée (non versionnée)
│
├── src/                    # Code source de l'application
│   ├── static/             # Fichiers CSS et JavaScript
│   │   └── js/main.js
│   ├── templates/          # Fichiers HTML (Flask/Jinja2)
│   ├── app_unified.py      # ✅ Application web Flask principale
│   ├── auth.py             # Module d'authentification et de gestion des utilisateurs
│   ├── create_unified_vectordb.py # ✅ Script d'ingestion et d'indexation
│   └── ingestion.py        # Fonctions d'extraction de texte
│
├── tests/                  # Tests automatisés
│   └── test_auth.py        # Tests unitaires pour le module d'authentification
│
├── .env.example            # Template pour le fichier de configuration
├── docker-compose.yml      # Configuration pour le déploiement Docker
├── Dockerfile              # Instructions pour construire l'image Docker
├── pyproject.toml          # Fichier de configuration du projet et de pytest
├── requirements.txt        # Dépendances Python
└── README.md               # Cette documentation
```

## 5. Installation et Configuration

### Prérequis

*   Git
*   Python 3.10+
*   Docker & Docker Compose
*   **Tesseract OCR** :
    *   Sous Windows (PowerShell) : `winget install --id=UB-Mannheim.TesseractOCR`
    *   Sous Linux (Debian/Ubuntu) : `sudo apt-get install tesseract-ocr`

### Étape 1 : Configuration de l'Environnement

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/rida12b/Chatbot_afpa.git
    cd chatbot_rag_project
    ```
2.  **Créez et configurez votre fichier d'environnement :**
    Copiez le fichier d'exemple. C'est votre fichier de configuration personnel, **il ne doit jamais être partagé ou versionné**.
    ```bash
    # Sous Linux/macOS
    cp .env.example .env

    # Sous Windows
    copy .env.example .env
    ```
3.  **Modifiez le fichier `.env`** avec vos propres valeurs.

    *   **Pour un usage 100% local :**
        Assurez-vous que `DATA_SOURCE` est réglé sur `local`. Vous n'avez pas besoin de remplir les variables Azure.
        ```env
        DATA_SOURCE=local
        FLASK_SECRET_KEY="changez-moi-avec-une-cle-secrete-forte"
        # Les variables Azure peuvent rester vides
        AZURE_INFERENCE_SDK_ENDPOINT=""
        ...
        ```

    *   **Pour un usage connecté à Azure :**
        Réglez `DATA_SOURCE` sur `azure` et remplissez **toutes** les variables Azure.
        ```env
        DATA_SOURCE=azure
        FLASK_SECRET_KEY="changez-moi-avec-une-cle-secrete-forte"
        AZURE_INFERENCE_SDK_ENDPOINT="https://..."
        AZURE_OPENAI_API_KEY="..."
        DEPLOYMENT_NAME="..."
        AZURE_SAS_URL="https://..."
        ```

### Étape 2 : Installation des Dépendances

Créez un environnement virtuel et installez les packages requis.

```bash
# Créez l'environnement virtuel
python -m venv venv

# Activez-le
# Sous Windows (PowerShell)
# .\venv\Scripts\Activate.ps1
# Sous Linux/macOS
# source venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt
```

## 6. Guide d'Utilisation

### Étape 0 : Récupération des Données Sources (Prérequis)

Avant de pouvoir construire la base de connaissances du chatbot, vous devez récupérer les documents qui serviront de source de vérité.

L'ensemble des documents de référence est centralisé sur la plateforme **SharePoint** de l'AFPA.

**Procédure d'accès :**

1.  Connectez-vous au SharePoint de l'AFPA.
2.  Naviguez vers le site **Plateforme E-achats**.
3.  Depuis l'accueil, accédez à la section **FINA**.
4.  Vous y trouverez l'ensemble des documents de procédure (`.pdf`, `.pptx`, etc.).

> **Conseil :** Pour simplifier le téléchargement de ces fichiers depuis SharePoint, il est plus facile d'utiliser **Power Automate** pour créer un flux simple qui copie les fichiers vers l'emplacement de votre choix.

**Action requise :**

1.  Récupérez l'intégralité de ces documents.
2.  Si vous travaillez en mode `local`, placez-les dans le dossier **`data/documents/`** à la racine de ce projet. Vous pouvez conserver la même arborescence que celle présente sur SharePoint.

> ⚠️ **Important** : Le script d'ingestion en mode `local` échouera si le dossier `data/documents/` est vide. Cette étape est donc **obligatoire** pour faire fonctionner l'application localement.

### Étape 1 : Ingestion des Données

Ce script doit être exécuté à chaque fois que vous mettez à jour la base de connaissances.

1.  Assurez-vous d'avoir correctement placé vos documents (pour le mode `local`) ou configuré votre `.env` (pour le mode `azure`).
2.  Lancez le script d'ingestion :
    ```bash
    python src/create_unified_vectordb.py
    ```
    Ce processus peut prendre plusieurs minutes. Il va créer ou mettre à jour les fichiers dans le dossier `models/`.

### Étape 2 : Lancement de l'Application

Une fois l'ingestion terminée, lancez le serveur web Flask :
```bash
python src/app_unified.py
```
Accédez à l'application dans votre navigateur à l'adresse **http://localhost:7860**.

**Identifiants par défaut (au premier lancement) :**
*   **Utilisateur :** `admin`
*   **Mot de passe :** `admin123`

## 7. Tests Automatisés

Pour garantir la stabilité du code, une suite de tests a été mise en place avec `pytest`.

*   **Pourquoi tester ?** Les tests vérifient automatiquement que les fonctions critiques (comme l'authentification) se comportent comme prévu. Ils agissent comme un filet de sécurité, vous permettant de modifier le code en toute confiance.
*   **Comment les lancer ?**
    ```bash
    # Assurez-vous que votre venv est activé
    python -m pytest -v
    ```
*   **Résultat attendu :** Une sortie verte indiquant que tous les tests ont réussi (`... passed in ...`).

## 8. Déploiement

Cette section couvre à la fois le déploiement local pour le développement et le déploiement en production sur Microsoft Azure.

### 8.1. Checklist de Sécurité

Avant de déployer en production, assurez-vous de :
1. **Changer le mot de passe `admin` par défaut** via l'interface d'administration.
2. **Générer une clé secrète Flask robuste** dans votre fichier `.env` de production.
3. **Utiliser un fichier `.env` de production** avec les bonnes informations d'identification Azure et ne jamais le versionner.

### 8.2. Déploiement avec Docker (Local)

Cette méthode est idéale pour tester l'environnement de production sur votre machine locale.

1. **Pré-requis :** Docker et Docker Compose doivent être installés.
2. **Construire l'image Docker :**
   Cette commande lit votre `docker-compose.yml` et `Dockerfile` pour construire une image contenant toute votre application et ses dépendances.
   ```bash
   # Sous Linux/macOS
   ./docker-deploy.sh build

   # Sous Windows (PowerShell)
   .\docker-deploy.ps1 build
   ```
3. **Démarrer le conteneur :**
   Cette commande lance l'application en arrière-plan.
   ```bash
   # Sous Linux/macOS
   ./docker-deploy.sh start

   # Sous Windows (PowerShell)
   .\docker-deploy.ps1 start
   ```
4. L'application sera accessible sur `http://localhost:7860`.

### 8.3. Déploiement sur Azure (Production)

Ce guide explique comment déployer l'application sur Azure App Service for Containers, une solution simple et scalable.

#### Prérequis pour le déploiement Azure
- Un compte Azure avec une souscription active
- Azure CLI installé et configuré

#### Étape 1 : Publier l'image Docker sur Azure Container Registry (ACR)
ACR est un registre privé pour vos images Docker sur Azure.

1. Connectez-vous à Azure :
   ```bash
   az login
   ```
2. Définissez des variables (remplacez par vos valeurs ; les noms doivent être uniques globalement) :
   ```bash
   RESOURCE_GROUP="rg-chatbot-afpa"
   LOCATION="francecentral"
   ACR_NAME="acchatbotafpa$RANDOM" # Doit être unique
   APP_SERVICE_PLAN="plan-chatbot-afpa"
   WEB_APP_NAME="webapp-chatbot-afpa-$RANDOM" # Doit être unique
   STORAGE_ACCOUNT_NAME="stchatbotafpa$RANDOM" # Doit être unique
   FILE_SHARE_NAME="chatbot-data"
   ```
3. Créez un groupe de ressources :
   ```bash
   az group create --name $RESOURCE_GROUP --location $LOCATION
   ```
4. Créez un Azure Container Registry (ACR) :
   ```bash
   az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
   ```
5. Construisez et poussez l'image vers ACR (ACR Tasks) :
   ```bash
   az acr build --registry $ACR_NAME --image afpa-chatbot-rag:latest .
   ```

#### Étape 2 : Créer un stockage de fichiers persistant
Les données de l'application (index FAISS dans `models/` et utilisateurs dans `data/`) doivent être persistées hors conteneur.

1. Créez un compte de stockage Azure :
   ```bash
   az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS
   ```
2. Créez un partage de fichiers (Azure Files) :
   ```bash
   az storage share create --name $FILE_SHARE_NAME --account-name $STORAGE_ACCOUNT_NAME
   ```
3. Uploadez vos données :
   - Après avoir exécuté localement `python src/create_unified_vectordb.py`, utilisez Azure Storage Explorer ou le portail Azure pour uploader le contenu de vos dossiers locaux `models/` et `data/` dans le partage.

#### Étape 3 : Créer et configurer l'App Service
1. Créez un plan App Service (puissance du serveur) :
   ```bash
   az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --is-linux --sku B1
   ```
2. Créez l'application web (Web App) liée à l'image Docker ACR :
   ```bash
   az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEB_APP_NAME --deployment-container-image-name $ACR_NAME.azurecr.io/afpa-chatbot-rag:latest
   ```
3. Configurez les variables d'environnement (secrets `.env`) :
   ```bash
   az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --settings \
     FLASK_SECRET_KEY="VOTRE_VRAIE_CLE_SECRETE_TRES_LONGUE" \
     AZURE_INFERENCE_SDK_ENDPOINT="https://..." \
     AZURE_OPENAI_API_KEY="VOTRE_CLE_OPENAI" \
     DEPLOYMENT_NAME="gpt-4o" \
     WEBSITES_PORT=7860
   ```
   Note: `WEBSITES_PORT=7860` indique à App Service sur quel port l'application écoute.

4. Montez le stockage de fichiers persistant :
   ```bash
   # Obtenir la clé du compte de stockage
   STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)

   # Monter le partage de fichiers pour /app/data
   az webapp config storage-account add --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME \
     --custom-id $FILE_SHARE_NAME \
     --storage-type AzureFiles \
     --share-name $FILE_SHARE_NAME \
     --account-name $STORAGE_ACCOUNT_NAME \
     --access-key $STORAGE_KEY \
     --mount-path /app/data

   # Monter le partage de fichiers pour /app/models
   az webapp config storage-account add --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME \
     --custom-id ${FILE_SHARE_NAME}models \
     --storage-type AzureFiles \
     --share-name $FILE_SHARE_NAME \
     --account-name $STORAGE_ACCOUNT_NAME \
     --access-key $STORAGE_KEY \
     --mount-path /app/models
   ```

#### Étape 4 : Accéder à l'application et aux logs
1. Accédez à votre application :
   - URL: `https://<VOTRE_WEB_APP_NAME>.azurewebsites.net`
2. Consultez les logs en temps réel :
   ```bash
   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME
   ```

## 9. Maintenance et Mises à Jour

### Mise à Jour de la Base de Connaissances

1.  Ajoutez, modifiez ou supprimez les fichiers dans votre source de données (`data/documents/` pour le local, ou le conteneur Blob pour Azure).
2.  Relancez le script d'ingestion : `python src/create_unified_vectordb.py`.
3.  Redémarrez l'application (ou le conteneur Docker : `./docker-deploy.sh restart`) pour qu'elle charge la nouvelle base de connaissances.

### Consultation des Logs

*   **En local :** Les logs s'affichent directement dans le terminal où vous avez lancé `python src/app_unified.py`.
*   **Avec Docker :** Utilisez la commande suivante pour voir les logs du conteneur en temps réel :
    ```bash
    # Sous Linux/macOS
    ./docker-deploy.sh logs

    # Sous Windows (PowerShell)
    .\docker-deploy.ps1 logs
    ```

## 10. Intégration Continue (CI/CD)

Le fichier `.github/workflows/ci.yml` configure une pipeline d'intégration continue via **GitHub Actions**.

*   **Objectif :** Garantir que chaque modification poussée sur le dépôt de code ne casse aucune fonctionnalité existante.
*   **Fonctionnement :** À chaque `push` de code, GitHub va automatiquement :
    1.  Créer un environnement virtuel propre.
    2.  Installer toutes les dépendances.
    3.  Lancer la suite de tests avec `python -m pytest`.
*   **Résultat :** Vous verrez une coche verte (succès) ou une croix rouge (échec) à côté de vos commits sur GitHub, vous informant instantanément de la santé de votre projet. 