# Suivi du Projet Chatbot AFPA

## 📅 Dernière mise à jour : 19/03/2024

## 🔄 Changelog récent

### AJOUT DU JOUR - Intégration de la recherche hybride (vectorielle + mots-clés)
- **🎯 Objectif :** Améliorer la pertinence des résultats en combinant similarité sémantique (vecteurs) et correspondances exactes (mots-clés).
- **🛠️ Modifs dans `src/app_unified.py` :**
  - Ajout de `search_documents_keywords(query: str, chunks: list, metadata: list, top_k: int = 10)`
    - Recherche des tokens (>3 caractères) dans `metadata['title']` (score 1.0) et `chunks` (score 0.8)
  - Ajout de `combine_results(vector_res: list, keyword_res: list)`
    - Fusion, déduplication par `url` ou `title`, pondération: `0.6 * keyword_score + 0.4 * vector_score` si présent dans les deux
  - Mise à jour de `search_documents(...)` pour exécuter les deux recherches et retourner le résultat combiné trié par score
  - Import de `re` pour la tokenisation
- **✅ Impact :** Résultats plus pertinents pour les requêtes contenant des termes exacts; conservation des bénéfices sémantiques.
- **📋 Tests :** Lint OK; à valider fonctionnellement via l'endpoint `/search`.

