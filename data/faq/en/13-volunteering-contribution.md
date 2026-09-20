---
id: volunteering
title: Volunteering / Contribution
icon: 🤝
icon_name: edit
order: 13
lang: en
---

## Is there a way to remove uploaded images for products?

Only moderators can remove photos, to avoid potential vandalism.

  

Just ask on Slack or at **contact@openfoodfacts.org** to remove your duplicates or any inappropriate photos (you should try to provide the barcode number or URL to so).  

We also have a new image report API if you're a programmer.

---

## I'm a designer. How can I help ?

We coordinate all design related activities on [https://github.com/openfoodfacts/openfoodfacts-design](https://github.com/openfoodfacts/openfoodfacts-design) and on a dedicated chat channel. We regularly do team meetings and brainjams on specific challenges.

---

## In some cases the same product can have different nutritional values for each country, how is this handled in Open Food Facts ?

99% of the time, producers will create different barcodes for different versions of their products. A famous example is the difference between French and German Nutella in terms of thickness, due to difference in bread across countries. 2 different formulas, 2 different barcodes.

  

Barcode clash can however happen on shorter codes (EAN-8) that are typically reused by some stores across Europe and the US. We don't currently handle those barcode clashes, but it should be doable to do so by getting the user's general location (it's even more rare to have barcode clashes within a country).

In the long term, we encourage producers to move to EAN-13 to avoid those barcode clashes.

---
