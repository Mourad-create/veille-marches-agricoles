"""
Classe de base pour tous les collecteurs de données.

Un collecteur n'a qu'une seule responsabilité : savoir aller chercher des
données brutes chez une source donnée (fetch). Tout le reste — archivage,
historisation, journalisation, gestion des erreurs — est mutualisé ici, dans
run(), pour que chaque nouveau collecteur (data.gouv.fr, NOAA, Open Data
Bénin, ...) n'ait besoin d'implémenter que fetch().
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from ..archive import GestionnaireArchive

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    #: identifiant court de la source, utilisé comme nom de dossier
    source_name: str = "base"

    def __init__(self, output_root: str | Path = "data/raw"):
        self.output_root = Path(output_root)
        self.archive = GestionnaireArchive(self.output_root, self.source_name)

    @abstractmethod
    def fetch(self) -> list[dict]:
        """
        Télécharge les données brutes depuis la source.

        Retourne une liste de dicts : {"filename": str, "content": bytes, "meta": dict}
        Ne doit pas écrire sur disque directement : c'est le rôle de
        GestionnaireArchive (séparation collecte / stockage), afin que la
        logique d'historisation reste identique pour toutes les sources.
        """
        raise NotImplementedError

    def run(self) -> dict:
        """Exécute la collecte complète pour cette source et retourne un résumé."""
        logger.info("=== Démarrage de la collecte : %s ===", self.source_name)
        try:
            fichiers_bruts = self.fetch()
        except Exception as exc:  # noqa: BLE001 - on isole l'échec d'une source
            return self.archive.enregistrer_erreur(str(exc))

        if not fichiers_bruts:
            logger.warning("[%s] Aucune donnée récupérée lors de ce run.", self.source_name)

        resume = self.archive.enregistrer_run(fichiers_bruts)
        logger.info(
            "=== Fin de la collecte : %s (%d fichier(s), %d nouveau(x), %d mis à jour, %d inchangé(s)) ===",
            self.source_name,
            resume["nb_fichiers"],
            resume["nb_nouveaux"],
            resume["nb_mis_a_jour"],
            resume["nb_inchanges"],
        )
        return resume
