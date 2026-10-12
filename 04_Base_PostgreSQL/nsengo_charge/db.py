"""
Fonctions bas niveau : création de la base si absente, exécution du schéma.

CREATE DATABASE ne peut pas s'exécuter dans une transaction PostgreSQL : on
utilise donc une connexion psycopg2 brute en autocommit, connectée à la base
technique "postgres" (toujours présente), plutôt que SQLAlchemy.
"""

from __future__ import annotations

import logging
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from . import config

logger = logging.getLogger(__name__)


def creer_base_si_absente() -> bool:
    """Crée la base config.DB_NAME si elle n'existe pas déjà.

    Retourne True si elle a été créée, False si elle existait déjà.
    """
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dbname="postgres",
        sslmode="require",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config.DB_NAME,))
            if cur.fetchone() is not None:
                logger.info("La base '%s' existe déjà.", config.DB_NAME)
                return False

            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(config.DB_NAME)))
            logger.info("Base '%s' créée.", config.DB_NAME)
            return True
    finally:
        conn.close()


def executer_schema(chemin_schema: str | Path) -> None:
    """Exécute le fichier schema.sql sur la base cible (config.DB_NAME)."""
    texte_sql = Path(chemin_schema).read_text(encoding="utf-8")

    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        dbname=config.DB_NAME,
        sslmode="require",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(texte_sql)
        conn.commit()
        logger.info("Schéma exécuté avec succès sur '%s'.", config.DB_NAME)
    finally:
        conn.close()
