# KPI SQL — Phase 5 (Vues décisionnelles)

Ce dossier correspond à la **Phase 5** du cahier des charges : écriture des
requêtes SQL (vues, agrégations, KPI) exploitées ensuite par Power BI
(Phase 6).

## Vues créées

| Vue | Rôle |
|---|---|
| `v_faostat_decompose` | Vue technique : décompose `variable` ("Produit - Élément") en deux colonnes. Base des autres vues FAOSTAT. |
| `v_production_annuelle` | Production, rendement, superficie récoltée par pays/produit/année. |
| `v_evolution_production` | Variation annuelle (absolue et %) de la production, année sur année. |
| `v_top_pays_producteurs` | Classement des pays producteurs, dernière année disponible par produit. |
| `v_commerce_annuel` | Export/import (quantité + valeur) par pays/produit/année. |
| `v_prix_unitaires` | Prix moyen estimé (valeur commerciale ÷ quantité) — proxy standard en l'absence de prix directs dans FAOSTAT. |
| `v_top_pays_exportateurs` | Classement des pays exportateurs, dernière année disponible par produit. |
| `v_rendement_moyen_par_produit` | Rendement moyen agrégé par produit (tous pays/années). |
| `v_indicateurs_macro_bruts` | Indicateurs World Bank (PIB, population, etc.), format brut ligne par ligne. |
| `v_indicateurs_macro_pivot` | Mêmes indicateurs, pivotés en colonnes (une ligne par pays/année). |

## Libellés World Bank confirmés

Vérifiés sur les vraies données (`dim_variable`) : `GDP (current US$)`,
`Population, total`, `Inflation, consumer prices (annual %)`,
`Agricultural land (% of land area)`, `Food production index (2014-2016 = 100)`.
La vue `v_indicateurs_macro_pivot` utilise ces libellés exacts.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
copy ..\04_Base_PostgreSQL\.env .env    # réutilise directement les identifiants de la Phase 4
```

## Utilisation

```bash
python run_vues.py
```

Le script est idempotent (`CREATE OR REPLACE VIEW`) : relance-le à chaque
fois que tu modifies `sql/vues_kpi.sql`.

## Exemples de requêtes utiles (à tester dans HeidiSQL)

```sql
-- Evolution de la production de maïs au Bénin
SELECT * FROM v_evolution_production
WHERE pays = 'Benin' AND produit = 'Maize (corn)'
ORDER BY annee;

-- Top 5 pays producteurs de riz (dernière année)
SELECT * FROM v_top_pays_producteurs
WHERE produit = 'Rice' AND rang <= 5;

-- Prix export du café, par pays, dernières années
SELECT * FROM v_prix_unitaires
WHERE produit = 'Coffee, green'
ORDER BY annee DESC;

-- Rendement moyen par produit
SELECT * FROM v_rendement_moyen_par_produit;

-- Indicateurs macro du Bénin, triés par année
SELECT * FROM v_indicateurs_macro_pivot
WHERE pays = 'Benin'
ORDER BY annee DESC;
```

## Prochaine étape

Phase 6 : connexion de Power BI directement sur ces vues (via le connecteur
PostgreSQL natif de Power BI) pour construire les tableaux de bord.
