#!/usr/bin/env python3
"""
clean_and_enrich_press_review.py

1. Fixes known accessible URLs (e.g. France 3 Paris Ile de France).
2. Cleans up internal editorial notes from 'verbatim' and 'topic'.
3. Moves internal editorial notes to 'editorial_note' (never displayed publicly).
4. Eliminates the 'OFF' acronym everywhere (replaces with 'Open Food Facts').
5. Normalizes country codes (e.g. fra, bel, che, deu, esp, ita, gbr, usa, can, eu, sen).
6. Adds granular 'media_scope':
   - 'national' (National press & media)
   - 'regional' (Regional press & PQR)
   - 'report' (Public reports, institutional studies, e.g. Cour des comptes)
   - 'culinary_blog' (Food & cooking blogs)
   - 'specialized' (Specialized agrifood, tech, and science press)
7. Tags items with accurate topics:
   - 'nutriscore'
   - 'nova'
   - 'upf' (Ultra-processed foods / aliments ultra-transformés)
   - 'green-score' (Eco-Score / Green-Score / environmental impact)
   - 'seasonal' (Fruits & vegetables in season)
   - 'data-journalism' (Data journalism, infographies, open data investigations)
   - 'additives' (Food additives & controversial substances)
   - 'open-data' (Open data & digital commons)
8. Adds 'dead_link': boolean flag for broken URLs, with archive fallbacks.
"""

import glob
import os
import re
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRESS_DIR = os.path.join(REPO_ROOT, "data", "press-review")

