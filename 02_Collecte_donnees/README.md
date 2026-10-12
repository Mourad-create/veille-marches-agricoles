# Pipeline d'acquisition — Module 1 (Collecte automatique)

Ce dossier contient le pipeline de collecte automatique de données ouvertes,
correspondant à la **Phase 2** du cahier des charges (« Développer un module
Python qui télécharge automatiquement les datasets, met à jour les données,
archive les anciennes versions »).

## Sources implémentées dans cette première version

| Source | Statut | Contenu |
|---|---|---|
| World Bank (API REST) | ✅ Implémenté | PIB, population, inflation, terres agricoles, indice de production alimentaire — Bénin + pays voisins + Monde |
| FAOSTAT (fichiers bulk) | ✅ Implémenté | Domaines Production (QCL) et Commerce (TCL) |
| data.gouv.fr | ⏳ À implémenter | Disponibilité et granularité des données « prix agricoles » à confirmer (cf. cahier des charges, section 5) |
| NOAA (Climate Data Online) | ⏳ À implémenter | Densité de stations à évaluer pour l'Afrique de l'Ouest |
| Open Data Bénin | ⏳ À implémenter | Disponibilité du portail non confirmée à ce jour |

Les trois sources restantes sont volontairement laissées de côté à ce stade
(risque identifié dans le cahier des charges), le temps de confirmer leur
disponibilité réelle. L'architecture (voir plus bas) est conçue pour qu'un
nouveau collecteur s'ajoute sans toucher au reste du pipeline.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Utilisation

```bash
# Toutes les sources implémentées
python -m nsengo_veille.run_collecte --sources all

# Une seule source
python -m nsengo_veille.run_collecte --sources world_bank

# Plusieurs sources, avec logs détaillés
python -m nsengo_veille.run_collecte --sources world_bank faostat --verbose
```

## Structure produite

```
data/
  raw/
    world_bank/
      20260811_143000/
        world_bank_NY.GDP.MKTP.CD.json
        world_bank_SP.POP.TOTL.json
        manifest.json
      _dernier_etat.json        <- utilisé pour détecter les changements
    faostat/
      20260811_143005/
        Production_Crops_Livestock_E_All_Data_(Normalized).zip
        manifest.json
      _dernier_etat.json
  logs/
    historique_collecte.jsonl   <- historique complet, un run par ligne
    dernier_resume.json
    pipeline_collecte.log
```

Chaque exécution crée un nouveau dossier horodaté (historisation demandée
dans le cahier des charges) et compare le contenu téléchargé à la version
précédente via un hash SHA-256, pour savoir si un fichier est nouveau, mis à
jour ou inchangé — cette information alimentera le futur rapport de qualité
(Phase 3).

## Architecture du code

```
nsengo_veille/
  config.py              <- catalogue des pays/indicateurs/domaines à collecter
  archive.py             <- horodatage, hash, manifeste, journal d'historique
  logging_config.py      <- configuration des logs (console + fichier)
  run_collecte.py        <- point d'entrée CLI
  collectors/
    base.py              <- classe abstraite : fetch() à implémenter, run() mutualisé
    world_bank.py         <- collecteur World Bank
    faostat.py            <- collecteur FAOSTAT
```

Pour ajouter une nouvelle source (data.gouv.fr, NOAA, Open Data Bénin) :
créer un nouveau fichier dans `collectors/`, hériter de `BaseCollector`,
implémenter uniquement `fetch()` (retourne une liste de
`{"filename", "content", "meta"}`), puis l'enregistrer dans
`collectors/__init__.py`. L'archivage, l'historisation et la gestion des
erreurs sont automatiquement pris en charge.

## Tests

```bash
python -m pytest -q
```

7 tests couvrent : le téléchargement et l'archivage (World Bank, FAOSTAT),
la détection nouveau / inchangé / mis à jour, la résilience en cas d'échec
partiel (une source en erreur n'empêche pas les autres de s'exécuter), et la
journalisation des erreurs. Ils simulent les réponses HTTP (librairie
`responses`) — aucun appel réseau réel n'est nécessaire pour les exécuter.

## Prochaines étapes (suite du planning)

1. Confirmer la disponibilité de data.gouv.fr / NOAA / Open Data Bénin et
   ajouter les collecteurs correspondants.
2. Phase 3 (Préparation / ETL) : nettoyage, filtrage sur les produits et
   pays prioritaires, détection d'anomalies, à partir des fichiers stockés
   dans `data/raw/`.
