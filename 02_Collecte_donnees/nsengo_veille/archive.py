"""
Archivage et historisation des fichiers collectés.

Chaque exécution d'un collecteur produit un dossier horodaté contenant les
fichiers bruts téléchargés, ainsi qu'un manifeste JSON décrivant ce run.
Un journal global (JSON Lines) conserve l'historique de toutes les
exécutions, pour pouvoir répondre à l'exigence du cahier des charges :
« téléchargement automatique, mise à jour, archivage des anciennes
versions ».

La détection de changement repose sur un hash SHA-256 du contenu : si le
hash est identique à celui du run précédent pour le même fichier, il est
marqué "inchangé" (le fichier est tout de même conservé, pour disposer d'un
historique complet et traçable).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


@dataclass
class FichierCollecte:
    filename: str
    chemin: str
    taille_octets: int
    sha256: str
    statut: str  # "nouveau" | "mis_a_jour" | "inchange" | "erreur"
    meta: dict = field(default_factory=dict)


class GestionnaireArchive:
    """Gère le stockage horodaté et l'historique d'une source de données."""

    def __init__(self, output_root: str | Path, source_name: str):
        self.output_root = Path(output_root)
        self.source_name = source_name
        self.source_dir = self.output_root / source_name
        self.logs_dir = self.output_root.parent / "logs"
        self.state_path = self.source_dir / "_dernier_etat.json"
        self.historique_path = self.logs_dir / "historique_collecte.jsonl"

    def _charger_dernier_etat(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Impossible de lire l'état précédent (%s) : %s", self.state_path, exc)
        return {}

    def _sauvegarder_etat(self, etat: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(etat, ensure_ascii=False, indent=2), encoding="utf-8")

    def enregistrer_run(self, fichiers_bruts: list[dict], horodatage: datetime | None = None) -> dict:
        """
        fichiers_bruts : liste de dicts {"filename": str, "content": bytes, "meta": dict}
        Retourne un résumé du run (dict), sérialisable en JSON.
        """
        horodatage = horodatage or datetime.now()
        timestamp_str = horodatage.strftime("%Y%m%d_%H%M%S")
        run_dir = self.source_dir / timestamp_str
        run_dir.mkdir(parents=True, exist_ok=True)

        ancien_etat = self._charger_dernier_etat()
        nouvel_etat: dict = {}
        fichiers_resultat: list[FichierCollecte] = []

        for item in fichiers_bruts:
            filename = item["filename"]
            content = item["content"]
            meta = item.get("meta", {})
            digest = sha256_bytes(content)

            ancien_digest = ancien_etat.get(filename, {}).get("sha256")
            if ancien_digest is None:
                statut = "nouveau"
            elif ancien_digest == digest:
                statut = "inchange"
            else:
                statut = "mis_a_jour"

            dest = run_dir / filename
            dest.write_bytes(content)

            nouvel_etat[filename] = {"sha256": digest, "derniere_maj": timestamp_str}
            fichiers_resultat.append(
                FichierCollecte(
                    filename=filename,
                    chemin=str(dest),
                    taille_octets=len(content),
                    sha256=digest,
                    statut=statut,
                    meta=meta,
                )
            )
            logger.info("[%s] %s -> %s (%.1f Ko)", self.source_name, filename, statut, len(content) / 1024)

        self._sauvegarder_etat(nouvel_etat)

        resume = {
            "source": self.source_name,
            "horodatage": horodatage.isoformat(timespec="seconds"),
            "dossier": str(run_dir),
            "fichiers": [f.__dict__ for f in fichiers_resultat],
            "nb_fichiers": len(fichiers_resultat),
            "nb_nouveaux": sum(1 for f in fichiers_resultat if f.statut == "nouveau"),
            "nb_mis_a_jour": sum(1 for f in fichiers_resultat if f.statut == "mis_a_jour"),
            "nb_inchanges": sum(1 for f in fichiers_resultat if f.statut == "inchange"),
        }

        manifest_path = run_dir / "manifest.json"
        manifest_path.write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")

        self._ajouter_historique(resume)
        return resume

    def enregistrer_erreur(self, erreur: str, horodatage: datetime | None = None) -> dict:
        horodatage = horodatage or datetime.now()
        resume = {
            "source": self.source_name,
            "horodatage": horodatage.isoformat(timespec="seconds"),
            "erreur": erreur,
            "nb_fichiers": 0,
        }
        self._ajouter_historique(resume)
        logger.error("[%s] Échec de la collecte : %s", self.source_name, erreur)
        return resume

    def _ajouter_historique(self, resume: dict) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        with self.historique_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(resume, ensure_ascii=False) + "\n")
