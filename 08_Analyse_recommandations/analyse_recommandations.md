# Analyse et recommandations (Phase 8)

Données : base `nsengo_veille` (FAOSTAT, Banque mondiale), dernière année disponible : **2024**.
Périmètre : 4 produits (café, coton, maïs, riz), Bénin et 5 pays de comparaison
(Côte d'Ivoire, Ghana, Nigeria, Sénégal, Togo) plus l'agrégat mondial.
Requêtes sources : `requetes_analyse.sql`.

## 1. Constats chiffrés

| # | Thème | Constat | Requête |
|---|---|---|---|
| 1 | Production du Bénin | Sur 2014-2024, la production de **coton** passe de 381 662 t à 635 976 t (+66,6 %) et celle de **maïs** de 1 354 344 t à 2 094 824 t (+54,7 %). Le **café** reste marginal (55 t, -3,8 %). | 2 |
| 2 | Volatilité du coton | La production de coton chute de 29,5 % en 2015 et de 23,3 % en 2022, après des hausses de 67,6 % (2016) et 32,5 % (2017). | 2 |
| 3 | Rendement du maïs | En 2024, le Bénin a le **rendement de maïs le plus faible** des six pays : 1 190,5 kg/ha, contre 2 814,5 (Sénégal), 2 772,1 (Ghana), 2 563,5 (Côte d'Ivoire), 2 029,8 (Nigeria) et 1 256,2 (Togo). Soit environ 42 % du rendement du Sénégal. | 4 |
| 4 | Rendement par produit | Rendement moyen, tous pays et années : riz 1 819 kg/ha, maïs 1 250, coton 851, café 501. | 3 |
| 5 | Poids du Bénin | Part de la production mondiale en 2024 : coton 0,873 %, maïs 0,172 %, riz 0,061 %, café 0,0 %. | 5 |
| 6 | Riz | Le Bénin est 5e du classement des cinq premiers pays producteurs de la zone (500 605 t), loin derrière le Nigeria (9 129 900 t) et la Côte d'Ivoire (2 381 129 t). | 1 |
| 7 | Prix export mondiaux (2014 → 2024) | Café : 2 991 → 4 305 USD/t (+43,9 %). Maïs : 232 → 225 USD/t (-3,2 %). Riz : 424 → 357 USD/t (-15,9 %). Pas de prix pour le coton dans la base. | 6 |
| 8 | Commerce du Bénin | En 2024, le solde commercial est négatif sur les trois produits suivis : maïs -3 343 k USD (export 1, import 3 344), riz -781 k USD (export 53, import 834), café -1 k USD. | 7 |
| 9 | Contexte macroéconomique | Inflation 2024 : Bénin 1,16 %, Sénégal 0,80 %, Togo 2,86 %, Côte d'Ivoire 3,45 %, Ghana 22,85 %, Nigeria 33,24 %. PIB du Bénin : 21,5 milliards USD, population 14,5 millions. | 8 |

## 2. Interprétation

- **La croissance du maïs n'est pas portée par le rendement** : la production a progressé de 55 % alors que le
  rendement reste le plus bas de la zone. L'hypothèse la plus probable est une extension des surfaces
  cultivées, à confirmer avec `superficie_ha` (voir section 4).
- **Le Bénin importe plus qu'il n'exporte** en maïs et en riz, malgré une production de maïs de plus de
  2 millions de tonnes (les flux informels ou transfrontaliers ne sont pas toujours enregistrés dans FAOSTAT).
- **Le coton est la filière où le Bénin pèse le plus** à l'échelle mondiale (0,87 %), mais c'est aussi la plus
  instable d'une année à l'autre.
- **Le café est négligeable** en volume, alors que son prix mondial a le plus progressé.

## 3. Recommandations

| # | Recommandation | Constat qui la justifie | Bénéfice attendu |
|---|---|---|---|
| 1 | Prioriser l'amélioration du **rendement du maïs** (semences, intrants, conseil technique) plutôt que l'extension des surfaces. | Constats 3 et 4 : rendement le plus bas de la zone, à 42 % du Sénégal. | Hausse de production à surface constante ; meilleure rentabilité pour les producteurs. |
| 2 | Suivre le **risque de volatilité du coton** avec des alertes sur les baisses de production. | Constat 2 : chutes de 29 % et 23 %. | Anticiper les années difficiles ; informer coopératives et décideurs. |
| 3 | Étudier la **substitution des importations** de maïs et de riz (connecter les producteurs locaux à la demande nationale). | Constats 6 et 8 : balance négative sur les deux produits. | Meilleur débouché local ; réduction de la dépendance aux importations. |
| 4 | Surveiller le **prix du riz**, en baisse sur dix ans, avant d'encourager de nouveaux investissements. | Constat 7 : -15,9 % sur 2014-2024. | Éviter de pousser les producteurs vers une filière à marge décroissante. |
| 5 | Considérer le **café comme une niche à explorer** plutôt qu'une priorité. | Constats 1, 5 et 7 : volume marginal, prix mondial en forte hausse. | Valorisation de petites quantités à plus forte valeur. |
| 6 | Intégrer les données **climatiques** (NOAA, NASA POWER) et locales (prix de marché) pour expliquer les variations de rendement et de prix. | Limites de la section 4. | Analyses plus fines, au-delà des moyennes nationales. |

## 4. Limites de l'analyse

- Les **prix sont des estimations** (valeur commerciale ÷ quantité), et non des prix de marché observés ;
  aucune série de prix pour le coton n'apparaît dans la base.
- Le **commerce enregistré par FAOSTAT** peut sous-estimer les échanges informels, notamment frontaliers.
- Les indicateurs « terres agricoles (% du territoire) » et « indice de production alimentaire » sont
  **vides (NULL) pour 2024** dans la vue macro : les chiffres de la Banque mondiale ne sont probablement pas
  encore publiés pour cette année. À vérifier avec la dernière année où ils sont renseignés.
- Le riz du Bénin et les prix du riz n'ont été lus que partiellement (la requête 2 est tronquée à l'écran) :
  relancer pour compléter le constat 1.
- Aucune donnée interne NSENGO n'est utilisée : conclusions à confirmer avec des données opérationnelles.

## 5. Perspectives

Ajouter les sources prévues (data.gouv.fr, NOAA, Open Data Bénin), mettre en place des alertes automatiques
(baisse de production, hausse de prix) et tester un modèle de prévision simple sur le prix ou la production.

## 6. Vérifications complémentaires (facultatives)

```sql
-- Évolution de la superficie récoltée du maïs au Bénin (hypothèse du constat 3)
SELECT annee, superficie_ha, production_tonnes, rendement
FROM v_production_annuelle
WHERE pays ILIKE 'Ben%' AND produit = 'Maïs' AND annee >= 2014
ORDER BY annee;

-- Dernière année où les indicateurs macro agricoles sont renseignés
SELECT pays, annee, terres_agricoles_pct, indice_production_alimentaire
FROM v_indicateurs_macro_pivot
WHERE terres_agricoles_pct IS NOT NULL OR indice_production_alimentaire IS NOT NULL
ORDER BY annee DESC, pays LIMIT 14;
```
