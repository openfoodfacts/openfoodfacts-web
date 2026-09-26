---
id: api-data-reuse
title: Données & API
icon: 💻
icon_name: wrench
order: 12
lang: fr
---

## Existe-t-il des recommandations dans la documentation concernant la taille des photos téléchargées ?

Cela peut dépendre des pays, si le réseau est lent ou coûteux. Tout ce qui dépasse 5000 pixels en poids ou en hauteur n'est probablement pas très utile. et si vous pouvez détecter que le réseau est lent, alors même une image de 2000 pixels serait très bien (certainement mieux que de ne pas avoir d'image !).

---

## Qu'en est-il des aliments sans code-barres ?

Open Food Facts ne contient que des informations sur les aliments emballés. Pour connaître les valeurs moyennes des fruits et légumes (par exemple, les tomates ou les bananes) et d'autres produits alimentaires, vous pouvez utiliser l'une des bases de données nationales officielles sur la nutrition.  

  

Remarque : la liste ci-dessous contient quelques-unes des principales bases de données nationales sur l'alimentation. Si vous pensez qu'une autre base de données devrait être incluse dans la liste, veuillez nous contacter à l'adresse suivante : [https://world.openfoodfacts.org/contact](https://world.openfoodfacts.org/contact)

  

  

**Liste des bases de données alimentaires nationales:**