KNOWN_DEAD_LINK_IDS = {
    "2012-05-19-mondeculinaircom-le-monde-culinair",
    "2012-05-22-deslivresdanslac-des-livres-dans-la-cuisine",
    "2012-05-25-slidesharenet-going-beyond-open-government-dat",
    "2012-06-01-lanetscouadecom-la-netscouade",
    "2012-06-01-veilleagrihautet-veille-agri",
    "2012-06-04-legoutcom-le-gout",
    "2012-06-05-agro-mediafr-agro-mediafr",
    "2012-06-07-demeteretkotlerw-demeter-et-kotler",
    "2012-06-12-123opendatacom-123-open-data",
    "2012-06-19-nutrissimecom-nutrissime",
    "2012-06-27-ile-reunionpress-press-ecologie-ile-de-la-reunion",
    "2012-06-29-blogslatefr-quand-lappetit-va-slate-blogs",
    "2012-08-01-magazine-cles-entrefilet-n78nbsp-aout-septembr",
    "2012-10-15-mincejesuisgourm-mincenbsp-je-suis-gourmandenbsp",
    "2012-10-15-watsdesignblogsp-what-is-design",
    "2012-12-06-eco-sapiens-eco-sapiens-a-propos-de-noteo-sh",
    "2012-12-07-lci-lci-votre-cabas-passe-au-crible",
    "2012-12-10-wiki2dorg-wiki2d-la-provence-10122012",
    "2013-01-01-imagination-for-open-food-facts-projet-collabora",
    "2013-02-14-slatefr-blog-bie-comment-lire-une-etiquette-quand",
    "2013-03-05-storifycom-rencontre-visual-decision-sur-lo",
    "2013-03-12-le-monde-blogs-le-monde-les-consommateurs-sorg",
    "2013-03-29-france-culture-le-choix-de-la-redaction-du-29",
    "2013-04-03-snackingfr-open-food-facts-le-wikipedia-de-l",
    "2013-05-02-club-de-la-presse-prix-du-club-de-la-presse-8-pro",
    "2013-05-03-blog-de-la-trans-lopen-data-alimentaire-au-serv",
    "2013-05-18-rue89-alimentation-ce-que-les-etiquett",
    "2013-05-21-snackingfr-open-food-facts-lance-une-campag",
    "2013-05-24-consoglobe-open-food-facts-le-crowdsourci",
    "2013-06-11-blogfrancetvinfo-quy-a-t-il-dans-vos-mmsnbsp-atte",
    "2013-06-25-ecocentric-blog-open-food-facts-pour-mieux-choi",
    "2013-07-07-la-tribune-open-food-facts-le-wikipedia-al",
    "2013-08-01-bio-contact-pour-une-transparence-alimentair",
    "2013-10-16-france-inter-carnets-de-campagne-du-16-octob",
    "2014-01-06-le-particulier-p-le-particulier-pratique-n416-ali",
    "2014-04-18-rue89-open-food-facts-le-succes-colla",
    "2014-06-03-radio-canada-une-epicerie-transparente-grace-a",
    "2014-06-17-bastamag-des-citoyens-creent-une-base-de",
    "2014-11-05-rue89-au-menu-du-premier-ministere-un-p",
    "2015-05-18-liberation-open-food-facts-le-fond-du-pani",
    "2015-07-06-liberation-open-food-facts-du-libre-dans-l",
    "2015-09-01-bastamag-donnees-publiques-ces-citoyens-q",
    "2015-09-23-ubucon-ubucontest-story-openfoodfacts",
    "2015-11-14-francetv-info-francetv-info-en-images-combien",
    "2016-01-07-la-gazette-des-c-quand-la-donnee-devient-moteur",
    "2016-02-09-magazinelarucheq-open-food-facts-le-wiki-des-etiq",
    "2016-03-02-smartattitudeoui-open-food-facts-lindispensable-b",
    "2016-04-25-up-le-mag-decryptez-enfin-les-etiquettes-d",
    "2016-05-26-e-rsenet-open-food-facts-mieux-connaitre",
    "2016-06-17-blog-du-sans-glu-une-application-pour-tout-savoir",
    "2016-08-24-consommateur-en-open-food-facts-le-collaboratif",
    "2016-12-17-lesgoodnewsfr-open-food-facts-la-base-alimenta",
    "2017-01-30-genma-openfoodfacts",
    "2017-06-06-superproffr-maitriser-son-alimentation-pour",
    "2017-06-29-genie-alimentair-open-food-facts-la-base-de-donne",
    "2017-10-18-a-consommer-de-p-comment-bien-lire-les-etiquettes",
    "2017-11-02-coordination-rur-pourquoi-nutri-score-va-entraine",
    "2018-02-02-brunoy-osteopath-une-appli-pour-bien-manger",
    "2018-05-16-retailblogfr-systeme-u-lance-bientot-lapplica",
    "2018-05-21-le-hub-la-poste-systeme-u-va-lancer-une-appli-po",
    "2018-05-27-biodinerminceurf-le-nutri-score-pour-mieux-compre",
    "2018-06-01-la-voix-du-nord-consommation-yuka-une-appli-pour",
    "2018-06-01-otherwise-on-a-teste-yuka-lapplication-qui",
    "2018-06-05-entreprisemonopr-monoprix-sengage-sur-la-transpar",
    "2018-08-29-la-depeche-des-applications-a-foison-pour-s",
    "2018-08-31-stripfoodfr-yuka-une-appli-presque-parfaite",
    "2018-09-06-e-marketingfr-systeme-u-devoile-ya-quoi-dedans",
    "2018-09-09-lyon-capitale-lapplication-i-boycott-un-yuka-a",
    "2018-09-17-emballagesmagazi-open-food-facts-en-carafe",
    "2018-09-17-oliverdauversfr-yuka-ya-quoi-dedans-des-differen",
    "2018-09-24-id-linfo-durable-cinq-applications-pour-vraiment",
    "2018-10-04-euractivfr-euractivfr",
    "2018-10-30-allopsmfr-yuka-et-le-phenomene-des-applica",
    "2018-11-01-sante-magazine-n-mention",
    "2018-11-04-iphonfr-mangez-mieux-avec-une-app-iphone",
    "2018-11-10-le-soir-papier-les-pieges-des-applis-qui-aident",
    "2018-12-14-lasantepubliquef-nutri-score-sante-publique-franc",
    "2018-12-21-blog-postgresqlv-importer-openfoodfacts-dans-post",
    "2019-01-10-themouseorg-lapplicationyuka-apres-lalimenta",
    "2019-01-31-blogs20minutoses-con-que-aplicaciones-se-mueve-me",
    "2019-03-21-mobile-marketing-ophelia-bierschwale-yuka-notre-a",
    "2019-05-06-lilo-open-food-facts",
    "2019-08-21-tf1-le-jt-manger-sain-faut-il-se-fier-aux",
    "2020-01-20-quoi-dans-mon-as-score-yuka-avis-et-analyse-comme",
    "2020-01-24-ecran-mobile-aymeric-bauguin-shopperux-la-don",
    "2020-01-29-enviscope-consommation-responsable-mylabel",
    "2022-07-13-blog-agena3000-open-food-facts-la-base-de-donne",
}

