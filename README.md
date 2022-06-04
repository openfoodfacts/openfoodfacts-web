# openfoodfacts-web

This project contains static contents for [openfoodfacts product-opener project](https://github.com/openfoodfacts/openfoodfacts-server/).

Having those file in a separate project helps being more agile on translations delivery.

## Help translate

https://crowdin.com/project/openfoodfacts

## Adding a new page or updating an existing page
* Create a pull request on openfoodfacts-web with the new or modified HTML file (you can do that with the "GitHub Desktop" app if you are unfamiliar with the command line)
* Set it up for translation in the .crowdin file
* Once the pull request gets approved and merged, it will be deployed on the test server
* Deployment to production is still manual

## Deployment

### Actual prod (no docker)

1. Move the `/lang` dir from openfoodfacts-server to openfoodfacts-resources (or maybe to make things even cleaner, to a new repo openfoodfacts-web. It's unclear if everything in openfoodfacts-resources is supposed to be available as-is on the web server).

2. Create a `/html/images/texts/` directory in openfoodfacts-web so that we can put the new images needed by texts there (we don't have to move the existing ones right away).

That way for deployment, we can just copy `/lang` and `/html` to `/srv/off/` and it will work.

### On docker

See [openfoodfacts-server:docs/how-to-guides/using-pages-from-openfoodfacts-web.md](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/how-to-guides/using-pages-from-openfoodfacts-web.md)

And that's it! That would be already be enough of a big change for a first step. Then we can have a look at what we have in `/html/` to see what we should move, one by one.

## Tools
- [Basic command generator](https://docs.google.com/spreadsheets/d/1WOBGwvPAnojJlCFJ54eq4FY9-tAkiPx39mgxlt9lnP4/edit#gid=525301263)
