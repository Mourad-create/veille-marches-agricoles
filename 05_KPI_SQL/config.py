"""Configuration de connexion PostgreSQL (identique à 04_Base_PostgreSQL/config.py)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

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