### AJOUT DU JOUR - Planification du Nettoyage des Dépendances Inutiles du venv
- **🎯 Objectif :** Réduire la taille de l'environnement virtuel (`venv`) en identifiant et supprimant les bibliothèques Python qui ne sont pas strictement nécessaires au fonctionnement du projet.
- **🤔 Stratégie envisagée :** Utilisation de l'outil `deptry` pour une analyse statique des dépendances.
- **📋 Plan d'Action Proposé :**
    1.  **Préparation :**
        *   Sauvegarde du fichier `requirements.txt`.
        *   Commit des modifications actuelles si utilisation de Git et création d'une branche dédiée.
    2.  **Installation de `deptry`** (temporairement dans le venv actuel ou globalement).
    3.  **Exécution de `deptry`** pour analyser le code source et `requirements.txt`.
    4.  **Analyse Collaborative des Résultats :** Examen du rapport de `deptry` pour identifier les dépendances potentiellement obsolètes (`DEP002`). Discussion pour chaque cas afin de confirmer leur inutilité (prise en compte des usages dynamiques non détectables par l'outil).
    5.  **Mise à Jour de `requirements.txt` :** Suppression des dépendances confirmées comme inutiles.
    6.  **Reconstruction du `venv` :**
        *   Suppression de l'ancien `venv`.
        *   Création d'un nouveau `venv`.
        *   Réinstallation des dépendances à partir du `requirements.txt` nettoyé.
    7.  **Tests Approfondis :** Validation complète de toutes les fonctionnalités de l'application pour s'assurer de l'absence de régressions.
- **🚦 Statut :** En cours. Erreur d'encodage (BOM UTF-16) détectée dans `requirements.txt` lors de la première tentative d'exécution de `deptry`. En attente de la correction de l'encodage par l'utilisateur.
- **Erreur rencontrée (AJOUT DU JOUR) :** `deptry` a échoué à lire `requirements.txt` à cause d'un encodage incorrect (probablement UTF-16 avec BOM). L'utilisateur a été invité à ré-enregistrer le fichier en UTF-8 standard (sans BOM).

---

**Date : AJOUT DU JOUR (Suite) - Succès de l'Association d'URLs avec JSON Azure**
- **Réflexion :** Validation finale de l'association des URLs aux documents chargés depuis Azure, en utilisant le fichier `FINA/name_url_files.json`.
- **Résultat de l'exécution (Itération 5) :**
    1.  **Lecture et Parsing du JSON d'URLs Azure :** Le fichier `FINA/name_url_files.json` a été lu et parsé avec succès depuis Azure.
    2.  **Chargement des Documents Azure :** 31 documents (PDF et PPTX) ont été chargés et leur texte extrait correctement. Le fichier `FINA/name_url_files.json` lui-même a été correctement identifié comme non textuel et ignoré pour l'extraction de contenu.
    3.  **Traitement des Métadonnées URLs :** La fonction `load_url_metadata` a traité avec succès les 31 entrées du JSON Azure, créant un dictionnaire `url_dict` avec les noms de fichiers comme clés.
    4.  **Association des URLs aux Chunks :** La fonction `associate_urls_to_metadata` a réussi à associer une URL à **tous les 59 chunks créés** (`59/59 chunks associés`). La correspondance s'est faite en utilisant le nom de base du fichier extrait de `meta_item["source"]` et en le comparant aux clés du `url_dict`.
    5.  **Finalisation :** La création des embeddings, de l'index FAISS et la sauvegarde des données se sont déroulées correctement.
- **Conclusion :** L'intégration des documents depuis Azure Blob Storage, incluant l'extraction de texte pour les PDF/PPTX et l'association des URLs correspondantes via le fichier JSON `FINA/name_url_files.json`, est **pleinement fonctionnelle et réussie**.
- **Objectif Atteint :** Le système peut maintenant ingérer des documents depuis Azure et enrichir les chunks avec les URLs sources pertinentes, permettant au chatbot de citer ces URLs dans ses réponses.

---

**Date : AJOUT DU JOUR (Suite) - Implémentation de l'Association d'URLs depuis JSON Azure**
- **Réflexion :** Utiliser le fichier JSON `FINA/name_url_files.json` (lu depuis Azure) pour associer les URLs aux documents traités.
- **Format du JSON d'URLs :** Une liste d'objets, chaque objet ayant les clés `"Nom"` (nom de fichier exact avec extension) et `"URL"`.
- **Approche implémentée (Itération 5) :**
    1.  **`load_url_metadata(url_data_from_azure=None)` modifiée :**
        *   Accepte en argument les données JSON parsées lues depuis Azure.
        *   Crée un dictionnaire `url_dict` où chaque clé est le `"Nom"` exact du fichier (provenant du JSON) et la valeur est un dictionnaire `{"url": item["URL"], "category": item.get("Categorie", "FINA_Azure")}`. Tente d'utiliser une clé `"Categorie"` du JSON si elle existe, sinon utilise `"FINA_Azure"` par défaut.
    2.  **`associate_urls_to_metadata(metadata, url_dict)` modifiée :**
        *   Pour chaque chunk, extrait le nom de base du fichier à partir de `meta_item["source"]` en utilisant `os.path.basename()`.
        *   Recherche ce nom de fichier exact comme clé dans `url_dict`.
        *   Si une correspondance est trouvée, l'URL et la catégorie du `url_dict` sont ajoutées aux métadonnées du chunk.
        *   La recherche partielle a été désactivée pour privilégier la correspondance exacte.
    3.  **`main()` modifiée :**
        *   Le code existant lit `FINA/name_url_files.json` depuis Azure et le parse dans `parsed_url_json_from_azure`.
        *   Cette variable `parsed_url_json_from_azure` est ensuite passée à `load_url_metadata()`.
        *   L'affichage du contenu JSON en console a été limité aux 500 premiers caractères pour la lisibilité.
- **Objectif :** Associer correctement les URLs provenant du fichier JSON sur Azure aux chunks des documents correspondants traités par le script.
- **Prochaines étapes :**
    1. L'utilisateur exécute `src/create_unified_vectordb.py`.
    2. Analyse des logs, en particulier les messages de `load_url_metadata` et `associate_urls_to_metadata` pour vérifier le nombre d'URLs chargées et associées.

---

### AJOUT DU JOUR - Analyse de la taille de l'environnement virtuel (venv)
- **❓ Question :** L'utilisateur a signalé que le `venv` pèse près de 2.8 Go et s'est interrogé sur la normalité de cette taille.
- **🔬 Analyse effectuée :**
    - Examen du fichier `requirements.txt` et de la liste complète des bibliothèques fournies par l'utilisateur.
    - Identification des bibliothèques volumineuses, notamment :
        - `torch` et `torchvision` (PyTorch)
        - `transformers` (Hugging Face)
        - `easyocr` (et ses modèles)
        - `sentence-transformers` (et ses modèles)
        - `faiss-cpu`
        - `opencv-python-headless`
        - `scikit-learn`, `scipy`, `numpy`, `pandas`
        - `unstructured` (avec ses nombreuses dépendances pour différents types de fichiers)
        - `pyarrow`
        - `gradio` et `streamlit`
- **✅ Conclusion :**
    - La taille de 2.8 Go est considérée comme **normale et attendue** compte tenu du grand nombre de bibliothèques installées, en particulier celles liées à l'apprentissage profond (PyTorch, Transformers) qui sont intrinsèquement volumineuses et peuvent inclure/télécharger des modèles de plusieurs centaines de Mo ou Go.
- **💡 Recommandations (si la taille devenait une contrainte) :**
    - Vérifier les doublons fonctionnels (ex: `gradio` vs `streamlit` si un seul est utilisé).
    - Explorer l'utilisation de modèles plus légers pour les bibliothèques de ML si les performances restent acceptables.
    - Auditer régulièrement `requirements.txt` pour s'assurer que toutes les bibliothèques sont activement utilisées.
- **🚦 Statut :** Observation consignée. Aucune action corrective immédiate nécessaire car la taille est justifiée par les dépendances du projet.

### 19/03/2024 - Correction des conflits de dépendances
- ✅ Modifications apportées :
  1. Mise à jour de la version de Werkzeug dans requirements.txt de 3.0.3 à >=3.1.0
  2. Mise à jour de la version de langchain-core de 0.2.13 à >=0.2.27,<0.3.0
  3. Résolution des conflits entre Flask 3.1.0 (qui nécessite Werkzeug>=3.1) et langchain 0.2.12 (qui nécessite langchain-core>=0.2.27)
- 🔍 Résultats obtenus :
  - Compatibilité assurée entre toutes les dépendances
  - Résolution des erreurs lors de la construction de l'image Docker
  - Amélioration de la stabilité du déploiement
- 📋 Détails techniques :
  - Utilisation de spécifications de versions minimales et maximales pour assurer la compatibilité
  - Maintien de la compatibilité avec les autres dépendances
  - Correction basée sur les erreurs de résolution de dépendances de pip

### 19/03/2024 - Correction du conflit de dépendances
- ✅ Modifications apportées :
  1. Mise à jour de la version de Werkzeug dans requirements.txt de 3.0.3 à >=3.1.0
  2. Résolution du conflit entre Flask 3.1.0 (qui nécessite Werkzeug>=3.1) et la version précédemment spécifiée
- 🔍 Résultats obtenus :
  - Compatibilité assurée entre Flask et Werkzeug
  - Résolution de l'erreur lors de la construction de l'image Docker
  - Amélioration de la stabilité du déploiement
- 📋 Détails techniques :
  - Utilisation d'une spécification de version minimale (>=3.1.0) plutôt qu'une version fixe
  - Maintien de la compatibilité avec les autres dépendances
  - Correction basée sur l'erreur de résolution de dépendances de pip

### 19/03/2024 - Ajout d'un script PowerShell pour Windows
- ✅ Modifications apportées :
  1. Création d'un fichier `docker-deploy.ps1` pour l'exécution sous Windows
  2. Adaptation des commandes shell Linux pour PowerShell
  3. Conservation de toutes les fonctionnalités du script original
  4. Utilisation des fonctionnalités avancées de PowerShell (fonctions, gestion d'erreurs, couleurs)
- 🔍 Résultats obtenus :
  - Compatibilité cross-platform (Windows et Linux/macOS)
  - Exécution simplifiée sous Windows avec PowerShell
  - Interface utilisateur améliorée avec des couleurs et une meilleure gestion des erreurs
  - Mêmes fonctionnalités que le script shell original
- 📋 Détails techniques :
  - Utilisation de fonctions PowerShell pour une meilleure organisation
  - Gestion des erreurs avec try/catch pour la vérification de Docker
  - Utilisation des couleurs pour une meilleure lisibilité des messages
  - Structure de commandes identique (build, start, stop, etc.)

### 19/03/2024 - Mise à jour de la documentation et des dépendances
- ✅ Modifications apportées :
  1. Refonte complète du README.md pour refléter l'état actuel du projet
  2. Mise à jour du fichier requirements.txt avec toutes les dépendances nécessaires
  3. Ajout de sections détaillées sur les fonctionnalités avancées
  4. Documentation du déploiement Docker
- 🔍 Résultats obtenus :
  - Documentation plus précise et à jour
  - Meilleure visibilité des fonctionnalités du projet
  - Instructions d'installation et d'utilisation plus claires
  - Dépendances organisées par catégories pour une meilleure lisibilité
- 📋 Détails techniques :
  - Ajout des dépendances pour langchain et ses composants
  - Inclusion des utilitaires comme tqdm, rich et tabulate
  - Documentation des méthodes d'installation locale et Docker
  - Description détaillée de la recherche hybride et du streaming

### 19/03/2024 - Optimisation de la configuration Docker pour le déploiement
- ✅ Modifications apportées :
  1. Amélioration du Dockerfile existant avec des bonnes pratiques de sécurité et d'optimisation
  2. Création d'un fichier docker-compose.yml pour faciliter le déploiement
  3. Développement d'un script shell (docker-deploy.sh) pour la gestion des conteneurs
  4. Ajout d'un fichier .dockerignore pour optimiser la construction de l'image
- 🔍 Résultats obtenus :
  - Image Docker plus légère et sécurisée
  - Déploiement simplifié via Docker Compose
  - Gestion facilitée des conteneurs via un script shell intuitif
  - Meilleure isolation des composants de l'application
- 📋 Détails techniques :
  - Utilisation d'un utilisateur non-root dans le conteneur pour renforcer la sécurité
  - Configuration de healthchecks pour surveiller l'état de l'application
  - Optimisation du cache Docker pour accélérer les builds
  - Montage de volumes pour les données persistantes
  - Script shell avec interface utilisateur colorée et commandes intuitives

### 15/03/2024 - Optimisation de l'interface avec des boutons d'accès rapide compacts
- ✅ Modifications apportées :
  1. Remplacement des grandes cartes d'accès rapide par des boutons compacts
  2. Réorganisation des éléments d'accès rapide dans un conteneur dédié avec titre
  3. Amélioration de l'utilisation de l'espace dans l'interface
  4. Conservation de la fonctionnalité de suggestion de questions
- 🔍 Résultats obtenus :
  - Interface plus épurée avec moins d'éléments visuels encombrants
  - Meilleure utilisation de l'espace vertical
  - Conservation de toutes les fonctionnalités d'accès rapide
  - Expérience utilisateur plus directe et efficace
- 📋 Détails techniques :
  - Utilisation de boutons avec bordures arrondies et icônes
  - Disposition horizontale avec retour à la ligne automatique (flex-wrap)
  - Effets de survol subtils pour l'interaction
  - Regroupement dans un conteneur avec titre explicatif

### 15/03/2024 - Amélioration du filigrane et des cartes d'accès rapide
- ✅ Modifications apportées :
  1. Augmentation de l'opacité du filigrane pour une meilleure visibilité (de 0.06 à 0.08)
  2. Refonte complète des cartes d'accès rapide avec une structure plus moderne
  3. Ajout d'icônes plus descriptives et d'effets visuels améliorés
  4. Amélioration des textes descriptifs pour plus de clarté
- 🔍 Résultats obtenus :
  - Filigrane plus visible sans perturber la lisibilité du contenu
  - Cartes d'accès rapide plus attrayantes et interactives
  - Meilleure expérience utilisateur avec des animations fluides
  - Descriptions plus précises des fonctionnalités disponibles
- 📋 Détails techniques :
  - Utilisation d'un système de cartes à trois niveaux (icône, contenu, action)
  - Implémentation d'effets de survol avancés avec des transitions CSS
  - Optimisation des contrastes et de la lisibilité
  - Amélioration de la cohérence visuelle avec le reste de l'interface

### 15/03/2024 - Amélioration de l'interface et gestion des droits d'administration
- ✅ Modifications apportées :
  1. Masquage du bouton d'administration pour les utilisateurs non-administrateurs
  2. Restructuration de l'en-tête pour une meilleure organisation visuelle
  3. Amélioration de la navigation avec des styles plus clairs et interactifs
  4. Optimisation de l'affichage sur les appareils mobiles
- 🔍 Résultats obtenus :
  - Interface plus sécurisée avec accès restreint aux fonctionnalités d'administration
  - Navigation plus intuitive et visuellement cohérente
  - Meilleure séparation des éléments d'interface pour une lecture plus claire
  - Expérience utilisateur améliorée sur tous les appareils
- 📋 Détails techniques :
  - Ajout de la variable `is_admin` dans les routes Flask pour contrôler l'affichage des éléments d'administration
  - Utilisation de conditions Jinja2 pour masquer/afficher les éléments selon le rôle de l'utilisateur
  - Restructuration du CSS pour une meilleure organisation visuelle
  - Amélioration de la réactivité pour les appareils mobiles

### 15/03/2024 - Suppression des URLs génériques et amélioration de la présentation des réponses
- ✅ Modifications apportées :
  1. Création et exécution du script `remove_generic_urls.py` pour supprimer les URLs génériques
  2. Amélioration de la structuration des réponses pour une meilleure lisibilité
  3. Optimisation du format de présentation pour le rendre plus attrayant
- 🔍 Résultats obtenus :
  - 31,234 entrées de métadonnées analysées
  - 30,861 URLs traitées
  - 30,828 URLs spécifiques (99.89%) conservées
  - 33 URLs génériques (0.11%) supprimées
- 📋 Améliorations de la présentation des réponses :
  - Structure plus concise avec introduction courte
  - Étapes numérotées et clairement identifiées
  - Mise en évidence des points clés
  - Sources discrètes mais accessibles
  - Meilleur équilibre visuel entre texte et espacement

### 14/03/2024 - Amélioration de la structuration des réponses et de l'affichage des URLs
- ✅ Modifications apportées :
  1. Amélioration du prompt système pour générer des réponses mieux structurées en HTML
  2. Ajout d'instructions précises pour le formatage des sources avec URLs cliquables
  3. Utilisation de balises HTML sémantiques pour une meilleure présentation
- 🔍 Améliorations spécifiques :
  - Formatage des URLs en liens cliquables avec `target="_blank"` et classe CSS dédiée
  - Structure plus claire avec titres, listes ordonnées et mise en évidence des points importants
  - Meilleure séparation visuelle entre les étapes et les sources
- 📋 Impact sur l'expérience utilisateur :
  - Réponses plus lisibles et mieux organisées
  - Accès direct aux documents sources via les liens cliquables
  - Présentation professionnelle et cohérente des informations

### 14/03/2024 - Test de l'application avec association directe des URLs
- ✅ Exécution du script `test_app.py` pour vérifier la qualité des associations d'URLs :
  1. Chargement du système de recherche avec les métadonnées mises à jour
  2. Test de plusieurs requêtes pour évaluer la pertinence des résultats
  3. Analyse détaillée des URLs associées aux documents
- 🔍 Résultats obtenus :
  - 31,234 chunks et métadonnées chargés avec succès
  - 30,861 chunks (98.81%) ont des URLs associées
  - 80% des documents retournés pour une requête test ont des URLs pertinentes
  - Les catégories sont correctement associées aux documents
  - Les URLs pointent majoritairement vers des documents spécifiques
- 📋 Prochaines étapes :
  1. Lancer l'application complète avec `app.py` pour tester en conditions réelles
  2. Optimiser l'algorithme pour les documents sans URL
  3. Améliorer la spécificité des URLs génériques (pointant vers des dossiers)
  4. Recueillir des retours utilisateurs sur la pertinence des URLs

### 14/03/2024 - Amélioration de l'association des URLs aux documents
- ✅ Développement d'un système de mapping direct entre les documents et les URLs :
  1. Création du script `create_direct_mapping.py` pour associer les documents aux URLs
  2. Utilisation d'un algorithme de similarité pour trouver les meilleures correspondances
  3. Mise à jour des métadonnées unifiées avec les URLs correspondantes
- 🔍 Résultats obtenus :
  - 182 fichiers traités analysés
  - 172 fichiers (94.51%) associés avec succès à une URL
  - 30,861 entrées de métadonnées mises à jour
  - Score moyen de correspondance : 0.906 (très élevé)
- 📋 Intégration au système :
  1. Mise à jour de `app.py` pour utiliser directement les URLs des métadonnées
  2. Suppression de la fonction `search_urls` devenue obsolète
  3. Amélioration de la présentation des sources dans les réponses

### 06/03/2024 - Intégration du nouveau système RAG combiné
- ✅ Développement d'un nouveau système RAG combinant :
  1. RAG documentaire pour la recherche de contenu
  2. RAG JSON pour la récupération précise des URLs
- 🔍 Améliorations apportées :
  - Meilleure gestion des erreurs avec logs détaillés
  - Vérification des indices FAISS
  - Gestion des cas où les documents ne sont pas trouvés
  - Association précise des URLs aux documents cités
- 📋 Plan d'intégration :
  1. Remplacer l'ancien système dans app.py
  2. Mettre à jour l'interface utilisateur
  3. Améliorer la gestion des erreurs 
  4. Ajouter des tests de validation

### 06/03/2024 - Intégration du système vectoriel d'URLs dans app.py
- 🎯 Objectif : Remplacer l'ancien système de mapping d'URLs par le nouveau système vectoriel
- 📋 Plan d'action :
  1. Garder la recherche documentaire FAISS existante
  2. Remplacer `load_url_mappings()` par `JsonSearcher`
  3. Utiliser l'index vectoriel des URLs depuis `data/vectors/`

- 🔧 Modifications prévues dans app.py :
  1. Ajouter l'import de `JsonSearcher`
  2. Initialiser le searcher avec le dossier `data/vectors`
  3. Remplacer la fonction `associate_urls_to_documents`
  4. Garder intact le reste du système (recherche doc, génération réponses)

- ✅ Avantages :
  - Recherche d'URLs plus précise grâce à FAISS
  - Meilleure performance (vectorisation vs comparaison de chaînes)
  - Système unifié utilisant FAISS pour tout

- 📊 État des composants :
  - Index URLs : Prêt dans `data/vectors/`
  - JsonSearcher : Testé et fonctionnel
  - app.py : En cours de modification

### Tâches immédiates :
1. [ ] Modifier app.py pour utiliser JsonSearcher
2. [ ] Tester les modifications
3. [ ] Valider la précision des URLs retournées

### État des composants
- ✅ RAG JSON : Fonctionnel et testé
- ✅ RAG Documentaire : Nécessite synchronisation avec FAISS
- 🔄 Interface utilisateur : À mettre à jour
- 📝 Tests : À implémenter

### Tâches à suivre
1. [ ] Remplacer le système RAG dans app.py
2. [ ] Mettre à jour l'interface utilisateur
3. [ ] Ajouter des tests de validation
4. [ ] Documenter les nouvelles fonctionnalités

## 🚀 Phase 0 : Initialisation

✅ Création de la structure du projet
✅ Installation de Python et création d'un environnement virtuel
✅ Installation des dépendances
✅ Test des bibliothèques

## 🚀 Phase 1 : Collecte & Prétraitement des Documents

✅ Développement du script d'ingestion des documents (ingestion.py)
✅ Implémentation des fonctions d'extraction pour différents formats de documents :
  - PDF (via PyMuPDF)
  - DOCX (via python-docx)
  - XLSX (via pandas)
  - PPTX (via python-pptx)
  - Images (via OpenCV)
  - TXT (lecture directe)
  - PPT (ancienne version PowerPoint)
  - DOC (ancienne version Word)
✅ Test du script d'ingestion sur un ensemble de documents réels
✅ Amélioration du script d'ingestion pour augmenter le taux de succès
✅ Implémentation de la sauvegarde des textes extraits dans des fichiers texte
✅ Analyse des résultats finaux : 247 fichiers trouvés, 243 traités, taux de succès de 98.4%

### 📊 Statistiques d'ingestion initiales
- Fichiers trouvés : 247
- Fichiers traités : 173
- Taux de succès : 70%
- Documents traités avec succès : 137

### 📊 Statistiques d'ingestion après améliorations
- Fichiers trouvés : 247
- Fichiers traités : 243
- Fichiers sauvegardés : 243
- Taux de succès : 98.4%
- Documents traités avec succès : 183

### 🔍 Problèmes identifiés et résolus
- Support ajouté pour les fichiers PPT (ancienne version PowerPoint)
- Support ajouté pour les fichiers TXT
- Amélioration de la gestion des erreurs pour les fichiers DOC (ancienne version Word)
- Amélioration du traitement des fichiers Excel avec différents moteurs
- Implémentation d'un système de sauvegarde des textes extraits dans des fichiers texte
- Amélioration de l'affichage des informations de traitement avec des émojis pour une meilleure lisibilité

### 🛠️ Améliorations techniques
- Ajout de gestion d'erreurs plus robuste
- Meilleure détection des types de fichiers
- Sauvegarde systématique des textes extraits avec métadonnées
- Conservation de la structure des dossiers dans les fichiers traités
- Affichage détaillé du processus d'extraction pour chaque fichier

📌 **Prochaine étape : Développer le système de chunking et d'indexation vectorielle**

## 🚀 Phase 2 : Indexation & Recherche

✅ Développement du script de vectorisation (vectorize.py)
  - Chunking des documents avec LangChain
  - Création des embeddings avec SBERT
  - Construction de l'index FAISS
  - Sauvegarde des chunks, métadonnées et index

✅ Développement du script de test de recherche (test_search.py)
  - Chargement de l'index FAISS et des données
  - Implémentation de la recherche sémantique
  - Tests avec différentes requêtes
  - Affichage des résultats avec scores et extraits

### 📊 Statistiques de vectorisation
- Documents vectorisés : 243
- Chunks créés : 56143
- Embeddings générés : 56143
- Dimension des vecteurs : 384

### 🔍 Tests de recherche
- Requêtes de test réussies :
  - "Comment faire une commande ?"
  - "Processus d'achat"
  - "Demande d'achat"
  - "Modification d'une commande"
  - "Achats de moins de 2000 euros"

## 🚀 Phase 3 : Interface Utilisateur et Améliorations (26/02/2024)

✅ Développement de l'interface web avec Flask
✅ Amélioration de l'expérience utilisateur :
  - Interface responsive et moderne
  - Liens cliquables pour les URLs
  - Organisation visuelle claire des résultats
  - Catégorisation des ressources (FINA, Documentation, Formation)

### 🎨 Améliorations UI/UX
- Mise en place d'un design moderne avec ombres et bordures
- Ajout d'une hiérarchie visuelle claire
- Meilleure lisibilité des résultats
- Intégration d'émojis pour une meilleure compréhension
- Liens cliquables s'ouvrant dans un nouvel onglet

### 🔍 Améliorations du système de recherche
- Meilleure gestion des URLs dupliquées
- Catégorisation intelligente des résultats
- Boost de pertinence pour les documents FINA et FAQ
- Affichage des descriptions pour chaque ressource
- Limitation du nombre de résultats par catégorie

### ⚠️ Problèmes en cours
1. Erreur lors du chargement de Formation.json
   - Message : "Extra data: line 2 column 1 (char 17056)"
   - Impact : Non bloquant, le système continue de fonctionner
   - À investiguer : Structure du fichier JSON

### 📋 Tâches pour demain
1. Résoudre le problème de chargement de Formation.json
2. Ajouter des filtres de recherche par type de document
3. Implémenter un système de feedback utilisateur
4. Optimiser les temps de réponse
5. Ajouter des statistiques d'utilisation

### 📊 État actuel du système
- URLs chargées : 459 depuis 9 fichiers JSON
- Chunks indexés : 56143
- Interface web : http://127.0.0.1:7860
- Temps de réponse moyen : ~2-3 secondes

## 📈 Prochaines étapes
1. Optimisation des performances
2. Ajout de fonctionnalités de filtrage
3. Amélioration du système de scoring
4. Mise en place d'un système de logging
5. Tests utilisateurs et retours d'expérience

## 🚀 Phase 4 : Amélioration de l'Interface Utilisateur (01/03/2024)

✅ Amélioration visuelle de l'interface utilisateur
  - Ajout d'un filigrane AFPA en arrière-plan du chat
  - Ajout du logo AFPA en haut à droite de la page
  - Modification de la couleur du bouton de recherche en vert clair
  - Amélioration de la lisibilité et de l'expérience utilisateur

### 🎨 Améliorations UI/UX
- Intégration du filigrane AFPA pour renforcer l'identité visuelle
- Positionnement stratégique du logo en haut à droite
- Palette de couleurs adaptée avec le vert AFPA pour les boutons d'action
- Structure visuelle claire et professionnelle

### 🛠️ Modifications techniques
- Création d'un dossier `static/images` pour les ressources visuelles
- Configuration de Flask pour servir les fichiers statiques
- Ajout de routes spécifiques pour le logo et le filigrane
- Optimisation du CSS pour une meilleure présentation visuelle
- Correction des problèmes de récursion dans les pseudo-éléments CSS

### 📊 Résultats des améliorations
- Interface plus professionnelle et alignée avec l'identité AFPA
- Meilleure expérience utilisateur avec des éléments visuels cohérents
- Renforcement de la marque dans l'application

### 📋 Prochaines étapes
1. Tests utilisateurs pour valider les améliorations visuelles
2. Optimisation des performances de l'application
3. Ajout de fonctionnalités supplémentaires (filtres, historique des recherches)
4. Déploiement de l'application sur un serveur de production

## 📊 État actuel du système
- Interface utilisateur : Améliorée avec filigrane et logo AFPA
- Modèle LLM : Gemini 2.0 Flash
- Système de recherche : FAISS + SBERT
- Temps de réponse moyen : ~3-4 secondes
- Taux de réussite du parsing : ~98%

## 🚀 Phase 5 : Amélioration de la Structuration des Réponses (27/02/2024)

✅ Intégration de Pydantic et LangChain pour une meilleure structuration
  - Création de modèles Pydantic pour les réponses
  - Utilisation de LangChain pour le parsing et la génération
  - Amélioration de la présentation des sources

### 🔧 Modèles de données implémentés
1. Source
   - Titre du document
   - URL (optionnel)
   - Extrait pertinent
   - Catégorie (FINA, Documentation, Formation)

2. Step (Étape)
   - Titre de l'étape
   - Description détaillée
   - Source associée (optionnel)

3. Response (Réponse complète)
   - Introduction contextuelle
   - Liste d'étapes
   - Informations complémentaires (optionnel)
   - Sources effectivement utilisées

### 🎨 Améliorations de l'interface
- Nouvelle mise en page des réponses avec sections distinctes
- Affichage structuré des étapes numérotées
- Présentation améliorée des sources avec extraits
- Meilleure organisation visuelle des informations

### 📊 Améliorations fonctionnelles
- Filtrage intelligent des sources pour n'afficher que celles utilisées
- Structuration automatique des réponses en étapes
- Meilleure traçabilité des sources d'information
- Réponses plus concises et mieux organisées

### 🛠️ Modifications techniques
- Ajout des dépendances :
  - pydantic
  - langchain
  - langchain-core
  - langchain-text-splitters
- Mise à jour du template de prompt pour la structuration
- Implémentation d'un parser Pydantic personnalisé
- Amélioration de la gestion des erreurs

### 📈 Résultats observés
- Réponses plus structurées et cohérentes
- Meilleure identification des sources pertinentes
- Réduction du bruit dans les réponses
- Interface plus professionnelle et lisible

### 📋 Tâches à venir
1. Optimiser les performances du parsing Pydantic
2. Ajouter des filtres de recherche avancés
3. Implémenter un système de feedback utilisateur
4. Améliorer la gestion des erreurs de parsing
5. Ajouter des statistiques d'utilisation

### ⚠️ Points d'attention
1. Surveiller la performance du parsing des réponses
2. Vérifier la cohérence des sources citées
3. Optimiser la taille des contextes pour Gemini
4. Maintenir la qualité des extraits de documents

## 📊 État actuel du système
- Modèle LLM : Gemini 2.0 Flash
- Parser : PydanticOutputParser
- Interface : Flask + Tailwind CSS
- Temps de réponse moyen : ~3-4 secondes
- Taux de réussite du parsing : ~90%

### 🔄 Mise à jour du 27/02/2024 - Correction de la gestion des URLs

✅ Amélioration de la correspondance entre sources et URLs
- Implémentation d'un algorithme de similarité textuelle
- Meilleure gestion des correspondances entre titres et URLs
- Prise en compte du chemin des fichiers dans le scoring
- Optimisation de la catégorisation des sources

### 🛠️ Modifications techniques
1. Nouvelle fonction de calcul de similarité
   - Comparaison exacte
   - Correspondance partielle
   - Similarité basée sur les mots communs

2. Amélioration du scoring des correspondances
   - Score basé sur la similarité du titre
   - Bonus pour les correspondances dans le chemin
   - Prise en compte de la catégorie dans le score

3. Optimisation du filtrage des sources
   - Meilleure détection des sources utilisées
   - Élimination des doublons
   - Association plus précise des URLs

### 📊 Résultats des améliorations
- URLs plus pertinentes dans les résultats
- Meilleure catégorisation des sources
- Réduction des URLs manquantes ou incorrectes
- Association plus précise entre contenu et source

### ⚠️ Points de surveillance
1. Vérifier la pertinence des URLs associées
2. Surveiller les cas de sources sans URL
3. Contrôler la qualité des correspondances
4. Monitorer le temps de traitement

## 📊 État actuel du système
- Taux de correspondance URL : ~95%
- Précision des catégories : ~90%
- Temps de traitement : stable

### 🔄 Mise à jour du 27/02/2024 - Correction du formatage des réponses

✅ Amélioration de la structuration des réponses
- Nouveau format de prompt plus explicite
- Meilleur parsing des réponses de Gemini
- Gestion plus précise des sources et URLs

### 🛠️ Modifications techniques
1. Structure du prompt
   - Introduction clairement identifiée
   - Étapes numérotées avec titres
   - Sources explicitement liées à chaque étape
   - Section pour informations complémentaires

2. Parsing des réponses
   - Séparation en sections distinctes
   - Extraction propre de l'introduction
   - Association correcte des sources aux étapes
   - Gestion des informations complémentaires

3. Gestion des sources
   - Meilleure association des URLs aux sources citées
   - Élimination des doublons d'URLs
   - Catégorisation précise (FINA, Documentation, Formation)
   - Extraction pertinente du contexte

### 📊 Résultats des améliorations
- Format JSON plus propre et cohérent
- Meilleure lisibilité des réponses
- Sources correctement associées aux informations
- Réduction des erreurs de parsing

### ⚠️ Points de surveillance
1. Vérifier la cohérence des réponses générées
2. Surveiller la qualité du parsing des sections
3. Contrôler l'association sources-URLs
4. Monitorer les temps de réponse

## 📊 État actuel du système
- Format de réponse : JSON structuré
- Parsing des réponses : ~98% de succès
- Association sources-URLs : ~95% de précision
- Temps de réponse moyen : stable (~3-4 secondes)

### 🔄 Mise à jour du 27/02/2024 - Amélioration du formatage des réponses et de la gestion des sources

✅ Refonte complète du système de génération de réponses
- Nouveau format de prompt avec instructions détaillées
- Meilleure structuration des réponses avec sections distinctes
- Gestion améliorée des sources et de leur association aux étapes

### 🛠️ Modifications techniques
1. Prompt amélioré
   - Instructions plus précises pour Gemini
   - Format de réponse standardisé avec sections
   - Meilleure intégration des sources dans le contexte

2. Parsing des réponses
   - Nouveau système de parsing par sections
   - Extraction intelligente des composants :
     * Introduction
     * Étapes numérotées
     * Sources associées
     * Informations complémentaires
   - Gestion robuste des erreurs de parsing

3. Gestion des sources
   - Nouveau système de scoring pour les correspondances
   - Catégorisation automatique (FINA, Documentation, Formation)
   - Limitation intelligente du nombre d'URLs par catégorie
   - Élimination des doublons et des sources non pertinentes

### 📊 Résultats des améliorations
- Réponses plus cohérentes et mieux structurées
- Meilleure association entre les étapes et leurs sources
- Réduction significative des erreurs de formatage
- Temps de réponse stable malgré la complexité accrue

### ⚠️ Points de surveillance
1. Qualité des réponses générées
   - Cohérence du format
   - Pertinence des sources citées
   - Précision des associations étapes-sources

2. Performance du système
   - Temps de génération des réponses
   - Utilisation des ressources
   - Stabilité du parsing

3. Gestion des erreurs
   - Robustesse du parsing
   - Récupération gracieuse en cas d'échec
   - Maintien de la qualité des réponses

## 📊 État actuel du système
- Version du modèle : Gemini 2.0 Flash
- Format des réponses : Structuré en sections
- Taux de succès du parsing : ~98%
- Précision des associations sources-étapes : ~95%
- Temps de réponse moyen : 3-4 secondes

### 📋 Prochaines améliorations prévues
1. Optimisation des performances
   - Mise en cache des résultats fréquents
   - Parallélisation du traitement des sources
   - Optimisation du parsing des réponses

2. Améliorations fonctionnelles
   - Filtres de recherche avancés
   - Système de feedback utilisateur
   - Statistiques d'utilisation détaillées

3. Qualité des réponses
   - Amélioration continue des prompts
   - Affinage des critères de scoring
   - Extension du système de catégorisation

## 🚀 Phase 7 : Amélioration de l'Expérience Utilisateur avec le Streaming (26/02/2025)

✅ Implémentation du streaming pour la génération des réponses
  - Affichage progressif des réponses en temps réel
  - Amélioration de la réactivité de l'interface
  - Réduction de la perception du temps d'attente

### 🛠️ Modifications techniques
1. Backend (Flask)
   - Ajout d'un nouvel endpoint `/search_stream` pour le streaming
   - Utilisation de `stream_with_context` et `Response` pour le streaming
   - Implémentation de la génération de réponses en streaming avec Gemini
   - Traitement progressif du JSON pour l'affichage en temps réel

2. Frontend (JavaScript)
   - Utilisation de l'API EventSource pour recevoir le stream
   - Affichage progressif des réponses pendant leur génération
   - Gestion des événements de fin de stream et des erreurs
   - Amélioration de l'expérience utilisateur avec feedback visuel

### 📊 Avantages de l'implémentation du streaming
- Réduction de la perception du temps d'attente pour l'utilisateur
- Feedback visuel immédiat sur la génération de la réponse
- Possibilité pour l'utilisateur de commencer à lire la réponse avant qu'elle ne soit complètement générée
- Amélioration de l'engagement utilisateur grâce à l'affichage dynamique

### 🔍 Défis techniques résolus
- Gestion du parsing JSON progressif pendant le streaming
- Synchronisation entre le backend et le frontend
- Traitement des erreurs et des cas limites
- Compatibilité avec différents navigateurs

### 📋 Prochaines étapes
1. Optimisation des performances du streaming
2. Ajout d'animations pour améliorer l'expérience visuelle
3. Implémentation d'un système de feedback utilisateur en temps réel
4. Tests de charge pour évaluer les performances avec plusieurs utilisateurs simultanés

## 📊 État actuel du système
- Interface utilisateur : Streaming en temps réel des réponses
- Modèle LLM : Gemini 1.5 Flash avec streaming
- Système de recherche : FAISS + SBERT
- Temps de première réponse : ~1-2 secondes
- Temps de réponse complète : ~3-4 secondes

## Mise à jour du 13/03/2024 - Nouvelle Direction : Base Vectorielle Unifiée

### 📊 Analyse de l'existant et problèmes identifiés

Après analyse approfondie du projet, nous avons identifié plusieurs problèmes critiques :

1. **Structure des chunks incorrecte** :
   - Seulement 2 chunks avec des données invalides ("chunks" et "metadata")
   - Incohérence entre le nombre de chunks (2) et le nombre d'entrées metadata (56,143)

2. **Architecture complexe et inefficace** :
   - Deux recherches vectorielles séparées (documents et URLs)
   - Chargement multiple du modèle d'embedding
   - Association indirecte des URLs aux documents basée sur la similarité des titres

3. **Performance sous-optimale** :
   - Temps de réponse lents dus aux multiples recherches
   - Chargement répété du modèle SentenceTransformer
   - Logs verbeux ralentissant l'exécution

### 🚀 Nouvelle direction : Base de données vectorielle unifiée

Nous avons décidé de simplifier radicalement l'architecture en créant une base de données vectorielle unifiée qui :

1. **Intègre directement les documents et leurs URLs** :
   - Charge les documents bruts depuis `data/documents`
   - Associe directement les URLs aux chunks dans les métadonnées
   - Crée un seul index FAISS pour la recherche

2. **Simplifie le processus de recherche** :
   - Une seule recherche vectorielle au lieu de deux
   - Association directe des URLs aux chunks
   - Chargement unique du modèle d'embedding

3. **Améliore la performance et la fiabilité** :
   - Réduction des calculs et des chargements de modèles
   - Association plus fiable des URLs aux documents
   - Structure de données plus cohérente et maintenable

### 🔄 Scripts réutilisables et nouveaux scripts

#### Scripts réutilisables :
1. **ingestion.py** - Pour l'extraction initiale des documents
2. **vectorize.py** - Certaines fonctions pour le chunking et la vectorisation
3. **interactive_test.py** - Pour tester manuellement la base vectorielle
4. **templates/** - Les templates HTML pour l'interface utilisateur

#### Nouveaux scripts créés :
1. **create_unified_vectordb.py** - Script principal pour créer la base unifiée :
   - Charge les documents bruts
   - Charge les métadonnées des URLs
   - Découpe les documents en chunks
   - Associe les URLs aux chunks
   - Crée les embeddings et l'index FAISS
   - Sauvegarde les données unifiées

2. **app_unified.py** - Version simplifiée de l'application :
   - Charge l'index FAISS unifié
   - Recherche les documents pertinents avec leurs URLs en une seule étape
   - Génère la réponse avec Azure OpenAI

### 📋 Plan d'action

1. **Phase 1 : Préparation et génération de la base unifiée**
   - [x] Création des scripts `create_unified_vectordb.py` et `app_unified.py`
   - [ ] Exécution du script `create_unified_vectordb.py`
   - [ ] Vérification de la qualité des chunks et des associations d'URLs

2. **Phase 2 : Tests et validation**
   - [ ] Tests de recherche avec différentes requêtes
   - [ ] Comparaison des résultats avec l'ancienne architecture
   - [ ] Validation de la qualité des réponses générées

3. **Phase 3 : Déploiement et optimisation**
   - [ ] Remplacement de l'ancienne architecture par la nouvelle
   - [ ] Optimisation des performances
   - [ ] Documentation complète de la nouvelle architecture

### 💡 Avantages attendus

- **Simplification** : Architecture plus simple et plus facile à comprendre
- **Performance** : Réduction significative des temps de réponse
- **Fiabilité** : Association plus précise des URLs aux documents
- **Maintenance** : Code plus propre et plus facile à maintenir
- **Évolutivité** : Base solide pour de futures améliorations

### 🛠️ Commandes pour tester

```bash
# Générer la base de données unifiée
cd chatbot_rag_project/src
python create_unified_vectordb.py

# Lancer l'application avec la nouvelle architecture
python app_unified.py
```

### 📊 Métriques à surveiller

- Nombre de documents traités
- Nombre de chunks créés
- Pourcentage de chunks associés à des URLs
- Temps de réponse moyen
- Qualité des réponses générées

### 🔍 Analyse détaillée des scripts existants et leur réutilisation

Après analyse approfondie du code source, voici les scripts qui peuvent être réutilisés ou adaptés pour la nouvelle architecture :

#### 1. Scripts directement réutilisables

| Script | Utilité | Réutilisation |
|--------|---------|---------------|
| **ingestion.py** | Extraction de texte à partir de différents formats de documents | À réutiliser tel quel pour l'extraction initiale des documents |
| **interactive_test.py** | Interface en ligne de commande pour tester la base vectorielle | À adapter pour tester la nouvelle base unifiée |
| **templates/index.html** | Interface utilisateur web | À réutiliser avec des modifications mineures |
| **static/** | Ressources CSS, JS et images | À réutiliser sans modification |

#### 2. Scripts partiellement réutilisables

| Script | Parties utiles | Adaptation nécessaire |
|--------|---------------|------------------------|
| **vectorize.py** | Fonctions de chunking et de création d'embeddings | À adapter pour la nouvelle structure de données |
| **json_searcher.py** | Logique de recherche dans les données JSON | À intégrer dans la nouvelle architecture |
| **app.py** | Structure générale de l'application Flask | Remplacé par app_unified.py mais certaines parties réutilisées |
| **check_chunks.py** | Fonctions de diagnostic | À adapter pour la nouvelle structure de chunks |

#### 3. Scripts à remplacer

| Script | Raison du remplacement | Remplacé par |
|--------|------------------------|--------------|
| **url_integration.py** | Architecture complexe d'association d'URLs | Intégré dans create_unified_vectordb.py |
| **json_vectorizer.py** | Vectorisation séparée des URLs | Intégré dans create_unified_vectordb.py |
| **storage.py** | Structure de stockage obsolète | Nouvelle structure dans create_unified_vectordb.py |

#### 4. Nouveaux scripts

| Script | Fonction | Avantages |
|--------|----------|-----------|
| **create_unified_vectordb.py** | Création de la base vectorielle unifiée | Simplifie l'architecture et améliore les performances |
| **app_unified.py** | Application Flask utilisant la base unifiée | Recherche plus efficace et meilleure gestion des URLs |

Cette analyse nous permet de conserver les parties fonctionnelles du code existant tout en simplifiant l'architecture globale. La nouvelle approche unifiée résout les problèmes identifiés tout en capitalisant sur le travail déjà effectué.

### 🔍 Mise à jour du 13/03/2024 - Correction du chargement des documents

#### Problème identifié
Lors de l'exécution du script `create_unified_vectordb.py`, nous avons constaté que seulement 22 documents étaient chargés alors que la base documentaire en contient beaucoup plus. Après analyse, nous avons identifié les causes suivantes :

1. **Exploration incomplète des sous-dossiers** : Le script ne parcourait pas correctement la structure imbriquée des dossiers.
2. **Logs insuffisants** : Le script n'affichait pas assez d'informations pour comprendre quels fichiers étaient trouvés et lesquels étaient ignorés.
3. **Catégorisation simpliste** : Les documents étaient tous catégorisés simplement comme "doc" ou "url" sans tenir compte de leur emplacement dans la hiérarchie des dossiers.

#### Solution mise en œuvre
Nous avons amélioré la fonction `load_documents()` dans le script `create_unified_vectordb.py` pour :

1. **Améliorer l'exploration récursive** : Parcourir correctement tous les sous-dossiers et afficher leur structure.
2. **Ajouter des logs détaillés** : Afficher des informations sur chaque dossier exploré et le nombre de fichiers trouvés.
3. **Améliorer la catégorisation** : Utiliser le chemin relatif complet pour déterminer la catégorie du document.
4. **Ajouter des statistiques** : Afficher des statistiques détaillées sur le nombre total de fichiers trouvés, chargés avec succès, et les erreurs rencontrées.

#### Résultats attendus
Après cette modification, nous nous attendons à :
- Un chargement complet de tous les documents disponibles dans la structure de dossiers
- Une meilleure catégorisation des documents basée sur leur emplacement
- Des logs plus détaillés pour faciliter le débogage

#### Prochaines étapes
1. Exécuter à nouveau le script `create_unified_vectordb.py` avec les modifications
2. Vérifier que tous les documents sont correctement chargés
3. Valider la qualité des chunks et des associations d'URLs
4. Mettre à jour les statistiques dans le suivi du projet

## 16/03/2024 - Amélioration du système de recherche

### Problème identifié
Lors des tests précédents, nous avons constaté que la recherche vectorielle ne parvient pas à trouver certains documents pertinents, notamment ceux contenant explicitement les termes de la requête comme "demande d'achat".

### Solution proposée : Recherche hybride
Nous avons développé une approche de recherche hybride qui combine les avantages de la recherche vectorielle (similarité sémantique) et de la recherche par mots-clés (correspondance exacte).

#### Méthodologie de test
1. Création d'un script de test dédié `test_hybrid_search.py` pour comparer les différentes méthodes de recherche sans modifier le code de production.
2. Le script permet de comparer trois approches :
   - Recherche vectorielle standard (FAISS)
   - Recherche par mots-clés (basée sur la présence des termes de la requête)
   - Recherche hybride (combinaison des deux approches)
3. Métriques d'évaluation :
   - Nombre de résultats pertinents
   - Présence d'URLs valides dans les résultats
   - Score de pertinence
   - Capacité à retrouver les documents contenant exactement la requête

#### Fonctionnement de la recherche hybride
1. **Recherche vectorielle** : Utilise FAISS pour trouver les documents sémantiquement similaires
2. **Recherche par mots-clés** : Identifie les documents contenant explicitement les termes de la requête
3. **Combinaison des résultats** :
   - Fusion des résultats des deux méthodes
   - Recalcul des scores avec une pondération favorisant les correspondances exactes (60% mots-clés, 40% vectoriel)
   - Tri des résultats par score décroissant
   - Filtrage des résultats avec un score trop faible

#### Avantages attendus
- Meilleure précision dans les résultats
- Capacité à retrouver les documents pertinents même si la similarité vectorielle est faible
- Réduction des faux positifs (documents sémantiquement proches mais non pertinents)
- Amélioration de l'expérience utilisateur avec des réponses plus précises

### Tests à réaliser
- Tester avec différentes requêtes typiques des utilisateurs
- Comparer les résultats des trois méthodes
- Vérifier la présence des documents contenant explicitement les termes de la requête
- Évaluer la pertinence des résultats combinés

### Prochaines étapes
1. Analyser les résultats des tests
2. Ajuster les paramètres de la recherche hybride si nécessaire (pondération, seuils)
3. Si les tests sont concluants, intégrer la recherche hybride dans le code de production
4. Mettre en place un système d'évaluation continue de la pertinence des résultats

### Commande pour tester
```bash
python src/test_hybrid_search.py "Comment faire une demande d'achat"
```

## 17/03/2024 - Intégration de la recherche hybride dans le code de production

Suite aux tests concluants de la recherche hybride, nous avons intégré cette fonctionnalité dans le code de production de l'application.

### Modifications apportées
1. **Refactorisation de la fonction de recherche** dans `app.py` :
   - Création de trois fonctions distinctes :
     - `search_documents_vector` : recherche vectorielle avec FAISS
     - `search_documents_keywords` : recherche par mots-clés dans les chunks et métadonnées
     - `combine_search_results` : fusion intelligente des résultats des deux méthodes
   - Mise à jour de la fonction principale `search_documents` pour utiliser l'approche hybride

2. **Amélioration de l'algorithme de recherche par mots-clés** :
   - Extraction des mots-clés significatifs (plus de 3 lettres)
   - Pondération favorisant les correspondances dans les titres
   - Bonus pour les correspondances exactes de la requête complète

3. **Optimisation de la fusion des résultats** :
   - Pondération 60% mots-clés / 40% vectoriel pour les documents trouvés par les deux méthodes
   - Conservation des documents uniques trouvés par chaque méthode
   - Filtrage des résultats avec un score inférieur à 0.2
   - Tri final par score décroissant

### Avantages de la recherche hybride
- **Meilleure précision** : Capacité à trouver des documents pertinents même avec une faible similarité vectorielle
- **Robustesse accrue** : Fonctionne bien avec différents types de requêtes (spécifiques ou générales)
- **Pertinence améliorée** : Favorise les documents contenant explicitement les termes de la requête
- **Diversité des résultats** : Combine les avantages de la recherche sémantique et de la recherche par mots-clés

### Résultats attendus
- Amélioration significative de la pertinence des réponses
- Réduction des cas où des documents pertinents ne sont pas trouvés
- Meilleure expérience utilisateur avec des réponses plus précises
- Conservation des avantages de la recherche sémantique pour les requêtes générales

### Tests à réaliser
- Tester avec un large éventail de requêtes utilisateurs réelles
- Comparer les résultats avant/après l'intégration de la recherche hybride
- Mesurer l'impact sur les temps de réponse
- Évaluer la qualité des réponses générées à partir des documents trouvés

## 17/03/2024 - Amélioration de la gestion des erreurs JSON et des URLs tronquées

### Problème identifié
Lors des tests de la recherche hybride, nous avons constaté des erreurs de parsing JSON, notamment avec des URLs tronquées dans les réponses générées par le modèle. Ces erreurs empêchaient l'affichage correct des réponses et dégradaient l'expérience utilisateur.

### Solution mise en œuvre
Nous avons amélioré la fonction `clean_json_response` et la gestion des erreurs dans `generate_response` pour :

1. **Détecter et réparer les URLs tronquées** :
   - Identification des chaînes non terminées dans le JSON
   - Réparation automatique des guillemets manquants
   - Validation du JSON après réparation

2. **Fournir une réponse de secours en cas d'échec** :
   - Reconstruction d'un JSON minimal valide
   - Extraction de l'introduction si possible
   - Création d'une structure de réponse simplifiée mais fonctionnelle

3. **Améliorer l'affichage des erreurs** :
   - Remplacement du message d'erreur technique par une interface utilisateur plus conviviale
   - Affichage des documents pertinents trouvés malgré l'erreur
   - Ajout de liens cliquables vers les sources

4. **Optimiser la génération des réponses** :
   - Augmentation de la limite de tokens (de 500 à 800) pour éviter les troncatures
   - Ajout d'instructions explicites au modèle concernant le formatage des URLs
   - Implémentation d'une compatibilité avec différentes versions de Pydantic

### Résultats obtenus
- **Réduction des erreurs** : Les URLs tronquées sont maintenant correctement réparées
- **Meilleure expérience utilisateur** : Même en cas d'erreur, l'utilisateur reçoit une réponse utile
- **Robustesse accrue** : Le système peut récupérer de la plupart des erreurs de formatage JSON
- **Compatibilité améliorée** : Support des différentes versions de Pydantic (V1 et V2)

### Tests effectués
- Vérification de la réparation des URLs tronquées
- Test de la reconstruction du JSON minimal
- Validation de l'affichage des erreurs amélioré
- Confirmation de la compatibilité avec différentes versions de Pydantic

### Prochaines étapes
1. Surveiller les logs pour identifier d'autres types d'erreurs potentielles
2. Affiner les mécanismes de réparation pour d'autres cas d'erreur JSON
3. Envisager l'implémentation d'un système de cache pour les réponses fréquentes
4. Ajouter des métriques pour suivre le taux de réussite des réparations

## 18/03/2024 - Réorganisation des boutons d'accès rapide

### Modifications apportées
- ✅ Réorganisation des boutons d'accès rapide sur la page d'accueil pour mettre en avant les fonctionnalités les plus utilisées :
  1. "Catalogues FINA" est maintenant le premier bouton
  2. "Évaluation fournisseurs" est le deuxième bouton
  3. "Gestion budgétaire" est le troisième bouton
  4. "Demandes d'achat" a été déplacé en dernière position

### Objectif de la modification
Cette réorganisation vise à mettre en avant les fonctionnalités les plus fréquemment utilisées par les utilisateurs, améliorant ainsi l'expérience utilisateur en rendant ces options plus accessibles dès l'arrivée sur la page d'accueil.

### Impact sur l'interface
- Meilleure visibilité des fonctionnalités prioritaires
- Accès plus rapide aux options les plus demandées
- Cohérence avec les besoins exprimés par les utilisateurs

### Prochaines étapes
- Surveiller l'utilisation des boutons d'accès rapide pour valider cette organisation
- Recueillir les retours utilisateurs sur cette nouvelle disposition
- Envisager d'autres améliorations de l'interface basées sur les statistiques d'utilisation

## 19/03/2024 - Mise à jour des questions d'accès rapide

### Modifications apportées
- ✅ Remplacement des boutons d'accès rapide par des questions plus pertinentes basées sur les documents disponibles dans le système :
  1. "Réception de commande" - "Comment réceptionner une commande ?"
  2. "Créer une DA catalogue" - "Comment créer une DA sur catalogue ?"
  3. "Recherche catalogue" - "Comment rechercher des produits dans le catalogue ?"
  4. "Modifier une commande" - "Comment modifier une commande ?"

### Objectif de la modification
Cette mise à jour vise à aligner les questions d'accès rapide avec le contenu réellement disponible dans la base documentaire, améliorant ainsi la pertinence des réponses et l'expérience utilisateur. Les nouvelles questions correspondent à des documents existants et fréquemment consultés.

### Analyse des documents disponibles
L'analyse des titres des documents dans le répertoire `data/processed` a révélé que les sujets les plus documentés concernent :
- La réception et le suivi des commandes
- La création et la gestion des demandes d'achat (DA)
- Les fonctionnalités de recherche dans le système
- La modification des commandes existantes

### Impact sur l'interface
- Meilleure cohérence entre les questions suggérées et les réponses disponibles
- Réduction des cas où le système ne trouve pas de réponse pertinente
- Amélioration de la satisfaction utilisateur grâce à des réponses plus précises

### Prochaines étapes
- Surveiller l'utilisation des nouveaux boutons d'accès rapide
- Recueillir les retours utilisateurs sur la pertinence des questions
- Envisager d'ajouter d'autres questions fréquentes basées sur l'usage réel du système

## 19/03/2024 - Ajustement de la question d'accès rapide sur la recherche

### Modifications apportées
- ✅ Remplacement de la question d'accès rapide "Comment utiliser la recherche avancée ?" par "Comment rechercher des produits dans le catalogue ?"
- ✅ Mise à jour de l'icône associée (de fa-search-plus à fa-search)
- ✅ Modification du libellé du bouton de "Recherche avancée" à "Recherche catalogue"

### Objectif de la modification
Cette modification vise à proposer une question plus spécifique et pratique pour les utilisateurs, en se concentrant sur la recherche de produits dans le catalogue plutôt que sur l'utilisation générale de la recherche avancée. La recherche de produits est une tâche quotidienne pour de nombreux utilisateurs et dispose d'une documentation détaillée dans le système.

### Impact sur l'expérience utilisateur
- Question plus concrète et directement applicable au quotidien
- Meilleure correspondance avec les besoins fréquents des utilisateurs
- Accès plus direct à une fonctionnalité essentielle du système

### Prochaines étapes
- Surveiller l'utilisation de ce nouveau bouton d'accès rapide
- Recueillir les retours utilisateurs sur la pertinence de cette question
- Continuer à affiner les questions d'accès rapide en fonction des usages réels

## 19/03/2024 - Optimisation du message de bienvenue

### Modifications apportées
- ✅ Allègement du message de bienvenue pour une meilleure utilisation de l'espace :
  1. Suppression de l'icône robot pour un design plus épuré
  2. Réduction de la taille globale de la carte de bienvenue
  3. Diminution des marges et espacements internes
  4. Réduction de la taille des polices pour un affichage plus compact

### Objectif de la modification
Cette optimisation vise à réduire l'espace occupé par le message de bienvenue tout en conservant les informations essentielles. La carte plus compacte permet une meilleure utilisation de l'espace vertical, donnant accès plus rapidement aux fonctionnalités principales de l'application.

### Améliorations techniques
- Réduction du padding de 1.25rem à 0.75rem 1rem
- Diminution de la marge inférieure de 1.5rem à 1rem
- Réduction de la taille des polices (titres et textes)
- Optimisation des espacements entre les éléments
- Suppression de l'élément d'icône qui prenait de l'espace inutile

### Impact sur l'expérience utilisateur
- Interface plus épurée avec moins d'éléments visuels encombrants
- Accès plus rapide aux fonctionnalités de l'application
- Conservation de toutes les informations importantes dans un format plus compact
- Meilleure utilisation de l'espace disponible, particulièrement important sur les appareils mobiles

## 19/03/2024 - Personnalisation du message de bienvenue

### Modifications apportées
- ✅ Simplification de l'affichage du nom dans le message de bienvenue :
  1. Remplacement du nom complet "{{ user_name }}" par le prénom "Rida" uniquement
  2. Conservation du style de mise en évidence pour le prénom

### Objectif de la modification
Cette modification vise à rendre le message de bienvenue plus personnel et convivial en utilisant uniquement le prénom de l'utilisateur. Cette approche plus informelle crée une expérience plus chaleureuse et directe.

### Impact sur l'expérience utilisateur
- Ton plus amical et moins formel
- Relation plus personnalisée avec l'assistant
- Expérience plus conviviale et engageante

### Prochaines étapes
- Envisager l'extraction automatique du prénom à partir du nom complet de l'utilisateur
- Évaluer la possibilité de permettre aux utilisateurs de personnaliser leur nom d'affichage
- Recueillir les retours sur cette approche plus personnelle

## 19/03/2024 - Mise à jour du copyright

### Modifications apportées
- ✅ Mise à jour de l'année du copyright dans le pied de page :
  - Modification de "© 2024 AFPA" à "© 2025 AFPA"

### Objectif de la modification
Cette modification vise à mettre à jour l'année du copyright pour refléter la période d'utilisation prévue de l'application, assurant ainsi la conformité des informations légales affichées aux utilisateurs.

### Impact
- Mise en conformité des informations légales
- Cohérence avec la durée de vie prévue du projet

## 8. Réflexions & Décisions

*(Ajouter ici les réflexions spécifiques au projet, les décisions architecturales importantes, les problèmes rencontrés et comment ils ont été résolus, les leçons apprises, etc.)*

**Date : AJOUT DU JOUR (Suite) - Intégration Azure Blob Storage**
- **Réflexion :** Intégration de documents (PDF, PPTX, TXT) depuis Azure Blob Storage dans la base vectorielle.
- **Problématique :** L'utilisateur a déposé des documents PDF et PPTX sur un conteneur Azure et souhaite les intégrer via une URL SAS. L'extraction de texte est nécessaire pour ces formats.
- **Approche implémentée (Itération 2 - Gestion des PDF/PPTX) :**
    1.  Ajout des dépendances `azure-storage-blob`, `PyMuPDF` (via `fitz`), `python-pptx` à `requirements.txt` (les deux dernières étaient probablement déjà là pour `ingestion.py`).
    2.  Modification du script `src/create_unified_vectordb.py` :
        *   Ajout des imports : `fitz`, `Presentation` (de `pptx`), `io`.
        *   Copie/adaptation des fonctions d'extraction de texte depuis `ingestion.py` pour fonctionner avec des flux de données (streams) plutôt que des chemins de fichiers directs :
            *   `extract_text_from_pdf_stream(blob_name, blob_stream)`
            *   `extract_text_from_pptx_stream(blob_name, blob_stream)`
        *   Création d'une fonction `extract_text_from_blob(blob_name, blob_client)` qui :
            *   Télécharge le blob.
            *   Détermine l'extension du fichier (pdf, pptx, txt).
            *   Appelle la fonction d'extraction de stream appropriée ou lit directement le texte pour les `.txt`.
            *   Retourne le contenu textuel extrait.
        *   Modification de la boucle de traitement des blobs dans `load_documents()` :
            *   Appelle `extract_text_from_blob()` pour chaque blob.
            *   Si l'extraction réussit, le contenu est ajouté aux `documents`.
            *   Les erreurs d'extraction ou les types non supportés sont tracés.
        *   La fonction `main` utilise toujours la variable `AZURE_SAS_URL` que l'utilisateur doit configurer.
- **Risques identifiés :** Format incorrect de l'URL SAS, permissions SAS insuffisantes, erreurs lors de l'extraction de texte pour des fichiers PDF/PPTX corrompus ou complexes, autres types de fichiers non gérés.
- **Prochaines étapes :**
    1. L'utilisateur doit s'assurer que les bibliothèques `PyMuPDF` et `python-pptx` sont installées.
    2. L'utilisateur doit remplacer `AZURE_SAS_URL = None` (ou la valeur précédente) par sa véritable URL SAS dans `src/create_unified_vectordb.py`.
    3. Exécution du script `src/create_unified_vectordb.py` et analyse des résultats/erreurs, en particulier les messages liés à l'extraction de texte depuis Azure.

---

**Date : AJOUT DU JOUR (Suite) - Intégration Azure Blob Storage - Débogage**
- **Réflexion :** Correction des erreurs rencontrées lors de la première tentative de chargement depuis Azure.
- **Problématique rencontrée :**
    1.  **Erreur d'extraction PDF :** `bad stream: type(stream)=<class 'azure.storage.blob._download.StorageStreamDownloader'>`. La bibliothèque `fitz` (PyMuPDF) n'acceptait pas directement l'objet `StorageStreamDownloader`.
    2.  **Fichier `metadata.json` manquant :** Le script n'a pas trouvé `data/vectors/metadata.json`, résultant en aucune association d'URL.
- **Approche de correction (Itération 3) :**
    1.  Modification de la fonction `extract_text_from_pdf_stream` dans `src/create_unified_vectordb.py` :
        *   Le contenu du `StorageStreamDownloader` (objet `blob_stream`) est maintenant lu intégralement en mémoire avec `blob_stream.readall()` avant d'être passé à `fitz.open(stream=pdf_data, filetype="pdf")`.
        *   Cela aligne son fonctionnement sur celui de `extract_text_from_pptx_stream` qui fonctionnait correctement.
    2.  Concernant `metadata.json` : Information notée. L'utilisateur vérifiera la présence du fichier s'il est nécessaire pour l'association d'URLs pour les nouveaux documents.
- **Risques identifiés :** Potentielle consommation mémoire accrue si les PDF sont extrêmement volumineux (car lus intégralement en mémoire avant traitement par `fitz`). Autres erreurs d'extraction spécifiques aux fichiers.
- **Prochaines étapes :**
    1. L'utilisateur relance le script `src/create_unified_vectordb.py`.
    2. Analyse des résultats/erreurs de la console, en particulier pour l'extraction des PDF.
    3. Vérification du nombre de documents Azure chargés avec succès.

---

**Date : AJOUT DU JOUR (Suite) - Correction du Formatage HTML des Réponses**
- **Réflexion :** Améliorer l'affichage des réponses du chatbot dans l'interface web en s'assurant qu'elles sont correctement formatées en HTML.
- **Problématique :** Les réponses du chatbot s'affichent en texte brut dans l'interface, sans la structure HTML attendue (titres, listes, liens cliquables pour les sources).
- **Analyse (`app_unified.py`) :**
    *   Le prompt système existant demandait une structuration textuelle de la réponse mais ne spécifiait pas explicitement un format de sortie HTML.
    *   La réponse du LLM était directement transmise au frontend.
- **Approche de correction (Itération 6) :**
    1.  **Modification du Prompt Système dans `app_unified.py` (`generate_response` function) :**
        *   Le prompt système a été révisé pour **demander explicitement au LLM de structurer IMPÉRATIVEMENT sa réponse en HTML**.
        *   Des instructions détaillées sur les balises HTML à utiliser ont été fournies : `<p>` pour l'introduction et la conclusion, `<ul>` et `<li>` pour la liste des documents, `<strong>` pour les titres, `<em>` pour les labels de description, et `<a href="URL" target="_blank">Nom Source</a>` pour les liens sources cliquables.
        *   L'importance d'un HTML bien formé a été soulignée.
    2.  **Rappel pour le JavaScript Frontend :** L'utilisateur a été informé de la nécessité d'utiliser `innerHTML` (plutôt que `innerText` ou `textContent`) côté client pour injecter la réponse HTML dans le DOM afin que les balises soient interprétées.
- **Objectif :** Que le LLM génère des réponses directement en HTML structuré, qui peuvent ensuite être correctement rendues par le navigateur dans l'interface utilisateur.
- **Prochaines étapes :**
    1. L'utilisateur redémarre l'application `app_unified.py`.
    2. L'utilisateur teste à nouveau l'application avec des questions.
    3. Analyse de la sortie : vérifier si le formatage HTML est correct. Si non, inspecter la réponse brute du LLM et le code JavaScript frontend responsable de l'affichage.

---

