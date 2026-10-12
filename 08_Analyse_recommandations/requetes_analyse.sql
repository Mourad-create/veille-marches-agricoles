-- Phase 8 - Requêtes pour obtenir les chiffres de l'analyse.
-- À lancer dans HeidiSQL sur la base nsengo_veille, puis noter les résultats
-- dans analyse_recommandations.md.
-- Les noms de pays et de produits suivent les libellés de la source (anglais) :
-- lancer d'abord les requêtes 0a et 0b pour les vérifier.

-- 0a. Pays disponibles
SELECT pays, code_pays_iso3 FROM dim_pays ORDER BY pays;

-- 0b. Produits disponibles
SELECT DISTINCT produit FROM v_production_annuelle ORDER BY produit;

-- 1. Principaux pays producteurs (dernière année) pour un produit
--    (remplacer le motif du produit, ex. '%Maize%')
SELECT produit, annee, pays, production_tonnes, rang
FROM v_top_pays_producteurs
WHERE produit ILIKE '%Maize%' AND rang <= 5
ORDER BY rang;

-- 2. Évolution de la production du Bénin sur 10 ans, par produit
SELECT produit, annee, production_tonnes, variation_pct
FROM v_evolution_production
WHERE pays ILIKE 'Ben%' AND annee >= (SELECT MAX(annee) - 10 FROM v_production_annuelle)
ORDER BY produit, annee;

-- 3. Rendement moyen par produit (classement)
SELECT * FROM v_rendement_moyen_par_produit;

-- 4. Rendement du Bénin comparé aux autres pays, dernière année
SELECT pays, produit, annee, rendement
FROM v_production_annuelle
WHERE produit ILIKE '%Maize%'
  AND annee = (SELECT MAX(annee) FROM v_production_annuelle WHERE produit ILIKE '%Maize%')
  AND pays <> 'World'
ORDER BY rendement DESC;

-- 5. Part du Bénin dans la production mondiale, dernière année
SELECT b.produit, b.annee,
       ROUND((b.production_tonnes / NULLIF(w.production_tonnes, 0) * 100)::numeric, 3) AS part_mondiale_pct
FROM v_production_annuelle b
JOIN v_production_annuelle w
  ON w.produit = b.produit AND w.annee = b.annee AND w.pays = 'World'
WHERE b.pays ILIKE 'Ben%'
  AND b.annee = (SELECT MAX(annee) FROM v_production_annuelle WHERE pays ILIKE 'Ben%')
ORDER BY b.produit;

-- 6. Prix export moyen par produit : dernière année vs il y a 10 ans (monde)
SELECT produit, annee, prix_export_usd_par_tonne
FROM v_prix_unitaires
WHERE pays = 'World'
  AND annee IN ((SELECT MAX(annee) FROM v_prix_unitaires), (SELECT MAX(annee) - 10 FROM v_prix_unitaires))
ORDER BY produit, annee;

-- 7. Balance commerciale du Bénin, dernière année (export - import, 1000 USD)
SELECT produit, annee,
       export_valeur_1000usd, import_valeur_1000usd,
       export_valeur_1000usd - import_valeur_1000usd AS solde_1000usd
FROM v_commerce_annuel
WHERE pays ILIKE 'Ben%'
  AND annee = (SELECT MAX(annee) FROM v_commerce_annuel WHERE pays ILIKE 'Ben%')
ORDER BY solde_1000usd;

-- 8. Contexte macro : Bénin vs pays voisins, dernière année
SELECT pays, annee, pib_usd_courants, population_totale, inflation_pct,
       terres_agricoles_pct, indice_production_alimentaire
FROM v_indicateurs_macro_pivot
WHERE annee = (SELECT MAX(annee) FROM v_indicateurs_macro_pivot WHERE pib_usd_courants IS NOT NULL)
ORDER BY pib_usd_courants DESC;
