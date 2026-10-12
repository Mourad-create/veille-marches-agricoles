"""
Configuration du filtrage métier (Phase 3 - Préparation).

Ce fichier doit rester cohérent avec 02_Collecte_donnees/nsengo_collecte/
nsengo_veille/config.py (mêmes pays, mêmes produits prioritaires) : la
collecte récupère plus large, la préparation resserre sur le périmètre
d'analyse retenu dans le cahier des charges.
"""

# ---------------------------------------------------------------------------
# Pays retenus pour l'analyse : Bénin + pays de comparaison régionale + Monde.
# Mapping nom (tel qu'utilisé par FAOSTAT, colonne "Area") <-> code ISO3
# (tel qu'utilisé par World Bank, colonne "countryiso3code").
# ---------------------------------------------------------------------------
PAYS_INTERET = {
    "Benin": "BEN",
    "Nigeria": "NGA",
    "Côte d'Ivoire": "CIV",
    "Ghana": "GHA",
    "Togo": "TGO",
    "Senegal": "SEN",
    "World": "WLD",
}

# ---------------------------------------------------------------------------
# Produits prioritaires (tels que nommés dans la colonne "Item" de FAOSTAT).
# Identique à PRODUITS_PRIORITAIRES du module de collecte.
# ---------------------------------------------------------------------------
PRODUITS_PRIORITAIRES = ["Maize (corn)", "Rice", "Seed cotton, unginned", "Coffee, green"]

# Éléments FAOSTAT à conserver pour le domaine Production (QCL).
# (on écarte par exemple "Area harvested" si on ne veut que les volumes/rendements)
ELEMENTS_PRODUCTION = ["Production", "Yield", "Area harvested"]

# Éléments FAOSTAT à conserver pour le domaine Commerce (TCL).
# Attention à la casse : contrairement au domaine Production, FAOSTAT utilise
# ici une minuscule sur "quantity"/"value" (vérifié sur données réelles).
ELEMENTS_COMMERCE = ["Export quantity", "Export value", "Import quantity", "Import value"]

# Colonnes FAOSTAT à conserver après nettoyage (le reste est jugé inutile :
# codes techniques redondants avec les libellés, notes, etc.).
COLONNES_FAOSTAT_UTILES = ["Area", "Item", "Element", "Year", "Unit", "Value", "Flag"]

# ---------------------------------------------------------------------------
# Domaines FAOSTAT à traiter, avec le nom de fichier archivé par la Phase 2
# (doit rester identique à nsengo_veille.config.FAOSTAT_DOMAINS), le libellé
# de source à utiliser dans la table de faits, et les éléments à retenir.
# ---------------------------------------------------------------------------
DOMAINES_FAOSTAT = {
    "QCL": {
        "fichier": "Production_Crops_Livestock_E_All_Data_(Normalized).zip",
        "source_label": "faostat_production",
        "elements": ELEMENTS_PRODUCTION,
    },
    "TCL": {
        "fichier": "Trade_CropsLivestock_E_All_Data_(Normalized).zip",
        "source_label": "faostat_trade",
        "elements": ELEMENTS_COMMERCE,
    },
}
