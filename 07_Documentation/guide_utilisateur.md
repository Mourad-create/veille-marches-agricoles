# Guide utilisateur — Tableau de bord « Veille des marchés agricoles »

Fichier : `06_Restitution_PowerBI/Projet_Stage.pbix` (à ouvrir avec Power BI Desktop).
Le tableau de bord comporte 4 pages, accessibles par les onglets en bas de l'écran.

## À qui s'adresse chaque page

| Page | Public visé | Question à laquelle elle répond |
|---|---|---|
| Direction | Direction, décideurs | Quelle est la production mondiale et comment évolue-t-elle ? |
| Produits | Coopératives, producteurs | Quels produits rendent le plus, et qui produit le plus ? |
| Prix | Coopératives, commerçants | À quel prix s'échangent les produits (export / import) ? |
| Pays | Décideurs, organismes d'appui | Comment se situe un pays par rapport à ses voisins ? |

## Utiliser les filtres

Les segments (listes déroulantes) en haut des pages filtrent tous les graphiques de la page :
choisir un ou plusieurs produits ou pays, puis cliquer à nouveau sur la valeur pour retirer le filtre.
Un clic sur un élément d'un graphique (une barre, un pays sur la carte) filtre aussi les autres
visuels de la page.

## Lire les pages

**Direction** : les trois cartes donnent la production mondiale, le nombre de produits suivis et
le nombre de pays suivis. La courbe montre l'évolution de la production mondiale de 1961 à 2024.
La carte répartit la production par pays.

**Produits** : le graphique en barres classe les produits par rendement moyen (kg/ha). La courbe
montre la production du Bénin par produit. Le tableau classe les pays producteurs pour la dernière
année disponible. Les quatre cartes donnent la production de café, coton, maïs et riz.

**Prix** : deux cartes donnent le prix export et le prix import moyens. Le graphique en barres
compare ces deux prix par produit, la courbe suit le prix export mondial en USD par tonne, et le
tableau détaille les prix par pays.

**Pays** : les cartes donnent le nombre de pays comparés et la production totale régionale. Le
graphique en barres classe les pays producteurs, la courbe suit leur évolution, le tableau regroupe
leurs indicateurs macroéconomiques, et la carte localise la production.

## Limites à connaître

- Les prix sont des **estimations** (valeur du commerce ÷ quantité échangée), pas des prix de marché.
- Les données viennent de sources ouvertes (FAOSTAT, Banque mondiale) : elles sont publiées avec un
  décalage d'un à deux ans et peuvent contenir des valeurs aberrantes à la source.
- Le tableau de bord est un **prototype** (preuve de concept), pas un outil en production.

## Mettre à jour les données

1. Relancer la collecte puis la préparation (`02_Collecte_donnees/`, `03_Preparation_donnees/`).
2. Recharger la base (`04_Base_PostgreSQL/`) puis recréer les vues (`05_KPI_SQL/`).
3. Dans Power BI Desktop : **Accueil → Actualiser**.