CULINARY_BLOG_SOURCES = {
    "audrey cookinglove",
    "dans la cuisine de lilimarti",
    "aventures gustatives",
    "le monde culin'air",
    "mondeculinair.com",
    "des livres dans la cuisine",
    "deslivresdanslacuisine.com",
    "la patiss de neness",
    "la-patiss-de-neness.blogspot.fr",
    "passion culinaire",
    "passionculinaire.canalblog.com",
    "un demi-siècle de recettes",
    "undemisieclederecettes.blogspot.fr",
    "blog-du-sans-gluten.com",
    "mince je suis gourmande",
    "mincejesuisgourmande.com",
    "blog.recettes.de",
    "le goût",
    "legout.com",
    "locavorespirit",
    "locavorespirit.wordpress.com",
    "demeter et kotler",
    "demeteretkotler.wordpress.com",
}

PUBLIC_REPORT_SOURCES = {
    "cour des comptes",
    "agriculture.gouv.fr",
    "etalab.gouv.fr",
    "santé publique france",
    "santepubliquefrance.fr",
    "lasantepubliquefrance.fr",
    "ademe",
    "the publications office of the european union",
    "eu open data portal",
    "epsiplatform.eu",
    "gouvernement.fr",
    "reseau nacre",
    "réseau national alimentation cancer recherche",
    "ffas",
}

REGIONAL_PRESS_SOURCES = {
    "ouest france",
    "ouest-france",
    "la montagne",
    "var matin",
    "var-matin",
    "sud ouest",
    "la dépêche",
    "la depeche",
    "la dépêche du midi",
    "l'indépendant",
    "lindependant",
    "le télégramme",
    "le telegramme",
    "la nouvelle république",
    "la nouvelle republique",
    "le populaire",
    "le populaire du centre",
    "la voix du nord",
    "lyon capitale",
    "france 3",
    "france 3 ile de france",
    "france 3 regions",
    "press ecologie ile de la reunion",
    "la provence",
    "paris-ile-de-france.france3.fr",
    "france3-regions.franceinfo.fr",
    "france 3 corse",
    "le dauphiné libéré",
    "midi libre",
    "dna",
}

NATIONAL_PRESS_SOURCES = {
    "le monde",
    "lemonde.fr",
    "le figaro",
    "le figaro santé",
    "madame figaro",
    "libération",
    "les echos",
    "les echos start",
    "l'express",
    "l'express styles",
    "le point",
    "le nouvel obs",
    "nouvel obs",
    "nouvelobs",
    "l'obs",
    "la croix",
    "le parisien",
    "20 minutes",
    "20minutes.fr",
    "france info",
    "franceinfo",
    "france inter",
    "radio france culture",
    "france culture",
    "rtl",
    "europe 1",
    "rfi",
    "tf1",
    "france 2",
    "france 5",
    "m6",
    "bfm tv",
    "bfmtv",
    "lci",
    "cnews",
    "the guardian",
    "bbc",
    "bbc radio",
    "el país",
    "il fatto alimentare",
    "le soir",
    "le soir +",
    "la tribune",
    "terra eco",
    "rue89",
    "slate",
    "slate.fr",
    "mr mondialisation",
    "consoglobe",
    "bastamag",
    "elle",
    "santé magazine",
    "pleine vie",
    "le particulier",
    "le particulier pratique",
    "novethic",
    "l'humanité",
}

