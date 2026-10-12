"""
Point d'entrée du pipeline de préparation (Modules Nettoyage + Transformation).

Usage :
    python -m nsengo_prepare.run_preparation --raw-root ../02_Collecte_donnees/nsengo_collecte/data/raw

Lit le dernier run de chaque source dans data/raw/, applique le nettoyage
(Script 2) puis la transformation/filtrage métier (Script 3), et écrit une
unique table de faits au format Parquet dans data/processed/.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from . import config, lecteurs, nettoyage, transformation

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    niveau = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=niveau, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline de préparation des données (nettoyage + transformation) - NSENGO"
    )
    parser.add_argument(
        "--raw-root",
        default="../02_Collecte_donnees/nsengo_collecte/data/raw",
        help="Dossier racine des données brutes produites par la Phase 2 (data/raw).",
    )
    parser.add_argument(
        "--output",
        default="data/processed/fact_marches_agricoles.parquet",
        help="Chemin du fichier Parquet de sortie.",
    )
    parser.add_argument("--verbose", action="store_true", help="Active les logs de niveau DEBUG.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    configure_logging(args.verbose)

    raw_root = Path(args.raw_root)
    tables_harmonisees = []

    # --- World Bank ---
    try:
        run_dir = lecteurs.trouver_dernier_run(raw_root, "world_bank")
        df_brut = lecteurs.lire_world_bank(run_dir)
        df_propre = nettoyage.nettoyer_world_bank(df_brut)
        tables_harmonisees.append(transformation.harmoniser_world_bank(df_propre))
    except FileNotFoundError as exc:
        logger.warning("World Bank ignoré : %s", exc)

    # --- FAOSTAT (un domaine à la fois) ---
    try:
        run_dir = lecteurs.trouver_dernier_run(raw_root, "faostat")
    except FileNotFoundError as exc:
        logger.warning("FAOSTAT ignoré : %s", exc)
        run_dir = None

    if run_dir is not None:
        for code_domaine, infos in config.DOMAINES_FAOSTAT.items():
            chemin_zip = run_dir / infos["fichier"]
            if not chemin_zip.exists():
                logger.warning("Domaine FAOSTAT %s non trouvé dans %s, ignoré.", code_domaine, run_dir)
                continue
            df_brut = lecteurs.lire_faostat(run_dir, infos["fichier"])
            df_propre = nettoyage.nettoyer_faostat(df_brut)
            tables_harmonisees.append(
                transformation.harmoniser_faostat(df_propre, infos["source_label"], infos["elements"])
            )

    table_finale = transformation.fusionner(*tables_harmonisees)

    if table_finale.empty:
        logger.error("Aucune donnée à écrire (table finale vide) — vérifie que la Phase 2 a bien été exécutée.")
        return 1

    chemin_sortie = Path(args.output)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    format_utilise = "parquet"
    try:
        table_finale.to_parquet(chemin_sortie, index=False)
    except ImportError as exc:
        # Contrainte d'environnement connue : certains postes (politiques de
        # sécurité type "contrôle d'application") bloquent le chargement des
        # librairies natives pyarrow/fastparquet. On bascule sur CSV plutôt
        # que de faire planter tout le pipeline.
        logger.warning(
            "Écriture Parquet impossible (%s). Bascule automatique sur CSV. "
            "Pour retrouver le Parquet, essaie 'pip install fastparquet' ou "
            "contacte ton administrateur système au sujet du blocage DLL.",
            exc,
        )
        chemin_sortie = chemin_sortie.with_suffix(".csv")
        table_finale.to_csv(chemin_sortie, index=False)
        format_utilise = "csv (repli automatique, Parquet indisponible)"

    print("\n=== Résumé de la préparation ===")
    print(f"  - {len(table_finale)} ligne(s) au total")
    for source, effectif in table_finale["source"].value_counts().items():
        print(f"  - {source} : {effectif} ligne(s)")
    print(f"  - Format : {format_utilise}")
    print(f"  - Fichier écrit : {chemin_sortie.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
