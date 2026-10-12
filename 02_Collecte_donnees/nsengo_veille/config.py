"""
Configuration du catalogue de données à collecter.

Ce fichier centralise la liste des pays, indicateurs et domaines à récupérer
pour chaque source. Le modifier ici suffit à étendre la collecte (pas besoin
de toucher au code des collecteurs).

Statut des sources (voir le cahier des charges, section 5 « Sources de
données envisagées ») :
  - World Bank : validé, API stable et documentée -> implémenté.
  - FAOSTAT    : validé, fichiers bulk stables -> implémenté.
  - data.gouv.fr, NOAA, Open Data Bénin : disponibilité/périmètre exact
    encore à confirmer (cf. cahier des charges) -> non implémentés dans
    cette première itération. Le module collectors/base.py est conçu pour
    qu'un nouveau collecteur s'ajoute sans modifier le reste du pipeline.
"""

# ---------------------------------------------------------------------------
# World Bank (World Development Indicators)
# ---------------------------------------------------------------------------

# Bénin + quelques pays voisins/de comparaison régionale + agrégat mondial.
# Codes ISO3 utilisés par l'API World Bank.
WORLD_BANK_COUNTRIES = ["BEN", "NGA", "CIV", "GHA", "TGO", "SEN", "WLD"]

# Indicateurs choisis pour couvrir : contexte macroéconomique (PIB, inflation),
# démographie (population) et agriculture (terres agricoles, production).
WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.CD": "PIB (US$ courants)",
    "SP.POP.TOTL": "Population totale",
    "FP.CPI.TOTL.ZG": "Inflation, prix à la consommation (% annuel)",
    "AG.LND.AGRI.ZS": "Terres agricoles (% de la superficie totale)",
    "AG.PRD.FOOD.XD": "Indice de production alimentaire (2014-2016=100)",
}

WORLD_BANK_DATE_RANGE = "2000:2024"

# ---------------------------------------------------------------------------
# FAOSTAT (fichiers bulk, domaine par domaine)
# ---------------------------------------------------------------------------

# Nom exact des archives telles que publiées sur bulks-faostat.fao.org.
# À vérifier/mettre à jour si la FAO modifie sa nomenclature de fichiers.
FAOSTAT_DOMAINS = {
    "QCL": "Production_Crops_Livestock_E_All_Data_(Normalized).zip",
    "TCL": "Trade_CropsLivestock_E_All_Data_(Normalized).zip",
}

# Produits prioritaires pour l'analyse (utilisés en phase 3 - transformation/
# filtrage, conservés ici pour que la configuration des priorités métier
# reste centralisée).
PRODUITS_PRIORITAIRES = ["Maize (corn)", "Rice", "Seed cotton, unginned", "Coffee, green"]

# ---------------------------------------------------------------------------
# Sources non encore activées (voir docstring du module)
# ---------------------------------------------------------------------------

SOURCES_A_VALIDER = ["data_gouv_fr", "noaa", "open_data_benin"]
