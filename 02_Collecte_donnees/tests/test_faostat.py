import json
from pathlib import Path

import responses

from nsengo_veille.collectors.faostat import FaostatCollector


@responses.activate
def test_fetch_and_run_creates_archive(tmp_path):
    contenu_zip_factice = b"PK\x03\x04-- contenu factice pour le test --"

    collecteur = FaostatCollector(
        output_root=tmp_path / "raw",
        domains={"QCL": "Production_Crops_Livestock_E_All_Data_(Normalized).zip"},
    )

    responses.add(
        responses.GET,
        "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip",
        body=contenu_zip_factice,
        status=200,
        content_type="application/zip",
    )

    resume = collecteur.run()

    assert resume["nb_fichiers"] == 1
    assert resume["nb_nouveaux"] == 1

    dossier_run = Path(resume["dossier"])
    fichier = dossier_run / "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
    assert fichier.exists()
    assert fichier.read_bytes() == contenu_zip_factice


@responses.activate
def test_domaine_en_echec_ne_bloque_pas_les_autres(tmp_path):
    collecteur = FaostatCollector(
        output_root=tmp_path / "raw",
        domains={
            "QCL": "Production_Crops_Livestock_E_All_Data_(Normalized).zip",
            "TCL": "Trade_CropsLivestock_E_All_Data_(Normalized).zip",
        },
    )

    responses.add(
        responses.GET,
        "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip",
        status=500,
    )
    responses.add(
        responses.GET,
        "https://bulks-faostat.fao.org/production/Trade_CropsLivestock_E_All_Data_(Normalized).zip",
        body=b"contenu-ok",
        status=200,
    )

    resume = collecteur.run()

    assert resume["nb_fichiers"] == 1
    assert resume["fichiers"][0]["filename"] == "Trade_CropsLivestock_E_All_Data_(Normalized).zip"
