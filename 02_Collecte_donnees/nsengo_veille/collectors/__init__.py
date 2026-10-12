from .base import BaseCollector
from .world_bank import WorldBankCollector
from .faostat import FaostatCollector

REGISTRE_COLLECTEURS = {
    WorldBankCollector.source_name: WorldBankCollector,
    FaostatCollector.source_name: FaostatCollector,
}

__all__ = ["BaseCollector", "WorldBankCollector", "FaostatCollector", "REGISTRE_COLLECTEURS"]
