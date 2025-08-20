Chatbot RAG AFPA 🤖
1. Description
Ce projet est un chatbot intelligent basé sur une architecture RAG (Retrieval-Augmented Generation). Il est conçu pour analyser et répondre aux questions des utilisateurs en se basant sur une base de connaissances constituée de documents internes de l'AFPA (PDF, DOCX, PPTX, etc.).
L'application utilise une base de données vectorielle unifiée pour associer directement le contenu des documents à leurs métadonnées (titre, URL, catégorie), garantissant des réponses rapides et des sources fiables.
2. Fonctionnalités Principales
📄 Ingestion Multi-Format : Prise en charge de divers types de fichiers, y compris PDF, DOCX, PPTX, et images (via OCR).
🧠 Base Vectorielle Unifiée : Un seul index FAISS contenant les embeddings des documents et leurs métadonnées associées, y compris les URLs, pour une performance et une cohérence maximales.
🔍 Recherche Sémantique : Utilisation de modèles de type Sentence-BERT et d'un index FAISS pour trouver les extraits de documents les plus pertinents sémantiquement.
🤖 Génération de Réponses avec Azure OpenAI : Exploitation de la puissance des modèles de langage d'Azure OpenAI pour synthétiser des réponses claires à partir des documents trouvés.
🔐 Authentification Utilisateur : Système de connexion sécurisé avec gestion des rôles (Utilisateur, Administrateur).
🌐 Interface Web Intuitive : Une interface utilisateur moderne et réactive construite avec Flask, proposant des suggestions de questions et un affichage clair des réponses et de leurs sources.
🐳 Déploiement Simplifié avec Docker : Scripts de déploiement pour Windows (PowerShell) et Linux/macOS pour une mise en service rapide et facile.
3. Architecture du Système
L'architecture actuelle a été simplifiée pour améliorer la performance et la maintenabilité.
Phase d'Indexation (Offline) :
Le script create_unified_vectordb.py orchestre le processus :
Les documents du dossier data/documents sont analysés et leur texte est extrait (ingestion.py).
Le texte est découpé en "chunks" (morceaux).
Les métadonnées (y compris les URLs de Url_nom_FINA.json) sont associées à chaque chunk.
Les chunks sont transformés en vecteurs (embeddings) via un modèle Sentence-Transformer.
Un index FAISS (unified_index.bin), un fichier de chunks (unified_chunks.json) et un fichier de métadonnées (unified_metadata.pkl) sont créés et sauvegardés dans le dossier models/.
Phase d'Interrogation (Online) :
L'application app_unified.py est lancée.
Un utilisateur pose une question via l'interface web.
La question est transformée en vecteur.
L'index FAISS est interrogé pour trouver les chunks les plus similaires.
Les chunks pertinents, avec leurs métadonnées, sont utilisés comme contexte pour une requête à l'API Azure OpenAI.
Le modèle de langage génère une réponse structurée qui est ensuite affichée à l'utilisateur.
4. Structure du Projet
Generated code
repomix-output/
│
├── data/
│   ├── documents/         # (À créer) Placer les documents sources ici.
│   ├── processed/         # Textes extraits par ingestion.py.
│   └── url/               # Fichiers JSON de mapping d'URLs.
│
├── models/                # Contient la base de données vectorielle unifiée.
│
├── src/
│   ├── templates/         # Fichiers HTML pour l'interface.
│   ├── app_unified.py     # ✅ Application principale (Flask).
│   ├── create_unified_vectordb.py # ✅ Script pour créer la base vectorielle.
│   ├── ingestion.py       # Logique d'extraction de texte des fichiers.
│   ├── auth.py            # Gestion de l'authentification.
│   └── ...
│
├── Dockerfile             # Fichier pour construire l'image Docker.
├── docker-compose.yml     # Configuration pour le déploiement multi-conteneurs.
├── docker-deploy.sh       # Script de déploiement pour Linux/macOS.
├── docker-deploy.ps1      # Script de déploiement pour Windows PowerShell.
├── requirements.txt       # Dépendances Python.
└── README.md              # Ce fichier.
Use code with caution.
5. Technologies Utilisées
Backend : Flask
Recherche Vectorielle : FAISS (Facebook AI Similarity Search)
Embeddings : Sentence-Transformers (all-MiniLM-L6-v2)
Génération de Langage : Azure OpenAI
Traitement de Documents : PyMuPDF (PDF), python-docx (Word), python-pptx (PowerPoint), Tesseract (OCR)
Déploiement : Docker, Docker Compose
6. Prérequis
Python 3.10+
Docker et Docker Compose
Tesseract OCR :
Sous Windows : winget install --id=UB-Mannheim.TesseractOCR
Sous Linux (Debian/Ubuntu) : sudo apt-get install tesseract-ocr
Compte Azure OpenAI avec un point de terminaison et une clé API.
7. Installation et Lancement
Étape 1 : Cloner le Dépôt et Configurer l'Environnement
Clonez ce dépôt sur votre machine.

