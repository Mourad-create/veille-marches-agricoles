"""
Script 2 - Nettoyage.

Nettoyage générique, sans aucun filtrage métier (pas de notion de pays ou de
produit prioritaire ici : c'est le rôle de transformation.py). On se contente
de :
  - retirer les colonnes inutiles ;
  - retirer les doublons ;
  - retirer les lignes sans valeur exploitable ;
  - normaliser les types (année en entier, valeur en nombre).
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config

logger = logging.getLogger(__name__)


def nettoyer_world_bank(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    avant = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=["valeur", "annee", "code_pays_iso3"])

    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
    df = df.dropna(subset=["annee", "valeur"])

    apres = len(df)
    logger.info("[world_bank] Nettoyage : %d -> %d lignes (%d retirées)", avant, apres, avant - apres)
    return df.reset_index(drop=True)


def nettoyer_faostat(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    avant = len(df)

    colonnes_presentes = [c for c in config.COLONNES_FAOSTAT_UTILES if c in df.columns]
    manquantes = set(config.COLONNES_FAOSTAT_UTILES) - set(colonnes_presentes)
    if manquantes:
        logger.warning("Colonnes attendues absentes du fichier FAOSTAT : %s", sorted(manquantes))
    df = df[colonnes_presentes].copy()

    df = df.drop_duplicates()
    df = df.dropna(subset=["Value"])

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df = df.dropna(subset=["Year", "Value"])

    apres = len(df)
    logger.info("[faostat] Nettoyage : %d -> %d lignes (%d retirées)", avant, apres, avant - apres)
    return df.reset_index(drop=True)
