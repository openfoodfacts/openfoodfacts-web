---
id: international
title: Améliorer Open Food Facts dans ma langue/pays
icon: 🌐
icon_name: globe
order: 15
lang: fr
---

## J'aimerais ajouter un nouveau logo pour les labels

![image](https://support.openfoodfacts.org/api/v1/attachments/1666)

  

Voici le processus :

trouver le nom canonique du label dans la [taxonomie](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/taxonomies/labels.txt) des labels (c'est le premier élément de la liste des synonymes des labels, par exemple fr:100% légumes)  

obtenir le logo en bonne qualité : éviter d'utiliser les photos du contributeur qui ne sont pas adaptées à ce cas ; la plupart des labels ont des sites web officiels avec des logos de haute qualité, parfois en format vectoriel (ce qui est encore mieux pour nous) ; tant que nous utilisons un logo pour informer objectivement de la présence d'un label sur l'emballage d'un produit, il n'est pas nécessaire de demander l'autorisation.

nommer le fichier comme suit : nom-du-label.[largeur]x90.png où largeur est la largeur du logo lorsqu'il a une hauteur de 90 pixels. Les noms de fichiers doivent être non accentués, en minuscules et utiliser "-" à la place des espaces.

ajoutez ensuite le logo dans le répertoire correspondant à son nom canonique. Si le nom canonique est en:something, ils doivent être placés dans /en/. Le répertoire racine pour les logos est [https://github.com/openfoodfacts/openfoodfacts-server/tree/main/html/images/lang](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/html/images/lang)

---

## Comment traduire Open Food Facts dans ma langue ?

[https://wiki.openfoodfacts.org/Country_Support](https://wiki.openfoodfacts.org/Country_Support)

---

## Comment traduire cette FAQ dans ma langue ?

Veuillez demander à contact@openfoodfacts.org l'accès à la base de connaissances.

---
