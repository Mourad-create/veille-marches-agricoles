"""
Collecteur FAOSTAT (fichiers bulk).

FAOSTAT publie, pour chaque domaine (production, commerce, prix...), une
archive ZIP téléchargeable directement sur bulks-faostat.fao.org. C'est
l'option la plus stable pour une collecte automatisée : contrairement à
l'API REST (paramètres de filtre plus complexes et sujets à changement),
l'URL d'un fichier bulk ne dépend que du nom du domaine.

Le filtrage sur les produits prioritaires (config.PRODUITS_PRIORITAIRES) et
les pays d'intérêt est volontairement laissé à l'étape de transformation
(phase 3 du projet) : ce module se contente de collecter et d'archiver la
donnée brute, fidèle à son rôle de Module 1 (Acquisition).

Attention : ces archives peuvent être volumineuses (plusieurs dizaines à
centaines de Mo selon le domaine). Prévoir un espace disque et une bande
passante suffisants lors de l'exécution réelle.
"""

from __future__ import annotations

import logging

import requests

from .. import config
from .base import BaseCollector

logger = logging.getLogger(__name__)


class FaostatCollector(BaseCollector):
    source_name = "faostat"

    BULK_URL_TEMPLATE = "https://bulks-faostat.fao.org/production/{filename}"

    def __init__(
        self,
        output_root: str = "data/raw",
        domains: dict[str, str] | None = None,
        session: requests.Session | None = None,
        timeout: int = 120,
        chunk_size: int = 1024 * 1024,
    ):
        super().__init__(output_root)
        self.domains = domains or config.FAOSTAT_DOMAINS
        self.session = session or requests.Session()
        self.timeout = timeout
        self.chunk_size = chunk_size

    def fetch(self) -> list[dict]:
        resultats = []

        for domain_code, filename in self.domains.items():
            url = self.BULK_URL_TEMPLATE.format(filename=filename)
            logger.info("Téléchargement FAOSTAT : domaine %s (%s)", domain_code, url)

            try:
                reponse = self.session.get(url, stream=True, timeout=self.timeout)
                reponse.raise_for_status()
            except requests.RequestException as exc:
                logger.error("Échec du téléchargement pour le domaine %s : %s", domain_code, exc)
                continue

            morceaux = []
            try:
                for chunk in reponse.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        morceaux.append(chunk)
            except requests.RequestException as exc:
                logger.error("Téléchargement interrompu pour le domaine %s : %s", domain_code, exc)
                continue

            contenu = b"".join(morceaux)
            if not contenu:
                logger.warning("Fichier vide reçu pour le domaine %s, ignoré.", domain_code)
                continue

            resultats.append(
                {
                    "filename": filename,
                    "content": contenu,
                    "meta": {"domaine": domain_code, "url": url, "taille_octets": len(contenu)},
                }
            )

        return resultats