SPECIALIZED_PRESS_SOURCES = {
    "lsa conso",
    "lsa-conso.fr",
    "usine nouvelle",
    "l'usine nouvelle",
    "l'usine digitale",
    "l'usine digitale.fr",
    "numerama",
    "zdnet",
    "clubic",
    "french web",
    "frenchweb",
    "journal du net",
    "jdn",
    "linuxfr",
    "linuxfr.org",
    "sciences et avenir",
    "pour la science",
    "futura-sciences",
    "futura",
    "towards data science",
    "food times",
    "great italian food trade",
    "agro-media.fr",
    "agro-info.fr",
    "emballages magazine",
    "snacking.fr",
    "culture nutrition",
    "april.org",
    "cap digital",
    "e-marketing.fr",
    "e-rsenet",
    "génie alimentaire",
    "la revue du digital",
    "olivierdauvers.fr",
    "stripfood.fr",
    "foodvisor",
    "efficycle",
    "citizen post",
}

COUNTRY_MAP = {
    "fr": "fra",
    "fra": "fra",
    "france": "fra",
    "re": "fra",
    "reu": "fra",
    "polynésie française": "fra",
    "pyf": "fra",
    "be": "bel",
    "bel": "bel",
    "belgique": "bel",
    "ch": "che",
    "che": "che",
    "suisse": "che",
    "de": "deu",
    "deu": "deu",
    "ger": "deu",
    "allemagne": "deu",
    "it": "ita",
    "ita": "ita",
    "italie": "ita",
    "es": "esp",
    "esp": "esp",
    "spain": "esp",
    "espagne": "esp",
    "uk": "gbr",
    "gbr": "gbr",
    "us": "usa",
    "usa": "usa",
    "ca": "can",
    "can": "can",
    "eu": "eu",
    "europe": "eu",
    "sen": "sen",
    "sénégal": "sen",
}

def remove_off_acronym(text):
    if not text:
        return text
    # Replace whole word OFF with Open Food Facts
    # d'OFF -> d'Open Food Facts
    t = re.sub(r"\bd'OFF\b", "d'Open Food Facts", text)
    t = re.sub(r"\bl'OFF\b", "l'application Open Food Facts", t)
    t = re.sub(r"\bqu'OFF\b", "qu'Open Food Facts", t)
    t = re.sub(r"\bOFF\b", "Open Food Facts", t)
    # Also standardize common variations in reviewer notes
    t = t.replace("OpenFoodFacts", "Open Food Facts")
    t = t.replace("OpenFoodFact", "Open Food Facts")
    return t

