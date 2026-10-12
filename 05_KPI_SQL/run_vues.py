"""
Exécute le fichier sql/vues_kpi.sql sur la base nsengo_veille (Phase 5).

Usage :
    python run_vues.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import psycopg2

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    chemin_sql = Path(__file__).parent / "sql" / "vues_kpi.sql"
    texte_sql = chemin_sql.read_text(encoding="utf-8")

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
        logger.info("Vues KPI créées/mises à jour avec succès sur '%s'.", config.DB_NAME)
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
