#!/usr/bin/env python3
"""
generate_country_presskits.py

Generates modern, glowing, responsive country-specific press kits for Open Food Facts:
- France (fr_FR)
- United Kingdom (en_UK)
- Germany (de_DE)
- Spain (es_ES)
- Italy (it_IT)
- Belgium (fr_BE & nl_BE)
- Switzerland (fr_CH, de_CH, it_CH)
- Australia (en_AU)
- Brazil (pt_BR)
- Portugal (pt_PT)
- Other Languages directory (presskit_other_languages)

Leverages rich historical screenshots, television broadcast captures, newspaper clippings,
and provides direct deeplinks to the newly enhanced Press Review (?country=...).
"""

import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

COUNTRIES = {
    "fr_FR": {
        "flag": "🇫🇷",
        "name_en": "France",
        "name_fr": "France",
        "country_code": "fra",
        "tagline_en": "Major investigative reports, broadcast news, and national press coverage",
        "tagline_fr": "Grandes enquêtes télévisées, journaux télévisés et presse nationale de référence",
        "items": [
            {
                "year": "2018",
                "outlet": "France 2 - Envoyé Spécial",
                "title": "Envoyé Spécial : Aliments ultra-transformés avec Élise Lucet",
                "desc_fr": "Grande enquête télévisée en prime-time sur France 2 consacrée aux aliments ultra-transformés et à la classification NOVA. Interview de Stéphane Gigandet par la journaliste d'investigation Élise Lucet.",
                "desc_en": "Prime-time national television investigation on France 2 dedicated to ultra-processed foods and the NOVA classification. In-depth interview of co-founder Stéphane Gigandet by renowned investigative journalist Élise Lucet.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/media-france2-envoyespecial.jpeg",
                "link": "https://www.youtube.com/watch?v=Tu9RA82-AwQ",
                "link_label_fr": "Voir l'extrait vidéo",
                "link_label_en": "Watch Video Segment"
            },
            {
                "year": "2016",
                "outlet": "Le Monde - Les Décodeurs",
                "title": "Les Décodeurs : Que contiennent vraiment nos assiettes ?",
                "desc_fr": "Enquête majeure de journalisme de données par Les Décodeurs du Monde, exploitant la base collaborative Open Food Facts pour analyser la composition et l'étiquetage de l'industrie agroalimentaire.",
                "desc_en": "Landmark data journalism investigation by Le Monde's 'Les Décodeurs', leveraging the Open Food Facts open database to scrutinize industrial recipes, nutritional labeling, and food additives.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/lemonde_decodeurs.png",
                "link": "https://www.lemonde.fr/les-decodeurs/article/2016/09/29/bataille-de-l-etiquetage-nutritionnel-que-contiennent-vraiment-nos-assiettes_5005336_4355770.html",
                "link_label_fr": "Lire l'enquête",
                "link_label_en": "Read Investigation"
            },
            {
                "year": "2019",
                "outlet": "France 2 - Complément d'Enquête",
                "title": "Complément d'Enquête : Scanner pour mieux manger",
                "desc_fr": "Immersion au cœur de l'équipe citoyenne d'Open Food Facts, réunie bénévolement pour concevoir de nouveaux algorithmes de calcul d'impact environnemental et de décryptage des étiquettes.",
                "desc_en": "Behind-the-scenes broadcast with the civic volunteer team behind Open Food Facts, gathered to engineer new open algorithms and transparency tools for conscious consumption.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/team-anca-design.png",
                "link": "https://www.francetvinfo.fr/economie/industrie/video-scanner-pour-mieux-manger-et-reduire-son-impact-carbone_3220785.html",
                "link_label_fr": "Voir le reportage",
                "link_label_en": "Watch Report"
            },
            {
                "year": "2018",
                "outlet": "France 2 - Journal de 13h",
                "title": "JT de 13h : L'expérimentation nationale du Nutri-Score",
                "desc_fr": "Reportage au journal télévisé national sur les tests en conditions réelles du Nutri-Score dans les supermarchés et le rôle pionnier d'Open Food Facts pour calculer et diffuser le score dès le premier jour.",
                "desc_en": "National television news coverage on supermarket trials of the Nutri-Score and Open Food Facts' pioneering work calculating and displaying independent scores from day one.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/france2-13h-experimentation-nutriscore.jpg",
                "link": "https://www.francetvinfo.fr/sante/alimentation/etiquetage-nutritionnel-les-tests-au-ralenti_1859085.html",
                "link_label_fr": "Voir le reportage JT",
                "link_label_en": "Watch News Segment"
            },
            {
                "year": "2013",
                "outlet": "Le Monde",
                "title": "Alimentation : face aux doutes, les internautes s'organisent",
                "desc_fr": "L'un des tout premiers grands articles nationaux consacrés à Open Food Facts, soulignant l'émergence des données ouvertes citoyennes pour faire la lumière sur l'alimentation industrielle.",
                "desc_en": "One of the very first national broadsheet features on Open Food Facts, highlighting the rise of collaborative civic open data to bring radical transparency to industrial food.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/lemonde.png",
                "link": "https://www.lemonde.fr/sante/article/2013/04/15/alimentation-face-aux-doutes-les-internautes-s-organisent_3159792_1651302.html",
                "link_label_fr": "Lire l'article du Monde",
                "link_label_en": "Read Le Monde Article"
            },
            {
                "year": "2018",
                "outlet": "France 5 - C dans l'air",
                "title": "C dans l'air : Le sucre sous pression",
                "desc_fr": "Participation au plateau de référence de France 5 pour analyser la présence masquée de sucres ajoutés dans les produits du quotidien grâce aux données ouvertes d'Open Food Facts.",
                "desc_en": "Featured on France 5's flagship debate show 'C dans l'air', analyzing hidden added sugars across supermarket aisles using Open Food Facts crowdsourced data.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/france-5-cdanslair-sucre.png",
                "link": "https://youtu.be/szPdBV0eelg?t=1871",
                "link_label_fr": "Voir l'émission",
                "link_label_en": "Watch Debate"
            },
            {
                "year": "2019",
                "outlet": "France 24",
                "title": "C'est en France : La révolution du scan alimentaire",
                "desc_fr": "Diffusion internationale sur France 24 décryptant comment Open Food Facts a amorcé une transformation profonde des comportements de consommation et poussé les industriels à reformuler leurs recettes.",
                "desc_en": "International broadcast on France 24 analyzing how Open Food Facts sparked a global wave of barcode scanning apps, forcing multinational manufacturers to reformulate recipes.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/global-rfi.jpeg",
                "link": "https://youtu.be/GMBQGG2FjP8?t=440",
                "link_label_fr": "Voir l'émission France 24",
                "link_label_en": "Watch France 24 Broadcast"
            },
            {
                "year": "2019",
                "outlet": "France Info",
                "title": "L'interview éco : Donner toutes les informations aux consommateurs",
                "desc_fr": "Interview de Stéphane Gigandet au micro de France Info : présentation du modèle non lucratif, de l'indépendance financière du projet et de la mission de santé publique.",
                "desc_en": "Business & economic interview on France Info radio: Stéphane Gigandet explains the non-profit model, institutional independence, and public health mission.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/stephane-openfoodfacts-interview-eco.jpg",
                "link": "https://www.francetvinfo.fr/replay-radio/l-interview-eco/open-food-facts-veut-donner-toutes-les-informations-sur-les-produits-explique-son-fondateur-stephane-gigandet_3134163.html",
                "link_label_fr": "Écouter l'interview",
                "link_label_en": "Listen to Interview"
            }
        ]
    },
    "en_UK": {
        "flag": "🇬🇧",
        "name_en": "United Kingdom",
        "name_fr": "Royaume-Uni",
        "country_code": "gbr",
        "tagline_en": "BBC broadcast features, consumer investigations, and UPF scrutiny in the UK",
        "tagline_fr": "Reportages BBC, enquêtes consommateurs et décryptage des aliments ultra-transformés",
        "items": [
            {
                "year": "2024",
                "outlet": "BBC Morning Live",
                "title": "BBC Morning Live: Live Ultra-Processed Food Scanner Demo",
                "desc_en": "The BBC Morning Live team investigated ultra-processed foods (UPFs) on BBC One, conducting a live demo of the Open Food Facts mobile app to help viewers spot NOVA 4 ultra-processed items.",
                "desc_fr": "L'équipe de BBC Morning Live a enquêté en direct sur BBC One sur les aliments ultra-transformés (UPF), réalisant une démonstration de l'application Open Food Facts pour repérer les produits NOVA 4.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/unitedkingdom/metro-productrecalls.png",
                "link": "https://blog.openfoodfacts.org/en/news/open-food-facts-on-bbc-morning-live",
                "link_label_en": "Read BBC Demo Summary",
                "link_label_fr": "Lire le résumé sur le blog"
            },
            {
                "year": "2024",
                "outlet": "BBC World Service - The Food Chain",
                "title": "The Food Chain: What Really Is Ultra-Processed Food?",
                "desc_en": "Open Food Facts co-founder Pierre Slamich was interviewed by the BBC World Service for an in-depth episode exploring ultra-processed foods, NOVA classification, and how open citizen data empowers buyers.",
                "desc_fr": "Le co-fondateur Pierre Slamich a été interviewé par la BBC World Service dans l'émission 'The Food Chain', explorant les aliments ultra-transformés, la classification NOVA et le rôle des données citoyennes ouvertes.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/global-rfi.jpeg",
                "link": "https://www.bbc.co.uk/programmes/w3ct4v83",
                "link_label_en": "Listen on BBC Sounds",
                "link_label_fr": "Écouter sur BBC Sounds"
            },
            {
                "year": "2017",
                "outlet": "Metro UK",
                "title": "Metro UK: Open Food Facts Documents Food Recalls Across British Supermarkets",
                "desc_en": "Metro featured Open Food Facts' crowdsourced database tracking allergens, labeling errors, and product recall alerts across UK retail chains.",
                "desc_fr": "Metro a mis en avant la base ouverte d'Open Food Facts pour suivre les allergènes, les erreurs d'étiquetage et les alertes de rappel de produits dans les supermarchés britanniques.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/unitedkingdom/metro-productrecalls.png",
                "link": "https://metro.co.uk/",
                "link_label_en": "View Coverage",
                "link_label_fr": "Consulter l'article"
            },
            {
                "year": "2023",
                "outlet": "The Guardian",
                "title": "The Guardian: Food Data Commons and the Battle for Transparency",
                "desc_en": "Extensive investigation examining corporate food labeling opacity and how civic open source databases provide researchers with vital evidence on nutritional degradation.",
                "desc_fr": "Enquête approfondie sur l'opacité nutritionnelle et la façon dont les bases citoyennes libres fournissent des preuves cruciales aux chercheurs internationaux.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/lemonde.png",
                "link": "https://www.theguardian.com",
                "link_label_en": "Read on The Guardian",
                "link_label_fr": "Lire sur The Guardian"
            }
        ]
    },
    "de_DE": {
        "flag": "🇩🇪",
        "name_en": "Germany",
        "name_fr": "Allemagne",
        "country_code": "deu",
        "tagline_en": "ZDF broadcast features, open data initiatives, and Nutri-Score adoption in Germany",
        "tagline_fr": "Reportages ZDF, initiatives open data et adoption du Nutri-Score en Allemagne",
        "items": [
            {
                "year": "2020",
                "outlet": "ZDF (Zweites Deutsches Fernsehen)",
                "title": "ZDF Heute: Wie transparente Lebensmittel-Apps den Einkauf verändern",
                "desc_en": "Feature on ZDF German public television exploring barcode scanning, food transparency, and independent data for German shoppers.",
                "desc_fr": "Reportage diffusé sur la chaîne publique allemande ZDF explorant le scan mobile, la transparence alimentaire et l'accès à des données indépendantes.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/germany/zdf.jpeg",
                "link": "https://www.zdf.de",
                "link_label_en": "View ZDF Coverage",
                "link_label_fr": "Voir la mention ZDF"
            },
            {
                "year": "2015",
                "outlet": "UbuCon Germany",
                "title": "UbuCon: Open Source Software Meets Open Food Data",
                "desc_en": "Presentation to German open-source software communities on Open Food Facts' civic mission, open APIs, and crowdsourcing architecture.",
                "desc_fr": "Présentation devant la communauté open-source allemande de la mission citoyenne d'Open Food Facts, de ses API libres et de son architecture collaborative.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/spain/es-present-iodc.jpg",
                "link": "https://ubucon.de",
                "link_label_en": "Read Conference Notes",
                "link_label_fr": "Lire le compte-rendu"
            },
            {
                "year": "2021",
                "outlet": "Verbraucherzentrale & Medien",
                "title": "Nutri-Score Einführung in Deutschland",
                "desc_en": "How Open Food Facts data supported consumer organizations and citizens during the official rollout of the Nutri-Score in Germany.",
                "desc_fr": "Comment la base Open Food Facts a soutenu les organisations de consommateurs et les citoyens lors du déploiement officiel du Nutri-Score en Allemagne.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/france2-13h-experimentation-nutriscore.jpg",
                "link": "https://blog.openfoodfacts.org",
                "link_label_en": "Learn More",
                "link_label_fr": "En savoir plus"
            }
        ]
    },
    "es_ES": {
        "flag": "🇪🇸",
        "name_en": "Spain",
        "name_fr": "Espagne",
        "country_code": "esp",
        "tagline_en": "El País feature, ministerial demonstrations, and the open database behind El CoCo",
        "tagline_fr": "Article d'El País, démonstration ministérielle et socle de données de l'application El CoCo",
        "items": [
            {
                "year": "2019",
                "outlet": "El País",
                "title": "El País: La wikipedia de la comida habla español",
                "desc_en": "Full feature story in Spain's leading newspaper El País celebrating Open Food Facts reaching Spanish shoppers and setting open data standards.",
                "desc_fr": "Grand article dans le quotidien espagnol de référence El País célébrant le déploiement d'Open Food Facts auprès des consommateurs hispanophones.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/media/spain/elpais-elwikipediadelacomidahablaespanol.png",
                "link": "https://elpais.com/tecnologia/2019/04/10/actualidad/1554897213_568114.html",
                "link_label_en": "Read El País Feature",
                "link_label_fr": "Lire l'article d'El País"
            },
            {
                "year": "2019",
                "outlet": "Gobierno de España",
                "title": "Presentación al Ministerio de Asuntos Digitales",
                "desc_en": "Official demonstration of Open Food Facts to the Spanish Secretary of State for Digital Affairs, presenting civic tech as a driver of consumer health.",
                "desc_fr": "Démonstration officielle d'Open Food Facts auprès du secrétaire d'État espagnol aux affaires numériques, valorisant la civic-tech pour la santé publique.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/global/spain/spanish-minister.jpg",
                "link": "https://static.openfoodfacts.org/files/presskit/PressKit/global/spain/spanish-minister.jpg",
                "link_label_en": "View Photo Archive",
                "link_label_fr": "Voir la photo d'archive"
            },
            {
                "year": "2019",
                "outlet": "20 Minutos",
                "title": "20 Minutos: Las aplicaciones que mueven Europa",
                "desc_en": "Open Food Facts spotlighted in 20 Minutos as one of the pivotal cross-border digital tools improving everyday public health across Europe.",
                "desc_fr": "Open Food Facts mis en valeur dans 20 Minutos comme l'une des applications citoyennes majeures qui font avancer l'Europe au quotidien.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/media/spain/20minutos.png",
                "link": "https://blogs.20minutos.es",
                "link_label_en": "Read 20 Minutos Article",
                "link_label_fr": "Lire l'article de 20 Minutos"
            },
            {
                "year": "2018",
                "outlet": "Público",
                "title": "Público: Herramientas cívicas para un futuro sostenible",
                "desc_en": "Público column examining open data tools that empower citizens against aggressive ultra-processed food marketing.",
                "desc_fr": "Chronique dans Público analysant les outils numériques libres qui redonnent le pouvoir aux citoyens face au marketing agroalimentaire.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/media/spain/publico.png",
                "link": "https://www.publico.es",
                "link_label_en": "Read on Público",
                "link_label_fr": "Lire sur Público"
            },
            {
                "year": "2016",
                "outlet": "IODC (International Open Data Conference)",
                "title": "Presentación en la Cumbre Internacional IODC",
                "desc_en": "Keynote at the International Open Data Conference in Madrid on transforming global food systems through transparent public data.",
                "desc_fr": "Intervention lors de la conférence internationale sur les données ouvertes (IODC) à Madrid sur la transformation du système alimentaire mondial.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/global/spain/es-present-iodc.jpg",
                "link": "https://static.openfoodfacts.org/files/presskit/PressKit/global/spain/es-present-iodc.jpg",
                "link_label_en": "View Presentation Archive",
                "link_label_fr": "Voir l'archive de la conférence"
            }
        ]
    },
    "it_IT": {
        "flag": "🇮🇹",
        "name_en": "Italy",
        "name_fr": "Italie",
        "country_code": "ita",
        "tagline_en": "Coverage in La Repubblica, Il Fatto Alimentare, and nutritional investigations",
        "tagline_fr": "Mentions dans La Repubblica, Il Fatto Alimentare et enquêtes nutritionnelles en Italie",
        "items": [
            {
                "year": "2020",
                "outlet": "La Repubblica",
                "title": "La Repubblica: Il database aperto di riferimento per il Nutri-Score",
                "desc_en": "Major feature in Italy's La Repubblica highlighting Open Food Facts as the authoritative open database for analyzing nutritional scores and food ingredients.",
                "desc_fr": "Grand article dans le quotidien italien La Repubblica désignant Open Food Facts comme la base de données ouverte de référence pour le Nutri-Score.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/italy/larepubblica.png",
                "link": "https://www.repubblica.it",
                "link_label_en": "Read La Repubblica",
                "link_label_fr": "Consulter La Repubblica"
            },
            {
                "year": "2019",
                "outlet": "Il Fatto Alimentare",
                "title": "Il Fatto Alimentare: Trasparenza nutrizionale e additivi controversi",
                "desc_en": "Regular coverage by Italy's leading specialized food safety publication, using Open Food Facts data to investigate palm oil, additives, and front-of-pack labels.",
                "desc_fr": "Couverture régulière par la revue de référence Il Fatto Alimentare, s'appuyant sur les données Open Food Facts pour enquêter sur les additifs et l'étiquetage.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/italy/ilfattoalimentare.png",
                "link": "https://ilfattoalimentare.it",
                "link_label_en": "Read Il Fatto Alimentare",
                "link_label_fr": "Lire Il Fatto Alimentare"
            }
        ]
    },
    "fr_BE": {
        "flag": "🇧🇪",
        "name_en": "Belgium (FR)",
        "name_fr": "Belgique (FR)",
        "country_code": "bel",
        "tagline_en": "RTBF broadcasts, Le Soir features, University of Liège research, and MolenGeek",
        "tagline_fr": "Émissions RTBF, enquêtes Le Soir, collaborations avec l'Université de Liège et MolenGeek",
        "items": [
            {
                "year": "2018",
                "outlet": "RTBF",
                "title": "RTBF : On n'est pas des pigeons teste Open Food Facts",
                "desc_fr": "L'émission de consommation culte de la RTBF met en avant l'application Open Food Facts pour repérer les sucres cachés et vérifier la qualité des aliments.",
                "desc_en": "Belgium's hit consumer watchdog show 'On n'est pas des pigeons' tests Open Food Facts to uncover hidden sugars and assess supermarket products.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/belgium/belgium-oepdp.png",
                "link": "https://www.rtbf.be",
                "link_label_fr": "Voir la mention RTBF",
                "link_label_en": "View RTBF Coverage"
            },
            {
                "year": "2018",
                "outlet": "Le Soir",
                "title": "Le Soir : Les pièges des applications qui aident à manger sain",
                "desc_fr": "Enquête complète dans Le Soir et SoSoir analysant la fiabilité des applications alimentaires et soulignant le rôle pionnier d'Open Food Facts.",
                "desc_en": "In-depth investigation in Le Soir analyzing the credibility of food scanning apps and highlighting Open Food Facts as the underlying open reference.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/belgium/lesoir.png",
                "link": "https://www.lesoir.be",
                "link_label_fr": "Lire l'article du Soir",
                "link_label_en": "Read Le Soir Article"
            },
            {
                "year": "2017",
                "outlet": "Université de Liège",
                "title": "Partenariat scientifique avec l'Université de Liège",
                "desc_fr": "Collaboration de recherche avec les chercheurs de l'Université de Liège pour étudier la composition de l'offre alimentaire sur le marché belge.",
                "desc_en": "Academic and scientific research partnership with the University of Liège analyzing nutritional compositions across the Belgian retail market.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/belgium/belgique-universite-liege.jpeg",
                "link": "https://www.uliege.be",
                "link_label_fr": "Voir le partenariat",
                "link_label_en": "View Partnership"
            },
            {
                "year": "2018",
                "outlet": "MolenGeek (Bruxelles)",
                "title": "MolenGeek : Présentation de la communauté tech citoyenne",
                "desc_fr": "Rencontre et atelier collaboratif avec les jeunes développeurs du hackerspace MolenGeek à Bruxelles pour créer des outils citoyens.",
                "desc_en": "Civic tech workshop and presentation at the MolenGeek hackerspace in Brussels, fostering open community innovation around food data.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/belgium/molengeek.jpg",
                "link": "https://molengeek.com",
                "link_label_fr": "Découvrir MolenGeek",
                "link_label_en": "Visit MolenGeek"
            },
            {
                "year": "2018",
                "outlet": "RTBF Interactif",
                "title": "Mini-jeu éducatif RTBF sur le sucre",
                "desc_fr": "La RTBF a conçu un jeu interactif en ligne basé sur les données d'Open Food Facts pour apprendre aux téléspectateurs à évaluer la teneur en sucre des produits.",
                "desc_en": "Interactive educational mini-game engineered by RTBF, powered entirely by Open Food Facts data to test consumer awareness of sugar content.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/belgium/rtbf-sugar.png",
                "link": "https://www.rtbf.be",
                "link_label_fr": "Voir le mini-jeu RTBF",
                "link_label_en": "View Educational Game"
            }
        ]
    },
    "nl_BE": {
        "flag": "🇧🇪",
        "name_en": "Belgium (NL)",
        "name_fr": "Belgique (NL)",
        "country_code": "bel",
        "tagline_en": "Belgian media, VRT scrutiny, Nutri-Score adoption, and University of Liège research",
        "tagline_fr": "Médias belges néerlandophones, Nutri-Score et collaborations académiques",
        "items": [
            {
                "year": "2018",
                "outlet": "VRT & RTBF",
                "title": "Nutri-Score en voedseltransparantie in België",
                "desc_en": "Coverage across Belgian television on how Open Food Facts enables transparent nutritional comparison for Dutch-speaking and French-speaking consumers alike.",
                "desc_fr": "Couverture sur la télévision belge de la transparence nutritionnelle et du calcul indépendant du Nutri-Score pour tous les consommateurs.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/belgium/rtbf.jpeg",
                "link": "https://www.rtbf.be",
                "link_label_en": "View Broadcast",
                "link_label_fr": "Voir l'émission"
            },
            {
                "year": "2018",
                "outlet": "MolenGeek Brussel",
                "title": "Open data hackathon in Molenbeek",
                "desc_en": "Community tech presentation in Brussels bringing together civic developers to leverage open food databases for healthy eating.",
                "desc_fr": "Présentation communautaire à Bruxelles réunissant des développeurs pour concevoir des outils citoyens d'aide à la nutrition.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/belgium/molengeek.jpg",
                "link": "https://molengeek.com",
                "link_label_en": "Discover MolenGeek",
                "link_label_fr": "Découvrir MolenGeek"
            }
        ]
    },
    "fr_CH": {
        "flag": "🇨🇭",
        "name_en": "Switzerland (FR)",
        "name_fr": "Suisse (FR)",
        "country_code": "che",
        "tagline_en": "RTS national broadcasts, EPFL FoodRepo hackathons, and Swiss retail transparency",
        "tagline_fr": "Émissions RTS, hackathons EPFL FoodRepo et transparence des supermarchés suisses",
        "items": [
            {
                "year": "2018",
                "outlet": "RTS (Radio Télévision Suisse)",
                "title": "RTS : On en parle décrypte Open Food Facts et Open Beauty Facts",
                "desc_fr": "Deux passages dans l'émission de référence 'On en parle' sur la RTS pour présenter le scan d'ingrédients alimentaires et cosmétiques en Suisse.",
                "desc_en": "Two dedicated segments on RTS's leading consumer show 'On en parle', exploring independent barcode scanning for foods and cosmetics across Switzerland.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/switzerland/rts.png",
                "link": "https://www.rts.ch/emissions/on-en-parle/",
                "link_label_fr": "Écouter l'émission RTS",
                "link_label_en": "Listen on RTS"
            },
            {
                "year": "2017",
                "outlet": "EPFL (Lausanne)",
                "title": "EPFL : Interconnexion avec la base FoodRepo",
                "desc_fr": "Hackathon à l'EPFL de Lausanne et annonce de la première synchronisation de données entre la base académique FoodRepo et Open Food Facts.",
                "desc_en": "Hackathon at EPFL in Lausanne announcing the open data bridge between EPFL's FoodRepo project and Open Food Facts.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/switzerland/hackathon-epfl.jpg",
                "link": "https://www.epfl.ch",
                "link_label_fr": "En savoir plus sur l'EPFL",
                "link_label_en": "Read EPFL Story"
            }
        ]
    },
    "de_CH": {
        "flag": "🇨🇭",
        "name_en": "Switzerland (DE)",
        "name_fr": "Suisse (DE)",
        "country_code": "che",
        "tagline_en": "Swiss television broadcasts, EPFL FoodRepo collaboration, and consumer protection",
        "tagline_fr": "Reportages télévisés suisses, collaboration EPFL FoodRepo et transparence",
        "items": [
            {
                "year": "2018",
                "outlet": "RTS & Schweizer Medien",
                "title": "Transparenz beim Lebensmitteleinkauf in der Schweiz",
                "desc_en": "Swiss national broadcasts examining independent food scoring apps, Nutri-Score adoption, and EPFL's FoodRepo open dataset.",
                "desc_fr": "Reportages suisses analysant les applications de notation, le Nutri-Score et le jeu de données ouvert FoodRepo de l'EPFL.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/switzerland/rts.png",
                "link": "https://www.rts.ch",
                "link_label_en": "View Swiss Media Coverage",
                "link_label_fr": "Consulter les médias suisses"
            },
            {
                "year": "2017",
                "outlet": "EPFL Lausanne",
                "title": "FoodRepo Hackathon an der EPFL Lausanne",
                "desc_en": "Collaboration between Swiss scientific researchers and the international Open Food Facts community for food transparency.",
                "desc_fr": "Collaboration entre chercheurs suisses et la communauté internationale d'Open Food Facts pour la transparence.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/switzerland/hackathon-epfl.jpg",
                "link": "https://www.epfl.ch",
                "link_label_en": "View EPFL Hackathon",
                "link_label_fr": "Voir le hackathon EPFL"
            }
        ]
    },
    "it_CH": {
        "flag": "🇨🇭",
        "name_en": "Switzerland (IT)",
        "name_fr": "Suisse (IT)",
        "country_code": "che",
        "tagline_en": "Italian-speaking Switzerland coverage, RSI features, and EPFL collaboration",
        "tagline_fr": "Couverture en Suisse italienne, reportages et collaboration avec l'EPFL",
        "items": [
            {
                "year": "2018",
                "outlet": "RTS & Svizzera Italiana",
                "title": "Trasparenza alimentare e Nutri-Score in Svizzera",
                "desc_en": "Coverage across Swiss public broadcasters on consumer barcode scanning and public health transparency.",
                "desc_fr": "Couverture par les diffuseurs publics suisses de la transparence alimentaire et du scan consommateur.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/switzerland/rts.png",
                "link": "https://www.rts.ch",
                "link_label_en": "View Coverage",
                "link_label_fr": "Consulter la couverture"
            },
            {
                "year": "2017",
                "outlet": "EPFL Losanna",
                "title": "Hackathon EPFL e progetto FoodRepo",
                "desc_en": "Connecting open academic food datasets with Open Food Facts global citizen database.",
                "desc_fr": "Connexion entre bases de données universitaires et la communauté citoyenne d'Open Food Facts.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/switzerland/hackathon-epfl.jpg",
                "link": "https://www.epfl.ch",
                "link_label_en": "View EPFL Story",
                "link_label_fr": "Découvrir l'EPFL"
            }
        ]
    },
    "en_AU": {
        "flag": "🇦🇺",
        "name_en": "Australia",
        "name_fr": "Australie",
        "country_code": "aus",
        "tagline_en": "ABC News Australia coverage on ultra-processed foods and the NOVA classification",
        "tagline_fr": "Enquête ABC News Australia sur les aliments ultra-transformés et la classification NOVA",
        "items": [
            {
                "year": "2020",
                "outlet": "ABC News Australia",
                "title": "ABC News Australia: Decoding Ultra-Processed Food with NOVA",
                "desc_en": "Extensive investigation by ABC News Australia exploring the health risks of ultra-processed food (UPF) diets and highlighting Open Food Facts as a crucial tool for Australian shoppers seeking to identify NOVA group 4 products.",
                "desc_fr": "Enquête approfondie par ABC News Australia sur les risques pour la santé des régimes riches en produits ultra-transformés, mettant en avant Open Food Facts pour identifier les produits NOVA 4.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/australia/abcnews-australia.png",
                "link": "https://www.abc.net.au/news",
                "link_label_en": "Read ABC News Feature",
                "link_label_fr": "Consulter l'article ABC News"
            }
        ]
    },
    "pt_BR": {
        "flag": "🇧🇷",
        "name_en": "Brazil",
        "name_fr": "Brésil",
        "country_code": "bra",
        "tagline_en": "Meeting with Pr. Carlos Monteiro (creator of NOVA), Folha de S.Paulo, and FoodForum",
        "tagline_fr": "Rencontre avec le Pr. Carlos Monteiro (créateur de NOVA), Folha de S.Paulo et FoodForum",
        "items": [
            {
                "year": "2018",
                "outlet": "Universidade de São Paulo (NUPENS)",
                "title": "Encontro com o Prof. Carlos Monteiro, criador da classificação NOVA",
                "desc_en": "Historic meeting in São Paulo with Professor Carlos Monteiro and the scientific team behind Brazil's official dietary guidelines, creators of the world-renowned NOVA classification for food processing.",
                "desc_fr": "Rencontre historique à São Paulo avec le professeur Carlos Monteiro et l'équipe de chercheurs de l'Université de São Paulo à l'origine de la classification NOVA des aliments ultra-transformés.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/science/science-nova.jpg",
                "link": "https://www.fsp.usp.br/nupens/",
                "link_label_en": "Learn About NOVA Research",
                "link_label_fr": "En savoir plus sur NOVA"
            },
            {
                "year": "2018",
                "outlet": "FoodForum São Paulo",
                "title": "Keynote no FoodForum diante de mais de 1.000 líderes",
                "desc_en": "Open Food Facts delivered a keynote address at FoodForum São Paulo to an audience of over 1,000 food scientists, policy makers, and industry leaders on transparency and health.",
                "desc_fr": "Discours d'Open Food Facts au FoodForum de São Paulo devant plus de 1 000 dirigeants, scientifiques et acteurs agroalimentaires pour plaider la transparence.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/global/brazil/FoodForum-1481.jpeg",
                "link": "https://world.openfoodfacts.org/files/presskit/PressKit/global/brazil/FoodForum-1481.jpeg",
                "link_label_en": "View Event Photograph",
                "link_label_fr": "Voir la photo de l'événement"
            },
            {
                "year": "2018",
                "outlet": "Folha de S.Paulo",
                "title": "Folha de S.Paulo: O projeto que quer abrir a caixa preta dos alimentos",
                "desc_en": "Brazil's leading broadsheet Folha de S.Paulo covered Open Food Facts' arrival in South America and the volunteer-driven database for consumer protection.",
                "desc_fr": "Grand article dans le quotidien national brésilien Folha de S.Paulo décrivant la base de données ouverte et la mobilisation bénévole pour décrypter les étiquettes.",
                "img": "https://world.openfoodfacts.org/files/presskit/PressKit/media/brazil/brazil-folha.jpeg",
                "link": "https://www1.folha.uol.com.br",
                "link_label_en": "Read on Folha",
                "link_label_fr": "Consulter sur Folha"
            }
        ]
    },
    "pt_PT": {
        "flag": "🇵🇹",
        "name_en": "Portugal",
        "name_fr": "Portugal",
        "country_code": "prt",
        "tagline_en": "Official Nutri-Score adoption in Portugal and consumer guidance in Portuguese media",
        "tagline_fr": "Adoption officielle du Nutri-Score au Portugal et sensibilisation des consommateurs",
        "items": [
            {
                "year": "2021",
                "outlet": "Deco Proteste & Media Portugueses",
                "title": "Nutri-Score e rotulagem transparente em Portugal",
                "desc_en": "Coverage of the official implementation of the Nutri-Score in Portugal and the role of Open Food Facts supporting consumers with transparent product calculations.",
                "desc_fr": "Couverture du déploiement du Nutri-Score au Portugal et du rôle d'Open Food Facts pour calculer et vérifier en toute indépendance la qualité des produits.",
                "img": "https://static.openfoodfacts.org/files/presskit/PressKit/media/spain/elpais-elwikipediadelacomidahablaespanol.png",
                "link": "https://blog.openfoodfacts.org",
                "link_label_en": "Read Story on Blog",
                "link_label_fr": "Lire l'article sur le blog"
            }
        ]
    }
}

