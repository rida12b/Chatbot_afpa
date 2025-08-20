import os
import json
import pickle
import faiss
import numpy as np
import logging
import re
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from dotenv import load_dotenv
from auth import login_required, get_user, generate_secret_key, verify_credentials

# Chargement des variables d'environnement
load_dotenv()

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', generate_secret_key())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 heures

# Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Variables globales
index = None
chunks = None
metadata = None
embedding_model = None

def load_unified_system():
    """Charge l'index FAISS unifié, les chunks et les métadonnées."""
    global embedding_model
    
    # Charger le modèle d'embedding une seule fois
    if embedding_model is None:
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Charger l'index et les données
    index = faiss.read_index("models/unified_index.bin")
    
    with open("models/unified_chunks.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        chunks = data.get("chunks", [])
        
    with open("models/unified_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
        
    return index, chunks, metadata

def search_documents(query, index, chunks, metadata, top_k=5):
    """Recherche hybride: vectorielle + mots-clés. Retourne des documents triés par score."""
    # Recherche vectorielle
    query_vector = embedding_model.encode([query])[0].astype('float32')
    distances, indices = index.search(np.array([query_vector]), top_k)

    vector_results = []
    for i, idx in enumerate(indices[0]):
        if idx >= 0 and idx < len(metadata):
            doc = {
                "title": metadata[idx]["title"],
                "extract": chunks[idx] if idx < len(chunks) else "",
                "score": float(1 - distances[0][i])
            }
            if "url" in metadata[idx]:
                doc["url"] = metadata[idx]["url"]
                doc["category"] = metadata[idx].get("url_category", metadata[idx].get("category", "Documentation"))
            else:
                doc["category"] = metadata[idx].get("category", "Documentation")
            vector_results.append(doc)

    # Recherche mots-clés
    keyword_results = search_documents_keywords(query, chunks, metadata, top_k=max(top_k, 10))

    # Combinaison des résultats
    combined = combine_results(vector_results, keyword_results)
    return combined[:top_k]

def search_documents_keywords(query: str, chunks: list, metadata: list, top_k: int = 10):
    """Recherche par mots-clés (> 3 caractères) dans titres et contenus.

    - Score 1.0 si correspondance dans le titre
    - Score 0.8 si correspondance dans le contenu
    Retourne une liste de dicts similaires à la recherche vectorielle.
    """
    tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 3]
    if not tokens:
        return []

    results = []
    for idx, meta in enumerate(metadata):
        title = meta.get("title", "")
        content = chunks[idx] if idx < len(chunks) else ""
        title_l = title.lower()
        content_l = content.lower() if isinstance(content, str) else ""

        match_in_title = any(tok in title_l for tok in tokens)
        match_in_content = any(tok in content_l for tok in tokens)

        if not (match_in_title or match_in_content):
            continue

        score = 0.0
        if match_in_title:
            score = max(score, 1.0)
        if match_in_content:
            score = max(score, 0.8)

        doc = {
            "title": title,
            "extract": content,
            "score": float(score)
        }
        if "url" in meta:
            doc["url"] = meta["url"]
            doc["category"] = meta.get("url_category", meta.get("category", "Documentation"))
        else:
            doc["category"] = meta.get("category", "Documentation")
        results.append(doc)

    results.sort(key=lambda d: d.get("score", 0.0), reverse=True)
    return results[:top_k]

def combine_results(vector_res: list, keyword_res: list):
    """Fusionne vectoriel et mots-clés, déduplique et applique un bonus.

    new_score = 0.6 * keyword_score + 0.4 * vector_score quand présent dans les deux.
    """
    def make_key(doc: dict):
        return doc.get("url") or doc.get("title")

    vec_map = {make_key(d): d for d in vector_res}
    key_map = {make_key(d): d for d in keyword_res}

    all_keys = set(vec_map.keys()) | set(key_map.keys())
    combined = []

    for k in all_keys:
        v = vec_map.get(k)
        w = key_map.get(k)
        if v and w:
            combined_score = 0.6 * float(w.get("score", 0.0)) + 0.4 * float(v.get("score", 0.0))
            merged = dict(v)
            merged["title"] = v.get("title", w.get("title"))
            merged["extract"] = v.get("extract") or w.get("extract")
            if "url" not in merged and w.get("url"):
                merged["url"] = w.get("url")
            if "category" not in merged and w.get("category"):
                merged["category"] = w.get("category")
            merged["score"] = float(combined_score)
            combined.append(merged)
        elif v:
            combined.append(v)
        elif w:
            combined.append(w)

    combined.sort(key=lambda d: d.get("score", 0.0), reverse=True)
    return combined

def generate_response(query, documents):
    """Génère une réponse structurée."""
    # Préparer le contexte
    context = "\n\n".join([
        f"Document: {doc['title']}\n" +
        (f"URL: {doc['url']}\n" if 'url' in doc else "") +
        f"Catégorie: {doc['category']}\n" +
        f"Extrait: {doc['extract']}"
        for doc in documents
    ])
    
    logger.debug("Contexte envoyé à Azure OpenAI:\n%s", context)
    
    # Configurer le client Azure OpenAI
    client = ChatCompletionsClient(
        endpoint=os.environ["AZURE_INFERENCE_SDK_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["AZURE_OPENAI_API_KEY"])
    )
    
    # Préparer les messages
    messages = [
        SystemMessage(
            content=(
                "Tu es un assistant documentaire AFPA. Utilise UNIQUEMENT les informations des documents fournis pour répondre. "
                "Ta tâche principale est de présenter les documents en relation avec la question de l'utilisateur, pas de répondre directement à la question. "
                "**Structure IMPÉRATIVEMENT ta réponse en HTML.** "
                "La réponse doit commencer par une introduction générale, par exemple : '<p>Voici les documents en relation avec votre question :</p>'. "
                "Ensuite, pour chaque document pertinent trouvé, présente-le comme suit, en utilisant une liste non ordonnée `<ul>` et des éléments de liste `<li>` pour chaque document : "
                "  '<li>' "
                "    '<strong>Titre du document</strong><br />' "
                "    '<em>Description :</em> Description concise et pertinente basée sur l'extrait fourni et la question de l'utilisateur.<br />' "
                "    '<em>Source :</em> <a href=\"URL_DU_DOCUMENT\" target=\"_blank\">Nom de la source (titre du document)</a>' " # Guillemets échappés ici
                "  '</li>' "
                "N'oublie pas de remplacer 'Titre du document', 'Description...', 'URL_DU_DOCUMENT', et 'Nom de la source' par les vraies valeurs. L'URL doit être cliquable et s'ouvrir dans un nouvel onglet. "
                "Assure-toi que le HTML est bien formé. "
                "Termine par une brève conclusion si nécessaire, par exemple : "
                "'<p>Si le document exact que vous cherchez n\\'est pas listé, il est possible qu\\'il ne soit pas disponible dans la base de données ou que votre question nécessite une reformulation.</p>'" # Apostrophes échappées
            )
        ),
        UserMessage(
            content=f"Question: {query}\n\nDocuments disponibles:\n{context}"
        )
    ]
    
    logger.debug("Message système: %s", messages[0].content)
    logger.info("Question envoyée: %s", query)
    
    # Générer la réponse
    response = client.complete(
        messages=messages,
        model=os.environ["DEPLOYMENT_NAME"],
        temperature=0.3,
        max_tokens=1500
    )
    
    logger.debug("Réponse reçue d'Azure OpenAI: %s", response.choices[0].message.content)
    return response.choices[0].message.content

@app.route('/')
@login_required
def home():
    # Récupérer les informations de l'utilisateur connecté
    username = session.get('username')
    user = get_user(username)
    user_name = user.get('name', username) if user else username
    is_admin = user and user.get('role') == 'admin'
    
    return render_template('index.html', user_name=user_name, is_admin=is_admin)

@app.route('/search', methods=['POST'])
@login_required
def search_endpoint():
    try:
        logger.info("Début du traitement de la requête")
        # Récupérer la requête
        query = request.json.get('query', '')
        logger.info("Requête reçue: %s", query)
        
        if not query:
            logger.warning("Erreur: requête vide")
            return jsonify({"error": "Query is required"}), 400
        
        # Rechercher les documents pertinents (avec URLs déjà incluses)
        logger.info("Recherche des documents...")
        documents = search_documents(query, index, chunks, metadata)
        logger.info("Documents trouvés: %d", len(documents))
        for doc in documents:
            logger.debug("- %s (score: %s)", doc['title'], doc['score'])
            if 'url' in doc:
                logger.debug("  URL: %s", doc['url'])
        
        # Générer la réponse
        logger.info("Génération de la réponse...")
        response = generate_response(query, documents)
        logger.info("Réponse générée")
        logger.debug("Longueur de la réponse: %d", len(response))
        
        result = {
            "response": {
                "content": response,
                "sources": documents
            }
        }
        logger.info("Envoi de la réponse au client")
        return jsonify(result)
        
    except Exception as e:
        logger.exception("Une erreur est survenue")
        return jsonify({"error": "Une erreur est survenue"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_credentials(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Identifiant ou mot de passe incorrect"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Chargement initial des données
logger.info("Chargement du système unifié...")
index, chunks, metadata = load_unified_system()
logger.info("Système unifié chargé")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860, debug=False) 