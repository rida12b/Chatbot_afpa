import os
import json
import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, request

# Chemin vers le fichier des utilisateurs
USERS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')

# Fonction pour créer le répertoire data s'il n'existe pas
def ensure_data_dir():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

# Fonction pour charger les utilisateurs depuis le fichier JSON
def load_users():
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        # Créer un fichier utilisateur par défaut avec un admin
        default_admin = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "name": "Administrateur"
            }
        }
        save_users(default_admin)
        return default_admin
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # En cas d'erreur, retourner un dictionnaire vide
        return {}

# Fonction pour sauvegarder les utilisateurs dans le fichier JSON
def save_users(users):
    ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# Fonction pour hacher un mot de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fonction pour vérifier les identifiants d'un utilisateur
def verify_credentials(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

# Fonction pour ajouter un nouvel utilisateur
def add_user(username, password, role="user", name=""):
    users = load_users()
    if username in users:
        return False, "Cet identifiant existe déjà"
    
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "name": name
    }
    
    save_users(users)
    return True, "Utilisateur ajouté avec succès"

# Fonction pour supprimer un utilisateur
def delete_user(username):
    users = load_users()
    if username not in users:
        return False, "Utilisateur introuvable"
    
    del users[username]
    save_users(users)
    return True, "Utilisateur supprimé avec succès"

# Fonction pour modifier un utilisateur
def update_user(username, new_password=None, role=None, name=None):
    users = load_users()
    if username not in users:
        return False, "Utilisateur introuvable"
    
    if new_password:
        users[username]["password"] = hash_password(new_password)
    
    if role:
        users[username]["role"] = role
    
    if name:
        users[username]["name"] = name
    
    save_users(users)
    return True, "Utilisateur mis à jour avec succès"

# Fonction pour obtenir les informations d'un utilisateur
def get_user(username):
    users = load_users()
    return users.get(username, None)

# Fonction pour obtenir la liste de tous les utilisateurs
def get_all_users():
    users = load_users()
    # Retourner une copie sans les mots de passe
    sanitized_users = {}
    for username, user_data in users.items():
        sanitized_users[username] = {
            "role": user_data["role"],
            "name": user_data["name"]
        }
    return sanitized_users

# Décorateur pour protéger les routes qui nécessitent une authentification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Décorateur pour restreindre l'accès aux administrateurs
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        
        username = session['username']
        user = get_user(username)
        if not user or user['role'] != 'admin':
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

# Fonction pour générer une clé secrète pour Flask
def generate_secret_key():
    return secrets.token_hex(16) 