"""
Construction des dimensions à partir de la table de faits produite en Phase 3.

Logique volontairement indépendante de toute connexion à une base de données,
pour rester testable simplement avec pandas.
"""

from __future__ import annotations

import pandas as pd


def construire_dim_pays(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par pays distinct (code_pays_iso3, pays)."""
    return (
        df[["code_pays_iso3", "pays"]]
        .drop_duplicates(subset=["code_pays_iso3"])
        .sort_values("code_pays_iso3")
        .reset_index(drop=True)
    )


def construire_dim_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par variable distincte (variable, unite), sans identifiant.

    L'identifiant (id_variable) est laissé à la charge de PostgreSQL (colonne
    SERIAL) : on le récupère après insertion via lire_mapping_variables().
    """
    return (
        df[["variable", "unite"]]
        .drop_duplicates(subset=["variable"])
        .sort_values("variable")
        .reset_index(drop=True)
    )


def construire_table_faits(df: pd.DataFrame, mapping_variable_vers_id: dict[str, int]) -> pd.DataFrame:
    """Remplace la colonne texte 'variable' par la clé étrangère 'id_variable'."""
    resultat = df.copy()
    resultat["id_variable"] = resultat["variable"].map(mapping_variable_vers_id)

    non_mappees = resultat["id_variable"].isna().sum()
    if non_mappees:
        raise ValueError(
            f"{non_mappees} ligne(s) référencent une variable absente du mapping "
            "(incohérence entre dim_variable et la table de faits)."
        )

    resultat["id_variable"] = resultat["id_variable"].astype(int)
    return resultat[["source", "code_pays_iso3", "annee", "id_variable", "valeur"]]
