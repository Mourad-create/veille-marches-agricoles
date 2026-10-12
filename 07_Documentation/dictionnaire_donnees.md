# Dictionnaire de données

Base PostgreSQL `nsengo_veille` (mini entrepôt de données, schéma en étoile simplifiée).
Schéma complet : `04_Base_PostgreSQL/sql/schema.sql`.

## 1. Tables

### `dim_pays` — dimension pays
Bénin, pays de comparaison régionale et agrégat « World ».

| Colonne | Type | Clé | Description |
|---|---|---|---|
| `code_pays_iso3` | VARCHAR(3) | PK | Code pays ISO 3166-1 alpha-3 |
| `pays` | VARCHAR(100) | | Nom du pays tel que fourni par la source |

### `dim_variable` — dimension variable
Un indicateur World Bank, ou un couple « Produit - Élément » FAOSTAT.

| Colonne | Type | Clé | Description |
|---|---|---|---|
| `id_variable` | SERIAL | PK | Identifiant technique auto-incrémenté |
| `variable` | VARCHAR(255) | unique | Libellé de la variable. FAOSTAT : « Produit - Élément » (ex. « Maize (corn) - Production »). World Bank : libellé de l'indicateur |
| `unite` | VARCHAR(50) | | Unité de mesure (tonnes, ha, 1000 USD, %…) |

### `fait_marches_agricoles` — table de faits
Une ligne par source, pays, année et variable.

| Colonne | Type | Clé | Description |
|---|---|---|---|
| `id` | BIGSERIAL | PK | Identifiant technique |
| `source` | VARCHAR(50) | | Origine : `faostat_production`, `faostat_trade` ou `world_bank` |
| `code_pays_iso3` | VARCHAR(3) | FK → `dim_pays` | Pays |
| `annee` | INTEGER | | Année de l'observation |
| `id_variable` | INTEGER | FK → `dim_variable` | Variable mesurée |
| `valeur` | DOUBLE PRECISION | | Valeur observée (non nulle) |

Contrainte d'unicité : (`source`, `code_pays_iso3`, `annee`, `id_variable`).
Index : pays, année, variable.

## 2. Vues (couche KPI, `05_KPI_SQL/sql/vues_kpi.sql`)

| Vue | Granularité | Colonnes principales | Rôle |
|---|---|---|---|
| `v_faostat_decompose` | ligne de fait FAOSTAT | `pays`, `annee`, `produit`, `element`, `unite`, `valeur` | Vue technique : sépare « Produit - Élément » |
| `v_production_annuelle` | pays / produit / année | `production_tonnes`, `rendement`, `superficie_ha` | Production, rendement et superficie récoltée |
| `v_evolution_production` | pays / produit / année | `production_tonnes`, `variation_absolue`, `variation_pct` | Variation vs année précédente |
| `v_top_pays_producteurs` | produit / pays (dernière année) | `annee`, `production_tonnes`, `rang` | Classement des pays producteurs, « World » exclu |
| `v_commerce_annuel` | pays / produit / année | `export_quantite_t`, `export_valeur_1000usd`, `import_quantite_t`, `import_valeur_1000usd` | Commerce extérieur |
| `v_prix_unitaires` | pays / produit / année | `prix_export_usd_par_tonne`, `prix_import_usd_par_tonne` | Prix moyen estimé = valeur ÷ quantité (proxy, FAOSTAT ne publie pas de prix directs) |
| `v_top_pays_exportateurs` | produit / pays (dernière année) | `export_quantite_t`, `rang` | Classement des exportateurs, « World » exclu |
| `v_rendement_moyen_par_produit` | produit | `rendement_moyen`, `nb_observations` | Rendement moyen, tous pays et années hors « World » |
| `v_indicateurs_macro_bruts` | pays / année / indicateur | `indicateur`, `valeur`, `unite` | Indicateurs World Bank, format long |
| `v_indicateurs_macro_pivot` | pays / année | `pib_usd_courants`, `population_totale`, `inflation_pct`, `terres_agricoles_pct`, `indice_production_alimentaire` | Mêmes indicateurs, une colonne chacun |

## 3. Sources

| Source | Code `source` | Contenu |
|---|---|---|
| FAOSTAT — Production (QCL) | `faostat_production` | Production, rendement, superficie récoltée |
| FAOSTAT — Commerce (TCL) | `faostat_trade` | Quantités et valeurs d'import / export |
| Banque mondiale — WDI | `world_bank` | PIB, population, inflation, terres agricoles, indice de production alimentaire |

## 4. Points d'attention

- Le prix unitaire est une **estimation** (valeur commerciale ÷ quantité), pas un prix de marché observé.
- Les valeurs commerciales FAOSTAT sont en **milliers de dollars US** ; les prix de `v_prix_unitaires` sont convertis en USD par tonne.
- Les classements excluent l'agrégat « World ».
- Les valeurs aberrantes éventuelles (erreurs de saisie à la source) ne sont pas corrigées automatiquement : à vérifier avant interprétation.
