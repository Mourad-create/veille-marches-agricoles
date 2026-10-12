-- =============================================================================
-- Vues KPI - NSENGO Veille des Marchés Agricoles (Phase 5)
-- =============================================================================
-- Toutes les vues sont en CREATE OR REPLACE : le script peut être relancé
-- sans risque. Elles s'appuient sur le schéma de la Phase 4
-- (dim_pays, dim_variable, fait_marches_agricoles).
--
-- Rappel de convention : pour les sources FAOSTAT, la colonne "variable" de
-- dim_variable a été construite en Phase 3 sous la forme "Produit - Élément"
-- (ex : "Maize (corn) - Production"). On la décompose ici avec split_part().
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Vue de base : décomposition Produit / Élément pour les données FAOSTAT
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_faostat_decompose AS
SELECT
    f.id,
    f.source,
    p.pays,
    p.code_pays_iso3,
    f.annee,
    split_part(v.variable, ' - ', 1) AS produit,
    split_part(v.variable, ' - ', 2) AS element,
    v.unite,
    f.valeur
FROM fait_marches_agricoles f
JOIN dim_pays p ON p.code_pays_iso3 = f.code_pays_iso3
JOIN dim_variable v ON v.id_variable = f.id_variable
WHERE f.source IN ('faostat_production', 'faostat_trade');


-- -----------------------------------------------------------------------------
-- KPI Production : une ligne par pays / produit / année
-- (production, rendement, superficie récoltée en colonnes)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_production_annuelle AS
SELECT
    pays,
    code_pays_iso3,
    produit,
    annee,
    MAX(valeur) FILTER (WHERE element = 'Production')     AS production_tonnes,
    MAX(valeur) FILTER (WHERE element = 'Yield')           AS rendement,
    MAX(valeur) FILTER (WHERE element = 'Area harvested')  AS superficie_ha
FROM v_faostat_decompose
WHERE source = 'faostat_production'
GROUP BY pays, code_pays_iso3, produit, annee;


-- -----------------------------------------------------------------------------
-- KPI Tendances : évolution annuelle de la production (variation vs année N-1)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_evolution_production AS
SELECT
    pays,
    code_pays_iso3,
    produit,
    annee,
    production_tonnes,
    production_tonnes - LAG(production_tonnes) OVER (PARTITION BY pays, produit ORDER BY annee)
        AS variation_absolue,
    ROUND(
        ((production_tonnes - LAG(production_tonnes) OVER (PARTITION BY pays, produit ORDER BY annee))
        / NULLIF(LAG(production_tonnes) OVER (PARTITION BY pays, produit ORDER BY annee), 0) * 100)::numeric,
        2
    ) AS variation_pct
FROM v_production_annuelle;


-- -----------------------------------------------------------------------------
-- KPI Pays : top pays producteurs, pour la dernière année disponible par produit
-- (le pays agrégé "World" est exclu du classement)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_top_pays_producteurs AS
WITH derniere_annee AS (
    SELECT produit, MAX(annee) AS annee_max
    FROM v_production_annuelle
    WHERE pays <> 'World'
    GROUP BY produit
)
SELECT
    vp.produit,
    vp.annee,
    vp.pays,
    vp.production_tonnes,
    RANK() OVER (PARTITION BY vp.produit ORDER BY vp.production_tonnes DESC) AS rang
FROM v_production_annuelle vp
JOIN derniere_annee da ON da.produit = vp.produit AND da.annee_max = vp.annee
WHERE vp.pays <> 'World';


-- -----------------------------------------------------------------------------
-- KPI Marchés : commerce extérieur (export/import) par pays / produit / année
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_commerce_annuel AS
SELECT
    pays,
    code_pays_iso3,
    produit,
    annee,
    MAX(valeur) FILTER (WHERE element = 'Export quantity') AS export_quantite_t,
    MAX(valeur) FILTER (WHERE element = 'Export value')    AS export_valeur_1000usd,
    MAX(valeur) FILTER (WHERE element = 'Import quantity') AS import_quantite_t,
    MAX(valeur) FILTER (WHERE element = 'Import value')    AS import_valeur_1000usd
