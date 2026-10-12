"""
Collecteur World Bank Open Data (World Development Indicators).

Documentation de l'API : https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
Endpoint utilisé : /v2/country/{codes};{codes}/indicator/{code}?format=json
"""

from __future__ import annotations

import logging

import requests

from .. import config
from .base import BaseCollector

logger = logging.getLogger(__name__)


class WorldBankCollector(BaseCollector):
    source_name = "world_bank"

    BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

    def __init__(
        self,
        output_root: str = "data/raw",
        countries: list[str] | None = None,
        indicators: dict[str, str] | None = None,
        date_range: str | None = None,
        per_page: int = 20000,
        session: requests.Session | None = None,
        timeout: int = 30,
    ):
        super().__init__(output_root)
        self.countries = countries or config.WORLD_BANK_COUNTRIES
        self.indicators = indicators or config.WORLD_BANK_INDICATORS
        self.date_range = date_range or config.WORLD_BANK_DATE_RANGE
        self.per_page = per_page
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch(self) -> list[dict]:
        resultats = []
        countries_param = ";".join(self.countries)

        for code, libelle in self.indicators.items():
            url = self.BASE_URL.format(countries=countries_param, indicator=code)
            params = {"format": "json", "per_page": self.per_page, "date": self.date_range}
            logger.info("Téléchargement World Bank : %s (%s)", code, libelle)

            try:
                reponse = self.session.get(url, params=params, timeout=self.timeout)
                reponse.raise_for_status()
            except requests.RequestException as exc:
                logger.error("Échec du téléchargement pour l'indicateur %s : %s", code, exc)
                continue

            try:
                donnees = reponse.json()
            except ValueError:
                logger.error("Réponse non-JSON pour l'indicateur %s (url=%s)", code, reponse.url)
                continue

            if not isinstance(donnees, list) or len(donnees) < 2 or donnees[1] is None:
                logger.warning(
                    "Réponse vide ou inattendue pour l'indicateur %s (pays peut-être invalides ou "
                    "indicateur retiré) : %s",
                    code,
                    donnees[0] if isinstance(donnees, list) and donnees else donnees,
                )
                continue

            page_info, observations = donnees[0], donnees[1]
            filename = f"world_bank_{code}.json"
            resultats.append(
                {
                    "filename": filename,
                    "content": reponse.content,
                    "meta": {
                        "indicateur": code,
                        "libelle": libelle,
                        "url": reponse.url,
                        "nb_observations": len(observations),
                        "pages": page_info,
                    },
                }
            )

        return resultats
