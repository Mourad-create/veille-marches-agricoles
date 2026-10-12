from pathlib import Path

import pandas as pd

from nsengo_prepare import lecteurs, nettoyage

FIXTURES = Path(__file__).parent / "fixtures"


def test_nettoyer_world_bank_retire_les_valeurs_nulles():
    df_brut = lecteurs.lire_world_bank(FIXTURES / "world_bank_run")
    df_propre = nettoyage.nettoyer_world_bank(df_brut)

    # La ligne Bénin/2022 a une valeur null dans la fixture -> doit disparaître
    assert len(df_propre) == 2
    assert df_propre["valeur"].isna().sum() == 0
    assert df_propre["annee"].dtype.name == "Int64"


def test_nettoyer_world_bank_gere_un_dataframe_vide():
    resultat = nettoyage.nettoyer_world_bank(pd.DataFrame())
    assert resultat.empty


def test_nettoyer_faostat_retire_colonnes_inutiles_doublons_et_valeurs_nulles():
    df_brut = pd.read_csv(FIXTURES / "faostat_sample.csv")
    df_propre = nettoyage.nettoyer_faostat(df_brut)

    # Colonnes de codes techniques absentes du résultat
    assert "Area Code" not in df_propre.columns
    assert "Item Code" not in df_propre.columns

    # La ligne Bénin/Maize/2022 a une valeur vide dans la fixture -> retirée
    assert df_propre["Value"].isna().sum() == 0
    assert len(df_propre) == 6
