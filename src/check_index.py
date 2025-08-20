import json
import faiss
import numpy as np

# Charger l'index FAISS
print("Chargement de l'index FAISS...")
index = faiss.read_index('models/faiss_index.bin')
print(f"Index FAISS chargé avec succès!")
print(f"Nombre de vecteurs: {index.ntotal}")
print(f"Dimension des vecteurs: {index.d}")

# Charger et vérifier les chunks
print("\nChargement des chunks...")
with open('models/chunks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

chunks = data.get('chunks', [])
print(f"Nombre de chunks chargés: {len(chunks)}")

# Afficher les 3 premiers chunks pour vérification
print("\nAperçu des 3 premiers chunks:")
for i, chunk in enumerate(chunks[:3]):
    print(f"\nChunk {i+1}:")
    if isinstance(chunk, dict):
        # Si le chunk est un dictionnaire avec métadonnées
        print(f"Texte: {chunk.get('text', '')[:200]}...")
        print(f"Source: {chunk.get('source', 'Non spécifiée')}")
    else:
        # Si le chunk est une simple chaîne de texte
        print(f"Texte: {str(chunk)[:200]}...") 