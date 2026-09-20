---
id: technical-faq
title: Technical FAQ
icon: 🛠️
icon_name: brands github
order: 16
lang: en
---

## Should I update all language files when I change a source string?

No you don't. You just need to update the English one
- Create your PR

Once it's merged, we will rebase crowdin-trigger manually and the Crowdin translation system triggerd by GitHub Actions will do the rest for other languages.

GitHub bot then creates a new PR automatically that we then review.

---