def clean_verbatim_and_notes(item):
    v = (item.get("verbatim") or "").strip()
    top = (item.get("topic") or "").strip()
    notes = (item.get("editorial_note") or "").strip()
    
    # 1. Check known leaked internal note patterns
    # Specific known leaked comments
    if "l’icone de l’appli apparait dans le trio" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif v.startswith("Mention page"):
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif v.startswith("Citation anecdotique"):
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "OFF mentionnée dans" in v or "Open Food Facts mentionnée dans" in v:
        notes = (notes + "; " if notes else "") + v
        m = re.search(r'"([^"]+)"', v)
        v = f'"{m.group(1)}"' if m else ""
    elif "Comparaison entre les chiffres" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "il semble qu'ils parlent d'OFF" in v or "il semble qu'ils parlent d'Open Food Facts" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Présentation d'OFF" in v or "Présentation d'Open Food Facts" in v or "Présentation de OFF" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Yuka déclare officiellement ne plus se servir" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Transcription d'un podcast" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Utilisation pratique de l'application" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "cité comme source des données" in v:
        notes = (notes + "; " if notes else "") + v
        # Check if there is also an actual quote in the text
        m = re.search(r'"([^"]+)"', v)
        v = f'"{m.group(1)}"' if m else ""
    elif "présenté comme source de données" in v or "présenté comme source des données" in v:
        notes = (notes + "; " if notes else "") + v
        m = re.search(r'"([^"]+)"', v)
        v = f'"{m.group(1)}"' if m else ""
    elif "rattraché à la définition" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "3 inconvénients présentés en fin d'article" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Copier/coller de l'article" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "Très courte évocation" in v:
        notes = (notes + "; " if notes else "") + v
        m = re.search(r'"([^"]+)"', v)
        v = f'"{m.group(1)}"' if m else ""
    elif "Citation de Pierre S." in v:
        notes = (notes + "; " if notes else "") + v
        m = re.search(r'"([^"]+)"', v)
        v = f'"{m.group(1)}"' if m else ""
    elif "Evocation \"En attendant son application" in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            notes = (notes + "; " if notes else "") + "Évocation dans l'article"
            v = f'"{m.group(1)}"'
    elif "OFF fait partie du top 5" in v or "Open Food Facts fait partie du top 5" in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            notes = (notes + "; " if notes else "") + "Classement top 5 des applis"
            v = f'"{m.group(1)}"'
    elif "cité en premier" in v and '"' in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            notes = (notes + "; " if notes else "") + "Cité en premier"
            v = f'"{m.group(1)}"'
    elif "positionnée en 4ème position" in v and '"' in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            notes = (notes + "; " if notes else "") + "Positionnée en 4ème position"
            v = f'"{m.group(1)}"'
    elif "Point négatif relevé" in v and '"' in v:
        notes = (notes + "; " if notes else "") + "Point négatif relevé face aux ambitions de l'ANIA"
        # Extract the quote inside
        m = re.search(r'"(Aujourd\'hui beaucoup d\'applications.*?)"', v)
        if m:
            v = f'"{m.group(1)}"'
    elif "Rôle de OFF mis en avant" in v or "Rôle d'Open Food Facts mis en avant" in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            notes = (notes + "; " if notes else "") + "Rôle d'Open Food Facts mis en avant"
            v = f'"{m.group(1)}"'
    elif "Simple citation \"À l’heure où les bases" in v:
        m = re.search(r'"([^"]+)"', v)
        if m:
            v = f'"{m.group(1)}"'
    elif "est cité en premier de la liste" in v:
        notes = (notes + "; " if notes else "") + v
        v = '"Note globale basée sur le Nutri-Score et le classement NOVA."'
    elif "Commentaire négatif en dessous de l'article" in v:
        notes = (notes + "; " if notes else "") + v
        v = ""
    elif "OFF permet une \"une analyse objective" in v or "Open Food Facts permet une \"une analyse objective" in v:
        v = '"une analyse objective des valeurs nutritionnelles du produit"'

    # 2. Check topic field for misplaced quotes or internal notes
    if top in {"PAS ACCES à L'ARTICLE", "Hors sujet", "Version papier de l'article précédent publié sur Le Soir +", "Traduction FR de l'article précédent"}:
        notes = (notes + "; " if notes else "") + top
        top = ""
    elif top.startswith('"') and top.endswith('"'):
        # Misplaced quote in topic
        if not v:
            v = top
            top = ""
        else:
            notes = (notes + "; " if notes else "") + top
            top = ""

    # Replace OFF acronym everywhere
    v = remove_off_acronym(v)
    top = remove_off_acronym(top)
    notes = remove_off_acronym(notes)

    item["verbatim"] = v
    item["topic"] = top
    if notes:
        item["editorial_note"] = notes
    elif "editorial_note" in item:
        del item["editorial_note"]