FROM v_faostat_decompose
WHERE source = 'faostat_trade'
GROUP BY pays, code_pays_iso3, produit, annee;


-- -----------------------------------------------------------------------------
-- KPI Marchés : prix unitaire moyen (proxy) = valeur commerciale / quantité
-- FAOSTAT ne fournit pas de prix directement : ce ratio (valeur export ou
-- import / quantité correspondante) est l'estimation standard utilisée dans
-- la littérature agro-économique pour approcher un prix moyen à la tonne.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_prix_unitaires AS
SELECT
    pays,
    code_pays_iso3,
    produit,
    annee,
    ROUND((export_valeur_1000usd * 1000.0 / NULLIF(export_quantite_t, 0))::numeric, 2) AS prix_export_usd_par_tonne,
    ROUND((import_valeur_1000usd * 1000.0 / NULLIF(import_quantite_t, 0))::numeric, 2) AS prix_import_usd_par_tonne
FROM v_commerce_annuel;


-- -----------------------------------------------------------------------------
-- KPI Pays : top pays exportateurs, dernière année disponible par produit
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_top_pays_exportateurs AS
WITH derniere_annee AS (
    SELECT produit, MAX(annee) AS annee_max
    FROM v_commerce_annuel
    WHERE pays <> 'World' AND export_quantite_t IS NOT NULL
    GROUP BY produit
)
SELECT
    vc.produit,
    vc.annee,
    vc.pays,
    vc.export_quantite_t,
    RANK() OVER (PARTITION BY vc.produit ORDER BY vc.export_quantite_t DESC) AS rang
FROM v_commerce_annuel vc
JOIN derniere_annee da ON da.produit = vc.produit AND da.annee_max = vc.annee
WHERE vc.pays <> 'World' AND vc.export_quantite_t IS NOT NULL;


-- -----------------------------------------------------------------------------
-- KPI Production : rendement moyen par produit (hors "World", toutes années)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_rendement_moyen_par_produit AS
SELECT
    produit,
    ROUND(AVG(rendement)::numeric, 2) AS rendement_moyen,
    COUNT(*) AS nb_observations
FROM v_production_annuelle
WHERE pays <> 'World' AND rendement IS NOT NULL
GROUP BY produit
ORDER BY rendement_moyen DESC;


-- -----------------------------------------------------------------------------
-- Indicateurs macroéconomiques (World Bank) - vue brute, non pivotée.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_indicateurs_macro_bruts AS
SELECT
    p.pays,
    p.code_pays_iso3,
    f.annee,
    v.variable AS indicateur,
    f.valeur,
    v.unite
FROM fait_marches_agricoles f
JOIN dim_pays p ON p.code_pays_iso3 = f.code_pays_iso3
JOIN dim_variable v ON v.id_variable = f.id_variable
WHERE f.source = 'world_bank';


-- -----------------------------------------------------------------------------
-- Indicateurs macroéconomiques (World Bank) - vue pivotée, une colonne par
-- indicateur, une ligne par pays/année. Libellés confirmés sur données réelles.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_indicateurs_macro_pivot AS
SELECT
    pays,
    code_pays_iso3,
    annee,
    MAX(valeur) FILTER (WHERE indicateur = 'GDP (current US$)')                    AS pib_usd_courants,
    MAX(valeur) FILTER (WHERE indicateur = 'Population, total')                   AS population_totale,
    MAX(valeur) FILTER (WHERE indicateur = 'Inflation, consumer prices (annual %)') AS inflation_pct,
    MAX(valeur) FILTER (WHERE indicateur = 'Agricultural land (% of land area)')   AS terres_agricoles_pct,
    MAX(valeur) FILTER (WHERE indicateur = 'Food production index (2014-2016 = 100)')
        AS indice_production_alimentaire
FROM v_indicateurs_macro_bruts
GROUP BY pays, code_pays_iso3, annee
ORDER BY pays, annee;
