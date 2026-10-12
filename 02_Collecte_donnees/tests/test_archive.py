from nsengo_veille.archive import GestionnaireArchive


def test_statuts_nouveau_puis_inchange_puis_mis_a_jour(tmp_path):
    gest = GestionnaireArchive(tmp_path / "raw", "source_test")

    r1 = gest.enregistrer_run([{"filename": "a.json", "content": b"v1", "meta": {}}])
    assert r1["fichiers"][0]["statut"] == "nouveau"

    r2 = gest.enregistrer_run([{"filename": "a.json", "content": b"v1", "meta": {}}])
    assert r2["fichiers"][0]["statut"] == "inchange"

    r3 = gest.enregistrer_run([{"filename": "a.json", "content": b"v2", "meta": {}}])
    assert r3["fichiers"][0]["statut"] == "mis_a_jour"

    historique = (tmp_path / "logs" / "historique_collecte.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(historique) == 3


def test_enregistrer_erreur_est_journalisee(tmp_path):
    gest = GestionnaireArchive(tmp_path / "raw", "source_test")
    resume = gest.enregistrer_erreur("timeout réseau")

    assert resume["erreur"] == "timeout réseau"
    historique_path = tmp_path / "logs" / "historique_collecte.jsonl"
    assert historique_path.exists()
    assert "timeout réseau" in historique_path.read_text(encoding="utf-8")
