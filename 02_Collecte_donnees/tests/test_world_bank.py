import json
from pathlib import Path

import responses

from nsengo_veille.collectors.world_bank import WorldBankCollector

FIXTURE = Path(__file__).parent / "fixtures" / "world_bank_sample.json"


@responses.activate
def test_fetch_and_run_creates_archive(tmp_path):
    sample = FIXTURE.read_text(encoding="utf-8")

    # Deux indicateurs -> deux appels HTTP mockés (même réponse pour simplifier)
    collecteur = WorldBankCollector(
        output_root=tmp_path / "raw",
        countries=["BEN"],
        indicators={
            "NY.GDP.MKTP.CD": "PIB (US$ courants)",
            "SP.POP.TOTL": "Population totale",
        },
    )

    for code in collecteur.indicators:
        responses.add(
            responses.GET,
            f"https://api.worldbank.org/v2/country/BEN/indicator/{code}",
            body=sample,
            status=200,
            content_type="application/json",
        )

    resume = collecteur.run()

    assert resume["nb_fichiers"] == 2
    assert resume["nb_nouveaux"] == 2
    assert resume["nb_mis_a_jour"] == 0

    dossier_run = Path(resume["dossier"])
    fichiers = sorted(p.name for p in dossier_run.iterdir())
    assert "world_bank_NY.GDP.MKTP.CD.json" in fichiers
    assert "world_bank_SP.POP.TOTL.json" in fichiers
    assert "manifest.json" in fichiers

    manifest = json.loads((dossier_run / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"] == "world_bank"
    assert manifest["nb_fichiers"] == 2


@responses.activate
def test_second_run_detects_unchanged_data(tmp_path):
    sample = FIXTURE.read_text(encoding="utf-8")
    output_root = tmp_path / "raw"

    def faire_un_run():
        collecteur = WorldBankCollector(
            output_root=output_root,
            countries=["BEN"],
            indicators={"NY.GDP.MKTP.CD": "PIB (US$ courants)"},
        )
        responses.add(
            responses.GET,
            "https://api.worldbank.org/v2/country/BEN/indicator/NY.GDP.MKTP.CD",
            body=sample,
            status=200,
            content_type="application/json",
        )
        return collecteur.run()

    premier_resume = faire_un_run()
    assert premier_resume["nb_nouveaux"] == 1

    deuxieme_resume = faire_un_run()
    assert deuxieme_resume["nb_inchanges"] == 1
    assert deuxieme_resume["nb_nouveaux"] == 0


@responses.activate
def test_reponse_invalide_est_ignoree_sans_planter(tmp_path):
    collecteur = WorldBankCollector(
        output_root=tmp_path / "raw",
        countries=["XXX"],  # code pays volontairement invalide
        indicators={"NY.GDP.MKTP.CD": "PIB (US$ courants)"},
    )
    responses.add(
        responses.GET,
        "https://api.worldbank.org/v2/country/XXX/indicator/NY.GDP.MKTP.CD",
        json=[{"message": [{"id": "120", "key": "Invalid value", "value": "country code"}]}],
        status=200,
    )

    resume = collecteur.run()
    assert resume["nb_fichiers"] == 0
