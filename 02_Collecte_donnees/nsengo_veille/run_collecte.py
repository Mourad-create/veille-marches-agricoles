"""
Point d'entrée du pipeline d'acquisition (Module 1).

Usage :
    python -m nsengo_veille.run_collecte --sources all
    python -m nsengo_veille.run_collecte --sources world_bank
    python -m nsengo_veille.run_collecte --sources world_bank faostat --output data/raw --verbose

Ce script est conçu pour être exécuté manuellement pendant le développement,
puis planifié (tâche planifiée / cron) une fois validé, conformément au
cahier des charges (mise à jour périodique des données).
"""

from __future__ import annotations

import argparse
import json
import sys

from .collectors import REGISTRE_COLLECTEURS
from .logging_config import configure_logging


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline de collecte automatique des données ouvertes - NSENGO"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=list(REGISTRE_COLLECTEURS) + ["all"],
        default=["all"],
        help="Sources à collecter (par défaut : toutes les sources implémentées).",
    )
    parser.add_argument("--output", default="data/raw", help="Dossier racine de stockage des données brutes.")
    parser.add_argument("--verbose", action="store_true", help="Active les logs de niveau DEBUG.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    configure_logging(args.verbose)

    noms_sources = list(REGISTRE_COLLECTEURS) if "all" in args.sources else args.sources

    resumes = []
    for nom in noms_sources:
        collecteur_cls = REGISTRE_COLLECTEURS[nom]
        collecteur = collecteur_cls(output_root=args.output)
        resumes.append(collecteur.run())

    print("\n=== Résumé de la collecte ===")
    for resume in resumes:
        if "erreur" in resume:
            print(f"  - {resume['source']} : ÉCHEC ({resume['erreur']})")
        else:
            print(
                f"  - {resume['source']} : {resume['nb_fichiers']} fichier(s) "
                f"({resume['nb_nouveaux']} nouveau(x), {resume['nb_mis_a_jour']} mis à jour, "
                f"{resume['nb_inchanges']} inchangé(s))"
            )

    echecs = [r for r in resumes if "erreur" in r]
    if echecs:
        print(f"\n{len(echecs)} source(s) en échec — voir data/logs/pipeline_collecte.log pour le détail.")

    resume_json_path = f"{args.output}/../logs/dernier_resume.json"
    try:
        with open(resume_json_path, "w", encoding="utf-8") as fh:
            json.dump(resumes, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass

    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
