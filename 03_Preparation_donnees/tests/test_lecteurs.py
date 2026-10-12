import zipfile
from pathlib import Path

import pytest

from nsengo_prepare import lecteurs

FIXTURES = Path(__file__).parent / "fixtures"


def test_trouver_dernier_run_prend_le_plus_recent(tmp_path):
    source_dir = tmp_path / "world_bank"
    (source_dir / "20260101_090000").mkdir(parents=True)
    (source_dir / "20260815_143000").mkdir(parents=True)
    (source_dir / "_dernier_etat.json").touch()  # ne doit pas être pris pour un run

    resultat = lecteurs.trouver_dernier_run(tmp_path, "world_bank")

    assert resultat.name == "20260815_143000"


def test_trouver_dernier_run_leve_une_erreur_si_source_absente(tmp_path):
    with pytest.raises(FileNotFoundError):
        lecteurs.trouver_dernier_run(tmp_path, "source_inconnue")


def test_lire_world_bank_aplatit_le_json():
    df = lecteurs.lire_world_bank(FIXTURES / "world_bank_run")

    assert len(df) == 3
    assert set(df.columns) == {
        "pays",
        "code_pays_iso3",
        "indicateur_code",
        "indicateur",
        "annee",
        "valeur",
        "unite",
    }
    assert "BEN" in df["code_pays_iso3"].values


def test_lire_faostat_lit_le_csv_dans_le_zip(tmp_path):
    zip_path = tmp_path / "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
    csv_source = FIXTURES / "faostat_sample.csv"

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(csv_source, arcname="Production_Crops_Livestock_E_All_Data_(Normalized).csv")

    df = lecteurs.lire_faostat(tmp_path, zip_path.name)

    assert len(df) == 7
    assert "Item" in df.columns
    assert "Value" in df.columns
