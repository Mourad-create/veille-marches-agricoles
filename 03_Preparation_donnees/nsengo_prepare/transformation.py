"""
Script 3 - Transformation.

Filtre les données nettoyées sur le périmètre métier retenu (pays d'intérêt,
produits prioritaires) et les harmonise vers un schéma commun unique — une
table de faits simple, indépendante de la source d'origine, prête à être
chargée en base (Phase 4) :

    source | pays | code_pays_iso3 | annee | variable | valeur | unite

"variable" porte le nom de l'indicateur (World Bank) ou la combinaison
"Produit - Élément" (FAOSTAT), par exemple "Maize (corn) - Production".
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config

logger = logging.getLogger(__name__)

COLONNES_FACT = ["source", "pays", "code_pays_iso3", "annee", "variable", "valeur", "unite"]


def harmoniser_world_bank(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=COLONNES_FACT)

    codes_valides = set(config.PAYS_INTERET.values())
    df = df[df["code_pays_iso3"].isin(codes_valides)].copy()

    df["source"] = "world_bank"
    df["variable"] = df["indicateur"]

    resultat = df[["source", "pays", "code_pays_iso3", "annee", "variable", "valeur", "unite"]]
    logger.info("[world_bank] %d ligne(s) retenue(s) après filtrage pays.", len(resultat))
    return resultat.reset_index(drop=True)


def harmoniser_faostat(df: pd.DataFrame, source_label: str, elements_autorises: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=COLONNES_FACT)

    df = df[df["Area"].isin(config.PAYS_INTERET.keys())]
    df = df[df["Item"].isin(config.PRODUITS_PRIORITAIRES)]
    df = df[df["Element"].isin(elements_autorises)].copy()

    df["source"] = source_label
    df["code_pays_iso3"] = df["Area"].map(config.PAYS_INTERET)
    df["variable"] = df["Item"] + " - " + df["Element"]

    resultat = df.rename(columns={"Area": "pays", "Year": "annee", "Value": "valeur", "Unit": "unite"})
    resultat = resultat[COLONNES_FACT]
    logger.info("[%s] %d ligne(s) retenue(s) après filtrage pays/produits.", source_label, len(resultat))
    return resultat.reset_index(drop=True)


def fusionner(*tables: pd.DataFrame) -> pd.DataFrame:
    """Concatène plusieurs tables de faits harmonisées en une seule."""
    tables_non_vides = [t for t in tables if not t.empty]
    if not tables_non_vides:
        return pd.DataFrame(columns=COLONNES_FACT)
    return pd.concat(tables_non_vides, ignore_index=True)[COLONNES_FACT]
