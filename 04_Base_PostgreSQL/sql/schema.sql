-- Schéma du mini Data Warehouse - NSENGO Veille des Marchés Agricoles
-- Toutes les instructions sont idempotentes (IF NOT EXISTS) : le script peut
-- être relancé sans risque sur une base déjà initialisée.

CREATE TABLE IF NOT EXISTS dim_pays (
    code_pays_iso3 VARCHAR(3) PRIMARY KEY,
    pays VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_variable (
    id_variable SERIAL PRIMARY KEY,
    variable VARCHAR(255) NOT NULL UNIQUE,
    unite VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS fait_marches_agricoles (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    code_pays_iso3 VARCHAR(3) NOT NULL REFERENCES dim_pays(code_pays_iso3),
    annee INTEGER NOT NULL,
    id_variable INTEGER NOT NULL REFERENCES dim_variable(id_variable),
    valeur DOUBLE PRECISION NOT NULL,
    CONSTRAINT uq_fait UNIQUE (source, code_pays_iso3, annee, id_variable)
);

CREATE INDEX IF NOT EXISTS idx_fait_pays ON fait_marches_agricoles (code_pays_iso3);
CREATE INDEX IF NOT EXISTS idx_fait_annee ON fait_marches_agricoles (annee);
CREATE INDEX IF NOT EXISTS idx_fait_variable ON fait_marches_agricoles (id_variable);

COMMENT ON TABLE dim_pays IS 'Dimension pays (Bénin + pays de comparaison régionale + Monde).';
COMMENT ON TABLE dim_variable IS 'Dimension variable : indicateur World Bank ou "Produit - Élément" FAOSTAT.';
COMMENT ON TABLE fait_marches_agricoles IS 'Table de faits issue de la Phase 3 (nettoyage + transformation).';
