"""
Lecture des données brutes produites par le pipeline de collecte (Phase 2).

Ce module sait uniquement *lire* les fichiers tels qu'archivés par
02_Collecte_donnees (structure : data/raw/<source>/<horodatage>/<fichier>),
et les charger en DataFrame pandas. Il ne fait aucun nettoyage ni filtrage :
c'est le rôle de nettoyage.py et transformation.py.
"""

from __future__ import annotations

import json
import re
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd

NOM_DOSSIER_HORODATE = re.compile(r"^\d{8}_\d{6}$")


def trouver_dernier_run(raw_root: str | Path, source_name: str) -> Path:
    """Retourne le dossier horodaté le plus récent pour une source donnée."""
    source_dir = Path(raw_root) / source_name
    if not source_dir.exists():
        raise FileNotFoundError(
            f"Aucune donnée brute trouvée pour la source '{source_name}' dans {source_dir}. "
            "As-tu bien exécuté la collecte (Phase 2) au préalable ?"
        )

    dossiers_runs = [p for p in source_dir.iterdir() if p.is_dir() and NOM_DOSSIER_HORODATE.match(p.name)]
    if not dossiers_runs:
        raise FileNotFoundError(f"Aucun run horodaté trouvé dans {source_dir}.")

    return sorted(dossiers_runs)[-1]


def lire_world_bank(run_dir: Path) -> pd.DataFrame:
    """
    Aplatit les fichiers JSON World Bank (un par indicateur) d'un run en une
    seule table : pays, code_pays_iso3, indicateur, annee, valeur, unite.
    """
    lignes = []
    for fichier in sorted(run_dir.glob("world_bank_*.json")):
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        if not isinstance(donnees, list) or len(donnees) < 2 or donnees[1] is None:
            continue

        for obs in donnees[1]:
            lignes.append(
                {
                    "pays": obs.get("country", {}).get("value"),
                    "code_pays_iso3": obs.get("countryiso3code"),
                    "indicateur_code": obs.get("indicator", {}).get("id"),
                    "indicateur": obs.get("indicator", {}).get("value"),
                    "annee": obs.get("date"),
                    "valeur": obs.get("value"),
                    "unite": obs.get("unit") or None,
                }
            )

    return pd.DataFrame(lignes)


def lire_faostat(run_dir: Path, domaine_filename: str) -> pd.DataFrame:
    """
    Lit le CSV normalisé contenu dans l'archive ZIP FAOSTAT d'un run.

    domaine_filename : nom du fichier ZIP tel qu'archivé (ex :
    "Production_Crops_Livestock_E_All_Data_(Normalized).zip"), tel que défini
    dans nsengo_veille.config.FAOSTAT_DOMAINS.
    """
    chemin_zip = run_dir / domaine_filename
    if not chemin_zip.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin_zip}")

    with zipfile.ZipFile(chemin_zip) as archive:
        noms_csv = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if not noms_csv:
            raise ValueError(f"Aucun fichier CSV trouvé dans l'archive {chemin_zip}")

        with archive.open(noms_csv[0]) as fh:
            contenu = fh.read()

    for encodage in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(BytesIO(contenu), encoding=encodage, low_memory=False)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("csv", b"", 0, 1, "Encodage non reconnu (essayé utf-8 et latin-1)")
