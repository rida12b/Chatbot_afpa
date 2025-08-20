*Chatbot RAG de l'AFPA : Documentation Technique Complète
![alt text](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![alt text](https://img.shields.io/badge/Flask-black?logo=flask)
![alt text](https://img.shields.io/badge/Docker-blue?logo=docker)
![alt text](https://img.shields.io/badge/Azure-blue?logo=microsoftazure)
![alt text](https://img.shields.io/badge/CI-Passing-brightgreen?logo=githubactions)
Table des Matières
Présentation du Projet
Fonctionnalités Clés
Architecture du Système
Phase 1 : Indexation (Offline)
Phase 2 : Requête (Online)
Structure du Projet
Installation et Configuration
Prérequis
Étape 1 : Configuration de l'Environnement
Étape 2 : Installation des Dépendances
Guide d'Utilisation
Étape 1 : Ingestion des Données
Étape 2 : Lancement de l'Application
Tests Automatisés
Déploiement en Production
Checklist de Sécurité
Déploiement avec Docker (Recommandé)
Maintenance et Mises à Jour
Mise à Jour de la Base de Connaissances
Consultation des Logs
Intégration Continue (CI/CD)
1. Présentation du Projet
Ce projet est un assistant conversationnel intelligent (chatbot) basé sur une architecture RAG (Retrieval-Augmented Generation). Sa mission est de fournir des réponses précises et contextuelles aux questions des collaborateurs de l'AFPA en s'appuyant exclusivement sur une base de documents d'entreprise validés.
Il est conçu pour être déployable en local pour le développement et prêt pour la production sur une infrastructure cloud comme Azure, grâce à une configuration flexible et une conteneurisation Docker.
2. Fonctionnalités Clés
Ingestion de Données Polyvalente : Capacité à traiter de multiples formats de fichiers (PDF, PPTX, DOCX, etc.) depuis des sources locales ou un stockage cloud (Azure Blob Storage).
Recherche Hybride Avancée : Combine la recherche sémantique (vectorielle) pour comprendre l'intention et la recherche par mots-clés pour la précision, garantissant une pertinence maximale des résultats.
Architecture Unifiée et Performante : Utilise une base de données vectorielle unique qui lie le contenu, les métadonnées et les URLs des documents dès l'indexation, simplifiant la logique et accélérant les temps de réponse.
Sécurité et Authentification : Système de connexion robuste avec gestion des rôles (Utilisateur, Administrateur) et protection des routes.
Prêt pour la Production : Déploiement simplifié via Docker, gestion centralisée de la configuration (.env), logging structuré et tests automatisés.
CI/CD Intégrée : Un workflow GitHub Actions est inclus pour exécuter automatiquement les tests à chaque modification du code, garantissant la stabilité du projet.
3. Architecture du Système
L'architecture est divisée en deux phases distinctes pour optimiser la performance et la maintenabilité.
Phase 1 : Indexation (Offline)
Ce processus transforme les documents bruts en une base de connaissances interrogeable. Il est exécuté par le script src/create_unified_vectordb.py.
Source des Données : Le script lit les documents soit depuis le dossier local data/documents/, soit depuis un conteneur Azure Blob Storage, en fonction de la variable DATA_SOURCE dans le fichier .env.
Extraction de Texte : Le contenu textuel de chaque document est extrait (la logique est dans src/ingestion.py).
Chunking : Le texte est divisé en petits morceaux de texte (chunks) pertinents.
Enrichissement des Métadonnées : Chaque chunk est associé à des métadonnées (titre du document source, catégorie, et URL si disponible).
Vectorisation (Embedding) : Les chunks sont transformés en vecteurs numériques via un modèle Sentence-Transformer.
Stockage : Les vecteurs sont stockés dans un index FAISS pour une recherche ultra-rapide. Les chunks et métadonnées sont sauvegardés dans des fichiers .json et .pkl.
Artefacts produits dans le dossier models/ : unified_index.bin, unified_chunks.json, unified_metadata.pkl.
Phase 2 : Requête (Online)
Ce processus se déroule en temps réel lorsqu'un utilisateur interagit avec l'application. Il est géré par src/app_unified.py.
Requête Utilisateur : L'utilisateur envoie une question via l'interface web Flask.
Recherche Hybride : La question est utilisée pour interroger la base de connaissances :
Une recherche vectorielle est effectuée sur l'index FAISS pour trouver les chunks sémantiquement similaires.
Une recherche par mots-clés est effectuée pour trouver les correspondances exactes.
Les résultats sont fusionnés et reclassés pour une pertinence optimale.
Génération du Contexte : Les chunks les plus pertinents et leurs métadonnées sont assemblés pour former un contexte.
Appel au LLM : Le contexte et la question initiale sont envoyés à Azure OpenAI.
Génération de la Réponse : Le LLM synthétise une réponse structurée en HTML en se basant uniquement sur le contexte fourni.
Affichage : La réponse HTML est transmise à l'interface utilisateur et affichée dans le navigateur.
4. Structure du Projet
code
Code
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
5. Installation et Configuration
Prérequis
Git
Python 3.10+
Docker & Docker Compose
Tesseract OCR :
Sous Windows (PowerShell) : winget install --id=UB-Mannheim.TesseractOCR
Sous Linux (Debian/Ubuntu) : sudo apt-get install tesseract-ocr
Étape 1 : Configuration de l'Environnement
Clonez le dépôt :
code
Bash
git clone <URL_DU_DEPOT>
cd chatbot_rag_project
Créez et configurez votre fichier d'environnement :
Copiez le fichier d'exemple. C'est votre fichier de configuration personnel, il ne doit jamais être partagé ou versionné.
code
Bash
# Sous Linux/macOS
cp .env.example .env

# Sous Windows
copy .env.example .env
Modifiez le fichier .env avec vos propres valeurs.
Pour un usage 100% local :
Assurez-vous que DATA_SOURCE est réglé sur local. Vous n'avez pas besoin de remplir les variables Azure.
code
Env
DATA_SOURCE=local
FLASK_SECRET_KEY="changez-moi-avec-une-cle-secrete-forte"
# Les variables Azure peuvent rester vides
AZURE_INFERENCE_SDK_ENDPOINT=""
...
Pour un usage connecté à Azure :
Réglez DATA_SOURCE sur azure et remplissez toutes les variables Azure.
code
Env
DATA_SOURCE=azure
FLASK_SECRET_KEY="changez-moi-avec-une-cle-secrete-forte"
AZURE_INFERENCE_SDK_ENDPOINT="https://..."
AZURE_OPENAI_API_KEY="..."
DEPLOYMENT_NAME="..."
AZURE_SAS_URL="https://..."
Étape 2 : Installation des Dépendances
Créez un environnement virtuel et installez les packages requis.
code
Bash
# Créez l'environnement virtuel
python -m venv venv

# Activez-le
# Sous Windows (PowerShell)
# .\venv\Scripts\Activate.ps1
# Sous Linux/macOS
# source venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt
6. Guide d'Utilisation
Étape 1 : Ingestion des Données
Ce script doit être exécuté à chaque fois que vous mettez à jour la base de connaissances.
Si vous êtes en mode local, assurez-vous que tous vos documents sources (PDF, PPTX, etc.) sont placés dans le dossier data/documents/.
Lancez le script d'ingestion :
code
Bash
python src/create_unified_vectordb.py
Ce processus peut prendre plusieurs minutes. Il va créer ou mettre à jour les fichiers dans le dossier models/.
Étape 2 : Lancement de l'Application
Une fois l'ingestion terminée, lancez le serveur web Flask :
code
Bash
python src/app_unified.py
Accédez à l'application dans votre navigateur à l'adresse http://localhost:7860.
Identifiants par défaut (au premier lancement) :
Utilisateur : admin
Mot de passe : admin123
7. Tests Automatisés
Pour garantir la stabilité du code, une suite de tests a été mise en place avec pytest.
Pourquoi tester ? Les tests vérifient automatiquement que les fonctions critiques (comme l'authentification) se comportent comme prévu. Ils agissent comme un filet de sécurité, vous permettant de modifier le code en toute confiance.
Comment les lancer ?
code
Bash
# Assurez-vous que votre venv est activé
python -m pytest -v
Résultat attendu : Une sortie verte indiquant que tous les tests ont réussi (... passed in ...).
8. Déploiement en Production
Le déploiement est simplifié grâce à Docker.
Checklist de Sécurité
Avant de déployer, assurez-vous de :
Changer le mot de passe admin par défaut via l'interface d'administration.
Générer une clé secrète Flask robuste dans votre fichier .env de production.
Utiliser un fichier .env de production avec les bonnes informations d'identification Azure et ne jamais le versionner.
Déploiement avec Docker (Recommandé)
Pré-requis : Docker et Docker Compose doivent être installés sur le serveur de production.
Construire l'image Docker :
Le script de déploiement va lire votre docker-compose.yml et Dockerfile pour construire une image contenant toute votre application et ses dépendances.
code
Bash
# Sous Linux/macOS
./docker-deploy.sh build

# Sous Windows (PowerShell)
.\docker-deploy.ps1 build
Démarrer le conteneur :
Cette commande lance l'application en arrière-plan.
code
Bash
# Sous Linux/macOS
./docker-deploy.sh start

# Sous Windows (PowerShell)
.\docker-deploy.ps1 start
L'application sera accessible sur le port 7860 de votre serveur.
9. Maintenance et Mises à Jour
Mise à Jour de la Base de Connaissances
Ajoutez, modifiez ou supprimez les fichiers dans votre source de données (data/documents/ pour le local, ou le conteneur Blob pour Azure).
Relancez le script d'ingestion : python src/create_unified_vectordb.py.
Redémarrez l'application (ou le conteneur Docker : ./docker-deploy.sh restart) pour qu'elle charge la nouvelle base de connaissances.
Consultation des Logs
En local : Les logs s'affichent directement dans le terminal où vous avez lancé python src/app_unified.py.
Avec Docker : Utilisez la commande suivante pour voir les logs du conteneur en temps réel :
code
Bash
# Sous Linux/macOS
./docker-deploy.sh logs

# Sous Windows (PowerShell)
.\docker-deploy.ps1 logs
10. Intégration Continue (CI/CD)
Le fichier .github/workflows/ci.yml configure une pipeline d'intégration continue via GitHub Actions.
Objectif : Garantir que chaque modification poussée sur le dépôt de code ne casse aucune fonctionnalité existante.
Fonctionnement : À chaque push de code, GitHub va automatiquement :
Créer un environnement virtuel propre.
Installer toutes les dépendances.
Lancer la suite de tests avec python -m pytest.
Résultat : Vous verrez une coche verte (succès) ou une croix rouge (échec) à côté de vos commits sur GitHub, vous informant instantanément de la santé de votre projet.*