**Australia** - FSANZ - NUTTAB 2006: [https://www.foodstandards.gov.au/media/documents/FSANZ%20Conf%20PostersNUTTAB.pdf](https://www.foodstandards.gov.au/media/documents/FSANZ%20Conf%20PostersNUTTAB.pdf)

**Belgium** - NUBEL - Belgian Food Composition Data: [https://www.internubel.be](https://www.internubel.be/)

**Canada** - FCEN: [https://aliments-nutrition.canada.ca/cnf-fce/index-fra.jsp](https://aliments-nutrition.canada.ca/cnf-fce/index-fra.jsp)

**Czech Republic** - Food Composition Database at National Institute of Public Health: [http://www.chpr.szu.cz/dbdata/foodcomp/nut2001.asp](http://www.chpr.szu.cz/dbdata/foodcomp/nut2001.asp)

**Denmark** - Danish Food Composition Databank: [https://frida.fooddata.dk/?lang=en](https://frida.fooddata.dk/?lang=en)

**Estonia** - Estonian Food Composition Database: [https://tka.nutridata.ee/en/](https://tka.nutridata.ee/en/)

**Finland** - Finnish Food Composition Database - FINELI: [https://fineli.fi/fineli/en/index](https://fineli.fi/fineli/en/index)

**France** - CIQUAL: [https://www.anses.fr/en/search/site/Table%20ciqual](https://www.anses.fr/en/search/site/Table%20ciqual)

**Germany** - Souci-Fachmann-Kraut Online Database: [https://www.sfk.online/#/home](https://www.sfk.online/#/home)

**Italy** - Banca Dati di Composizione degli Alimenti CREA: [https://www.crea.gov.it/web/alimenti-e-nutrizione/banche-dati](https://www.crea.gov.it/web/alimenti-e-nutrizione/banche-dati)

**Netherlands** - Dutch Food Composition Database: [https://www.rivm.nl/en/dutch-food-composition-database](https://www.rivm.nl/en/dutch-food-composition-database)

**Norway** - The Norwegian Food Composition Table 2006: [https://www.matvaretabellen.no/?language=en](https://www.matvaretabellen.no/?language=en)

**Poland** - Food Composition Tables: [http://www.izz.waw.pl/en/?lang=en](http://www.izz.waw.pl/en/?lang=en)

**Spain** - Spanish Food Composition Database - BEDCA: [https://www.bedca.net/bdpub/index.php](https://www.bedca.net/bdpub/index.php)

**Switzerland** - Swiss Food Composition Database: [https://www.naehrwertdaten.ch/de/](https://www.naehrwertdaten.ch/de/)

**UK** - Composition of foods integrated dataset (CoFID): [https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid](https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid)

**USA** - USDA: [https://ndb.nal.usda.gov/](https://ndb.nal.usda.gov/)

---

## Puis-je rechercher un nom de produit précis avec l'API ?

Malheureusement, il n'est pas encore possible d'effectuer une recherche précise sur le nom d'un produit uniquement à l'aide de l'API.  

  

L'utilisation d'un filtre sur la catégorie peut cependant vous aider à rendre votre recherche plus précise.

---

## Comment puis-je accéder aux données et les collecter pour mes projets ?

Sur la page principale d'Open Food Facts, dans le coin supérieur gauche de l'écran, il y a un menu déroulant. En bas de celui-ci, vous trouverez l'option "recherche avancée", sur laquelle vous pouvez cliquer. Il vous appartient alors de déterminer les critères les plus pertinents pour votre/vos projet(s). Une fois choisis, vous pourrez télécharger les résultats obtenus en descendant au bas de la page et en cliquant sur "Télécharger les résultats".  

  

Vous pouvez également consulter: 

  

La documentation de notre API : [https://openfoodfacts.github.io/api-documentation/](https://openfoodfacts.github.io/api-documentation/)

  

Les conditions d'utilisation d'Open Food Facts : [https://fr.openfoodfacts.org/terms-of-use](https://fr.openfoodfacts.org/terms-of-use)

  

Sur nos données : [https://fr.openfoodfacts.org/data](https://fr.openfoodfacts.org/data)

---

## Je souhaite un export CSV pour un pays / une marque… en particulier.

Je souhaite un export CSV pour un pays / une marque… en particulier.

  

Si vous souhaitez un export uniquement pour le Royaume-Uni, vous pouvez le télécharger via mirabelle (notre instance de datasette), en cliquant sur "(avancé)" à côté du lien "CSV" : [http://mirabelle.openfoodfacts.org/products/all?_sort=rowid&countries_en__like=%25United+Kingdom%25#export](http://mirabelle.openfoodfacts.org/products/all?_sort=rowid&countries_en__like=%25United+Kingdom%25#export)  

  

[https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv](https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv)  

[https://static.openfoodfacts.org/data/fr.openfoodfacts.org.products.csv](https://static.openfoodfacts.org/data/fr.openfoodfacts.org.products.csv)

---

## Y-a t-il des conditions pour utiliser l'API ?

Toute la documentation sur l'utilisation de l'API peut être trouvée sur [la page de documentation de l'API](https://openfoodfacts.github.io/openfoodfacts-server/api/), mais voici un bref résumé :

  

- La base de données Open Food Facts est disponible en données ouvertes sous *Open Database License* (ODbL), cf [https://world.openfoodfacts.org/terms-of-use](https://world.openfoodfacts.org/terms-of-use) pour les détails juridiques. Les deux conditions sont l'attribution et le partage. Si vous combinez les données d'Open Food Facts avec d'autres bases de données, l'ODbL exige que la base de données résultante soit également publiée en tant que données ouvertes. Cela signifie aussi que vous pouvez combiner les données uniquement avec des sources qui permettraient une telle redistribution.

- Vous devez toujours utiliser un *User-Agent* personnalisé lorsque vous effectuez des appels d'API pour identifier votre application.

- Des *rate-limits* sont appliquées pour chaque point de terminaison de l'API.

---

## Comment puis-je accéder aux données historiques ?

Actuellement, nous ne proposons pas d'export des données historiques (JSONL, MongoDB, CSV).

  

Cependant, pour des produits individuels, il est possible d'accéder aux versions précédentes des données du produit à l'aide de l'API ou sur la page du produit à l'aide des révisions.

  

Chaque fois qu'un produit est mis à jour, une nouvelle révision (chiffre croissant à partir de 1) est créée.

Par exemple, pour obtenir la première révision (=première version du produit) de ce produit, utilisez

[https://world.openfoodfacts.org/product/7623186089763/joghurt-baumnuss-migros?rev=1](https://world.openfoodfacts.org/product/7623186089763/joghurt-baumnuss-migros?rev=1).

  

De même, le paramètre rev peut être utilisé avec l'API :

[https://world.openfoodfacts.org/api/v2/product/7623186089763?rev=1](https://world.openfoodfacts.org/api/v2/product/7623186089763?rev=1)

---
