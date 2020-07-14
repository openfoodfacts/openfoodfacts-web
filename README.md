# openfoodfacts-web


mv the /lang dir from openfoodfacts-server to openfoodfacts-resources (or maybe to make things even cleaner, to a new repo openfoodfacts-web, it's unclear if everything in openfoodfacts-resources is supposed to be available as-is on the web server).

create a /html/images/texts/ directory in openfoodfacts-web so that we can put the new images needed by texts there (we don't have to move the existing ones right away).

That way for deployment, we can just copy /lang and /html to /srv/off/ and it will work.

And that's it, that would be already be enough of a big change for a first step. Then we can have a look at what we have in /html/ to see what we should move, one by one.