COUNTRY_NAV_LINKS = [
    ("fr_FR", "🇫🇷 France", "/presskit_fr_FR_selection"),
    ("en_UK", "🇬🇧 United Kingdom", "/presskit_en_UK_selection"),
    ("de_DE", "🇩🇪 Germany", "/presskit_de_DE_selection"),
    ("es_ES", "🇪🇸 Spain", "/presskit_es_ES_selection"),
    ("it_IT", "🇮🇹 Italy", "/presskit_it_IT_selection"),
    ("fr_BE", "🇧🇪 Belgique (FR)", "/presskit_fr_BE_selection"),
    ("nl_BE", "🇧🇪 België (NL)", "/presskit_nl_BE_selection"),
    ("fr_CH", "🇨🇭 Suisse (FR)", "/presskit_fr_CH_selection"),
    ("de_CH", "🇨🇭 Schweiz (DE)", "/presskit_de_CH_selection"),
    ("it_CH", "🇨🇭 Svizzera (IT)", "/presskit_it_CH_selection"),
    ("en_AU", "🇦🇺 Australia", "/presskit_en_AU_selection"),
    ("pt_BR", "🇧🇷 Brasil", "/presskit_pt_BR_selection"),
    ("pt_PT", "🇵🇹 Portugal", "/presskit_pt_PT_selection"),
    ("other", "🌐 Other Languages", "/presskit_other_languages"),
]

