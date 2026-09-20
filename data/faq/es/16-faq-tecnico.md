---
id: technical-faq
title: FAQ técnico
icon: 🛠️
icon_name: brands github
order: 16
lang: es
---

## ¿Debo actualizar todos los archivos de idioma cuando cambie una cadena de origen?

No es necesario.  

sólo actualice el inglés

Crea tu PR

Una vez que se fusiona, vamos a rebase crowdin-trigger manualmente y el sistema de traducción Crowdin triggerd por GitHub Acciones hará el resto para otros idiomas.

GitHub bot entonces crea un nuevo PR automáticamente que luego revisamos.

---
