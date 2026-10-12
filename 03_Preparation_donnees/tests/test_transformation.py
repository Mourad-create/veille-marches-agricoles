from pathlib import Path

import pandas as pd

from nsengo_prepare import config, lecteurs, nettoyage, transformation

FIXTURES = Path(__file__).parent / "fixtures"


def test_harmoniser_world_bank_filtre_les_pays_hors_perimetre():
    df_brut = lecteurs.lire_world_bank(FIXTURES / "world_bank_run")
    df_propre = nettoyage.nettoyer_world_bank(df_brut)
    resultat = transformation.harmoniser_world_bank(df_propre)

    # Le pays "ZZZ" de la fixture est hors périmètre (config.PAYS_INTERET)
    assert "ZZZ" not in resultat["code_pays_iso3"].values
    assert list(resultat.columns) == transformation.COLONNES_FACT
    assert (resultat["source"] == "world_bank").all()


def test_harmoniser_faostat_filtre_pays_produits_et_elements():
    df_brut = pd.read_csv(FIXTURES / "faostat_sample.csv")
    df_propre = nettoyage.nettoyer_faostat(df_brut)
    resultat = transformation.harmoniser_faostat(
        df_propre, source_label="faostat_production", elements_autorises=config.ELEMENTS_PRODUCTION
    )

    # Burkina Faso hors périmètre, Bananas hors produits prioritaires
    assert not (resultat["pays"] == "Burkina Faso").any()
    assert not resultat["variable"].str.contains("Bananas").any()

    # Maize/Production et Maize/Area harvested pour le Bénin doivent être présents
    variables = set(resultat["variable"])
    assert "Maize (corn) - Production" in variables
    assert "Maize (corn) - Area harvested" in variables

    assert resultat.loc[resultat["pays"] == "Benin", "code_pays_iso3"].eq("BEN").all()


def test_fusionner_concatene_et_ignore_les_tables_vides():
    table_a = pd.DataFrame([{"source": "world_bank", "pays": "Benin", "code_pays_iso3": "BEN",
                              "annee": 2023, "variable": "PIB", "valeur": 100.0, "unite": None}])
    table_vide = pd.DataFrame(columns=transformation.COLONNES_FACT)

    resultat = transformation.fusionner(table_a, table_vide)

    assert len(resultat) == 1
    assert list(resultat.columns) == transformation.COLONNES_FACT
