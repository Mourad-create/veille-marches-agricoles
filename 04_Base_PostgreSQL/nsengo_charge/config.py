"""
Configuration de connexion PostgreSQL.

Les identifiants ne sont JAMAIS écrits en dur dans le code : ils sont lus
depuis des variables d'environnement (via un fichier .env local, qui ne doit
jamais être commité/partagé). Un fichier .env.example fournit un modèle.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env s'il existe, ne fait rien sinon

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nsengo_veille")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if DB_PASSWORD is None:
    raise RuntimeError(
        "Variable d'environnement DB_PASSWORD manquante. "
        "Copie .env.example vers .env et renseigne ton mot de passe PostgreSQL."
    )


def url_connexion(nom_base: str | None = None) -> str:
    """URL SQLAlchemy vers la base cible (ou DB_NAME par défaut).

    sslmode=require : ce projet se connecte à un serveur PostgreSQL distant
    (pas localhost) sur lequel le SSL est activé.
    """
    base = nom_base or DB_NAME
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{base}?sslmode=require"