Copiez le fichier d'exemple d'environnement et remplissez-le avec vos valeurs:
- `cp .env.example .env` (Linux/macOS) ou `copy .env.example .env` (Windows)
- Le fichier `.env` est la SEULE source de vérité pour les secrets et configurations (ne rien coder en dur).

Configuration de la source de données via `DATA_SOURCE`:
- `DATA_SOURCE=local`: le script d'ingestion lit les fichiers locaux. Placez les documents sources dans `data/documents/` (des sous-dossiers sont acceptés). Aucune configuration Azure n'est requise.
- `DATA_SOURCE=azure`: le script d'ingestion lit les blobs Azure. Renseignez impérativement `AZURE_SAS_URL` (URL SAS du conteneur). Les variables Azure OpenAI (`AZURE_INFERENCE_SDK_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `DEPLOYMENT_NAME`) doivent également être définies pour la génération des réponses.
Étape 2 : Préparer les Données
Créez le dossier data/documents.
Placez tous les documents que le chatbot doit connaître dans data/documents (il peut y avoir des sous-dossiers).
Étape 3 : Choisir une Méthode de Lancement
Méthode A : Déploiement avec Docker (Recommandé)
Note importante : Le Dockerfile du projet pointe vers l'ancien script app.py. Vous devez le corriger manuellement avant de construire l'image.
Ouvrez le fichier Dockerfile et modifiez la dernière ligne :
Remplacer : CMD ["python", "src/app.py"]
Par : CMD ["python", "src/app_unified.py"]
Construire la base de données vectorielle :
Pour que Docker puisse inclure la base de données dans l'image, vous devez la créer une première fois localement.
Installez les dépendances : pip install -r requirements.txt
Lancez le script de création : python src/create_unified_vectordb.py
Construire et lancer les conteneurs Docker :
Sous Linux/macOS :
Generated bash
# Rendre le script exécutable
chmod +x docker-deploy.sh
# Construire l'image
./docker-deploy.sh build
# Démarrer le conteneur
./docker-deploy.sh start
Use code with caution.
Bash
Sous Windows (dans PowerShell) :
Generated powershell
# Construire l'image
.\docker-deploy.ps1 build
# Démarrer le conteneur
.\docker-deploy.ps1 start
Use code with caution.
Powershell
Méthode B : Lancement Local
Installer les dépendances :
Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
Construire la base de données vectorielle :
Generated bash
python src/create_unified_vectordb.py
Use code with caution.
Bash
Lancer l'application :
Generated bash
python src/app_unified.py
Use code with caution.
Bash
8. Utilisation
Une fois l'application lancée, accédez à http://localhost:7860 dans votre navigateur.
Utilisez les identifiants par défaut pour vous connecter (créés au premier lancement) :
Identifiant : admin
Mot de passe : admin123
Utilisez la barre de recherche ou les questions suggérées pour interroger le chatbot. La page d'administration est accessible via le menu pour les utilisateurs avec le rôle admin.
9. Maintenance
Pour mettre à jour la base de connaissances du chatbot, ajoutez, modifiez ou supprimez des documents dans le dossier data/documents et relancez le script create_unified_vectordb.py.
Pour l'historique détaillé des changements et des décisions de conception, consultez le fichier suivi_projet.md.