---
id: api-data-reuse
title: API y reutilización de datos
icon: 💻
icon_name: wrench
order: 12
lang: es
---

## ¿Hay recomendaciones en algún lugar de la documentación sobre cuál sería un buen tamaño para las fotos subidas?

Eso puede depender de los países, si la red es lenta o cara. cualquier cosa por encima de 5000 píxeles en peso o altura probablemente no sea muy útil. y si de alguna manera se puede detectar que la red es lenta, entonces incluso una imagen de 2000 píxeles sería genial (¡sin duda mejor que no tener una imagen!)

---

## ¿Y los alimentos sin código de barras?

Open Food Facts sólo contiene información sobre alimentos envasados. Para conocer los valores medios de los productos agrícolas (por ejemplo, tomates o plátanos) y otros productos alimenticios, puede utilizar en su lugar una de las bases de datos nacionales oficiales sobre nutrición.

  

Nota: La siguiente lista contiene algunas de las bases de datos nacionales sobre alimentos más importantes. Si cree que debería incluirse en la lista alguna otra base de datos, póngase en contacto con nosotros en: [https://world.openfoodfacts.org/contact](https://world.openfoodfacts.org/contact)

  

Lista de bases de datos alimentarias nacionales: 

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

## ¿Puedo buscar un nombre de producto preciso con la API?

Desgraciadamente, todavía no es posible buscar fácilmente y con precisión sólo el nombre del producto a través de la API.  

  

Sin embargo, el uso de un filtro por categoría puede ayudarle a realizar una búsqueda más precisa.

---

## ¿Cómo puedo acceder a los datos para mis proyectos?

En la página principal de Open Food Facts, en la esquina superior izquierda de la pantalla, hay un menú desplegable. En la parte inferior del mismo, encontrará la opción "búsqueda avanzada", en la que puede hacer clic. A continuación, deberá determinar qué criterios son los más pertinentes para su(s) proyecto(s). Una vez elegidos, podrá descargar los resultados obtenidos desplazándose hacia abajo en la parte inferior de la página y haciendo clic en "Descargar resultados".  

  

También puede consultar;

  

La documentación de nuestra API:[https://openfoodfacts.github.io/api-documentation/](https://openfoodfacts.github.io/api-documentation/)

Condiciones de uso de Open Food Facts:[https://world.openfoodfacts.org/terms-of-use](https://world.openfoodfacts.org/terms-of-use)

Sobre nuestros datos:[https://world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)

---

## ¿Existen condiciones para utilizar la API?

Toda la documentación sobre el uso de API se puede encontrar en [la página de documentación de API](https://openfoodfacts.github.io/openfoodfacts-server/api/), pero aquí hay un resumen rápido:

  

- La base de datos Open Food Facts está disponible como datos abiertos bajo la *Open Database License* (ODbL); consulte [https://world.openfoodfacts.org/terms-of-use](https://world.openfoodfacts.org/terms-of-use) para obtener detalles legales. Las dos condiciones son la atribución y la participación por igual. Si combina datos de Open Food Facts con otras bases de datos, la ODbL exige que la base de datos resultante también se publique como datos abiertos. También significa que puede combinar los datos sólo con fuentes que permitan dicha redistribución.

- Siempre debes utilizar un *User-Agent* personalizado al realizar llamadas API para identificar su aplicación.

- Se aplican *rate-limits* para cada *API endpoint*.

---