def determine_topics(item):
    text = " ".join([
        str(item.get("title", "")),
        str(item.get("verbatim", "")),
        str(item.get("topic", "")),
        str(item.get("source", "")),
        str(item.get("link", ""))
    ]).lower()

    topics = []

    # 1. Nutri-Score
    if re.search(r"nutri-?score|5-c\b|code 5 couleurs|etiquetage nutritionnel|profils nutritionnels|profil nutritionnel", text):
        topics.append("nutriscore")

    # 2. NOVA
    if re.search(r"\bnova\b|classification nova|score nova|groupe nova", text):
        topics.append("nova")

    # 3. UPF (Ultra-processed foods)
    if re.search(r"ultra-?transform[eé]|ultra-?processed|\bupf\b|craking|cracking|émulsifiant|emulsifiant", text):
        topics.append("upf")

    # 4. Green-Score / Eco-Score / Environmental impact
    if re.search(r"green-?score|[eé]co-?score|impact [eé]cologique|impact environnemental|empreinte environnementale|emballages|climat", text):
        topics.append("green-score")

    # 5. Seasonal
    if re.search(r"fruits? et l[eé]gumes? de saison|saisonnalit[eé]|\bseasonal\b|de saison", text):
        topics.append("seasonal")

    # 6. Data Journalism / Open Data investigations
    if re.search(r"data journalist|journalisme de donn[eé]es|infograph|enqu[eê]te.*donn[eé]es|data for good|big data|datathon|analyse.*donn[eé]es", text):
        topics.append("data-journalism")

    # 7. Additives
    if re.search(r"additif|e171|dioxyde de titane|perturbateur|ingr[eé]dients? controvers[eé]", text):
        topics.append("additives")

    # 8. Open data / Digital commons
    if re.search(r"open data|donn[eé]es ouvert|science participative|collaboratif|communs|wikipedia de l'alimentation", text):
        topics.append("open-data")

    return topics

def determine_media_scope(item):
    src = (item.get("source") or "").strip().lower()
    dom = (item.get("domain") or "").strip().lower()
    raw = (item.get("raw_type") or "").strip().lower()
    title = (item.get("title") or "").strip().lower()

    # Public reports & institutions
    if src in PUBLIC_REPORT_SOURCES or dom in PUBLIC_REPORT_SOURCES or any(p in src or p in dom for p in ["cour des comptes", "agriculture.gouv", "santepublique", "etalab.gouv", "ademe"]):
        return "report"
    if "rapport" in raw or "rapport pdf" in raw:
        return "report"

    # Culinary blogs
    if src in CULINARY_BLOG_SOURCES or dom in CULINARY_BLOG_SOURCES or any(w in src or w in dom for w in ["culinair", "recette", "cuisine", "patiss", "gourmand", "sans-gluten", "gustative"]):
        return "culinary_blog"
    if "blog culinaire" in raw:
        return "culinary_blog"

    # Regional press
    if src in REGIONAL_PRESS_SOURCES or dom in REGIONAL_PRESS_SOURCES or any(w in src for w in ["ouest france", "ouest-france", "montagne", "var matin", "var-matin", "sud ouest", "depeche", "independant", "telegramme", "nouvelle republique", "populaire", "voix du nord", "lyon capitale", "france 3", "la provence"]):
        return "regional"
    if "pqr" in raw or "tv régionale" in raw or "presse régionale" in raw:
        return "regional"

    # National press
    if src in NATIONAL_PRESS_SOURCES or dom in NATIONAL_PRESS_SOURCES or any(w in src for w in ["le monde", "le figaro", "libération", "les echos", "l'express", "le point", "nouvel obs", "l'obs", "la croix", "le parisien", "20 minutes", "france info", "france inter", "radio france", "tf1", "france 2", "france 5", "m6", "bfm", "lci", "cnews"]):
        return "national"

    # Specialized
    if src in SPECIALIZED_PRESS_SOURCES or dom in SPECIALIZED_PRESS_SOURCES or any(w in src for w in ["lsa", "usine nouvelle", "usine digitale", "numerama", "zdnet", "clubic", "french web", "jdn", "linuxfr", "sciences et avenir", "futura", "towards data", "agro-media"]):
        return "specialized"

    # Fallback checks
    if item.get("type") == "study":
        return "report"

    return "national"

