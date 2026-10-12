"""Configuration centralisée des logs (console + fichier journal)."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(verbose: bool = False, log_dir: str | Path = "data/logs") -> None:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    niveau = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    root = logging.getLogger()
    root.setLevel(niveau)
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    fichier = logging.FileHandler(log_dir / "pipeline_collecte.log", encoding="utf-8")
    fichier.setFormatter(formatter)
    root.addHandler(fichier)
