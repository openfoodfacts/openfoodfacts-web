---
id: producers-products
title: Gestionar mis productos
icon: 📦
icon_name: box
order: 21
lang: es
---

## ¿Cómo podemos estar seguros de que los productos presentados en Open Food Facts presentan datos originales y correctos?

Para mejorar continuamente la calidad de los datos nos basamos en 4 pilares:

1. La comunidad añade constantemente datos y fotos y es una auténtica patrulla de revisores.

2. Hemos establecido reglas lógicas para identificar errores en las fichas de los productos. Por ejemplo: si la suma del peso de los ingredientes es mayor que el peso total del producto, hay una anomalía. Tenemos unos 50 controles de calidad más.

3. Gracias al aprendizaje automático, limitamos el riesgo de errores de entrada. Nuestra tecnología nos permite extraer datos textuales de las fotos tomadas por los colaboradores

4. Gracias al apoyo de Santé Publique France, desarrollamos un portal que permite a los productores cargar sus datos masivos y así corregir/completar las contribuciones de la comunidad.

---

## ¿Cómo añadir productos?

Para añadir productos a nuestra plataforma, todo lo que tiene que hacer es:

* Añadir un documento Excel con los datos de sus productos, entonces nuestra plataforma creará y rellenará las hojas.

* Si tiene una cuenta EQUADIS o AGENA3000. La importación también es posible.

* Si tiene un pequeño número de productos, todavía es posible crearlos a mano en la plataforma de productores (tenga en cuenta que las modificaciones en la plataforma pública a través de su cuenta profesional no están protegidas, estas modificaciones deben realizarse a través de la plataforma de productores y luego exportarse en la plataforma pública para obtener protección)

---

## ¿Existe una función de carga automática de productos?

Sí, si utiliza EQUADIS o AGENA3000 y establece la configuración adecuada, la importación puede realizarse automáticamente y, por tanto, actualizar los datos del producto en Open Food Facts.

---

## ¿Está limitado el número de productos añadidos?

No hay límite, puedes subir el número de productos que quieras en nuestra plataforma.

---

## ¿Es posible eliminar los productos que ya no se venden?

Si quieres eliminar un producto que ya no está a la venta, sólo tienes que marcar la casilla "este producto ya no se vende" cuando quieras modificar tu ficha de producto. También puede ponerse en contacto con nosotros a través de [support@openfoodfacts.org](mailto:support@openfoodfacts.org) con los distintos enlaces de sus productos para que nos encarguemos de ello.

Como el producto ya no se vende, en cualquier caso ya no será escaneado y, por tanto, ya no se mostrará a los consumidores.

Sin embargo, permanecerá en nuestra base de datos, sirviendo de archivo. Muchos estudios utilizan la base de datos Open Food Facts para informar sobre la alimentación en diferentes momentos.

---

## ¿La información de la empresa tiene prioridad sobre la información ya presente en la plataforma?

Cuando un productor ponga en línea uno de sus productos con su cuenta de productor y ya exista una ficha de producto, ésta se completará. 

La información que el productor haya colgado tendrá siempre prioridad y sólo él podrá modificar sus productos cuando la información esté completa.

Si los datos enviados a través de la plataforma están fragmentados, la información añadida por la comunidad desde el envase podrá completarla.

---

## ¿Qué información se solicita y en qué forma?

Cualquier tabla con sus datos es suficiente. El algoritmo hará un máximo de coincidencias de forma automática y algunas pueden ajustarse manualmente.