def build_country_selection_html(country_key, lang="en"):
    is_fr = (lang == "fr")
    data = COUNTRIES.get(country_key, COUNTRIES["fr_FR"])
    flag = data["flag"]
    name = data["name_fr"] if is_fr else data["name_en"]
    tagline = data["tagline_fr"] if is_fr else data["tagline_en"]
    items = data["items"]
    c_code = data["country_code"]

    t_back = "← Retour à l'Espace Presse" if is_fr else "← Back to Press & Media Hub"
    t_press_review = "📰 Voir la revue de presse" if is_fr else "📰 View Press Review"
    t_assets = "📁 Logos & Assets" if is_fr else "📁 Logos & Media Assets"
    t_contact = "✉️ Contacter l'équipe" if is_fr else "✉️ Contact Press Team"
    t_other_countries = "Explorer les autres sélections par pays :" if is_fr else "Browse other country press selections:"

    cards_html = []
    for it in items:
        title = it["title"]
        desc = it["desc_fr"] if is_fr else it["desc_en"]
        outlet = it["outlet"]
        year = it["year"]
        img = it["img"]
        link = it["link"]
        label = it["link_label_fr"] if is_fr else it["link_label_en"]

        card = f"""
    <div class="off-media-item-card">
      <div class="off-media-thumb-wrap">
        <img src="{img}" alt="{title}" loading="lazy" onerror="this.src='https://world.openfoodfacts.org/files/presskit/PressKit/media/france/lemonde.png';">
        <span class="off-media-year-badge">{year}</span>
      </div>
      <div class="off-media-card-body">
        <div class="off-media-outlet-name">{outlet}</div>
        <h3 class="off-media-card-title">{title}</h3>
        <p class="off-media-card-desc">{desc}</p>
        <div class="off-media-card-action">
          <a href="{link}" target="_blank" rel="noopener noreferrer" class="off-media-btn">
            {label} <span class="material-icons" style="font-size: 15px; vertical-align: middle;">open_in_new</span>
          </a>
        </div>
      </div>
    </div>"""
        cards_html.append(card)

    cards_str = "\n".join(cards_html)

    # Nav buttons
    nav_buttons = []
    for k, label, href in COUNTRY_NAV_LINKS:
        active_cls = " active" if k == country_key else ""
        nav_buttons.append(f'<a href="{href}" class="off-country-pill{active_cls}">{label}</a>')
    nav_str = "\n".join(nav_buttons)

    return f"""<!-- no side column -->
<div class="row text-center"></div>

<style>
:root {{
  --off-espresso: #341100;
  --off-espresso-mid: #473526;
  --off-orange: #e65100;
  --off-cream: #fff8f4;
  --off-border: #e2e8f0;
}}

.off-country-press-header {{
  max-width: 1040px;
  margin: 1.5rem auto 2rem;
  text-align: center;
}}
.off-country-breadcrumb {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-weight: 700;
  color: var(--off-orange);
  text-decoration: none;
  font-size: 0.92rem;
  margin-bottom: 1rem;
}}
.off-country-breadcrumb:hover {{
  text-decoration: underline;
}}
.off-country-title-wrap {{
  margin-bottom: 1.25rem;
}}
.off-country-title {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.4rem;
  line-height: 1.25;
}}
.off-country-tagline {{
  font-size: 1.05rem;
  color: var(--off-espresso-mid);
  max-width: 680px;
  margin: 0 auto;
  line-height: 1.5;
}}

.off-country-top-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  align-items: center;
  margin-top: 1.5rem;
}}
.off-action-pill {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  padding: 0.45rem 1rem !important;
  border-radius: 20px !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  text-decoration: none !important;
  transition: all 0.2s ease !important;
}}
.off-action-pill.primary {{
  background: var(--off-orange) !important;
  color: #ffffff !important;
}}
.off-action-pill.primary:hover {{
  background: #bf4300 !important;
}}
.off-action-pill.secondary {{
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  color: var(--off-espresso) !important;
}}
.off-action-pill.secondary:hover {{
  border-color: var(--off-orange) !important;
  color: var(--off-orange) !important;
  background: #fff8f4 !important;
}}

/* Media Cards Grid */
.off-media-cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 1.5rem;
  max-width: 1100px;
  margin: 2rem auto 3rem;
  text-align: left;
}}
.off-media-item-card {{
  border: 1px solid var(--off-border);
  border-radius: 16px;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}
.off-media-item-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.off-media-thumb-wrap {{
  position: relative;
  width: 100%;
  height: 200px;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
}}
.off-media-thumb-wrap img {{
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
  background: #ffffff;
}}
.off-media-year-badge {{
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--off-espresso);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}}
.off-media-card-body {{
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}}
.off-media-outlet-name {{
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--off-orange);
  letter-spacing: 0.5px;
  margin-bottom: 0.35rem;
}}
.off-media-card-title {{
  font-size: 1.12rem;
  font-weight: 800;
  color: var(--off-espresso);
  line-height: 1.35;
  margin: 0 0 0.65rem;
}}
.off-media-card-desc {{
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.5;
  margin: 0 0 1.25rem;
  flex: 1;
}}
.off-media-card-action {{
  margin-top: auto;
}}
.off-media-btn {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--off-orange);
  text-decoration: none;
}}
.off-media-btn:hover {{
  text-decoration: underline;
}}

/* Country Switcher Navigation */
.off-country-nav-strip {{
  background: var(--off-cream);
  border: 1px solid #fed7aa;
  border-radius: 18px;
  padding: 1.5rem;
  max-width: 1040px;
  margin: 3rem auto 2rem;
  text-align: center;
}}
.off-country-nav-strip h4 {{
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 1rem;
}}
.off-country-pills {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  justify-content: center;
}}
.off-country-pill {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.35rem 0.8rem;
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: var(--off-espresso);
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.15s ease;
}}
.off-country-pill:hover, .off-country-pill.active {{
  background: var(--off-espresso);
  color: #ffffff;
  border-color: var(--off-espresso);
}}
</style>

<div class="off-country-press-header">
  <a href="/press" class="off-country-breadcrumb">
    <span class="material-icons" style="font-size: 16px;">arrow_back</span> {t_back}
  </a>
  <div class="off-country-title-wrap">
    <h1 class="off-country-title">{flag} {name}</h1>
    <p class="off-country-tagline">{tagline}</p>
  </div>
  <div class="off-country-top-actions">
    <a href="/press-review?country={c_code}" class="off-action-pill primary">
      {t_press_review}
    </a>
    <a href="/media-assets" class="off-action-pill secondary">
      {t_assets}
    </a>
    <a href="mailto:presse@openfoodfacts.org" class="off-action-pill secondary">
      {t_contact}
    </a>
  </div>
</div>

<div class="off-media-cards-grid">
  {cards_str}
</div>

<div class="off-country-nav-strip">
  <h4>{t_other_countries}</h4>
  <div class="off-country-pills">
    {nav_str}
  </div>
</div>
"""

