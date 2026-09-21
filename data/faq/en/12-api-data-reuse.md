---
id: api-data-reuse
title: API & data reuse
icon: 💻
icon_name: wrench
order: 12
lang: en
---

## Are there recommendations anywhere in the documentation on what would be a good size for uploaded photos?

That may depend on countries, if network is slow or expensive. anything above 5000 pixels in weight or height is probably not very useful. and if you can somehow detect that network is slow, then even a 2000 pixels image would be great (certainly better than not having an image!)

---

## What about food without barcodes ?

Open Food Facts contains only information about packaged food. For average values of produce (for example, tomatoes or bananas) and other food products, you can use one of the official national nutrition databases instead.

**Note:** The list below contains some of the most important national food databases. If you think some other database should be included in the list, please contact us at: [https://world.openfoodfacts.org/contact](https://world.openfoodfacts.org/contact)

**List of National Food Databases**

- 
**Australia** - FSANZ - NUTTAB 2006: [https://www.foodstandards.gov.au/media/documents/FSANZ%20Conf%20PostersNUTTAB.pdf](https://www.foodstandards.gov.au/media/documents/FSANZ%20Conf%20PostersNUTTAB.pdf)

- 
**Belgium** - NUBEL - Belgian Food Composition Data: [https://www.internubel.be](https://www.internubel.be/)

- 
**Canada** - FCEN: [https://aliments-nutrition.canada.ca/cnf-fce/index-fra.jsp](https://aliments-nutrition.canada.ca/cnf-fce/index-fra.jsp)

- 
**Czech Republic** - Food Composition Database at National Institute of Public Health: [http://www.chpr.szu.cz/dbdata/foodcomp/nut2001.asp](http://www.chpr.szu.cz/dbdata/foodcomp/nut2001.asp)

- 
**Denmark** - Danish Food Composition Databank: [https://frida.fooddata.dk/?lang=en](https://frida.fooddata.dk/?lang=en)

- 
**Estonia** - Estonian Food Composition Database: [https://tka.nutridata.ee/en/](https://tka.nutridata.ee/en/)

- 
**Finland** - Finnish Food Composition Database - FINELI: [https://fineli.fi/fineli/en/index](https://fineli.fi/fineli/en/index)

- 
**France** - CIQUAL: [https://www.anses.fr/en/search/site/Table%20ciqual](https://www.anses.fr/en/search/site/Table%20ciqual)

- 
**Germany** - Souci-Fachmann-Kraut Online Database: [https://www.sfk.online/#/home](https://www.sfk.online/#/home) or the official German Database: Bundeslebensmittelschlüssel: [https://blsdb.de/](https://blsdb.de/)

-  **Italy** - Banca Dati di Composizione degli Alimenti CREA: [https://www.crea.gov.it/web/alimenti-e-nutrizione/banche-dati](https://www.crea.gov.it/web/alimenti-e-nutrizione/banche-dati)

- 
**Netherlands** - Dutch Food Composition Database: [https://www.rivm.nl/en/dutch-food-composition-database](https://www.rivm.nl/en/dutch-food-composition-database)

- 
**Norway** - The Norwegian Food Composition Table 2006: [https://www.matvaretabellen.no/?language=en](https://www.matvaretabellen.no/?language=en)

- 
**Poland** - Food Composition Tables: [http://www.izz.waw.pl/en/?lang=en](http://www.izz.waw.pl/en/?lang=en)

- 
**Spain** - Spanish Food Composition Database - BEDCA: [https://www.bedca.net/bdpub/index.php](https://www.bedca.net/bdpub/index.php)

- 
**Switzerland** - Swiss Food Composition Database: [https://www.naehrwertdaten.ch/de/](https://www.naehrwertdaten.ch/de/)

- 
**UK** - Composition of foods integrated dataset (CoFID): [https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid](https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid)

- 
**USA** - USDA: [https://ndb.nal.usda.gov/](https://ndb.nal.usda.gov/)

---

## Can I search a precise product name with the API?

Unfortunately it's not yet possible to easily search on product name only and precisely through the API.

  

Using a filter on category might help you make your search more precise though.

---

## How can I access/collect data for my projects?

On Open Food Facts’ main page, at the top left corner of the screen, there’s a scrolling menu. At the bottom of it, you’ll find the “advanced search” option, on which you can click. It is then up to you to determine which criteria are the most relevant to your project(s). Once chosen, you’ll be able to download the obtained results by scrolling down at the bottom of the page and clicking on “Download results”. 

  

You can also consult: 

- Our API documentation:[ https://openfoodfacts.github.io/api-documentation/](https://openfoodfacts.github.io/api-documentation/)
- Open Food Facts' Terms of Use:[ ](https://world.openfoodfacts.org/terms-of-use)[https://world.openfoodfacts.org/terms-of-use](https://world.openfoodfacts.org/terms-of-use)
- On our data:[ https://world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)

---

## Are there conditions to use the API?

All the documentation about API usage can be found on the [API documentation page](https://openfoodfacts.github.io/openfoodfacts-server/api/), but here is a quick summary:

  

-  The Open Food Facts database is available as open data under the Open Database License (ODbL), see [https://world.openfoodfacts.org/terms-of-use](https://world.openfoodfacts.org/terms-of-use) for the legal details. The two conditions are attribution and share-alike. If you combine data from Open Food Facts with other databases, then the ODbL requires that the resulting database must be released as open data as well. It also means that you can combine the data only with sources that would allow such redistribution.

- You must **always** use a custom User-Agent when performing API calls to identify your app.

- Rate-limits are enforced for each API endpoint.

---

## How can I access historical data?

Currently, we don't offer historical data dump (JSONL, MongoDB, CSV).

  

However, for individual products, it's possible to access previous versions of the product data using the API or on the product page using revisions.

  

Every time a product is updated, a new revision (increasing digit starting from 1) is created.

For example, to get the first revision (=first product version) of this product, use

[https://world.openfoodfacts.org/product/7623186089763/joghurt-baumnuss-migros?rev=1](https://world.openfoodfacts.org/product/7623186089763/joghurt-baumnuss-migros?rev=1).

  

Similarly, the rev parameter can be used with the API:

[https://world.openfoodfacts.org/api/v2/product/7623186089763?rev=1](https://world.openfoodfacts.org/api/v2/product/7623186089763?rev=1)

---