Tenemos un ejemplo [aquí](https://fr.pro.openfoodfacts.org/cgi/generate_sample_import_file.pl) 

Aunque Open Food Facts proporciona una plantilla, puede enviarnos los Excels que ya tenga con los nombres de las columnas que desee. La plataforma será capaz de reconocer sus variaciones y realizar el cotejo y la normalización con el modelo de datos de Open Food Facts.

---

## ¿Está integrado con Equadis / AGENA3000 / ConsoTrust?

Los fabricantes pueden ahora enviar sus datos y fotos de productos en tiempo real desde Equadis y AGENA3000 a Open Food Facts. Si es usted cliente de un catálogo de datos de productos, comuníquenoslo en [producers@openfoodfacts.org](mailto:producers@openfoodfacts.org).

Por supuesto, también se beneficiará de las sugerencias de reformulación y de todas las funciones de la plataforma.

En nuestra [entrada del blog](https://blog.openfoodfacts.org/en/news/real-time-product-data-from-producers-on-open-food-facts-thanks-to-the-new-equadis-integration) se explican los pasos a seguir si es cliente de EQUADIS.

Si es cliente de AGENA3000 (Producto A3 PIM INDUSTRY), sólo tiene que seleccionar el destinatario "Open Food Facts" al enviar sus fichas de producto. Más información en esta [entrada del blog](https://blog.openfoodfacts.org/en/news/share-your-product-data-in-1-click-with-the-new-agena3000-connector).

---

## Quiero añadir productos sin código de barras a través de la plataforma de productores

Para los productos sin código de barras, en el sitio o en la plataforma de productores, hay un botón "Producto sin código de barras" en la columna de la izquierda que permite añadirlos. A continuación se genera automáticamente un identificador.

---

## ¿Pueden integrarse en Open Food Facts los productos animales, los productos no alimentarios, los cosméticos y otros productos?

Hemos creado proyectos específicos para los cosméticos, para la alimentación animal, así como para otros productos (Open Beauty Facts, Open Pet Food Facts y Open Products Facts respectivamente). Por lo tanto, estamos encantados de poder importar sus productos al proyecto que les convenga.

---

## Los datos de los productos de mi empresa están disponibles en Open Food Facts. Es posible tomar el control de la cuenta de productor asociada?

Sí, por supuesto. Puede tomar el control de la cuenta de productor asociada creando una cuenta Open Food Facts con la dirección de su empresa. Al registrarse, mencione el nombre de la organización presente en el formulario para poder acceder al espacio de productor correspondiente. 

Será necesario un breve paso de validación para garantizar que usted es realmente el productor.

Podrá completar los datos, añadir imágenes, obtener recomendaciones automáticas para mejorar el Nutr-Score, y mucho más. Todo esto es, por supuesto, completamente gratuito. También puede conectar un sistema de gestión de datos de productos de terceros, como EQUADIS o AGENA3000

---

## ¿Cuánto tardan en actualizarse los datos de los productores en otra aplicación que reutiliza la base de datos de Open Food Facts?

Depende de las aplicaciones. Para las que utilizan nuestras API, que son la gran mayoría, es inmediato.

Para las que utilizan nuestras exportaciones diarias, es D+1 siempre que la actualicen.

---

## ¿La importación de los datos de una ficha de producto completa o sobrescribe la ficha de producto existente?

Utilizamos el código de barras para identificar los productos, si importa un registro con el mismo código de barras que un registro existente, la información se fusionará.

Para datos como la lista de ingredientes, los valores nutricionales (sólo un valor correcto posible), los datos enviados a través de la plataforma del productor sobrescribirán los datos existentes.

Para datos como etiquetas/categorías/marcas (varios valores correctos posibles), la información se fusionará. Si los datos son incorrectos en la plataforma pública, puede modificar la ficha del producto en la plataforma pública para eliminar los valores incorrectos.

---

## ¿Es importante el orden de los ingredientes?

El orden de los ingredientes es importante: representa el orden por cantidad. La mejor manera de rellenar los ingredientes es seguir exactamente lo que está escrito en el envase. Por eso también es tan importante tener fotos de los ingredientes impresas.

---

## ¿Puedo enviar imágenes también a través de AGENA3000?

Puede enviar imágenes, pero en la práctica solo se seleccionará automáticamente la imagen principal, las demás imágenes se enviarán, pero no se recortarán ni seleccionarán para ingredientes, nutrición, etc.

---

## ¿Cómo acceder a los tutoriales de la plataforma Pro?

Puedes acceder a los tutoriales de la plataforma pro  

  

A través de la propia plataforma pro: [https://es.pro.openfoodfacts.org/](https://es.pro.openfoodfacts.org/)

  

Directamente en [YouTube](https://www.youtube.com/playlist?list=PLjAH-USadsF3xgSVfUUBS4we3XBr-1r55)

  

→ También puedes descargar nuestra [guía de usuario](https://blog.openfoodfacts.org/wp-content/uploads/2023/03/EN-Pro-Plateform-User-Guide.pdf) ([https://blog.openfoodfacts.org/wp-content/uploads/2023/03/EN-Pro-Plateform-User-Guide.pdf](https://blog.openfoodfacts.org/wp-content/uploads/2023/03/EN-Pro-Plateform-User-Guide.pdf)) (inglés)

---
