import pandas as pd
import pytest

from nsengo_charge import transformation_dimensions as dims


def _table_faits_exemple() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"source": "world_bank", "pays": "Benin", "code_pays_iso3": "BEN", "annee": 2023,
             "variable": "PIB (US$ courants)", "valeur": 19_640_000_000.0, "unite": None},
            {"source": "world_bank", "pays": "Benin", "code_pays_iso3": "BEN", "annee": 2022,
             "variable": "PIB (US$ courants)", "valeur": 18_000_000_000.0, "unite": None},
            {"source": "faostat_production", "pays": "Benin", "code_pays_iso3": "BEN", "annee": 2023,
             "variable": "Maize (corn) - Production", "valeur": 1_500_000.0, "unite": "t"},
            {"source": "faostat_production", "pays": "Nigeria", "code_pays_iso3": "NGA", "annee": 2023,
             "variable": "Maize (corn) - Production", "valeur": 12_000_000.0, "unite": "t"},
        ]
    )


def test_construire_dim_pays_une_ligne_par_pays():
    df = _table_faits_exemple()
    dim_pays = dims.construire_dim_pays(df)

    assert len(dim_pays) == 2  # Benin, Nigeria (le doublon Benin/2022+2023 est fusionné)
    assert set(dim_pays["code_pays_iso3"]) == {"BEN", "NGA"}
    assert list(dim_pays.columns) == ["code_pays_iso3", "pays"]


def test_construire_dim_variable_une_ligne_par_variable():
    df = _table_faits_exemple()
    dim_variable = dims.construire_dim_variable(df)

    # 2 variables distinctes : PIB, Maize Production (répétée 2 fois dans les faits)
    assert len(dim_variable) == 2
    assert set(dim_variable["variable"]) == {"PIB (US$ courants)", "Maize (corn) - Production"}
    assert "id_variable" not in dim_variable.columns  # laissé à PostgreSQL (SERIAL)


def test_construire_table_faits_remplace_variable_par_id():
    df = _table_faits_exemple()
    mapping = {"PIB (US$ courants)": 1, "Maize (corn) - Production": 2}

    table_faits = dims.construire_table_faits(df, mapping)

    assert list(table_faits.columns) == ["source", "code_pays_iso3", "annee", "id_variable", "valeur"]
    assert set(table_faits["id_variable"]) == {1, 2}
    assert table_faits["id_variable"].dtype == int


def test_construire_table_faits_leve_une_erreur_si_variable_non_mappee():
    df = _table_faits_exemple()
    mapping_incomplet = {"PIB (US$ courants)": 1}  # "Maize (corn) - Production" manquant

    with pytest.raises(ValueError, match="référencent une variable absente"):
        dims.construire_table_faits(df, mapping_incomplet)
