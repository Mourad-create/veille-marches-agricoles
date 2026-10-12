# Veille des marchés agricoles — NSENGO (preuve de concept)

Plateforme décisionnelle de veille des marchés agricoles construite à partir de
**données ouvertes** (FAOSTAT, Banque mondiale). Projet réalisé dans le cadre d'un
stage Data Analyst chez NSENGO. Aucune donnée interne de l'entreprise n'est utilisée.

## Architecture (ETL)

Collecte (Python) → Préparation (Python / pandas) → Base PostgreSQL (modèle en étoile)
→ Vues SQL de KPI → Restitution (Power BI)

## Avancement par phase

| Phase | Dossier | État |
|---|---|---|
| 1. Analyse | `01_Cadrage/` | Fait (cahier des charges) |
| 2. Collecte | `02_Collecte_donnees/` | Fait : World Bank et FAOSTAT (autres sources à venir) |
| 3. Préparation / ETL | `03_Preparation_donnees/` | Fait |
| 4. Base PostgreSQL | `04_Base_PostgreSQL/` | Fait (schéma + chargement) |
| 5. Indicateurs SQL | `05_KPI_SQL/` | Fait (10 vues) |
| 6. Restitution Power BI | `06_Restitution_PowerBI/` | Fait (4 pages : Direction, Produits, Prix, Pays) |
| 7. Documentation (dictionnaire, guide utilisateur) | `07_Documentation/` | Fait |
| 8. Analyse et recommandations | `08_Analyse_recommandations/` | Requêtes prêtes, analyse à compléter avec les résultats |

Chaque dossier contient son propre `README.md` (installation, utilisation, tests).

## Ordre d'exécution

```bash
# 02 : télécharger les données brutes
python -m nsengo_veille.run_collecte --sources all
# 03 : nettoyer et transformer
python -m nsengo_prepare.run_preparation
# 04 : créer le schéma et charger la base (copier .env.example en .env)
python -m nsengo_charge.run_chargement
# 05 : créer les vues KPI
python run_vues.py
```

Voir les README de chaque dossier pour les options exactes.

## Configuration

Les identifiants PostgreSQL se placent dans un fichier `.env` (modèle : `.env.example`),
jamais versionné.

## Auteur

Mourad SAIZONOU — ESIGELEC, dominante BDTN.
