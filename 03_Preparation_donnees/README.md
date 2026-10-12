# Pipeline de préparation — Phase 3 (Nettoyage / Transformation)

Ce dossier contient le pipeline de préparation des données, correspondant à
la **Phase 3** du cahier des charges (« Nettoyage, Fusion, Normalisation,
Contrôle qualité »). Il prend en entrée les données brutes produites par la
Phase 2 (`02_Collecte_donnees/nsengo_collecte/data/raw/`) et produit une
table de faits unique, propre, au format **Parquet**, prête à être chargée
en base PostgreSQL (Phase 4).

## Découpage en deux scripts (fidèle au plan d'origine)

| Script | Rôle |
|---|---|
| `nettoyage.py` (Script 2) | Nettoyage générique, sans logique métier : retire les colonnes inutiles, les doublons, les valeurs manquantes, normalise les types. |
| `transformation.py` (Script 3) | Filtrage métier (pays d'intérêt, produits prioritaires) et harmonisation des deux sources vers un schéma commun unique. |

## Schéma de sortie (table de faits)

| Colonne | Description |
|---|---|
| `source` | `world_bank`, `faostat_production` ou `faostat_trade` |
| `pays` | Nom du pays (ex : `Benin`) |
| `code_pays_iso3` | Code ISO3 (ex : `BEN`) |
| `annee` | Année de l'observation |
| `variable` | Nom de l'indicateur (World Bank) ou `Produit - Élément` (FAOSTAT), ex : `Maize (corn) - Production` |
| `valeur` | Valeur numérique |
| `unite` | Unité (ex : `t`, `ha`, `%`) |

## Périmètre métier (config.py)

- **Pays retenus** : Bénin + Nigeria, Côte d'Ivoire, Ghana, Togo, Sénégal (comparaison régionale) + Monde.
- **Produits prioritaires** : maïs, riz, coton graine non égrené, café vert.
- Ce périmètre doit rester cohérent avec `02_Collecte_donnees/nsengo_collecte/nsengo_veille/config.py` (mêmes pays/produits) — la collecte récupère plus large, la préparation resserre sur ce qui sera analysé.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Utilisation

```bash
python -m nsengo_prepare.run_preparation \
    --raw-root ../02_Collecte_donnees/nsengo_collecte/data/raw \
    --output data/processed/fact_marches_agricoles.parquet \
    --verbose
```

Le script :
1. trouve automatiquement le **dernier run** de chaque source (le dossier horodaté le plus récent) ;
2. nettoie chaque source séparément ;
3. filtre et harmonise vers le schéma commun ;
4. fusionne le tout et écrit un unique fichier Parquet.

## Tests

```bash
python -m pytest -q
```

Les tests couvrent : la lecture des fichiers bruts (JSON World Bank aplati,
CSV extrait d'un ZIP FAOSTAT), le nettoyage (suppression colonnes/doublons/
valeurs nulles), et la transformation (filtrage pays/produits/éléments,
fusion). Aucun accès réseau n'est nécessaire : tout est basé sur des
fixtures locales représentatives des vrais formats de données.

⚠️ **Note sur l'environnement de développement** : comme pour la Phase 2, ce
code a été écrit et vérifié manuellement (logique testée ligne par ligne à
la main) dans un environnement sans accès à `pip install` pour les paquets
`pytest`/`pyarrow`. Avant de considérer cette phase comme définitivement
validée, lance `pip install -r requirements.txt` puis `python -m pytest -q`
sur ton PC pour confirmer que la suite de tests passe dans un environnement
complet.

## Prochaines étapes

1. Valider `python -m pytest -q` sur un poste avec toutes les dépendances installées.
2. Lancer `run_preparation.py` sur les vraies données collectées (Phase 2) et vérifier le fichier Parquet produit (ex : `pandas.read_parquet(...)`, ou un simple `.head()`).
3. Phase 4 : conception du schéma PostgreSQL et chargement de cette table de faits.
