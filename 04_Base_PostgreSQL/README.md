# Base PostgreSQL — Phase 4 (Data Warehouse)

Ce dossier correspond à la **Phase 4** du cahier des charges : conception
d'un mini Data Warehouse PostgreSQL et chargement de la table de faits
produite en Phase 3.

## Schéma (étoile simplifiée)

```
dim_pays                 dim_variable
├─ code_pays_iso3 (PK)    ├─ id_variable (PK, auto)
└─ pays                   ├─ variable
                          └─ unite

              fait_marches_agricoles
              ├─ id (PK, auto)
              ├─ source
              ├─ code_pays_iso3 (FK)
              ├─ annee
              ├─ id_variable (FK)
              └─ valeur
```

Voir `sql/schema.sql` pour le détail (contraintes, index).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
cp .env.example .env
# puis édite .env et renseigne ton mot de passe PostgreSQL
```

⚠️ Le fichier `.env` contient un mot de passe : ne jamais le partager ni le
déposer dans un rendu de projet. Seul `.env.example` (sans vrai mot de
passe) doit être livré.

## Utilisation

Première exécution (crée la base si elle n'existe pas encore) :

```bash
python -m nsengo_charge.run_chargement \
    --parquet ../03_Preparation_donnees/data/processed/fact_marches_agricoles.parquet \
    --creer-base --verbose
```

Exécutions suivantes (la base existe déjà, on recharge juste les données) :

```bash
python -m nsengo_charge.run_chargement \
    --parquet ../03_Preparation_donnees/data/processed/fact_marches_agricoles.parquet \
    --verbose
```

Le script vide les tables avant chaque chargement (`TRUNCATE ... CASCADE`)
puis recharge l'intégralité des données — c'est un choix simple assumé pour
un pipeline batch qui recharge tout l'historique à chaque exécution.

## Tests

```bash
python -m pytest -q
```

Les tests couvrent uniquement la construction des dimensions (logique pure,
pandas), sans connexion réelle à PostgreSQL — testable sur n'importe quelle
machine, même sans base installée.

⚠️ **Note sur l'environnement de développement** : comme pour les phases
précédentes, ce code a été écrit et vérifié manuellement (logique de
dimensions testée à la main avec des données d'exemple) dans un
environnement sans accès réseau ni serveur PostgreSQL. La création de base,
l'exécution du schéma et le chargement réel (`db.py`, `charger.py`,
`run_chargement.py`) n'ont pas pu être testés de bout en bout avant livraison
— c'est le test en conditions réelles sur ton PC qui validera cette partie,
exactement comme pour les Phases 2 et 3.

## Vérifier le résultat

```sql
-- Dans psql ou un client SQL (pgAdmin, DBeaver...)
SELECT COUNT(*) FROM fait_marches_agricoles;
SELECT * FROM dim_variable LIMIT 10;
SELECT p.pays, v.variable, f.annee, f.valeur
FROM fait_marches_agricoles f
JOIN dim_pays p ON p.code_pays_iso3 = f.code_pays_iso3
JOIN dim_variable v ON v.id_variable = f.id_variable
WHERE p.pays = 'Benin'
ORDER BY f.annee DESC
LIMIT 10;
```

## Prochaine étape

Phase 5 : écriture des requêtes SQL de calcul des KPI (vues, agrégations,
top 10 pays/produits, évolutions annuelles) sur ce schéma.
