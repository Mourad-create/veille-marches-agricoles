"""
Chargement des données dans PostgreSQL.

Stratégie : on vide les tables avant chaque chargement (TRUNCATE ... CASCADE)
plutôt que de faire un upsert ligne à ligne. C'est volontairement simple et
adapté à un pipeline batch qui recharge l'intégralité de l'historique à
chaque exécution (cohérent avec la Phase 2/3 qui archivent tout mais ne
fusionnent pas incrémentalement). Documenté comme choix assumé dans le README.
"""

from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def vider_tables(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fait_marches_agricoles, dim_pays, dim_variable RESTART IDENTITY CASCADE"))
    logger.info("Tables vidées (rechargement complet).")


def charger_dim_pays(engine: Engine, dim_pays: pd.DataFrame) -> None:
    dim_pays.to_sql("dim_pays", engine, if_exists="append", index=False)
    logger.info("dim_pays : %d ligne(s) chargée(s).", len(dim_pays))


def charger_dim_variable(engine: Engine, dim_variable: pd.DataFrame) -> None:
    dim_variable.to_sql("dim_variable", engine, if_exists="append", index=False)
    logger.info("dim_variable : %d ligne(s) chargée(s).", len(dim_variable))


def lire_mapping_variables(engine: Engine) -> dict[str, int]:
    """Relit dim_variable pour récupérer les id_variable générés par PostgreSQL (SERIAL)."""
    df = pd.read_sql("SELECT id_variable, variable FROM dim_variable", engine)
    return dict(zip(df["variable"], df["id_variable"]))


def charger_faits(engine: Engine, table_faits: pd.DataFrame, taille_lot: int = 5000) -> None:
    table_faits.to_sql("fait_marches_agricoles", engine, if_exists="append", index=False, chunksize=taille_lot)
    logger.info("fait_marches_agricoles : %d ligne(s) chargée(s).", len(table_faits))