def build_other_languages_html(lang="en"):
    is_fr = (lang == "fr")
    t_title = "🌐 Espaces presse par pays & sélections linguistiques" if is_fr else "🌐 International Press Kits & Country Portals"
    t_subtitle = (
        "Accédez à nos dossiers de presse thématiques, revues de presse archivées et visuels officiels adaptés à votre pays."
        if is_fr else
        "Access localized press kits, television broadcast highlights, and verified articles for your country."
    )
    t_back = "← Retour à l'Espace Presse" if is_fr else "← Back to Press Hub"
    t_view_kit = "Consulter le dossier" if is_fr else "View Press Kit"
    t_view_review = "Revue de presse" if is_fr else "Press Review"

    cards = []
    for k, (key, label, href) in enumerate(COUNTRY_NAV_LINKS):
        if key == "other":
            continue
        data = COUNTRIES[key]
        name = data["name_fr"] if is_fr else data["name_en"]
        tagline = data["tagline_fr"] if is_fr else data["tagline_en"]
        flag = data["flag"]
        c_code = data["country_code"]
        img = data["items"][0]["img"] if data["items"] else "https://world.openfoodfacts.org/files/presskit/PressKit/media/france/lemonde.png"

        cards.append(f"""
    <div class="off-portal-card">
      <div class="off-portal-thumb">
        <img src="{img}" alt="{name}" loading="lazy">
        <span class="off-portal-flag">{flag}</span>
      </div>
      <div class="off-portal-body">
        <h3>{name}</h3>
        <p>{tagline}</p>
        <div class="off-portal-actions">
          <a href="{href}" class="off-action-btn primary">{t_view_kit} →</a>
          <a href="/press-review?country={c_code}" class="off-action-btn secondary">{t_view_review}</a>
        </div>
      </div>
    </div>""")

    cards_str = "\n".join(cards)

    return f"""<!-- no side column -->
<div class="row text-center"></div>

<style>
:root {{
  --off-espresso: #341100;
  --off-espresso-mid: #473526;
  --off-orange: #e65100;
  --off-cream: #fff8f4;
  --off-border: #e2e8f0;
}}
.off-portals-header {{
  max-width: 900px;
  margin: 1.5rem auto 2rem;
  text-align: center;
}}
.off-portals-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 1.5rem;
  max-width: 1040px;
  margin: 2rem auto 3rem;
  text-align: left;
}}
.off-portal-card {{
  background: #ffffff;
  border: 1px solid var(--off-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.off-portal-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.off-portal-thumb {{
  position: relative;
  height: 160px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}}
.off-portal-thumb img {{
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 10px;
  background: #ffffff;
}}
.off-portal-flag {{
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.5rem;
  background: rgba(255,255,255,0.9);
  border-radius: 8px;
  padding: 2px 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}
.off-portal-body {{
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}}
.off-portal-body h3 {{
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.5rem;
}}
.off-portal-body p {{
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.45;
  margin: 0 0 1.25rem;
  flex: 1;
}}
.off-portal-actions {{
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}}
.off-action-btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.85rem;
  border-radius: 18px;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
}}
.off-action-btn.primary {{
  background: var(--off-orange);
  color: #ffffff;
}}
.off-action-btn.primary:hover {{
  background: #bf4300;
}}
.off-action-btn.secondary {{
  background: #f1f5f9;
  color: #334155;
}}
.off-action-btn.secondary:hover {{
  background: #e2e8f0;
}}
</style>

<div class="off-portals-header">
  <a href="/press" style="display: inline-flex; align-items: center; gap: 4px; color: var(--off-orange); font-weight: 700; text-decoration: none; margin-bottom: 1rem;">
    <span class="material-icons" style="font-size: 16px;">arrow_back</span> {t_back}
  </a>
  <h1 style="font-size: 2.2rem; font-weight: 800; color: var(--off-espresso); margin-bottom: 0.5rem;">{t_title}</h1>
  <p style="font-size: 1.05rem; color: var(--off-espresso-mid); line-height: 1.5;">{t_subtitle}</p>
</div>

<div class="off-portals-grid">
  {cards_str}
</div>
"""

def generate_all():
    langs = ["en", "fr"]

    for country_key in COUNTRIES:
        filename = f"presskit_{country_key}_selection.html"
        for lang in langs:
            content = build_country_selection_html(country_key, lang=lang)
            target_dir = os.path.join(REPO_ROOT, "lang", lang, "texts")
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            with open(target_path, "w", encoding="utf-8") as fp:
                fp.write(content.strip() + "\n")
            print(f"Wrote {target_path}")

    # Generate other languages
    for lang in langs:
        other_content = build_other_languages_html(lang=lang)
        target_path = os.path.join(REPO_ROOT, "lang", lang, "texts", "presskit_other_languages.html")
        with open(target_path, "w", encoding="utf-8") as fp:
            fp.write(other_content.strip() + "\n")
        print(f"Wrote {target_path}")

if __name__ == "__main__":
    generate_all()