def enrich_press_items():
    yaml_files = sorted(glob.glob(os.path.join(PRESS_DIR, "*.yaml")) + glob.glob(os.path.join(PRESS_DIR, "*.yml")))
    print(f"Processing {len(yaml_files)} YAML files...")

    stats = {
        "fixed_urls": 0,
        "dead_links": 0,
        "editorial_notes_cleaned": 0,
        "off_acronyms_replaced": 0,
        "scopes": {},
        "topics": {}
    }

    for fpath in yaml_files:
        with open(fpath, "r", encoding="utf-8") as fp:
            item = yaml.safe_load(fp)

        p_id = item.get("id")

        # 1. Fix France 3 URL & Title
        if p_id == "2013-03-03-france-3-ile-de-paris-ile-de-france-france3":
            item["link"] = "https://france3-regions.franceinfo.fr/paris-ile-de-france/2013/02/28/comment-courcircuiter-les-circuits-de-la-distribution-internet-la-rescousse-du-mieux-consommer-208243.html"
            item["title"] = "Comment court-circuiter les circuits de la distribution ? Internet à la rescousse du mieux consommer"
            item["domain"] = "france3-regions.franceinfo.fr"
            stats["fixed_urls"] += 1

        # 2. Fix Cour des comptes type
        if "cour des comptes" in (item.get("source") or "").lower():
            item["type"] = "study"

        # 3. Clean verbatims, topics, and editorial notes
        orig_v = item.get("verbatim", "")
        clean_verbatim_and_notes(item)
        if item.get("editorial_note") or orig_v != item.get("verbatim", ""):
            stats["editorial_notes_cleaned"] += 1

        # 4. Remove OFF acronym from title, source, author
        for field in ["title", "source", "author"]:
            val = item.get(field)
            if val and "OFF" in val:
                item[field] = remove_off_acronym(val)
                stats["off_acronyms_replaced"] += 1

        # 5. Normalize country
        c = (item.get("country") or "fra").strip().lower()
        norm_c = COUNTRY_MAP.get(c, "fra")
        item["country"] = norm_c

        # 6. Granular media scope
        scope = determine_media_scope(item)
        item["media_scope"] = scope
        stats["scopes"][scope] = stats["scopes"].get(scope, 0) + 1

        # 7. Topic tags
        topics = determine_topics(item)
        item["topics"] = topics
        for t in topics:
            stats["topics"][t] = stats["topics"].get(t, 0) + 1

        # 8. Dead link marking
        is_dead = (p_id in KNOWN_DEAD_LINK_IDS)
        item["dead_link"] = is_dead
        if is_dead:
            stats["dead_links"] += 1

        # Write back YAML cleanly
        key_order = [
            "id", "date", "source", "title", "link", "domain",
            "type", "media_scope", "raw_type", "lang", "country",
            "author", "topic", "topics", "verbatim", "editorial_note",
            "dead_link", "selected", "origin"
        ]
        ordered = {}
        for k in key_order:
            if k in item:
                ordered[k] = item[k]
        for k, v in item.items():
            if k not in ordered:
                ordered[k] = v

        with open(fpath, "w", encoding="utf-8") as fp:
            yaml.dump(ordered, fp, allow_unicode=True, sort_keys=False, width=120)

    print("\n✅ Enrichment complete!")
    print(f"Fixed URLs: {stats['fixed_urls']}")
    print(f"Dead links tagged: {stats['dead_links']}")
    print(f"Editorial notes sanitized: {stats['editorial_notes_cleaned']}")
    print(f"OFF acronyms replaced: {stats['off_acronyms_replaced']}")
    print("\nMedia scopes:")
    for k, v in sorted(stats["scopes"].items()):
        print(f"  {k}: {v}")
    print("\nTopic distribution:")
    for k, v in sorted(stats["topics"].items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    enrich_press_items()
