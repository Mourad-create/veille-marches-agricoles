"""
Point d'entrée du chargement PostgreSQL (Phase 4).

Usage :
    python -m nsengo_charge.run_chargement \\
        --parquet ../03_Preparation_donnees/data/processed/fact_marches_agricoles.parquet \\
        --creer-base --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from . import charger, config, db, transformation_dimensions as dims

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    niveau = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=niveau, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chargement PostgreSQL - NSENGO Veille des Marchés Agricoles")
    parser.add_argument(
        "--parquet",
        default="../03_Preparation_donnees/data/processed/fact_marches_agricoles.parquet",
        help="Chemin du fichier Parquet produit par la Phase 3.",
    )
    parser.add_argument(
        "--schema",
        default="sql/schema.sql",
        help="Chemin du fichier SQL de définition du schéma.",
    )
    parser.add_argument(
        "--creer-base",
        action="store_true",
        help="Crée la base de données si elle n'existe pas encore (sinon, elle doit déjà exister).",
    )
    parser.add_argument("--verbose", action="store_true", help="Active les logs de niveau DEBUG.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    configure_logging(args.verbose)

    chemin_parquet = Path(args.parquet)
    if not chemin_parquet.exists():
        # Repli CSV : cohérent avec le comportement de la Phase 3 si Parquet
        # était indisponible sur la machine (contrainte d'environnement).
        chemin_csv = chemin_parquet.with_suffix(".csv")
        if chemin_csv.exists():
            logger.warning("Fichier Parquet introuvable, utilisation du CSV de repli : %s", chemin_csv)
            table_faits_brute = pd.read_csv(chemin_csv)
        else:
            logger.error("Fichier introuvable : %s (ni .parquet ni .csv)", chemin_parquet)
            return 1
    else:
        table_faits_brute = pd.read_parquet(chemin_parquet)

    if args.creer_base:
        db.creer_base_si_absente()

    db.executer_schema(args.schema)

    engine = create_engine(config.url_connexion())

    dim_pays = dims.construire_dim_pays(table_faits_brute)
    dim_variable = dims.construire_dim_variable(table_faits_brute)

    charger.vider_tables(engine)
    charger.charger_dim_pays(engine, dim_pays)
    charger.charger_dim_variable(engine, dim_variable)

    mapping = charger.lire_mapping_variables(engine)
    table_faits = dims.construire_table_faits(table_faits_brute, mapping)
    charger.charger_faits(engine, table_faits)

    print("\n=== Résumé du chargement ===")
    print(f"  - dim_pays : {len(dim_pays)} ligne(s)")
    print(f"  - dim_variable : {len(dim_variable)} ligne(s)")
    print(f"  - fait_marches_agricoles : {len(table_faits)} ligne(s)")
    print(f"  - Base : {config.DB_NAME} ({config.DB_HOST}:{config.DB_PORT})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
