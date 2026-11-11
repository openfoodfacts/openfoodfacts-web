---
id: api-data-reuse
title: API & gegevenshergebruik
icon: 💻
icon_name: wrench
order: 12
lang: nl
---

## Zijn er aanbevelingen voor de resolutie van geüploade foto's?

Dat hangt mede af van de netwerksnelheid. Afbeeldingen groter dan 5000 pixels in de breedte of hoogte zijn meestal onnodig zwaar. Een foto van rond de 2000 pixels is ruim voldoende voor kwalitatieve tekstherkenning (OCR).

---

## Hoe zit het met voedingsmiddelen zonder streepjescode?

Open Food Facts richt zich primair op voorverpakte voeding met een streepjescode. Voor gemiddelde voedingswaarden van verse losse producten (zoals onverpakte tomaten of appels) kun je gebruikmaken van officiële nationale voedingsmiddelentabellen zoals de Nederlandse NEVO-tabel of de Belgische NUBEL.

---

## Is er een snelheidslimiet (rate limit) op de openbare API?

Ja, om onze openbare servers stabiel en gratis beschikbaar te houden voor iedereen, hanteren we redelijke limieten voor niet-geauthenticeerde verzoeken. Voor zware toepassingen raden we aan om onze dagelijkse data-dumps te downloaden of een eigen mirror op te zetten.

---

## Kan ik eerdere revisies van een product opvragen via de API?

Ja, met de parameter `?rev=1` (of een ander versienummer) kun je specifieke historische revisies van een product opvragen via de API en website.

---

## Bieden jullie SDK's aan voor verschillende programmeertalen?

Ja, er zijn officiële en door de gemeenschap onderhouden libraries beschikbaar voor onder meer Python, Dart/Flutter, JavaScript/TypeScript, PHP, Java/Kotlin, Swift en Rust.

---

## Waar vind ik de officiële API-documentatie?

De complete API v2/v3 documentatie is te vinden op [https://openfoodfacts.github.io/openfoodfacts-server/api/ref-v2/](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-v2/).

---
