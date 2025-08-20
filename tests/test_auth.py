import pytest
import os
import json
from src.auth import verify_credentials, hash_password


@pytest.fixture
def temp_users_file(tmp_path, monkeypatch):
    # Créer un dossier data temporaire et un fichier users.json
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    temp_user_file = data_dir / "users.json"

    # Écrire un utilisateur de test avec mot de passe haché
    users = {
        "testuser": {
            "password": hash_password("password123"),
            "role": "user",
            "name": "Test User",
        }
    }
    temp_user_file.write_text(json.dumps(users), encoding="utf-8")

    # Rediriger USERS_FILE du module src.auth vers ce fichier temporaire
    monkeypatch.setattr('src.auth.USERS_FILE', str(temp_user_file))

    return str(temp_user_file)


def test_verify_credentials_success(temp_users_file):
    assert verify_credentials('testuser', 'password123') is True


def test_verify_credentials_failure_wrong_password(temp_users_file):
    assert verify_credentials('testuser', 'wrongpassword') is False


def test_verify_credentials_failure_no_user(temp_users_file):
    assert verify_credentials('nouser', 'password123') is False


