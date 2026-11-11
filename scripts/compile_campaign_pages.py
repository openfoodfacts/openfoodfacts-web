#!/usr/bin/env python3
"""
Compilation script for Open Food Facts Historical Campaign & Mission Pages:
- Opération Sodas (`operation-sodas.html`)
- What's in my yogurt? (`whats-in-my-yogurt.html`)
- What's in my shampoo? (`whats-in-my-shampoo.html`)

Generates:
1. `lang/en/texts/<slug>.html` (World/English Product Opener text fragment)
2. `lang/fr/texts/<slug>.html` (French Product Opener text fragment)
3. `<slug>.html` (Standalone root HTML5 preview page with navigation)
"""

import json
import os
import sys

# Ensure vendor path for yaml
try:
    from i18n_utils import ensure_vendor_path, get_localized_field, SUPPORTED_LANGUAGES
    ensure_vendor_path()
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from i18n_utils import ensure_vendor_path, get_localized_field, SUPPORTED_LANGUAGES
    ensure_vendor_path()

import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")

SODAS_TRANSLATIONS = {
    "fr": {
        "eyebrow": "🚀 Première Opération Thématique • Juin 2012",
        "title": "Opération Sodas",
        "lead": "Du 18 au 24 juin 2012, les premiers contributeurs d'Open Food Facts ont uni leurs forces pour collecter, photographier et analyser 150 boissons gazeuses et sucrées à travers la France. Une aventure pionnière qui a donné naissance aux premiers graphiques interactifs et prouvé la puissance des données ouvertes pour la santé publique.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Sodas Décryptés",
        "stat_sodas_sub": "Colas, limonades, tonics, thés glacés",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Pionniers Mobilisés",
        "stat_contrib_sub": "En rayon, en ligne & à Nantes",
        "stat_viz_num": "1er",
        "stat_viz_lbl": "Graphique Interactif",
        "stat_viz_sub": "Fonctionnalité en 3 clics",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Contexte Fiscal & Santé",
        "stat_tax_sub": "Lancement de la taxe soda",
        "ctx_title": "Aux origines de l'opération : faire parler les étiquettes",
        "ctx_p1": "Open Food Facts a été lancé publiquement le 19 mai 2012. Dès les premières semaines, une question s'est imposée : à quoi peuvent servir concrètement des données alimentaires ouvertes ? Fin 2011 et début 2012, les débats parlementaires sur la « taxe soda » (entrée en vigueur le 1er janvier 2012) battaient leur plein. Mais au-delà de la célèbre canette rouge et blanche, de quoi sont réellement composés les milliers de sodas vendus en France ?",
        "ctx_p2": "L'Opération Sodas a été le premier banc d'essai collaboratif pour tester la réactivité de la communauté naissante, mobiliser des data journalistes et concevoir des outils d'exploration visuelle innovants.",
        "inq_title": "Les 5 Grandes Questions Citoyennes Posées en Rayon",
        "chart_title": "La Naissance des « Graphiques en 3 Clics »",
        "chart_lead": "L'un des apports majeurs de l'Opération Sodas a été le développement d'un générateur dynamique de nuages de points (scatter plots), permettant de croiser n'importe quel nutriment avec le nombre d'additifs.",
        "chart_caption": "Graphique historique croisant sucres et nombre d'additifs dans les sodas (Open Food Facts, juin 2012)",
        "chart_cta": "Exécuter la requête en direct sur Open Food Facts &rarr;",
        "media_title": "Écho Médiatique & Partenaires Pionniers",
        "media_lead": "Dès 2012, journalistes de données et spécialistes de santé se sont emparés des premiers jeux de données d'Open Food Facts :",
        "legacy_title": "De l'Opération Sodas à 3,8 millions de produits",
        "legacy_desc": "Opération Sodas a été l'étincelle qui a démontré que la foule citoyenne pouvait cartographier une catégorie alimentaire complète en quelques jours. Cette méthode a ensuite inspiré <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016), et l'ensemble des Scan Parties qui se déroulent aujourd'hui dans toute l'Europe.",
        "btn_scan_party": "Découvrir les Scan Parties d'aujourd'hui",
        "btn_add_product": "Ajouter une boisson à la base",
    },
    "de": {
        "eyebrow": "🚀 Erste thematische Datenkampagne • Juni 2012",
        "title": "Aktion Limonaden (Opération Sodas)",
        "lead": "Vom 18. bis 24. Juni 2012 bündelten die ersten Mitwirkenden von Open Food Facts ihre Kräfte, um 150 kohlensäurehaltige und gezuckerte Getränke in ganz Frankreich zu fotografieren, zu erfassen und zu analysieren. Eine wegweisende Pionierkampagne, aus der die ersten interaktiven 3-Klick-Grafiken hervorgingen und die den Nutzen offener Lebensmitteldaten für die öffentliche Gesundheit unter Beweis stellte.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Limonaden analysiert",
        "stat_sodas_sub": "Colas, Limonaden, Tonics, Eistees",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Mobilisierte Pioniere",
        "stat_contrib_sub": "In Supermärkten, online & in Nantes",
        "stat_viz_num": "1.",
        "stat_viz_lbl": "Interaktive Grafik",
        "stat_viz_sub": "3-Klick-Visualisierung",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Steuer & Gesundheit",
        "stat_tax_sub": "Einführung der Limonadensteuer",
        "ctx_title": "Die Ursprünge der Aktion: Nährwertangaben verständlich machen",
        "ctx_p1": "Open Food Facts startete am 19. Mai 2012. Schon in den ersten Wochen stellte sich eine zentrale Frage: Welchen konkreten Nutzen bringen offene Lebensmitteldaten den Bürgerinnen und Bürgern? Ende 2011 und Anfang 2012 tobten die Debatten über die Einführung der französischen Limonadensteuer. Doch jenseits der weltbekannten rot-weißen Cola-Dose: Was steckt wirklich in den tausenden Erfrischungsgetränken in den Regalen?",
        "ctx_p2": "Die Aktion Limonaden war das erste kollaborative Testfeld, um die Tatkraft der wachsenden Community zu erproben, Datenjournalisten einzubinden und innovative visuelle Erkundungstools zu schaffen.",
        "inq_title": "Die 5 zentralen Bürgerfragen im Supermarktregal",
        "chart_title": "Die Geburtsstunde der „3-Klick-Grafiken“",
        "chart_lead": "Ein zentraler Meilenstein der Aktion Limonaden war die Entwicklung eines dynamischen Streudiagramm-Generators in Open Food Facts, der jeden Nährstoff mit der Anzahl der Zusatzstoffe korrelieren kann.",
        "chart_caption": "Historisches Streudiagramm: Zuckergehalt vs. Anzahl der Zusatzstoffe in Limonaden (Open Food Facts, Juni 2012)",
        "chart_cta": "Diese Live-Abfrage auf Open Food Facts ausführen &rarr;",
        "media_title": "Medienecho & Pionier-Partner",
        "media_lead": "Bereits 2012 griffen Datenjournalisten und Gesundheitsexperten auf die ersten Datensätze von Open Food Facts zurück:",
        "legacy_title": "Von der Aktion Limonaden zu 3,8 Millionen Produkten",
        "legacy_desc": "Die Aktion Limonaden bewies, dass Bürgerinnen und Bürger eine ganze Lebensmittelkategorie in wenigen Tagen kartografieren können. Diese Methode inspirierte später <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016) und die Scan-Parties in ganz Europa.",
        "btn_scan_party": "Heutige Scan-Parties entdecken",
        "btn_add_product": "Getränk zu Open Food Facts hinzufügen",
    },
    "it": {
        "eyebrow": "🚀 Prima operazione tematica • Giugno 2012",
        "title": "Operazione Bibite (Opération Sodas)",
        "lead": "Dal 18 al 24 giugno 2012, i primi contributori di Open Food Facts hanno unito le forze per fotografare, catalogare e analizzare 150 bevande gassate e zuccherate in tutta la Francia. Un'avventura pionieristica che ha dato vita ai primi grafici interattivi e dimostrato il valore dei dati aperti per la salute pubblica.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Bibite decifrate",
        "stat_sodas_sub": "Cole, limonate, toniche, tè freddi",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Pionieri mobilitati",
        "stat_contrib_sub": "Nei negozi, online e a Nantes",
        "stat_viz_num": "1°",
        "stat_viz_lbl": "Grafico interattivo",
        "stat_viz_sub": "Funzione grafico in 3 clic",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Fisco e salute",
        "stat_tax_sub": "Applicazione della soda tax",
        "ctx_title": "Le origini dell'operazione: far parlare le etichette",
        "ctx_p1": "Open Food Facts è stato lanciato il 19 maggio 2012. Fin dalle prime settimane si è imposta una domanda fondamentale: a cosa possono servire concretamente i dati alimentari aperti? A fine 2011 e inizio 2012 infuriava il dibattito sulla «soda tax». Ma oltre alla celebre lattina rossa e bianca, di cosa sono realmente fatte le migliaia di bibite vendute nei supermercati?",
        "ctx_p2": "L'Operazione Bibite è stata il primo banco di prova collaborativo per testare l'energia della neonata comunità, coinvolgere data journalist e progettare strumenti di esplorazione visiva innovativi.",
        "inq_title": "Le 5 grandi domande dei cittadini tra le corsie del supermercato",
        "chart_title": "La nascita dei «Grafici in 3 clic»",
        "chart_lead": "Uno dei maggiori contributi dell'Operazione Bibite è stato lo sviluppo di un generatore dinamico di grafici a dispersione su Open Food Facts, capace di incrociare qualsiasi nutriente con il numero di additivi.",
        "chart_caption": "Grafico storico che incrocia zuccheri e numero di additivi nelle bibite (Open Food Facts, giugno 2012)",
        "chart_cta": "Esegui questa query in tempo reale su Open Food Facts &rarr;",
        "media_title": "Eco mediatica e partner pionieri",
        "media_lead": "Già nel 2012 giornalisti di dati e specialisti della salute hanno iniziato a esplorare i primi dataset di Open Food Facts:",
        "legacy_title": "Dall'Operazione Bibite a 3,8 milioni di prodotti",
        "legacy_desc": "L'Operazione Bibite ha dimostrato che il crowdsourcing civico può mappare un'intera categoria di prodotti in pochi giorni. Questo metodo ha poi ispirato <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016) e tutte le Scan Party europee.",
        "btn_scan_party": "Scopri le Scan Party di oggi",
        "btn_add_product": "Aggiungi una bevanda a Open Food Facts",
    },
    "es": {
        "eyebrow": "🚀 Primera operación temática • Junio de 2012",
        "title": "Operación Refrescos (Opération Sodas)",
        "lead": "Del 18 al 24 de junio de 2012, los primeros colaboradores de Open Food Facts unieron sus fuerzas para fotografiar, registrar y analizar 150 refrescos y bebidas azucaradas en toda Francia. Una campaña pionera que dio origen a los primeros gráficos interactivos en 3 clics y demostró el poder de los datos abiertos para la salud pública.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Refrescos analizados",
        "stat_sodas_sub": "Colas, limonadas, tónicas, tés helados",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Pioneros movilizados",
        "stat_contrib_sub": "En estanterías, online y en Nantes",
        "stat_viz_num": "1.º",
        "stat_viz_lbl": "Gráfico interactivo",
        "stat_viz_sub": "Gráficos en 3 clics",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Fiscalidad y salud",
        "stat_tax_sub": "Impuesto sobre refrescos",
        "ctx_title": "Los orígenes: hacer hablar a las etiquetas nutricionales",
        "ctx_p1": "Open Food Facts se lanzó públicamente el 19 de mayo de 2012. Desde las primeras semanas surgió una pregunta crucial: ¿para qué sirven concretamente los datos alimentarios abiertos? A finales de 2011 y principios de 2012, el debate sobre el impuesto a los refrescos estaba en pleno auge. Pero más allá de la célebre lata roja y blanca, ¿de qué están compuestos realmente los miles de refrescos vendidos en los supermercados?",
        "ctx_p2": "La Operación Refrescos fue el primer banco de pruebas colaborativo para testar la fuerza de la comunidad, conectar con periodistas de datos e idear herramientas de exploración visual innovadoras.",
        "inq_title": "Las 5 grandes preguntas ciudadanas en el supermercado",
        "chart_title": "El nacimiento de los «Gráficos en 3 clics»",
        "chart_lead": "Uno de los grandes hitos de la Operación Refrescos fue el desarrollo de un generador dinámico de diagramas de dispersión, que permite cruzar cualquier nutriente con el número de aditivos.",
        "chart_caption": "Gráfico histórico que cruza azúcares y número de aditivos en refrescos (Open Food Facts, junio de 2012)",
        "chart_cta": "Ejecutar esta consulta en vivo en Open Food Facts &rarr;",
        "media_title": "Eco en los medios y aliados pioneros",
        "media_lead": "Ya en 2012, periodistas de datos y expertos en salud emplearon los primeros conjuntos de datos de Open Food Facts:",
        "legacy_title": "De la Operación Refrescos a 3,8 millones de productos",
        "legacy_desc": "La Operación Refrescos demostró que la colaboración ciudadana podía mapear una categoría entera en pocos días. Este método inspiró después <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016) y todas las Scan Parties actuales.",
        "btn_scan_party": "Descubrir las Scan Parties de hoy",
        "btn_add_product": "Añadir una bebida a Open Food Facts",
    },
    "nl": {
        "eyebrow": "🚀 Eerste thematische sprint • Juni 2012",
        "title": "Operatie Frisdranken (Opération Sodas)",
        "lead": "Van 18 tot 24 juni 2012 bundelden de eerste vrijwilligers van Open Food Facts hun krachten om 150 koolzuurhoudende en suikerhoudende dranken in Frankrijk te fotograferen, registreren en analyseren. Een baanbrekende pionierscampagne die leidde tot de eerste interactieve 3-klik-grafieken en het nut van open voedseldata voor de volksgezondheid bewees.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Frisdranken ontcijferd",
        "stat_sodas_sub": "Cola's, limonades, tonics, ijsthee",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Gemobiliseerde pioniers",
        "stat_contrib_sub": "In winkels, online & in Nantes",
        "stat_viz_num": "1e",
        "stat_viz_lbl": "Interactieve grafiek",
        "stat_viz_sub": "3-klik-grafiekfunctie",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Fiscaal & gezondheid",
        "stat_tax_sub": "Invoering van de suikertaks",
        "ctx_title": "De oorsprong van de operatie: etiketten laten spreken",
        "ctx_p1": "Open Food Facts werd gelanceerd op 19 mei 2012. Vanaf de allereerste weken rees een fundamentele vraag: welk tastbaar nut heeft open data voor burgers? Eind 2011 en begin 2012 woedden debatten over de invoering van een suikertaks op frisdranken. Maar afgezien van het bekende rood-witte colablikje: wat zit er écht in de duizenden frisdranken in de supermarkt?",
        "ctx_p2": "Operatie Frisdranken was de allereerste collectieve proeftuin om de daadkracht van de prille gemeenschap te testen, datajournalisten te betrekken en innovatieve visuele analysetools te bouwen.",
        "inq_title": "De 5 grote burgervragen in het frisdrankschap",
        "chart_title": "De geboorte van de «3-klik-grafieken»",
        "chart_lead": "Een van de belangrijkste doorbraken van Operatie Frisdranken was de ontwikkeling van een dynamische scatterplot-generator in Open Food Facts, waarmee elke voedingsstof kan worden gekoppeld aan het aantal additieven.",
        "chart_caption": "Historisch scatterplot met suikers versus aantal additieven in frisdranken (Open Food Facts, juni 2012)",
        "chart_cta": "Voer deze live analyse uit op Open Food Facts &rarr;",
        "media_title": "Media-aandacht & pionierspartners",
        "media_lead": "Al in 2012 gingen datajournalisten en gezondheidswetenschappers met de eerste datasets van Open Food Facts aan de slag:",
        "legacy_title": "Van Operatie Frisdranken naar 3,8 miljoen producten",
        "legacy_desc": "Operatie Frisdranken bewees dat burgers in enkele dagen een complete productcategorie in kaart kunnen brengen. Deze methode inspireerde later <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016) en alle Scan Parties in heel Europa.",
        "btn_scan_party": "Ontdek de Scan Parties van nu",
        "btn_add_product": "Voeg een drank toe aan Open Food Facts",
    },
    "en": {
        "eyebrow": "🚀 Landmark 1st Thematic Sprint • June 2012",
        "title": "Operation Sodas",
        "lead": "From June 18 to 24, 2012, Open Food Facts' earliest contributors joined forces to photograph, catalog, and analyze 150 sugary and carbonated drinks across France. A landmark pioneer campaign that birthed interactive 3-click charts and proved the power of open food data for public health.",
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Sodas Mapped",
        "stat_sodas_sub": "Colas, lemonades, tonics, iced teas",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Pioneers Mobilized",
        "stat_contrib_sub": "In stores, online & in Nantes",
        "stat_viz_num": "1st",
        "stat_viz_lbl": "Interactive Chart",
        "stat_viz_sub": "3-click chart feature",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Tax & Public Health",
        "stat_tax_sub": "Soda tax enforcement",
        "ctx_title": "The Genesis: Making Nutrition Labels Speak",
        "ctx_p1": "Open Food Facts launched on May 19, 2012. Within weeks, a fundamental question arose: how can open food data deliver immediate, concrete value to citizens? In late 2011 and early 2012, French parliamentary debates on the 'soda tax' (enforced January 1, 2012) were raging. Yet beyond the ubiquitous red-and-white Coca-Cola can, what was actually inside the thousands of sodas sold across supermarkets?",
        "ctx_p2": "Operation Sodas served as the very first collaborative proving ground to test the emerging community's energy, team up with data journalists, and build innovative visual exploration tools.",
        "inq_title": "The 5 Core Citizen Inquiries in Supermarket Aisles",
        "chart_title": "The Birth of '3-Click Interactive Charts'",
        "chart_lead": "One of Operation Sodas' defining breakthroughs was the development of a dynamic scatter plot generator directly within Open Food Facts, plotting any nutrient against the number of food additives.",
        "chart_caption": "Historical scatter plot plotting sugars vs number of additives in sodas (Open Food Facts, June 2012)",
        "chart_cta": "Run this live scatter query on Open Food Facts &rarr;",
        "media_title": "Media Echo & Landmark Partners",
        "media_lead": "Back in 2012, data journalists and clinical specialists immediately seized Open Food Facts' raw datasets to investigate food quality:",
        "legacy_title": "From Operation Sodas to 3.8 Million Products",
        "legacy_desc": "Operation Sodas proved that citizen crowdsourcing could map an entire grocery category in just a few days. This methodology laid the blueprint for <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016), and the vibrant Scan Parties organized across Europe today.",
        "btn_scan_party": "Explore Today's Scan Parties",
        "btn_add_product": "Add a beverage to Open Food Facts",
    }
}


YOGURT_TRANSLATIONS = {
    "fr": {
        "eyebrow": "🌍 Open Data Day 2014 • Campagne Mondiale",
        "title": "Qu'y a-t-il dans mon yaourt ?",
        "lead": "Lancé lors de la Journée Internationale des Données Ouvertes (22 février 2014), le projet « What's in my yogurt? » a mobilisé des citoyens dans plus de 20 pays pour décrypter les rayons frais : portions de 125g contre 180g, taux de vrais fruits, additifs dans les 0% et sucres ajoutés sous toutes les latitudes.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yaourts Décryptés",
        "stat_yogurts_sub": "Nature, aux fruits, brassés, soja",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Pays Mobilisés",
        "stat_countries_sub": "Équipes nationales citoyennes",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Écarts de Portion",
        "stat_formats_sub": "France vs Suisse & États-Unis",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "Le « Cheval de Troie » au fond du réfrigérateur",
        "trojan_p1": "Pourquoi choisir les yaourts après les sodas ? Parce que le yaourt est un aliment du quotidien consommé massivement par les familles et les enfants. Pourtant, derrière une image universelle de produit « santé », les étiquettes recèlent des disparités frappantes : épaississants masquant le manque de matière grasse, sirop de glucose-fructose, faux morceaux de fruits et variations géographiques majeures.",
        "trojan_p2": "En incitant chacun à photographier le pot de son frigo ou de l'épicerie du coin, Open Food Facts a utilisé le yaourt comme un cheval de Troie pour faire entrer la transparence alimentaire dans les foyers.",
        "inq_title": "Les Révélations de l'Enquête Mondiale",
        "squads_title": "Équipes Internationales & Compétition Conviviale",
        "queries_title": "Explorer les Données en Direct (Requêtes Live)",
        "queries_lead": "Grâce aux données collectées, plusieurs visualisations et analyses comparatives continuent d'éclairer les consommateurs en temps réel :",
        "btn_scan_party": "Participer à une Scan Party",
        "btn_add_yogurt": "Ajouter un yaourt à Open Food Facts",
        "view_query": "Voir l'analyse &rarr;",
        "bottom_cta_title": "🥛 Prêt à faire parler les rayons frais ?",
        "bottom_cta_desc": "Découvrez les scan parties organisées près de chez vous ou enrichissez directement la base de données ouverte !",
    },
    "de": {
        "eyebrow": "🌍 Open Data Day 2014 • Weltweite Kampagne",
        "title": "Was ist in meinem Joghurt? (What's in my yogurt?)",
        "lead": "Gestartet am Internationalen Open Data Day (22. Februar 2014), mobilisierte „What's in my yogurt?“ Bürger in über 20 Ländern, um das Kühlregal zu entschlüsseln: 125g- vs. 180g-Becher, tatsächlicher Fruchtgehalt, Zusatzstoffe in fettfreien Produkten und weltweite Zuckerwerte.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Joghurts analysiert",
        "stat_yogurts_sub": "Natur, Frucht, gerührt, Soja & griechisch",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Länder beteiligt",
        "stat_countries_sub": "Nationale Bürgerteams",
        "stat_formats_num": "125g vs. 180g",
        "stat_formats_lbl": "Portionsunterschiede",
        "stat_formats_sub": "Frankreich vs. Schweiz & USA",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "Das „Trojanische Pferd“ im Kühlschrank",
        "trojan_p1": "Warum Joghurt nach Limonade? Weil Joghurt ein tägliches Grundnahrungsmittel für Millionen Familien und Kinder ist. Doch hinter dem gesunden Image verbergen sich erhebliche Kontraste: künstliche Verdickungsmittel, Glukose-Fruktose-Sirup, winzige Fruchtanteile und drastische regionale Rezepturunterschiede.",
        "trojan_p2": "Indem jeder aufgerufen wurde, den Joghurt im heimischen Kühlschrank oder Supermarkt zu fotografieren, wurde Joghurt zum trojanischen Pferd für mehr Lebensmittelkompetenz im Alltag.",
        "inq_title": "Wichtige Erkenntnisse der weltweiten Joghurt-Untersuchung",
        "squads_title": "Internationale Teams & freundschaftlicher Wettbewerb",
        "queries_title": "Live-Datensätze erkunden (Interaktive Abfragen)",
        "queries_lead": "Dank der gesammelten Daten informieren mehrere Live-Abfragen und Streudiagramme Verbraucher bis heute:",
        "btn_scan_party": "An einer Scan-Party teilnehmen",
        "btn_add_yogurt": "Joghurt zu Open Food Facts hinzufügen",
        "view_query": "Live-Abfrage ansehen &rarr;",
        "bottom_cta_title": "🥛 Bereit, das Kühlregal zu entschlüsseln?",
        "bottom_cta_desc": "Entdecken Sie Scan-Parties in Ihrer Nähe oder erfassen Sie Joghurts mit der Open Food Facts App!",
    },
    "it": {
        "eyebrow": "🌍 Open Data Day 2014 • Campagna Globale",
        "title": "Cosa c'è nel mio yogurt? (What's in my yogurt?)",
        "lead": "Lanciato durante l'Open Data Day (22 febbraio 2014), il progetto «What's in my yogurt?» ha mobilitato cittadini in oltre 20 paesi per decifrare il banco frigo: vasetti da 125g contro 180g, percentuali di vera frutta, additivi nelle formule 0% e livelli di zuccheri nel mondo.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yogurt decifrati",
        "stat_yogurts_sub": "Bianco, alla frutta, compatto, soia",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Paesi mobilitati",
        "stat_countries_sub": "Squadre nazionali di cittadini",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Disparità nei formati",
        "stat_formats_sub": "Francia vs Svizzera & USA",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "Il «Cavallo di Troia» nel frigorifero",
        "trojan_p1": "Perché lo yogurt dopo le bibite? Perché lo yogurt è un alimento base consumato quotidianamente da famiglie e bambini. Dietro la sua immagine di salute, le etichette nascondono forti contrasti: addensanti sintetici, sciroppo di glucosio-fruttosio e variazioni geografiche marcate.",
        "trojan_p2": "Invitando i consumatori a fotografare i vasetti a casa o al supermercato, Open Food Facts ha usato lo yogurt come cavallo di Troia per portare la trasparenza alimentare nelle abitudini quotidiane.",
        "inq_title": "Scoperte chiave dell'indagine globale sullo yogurt",
        "squads_title": "Squadre nazionali & competizione conviviale",
        "queries_title": "Esplora i dati in tempo reale (Query Live)",
        "queries_lead": "Grazie ai dati raccolti, diverse visualizzazioni continuano a informare i consumatori in tempo reale:",
        "btn_scan_party": "Partecipa a una Scan Party",
        "btn_add_yogurt": "Aggiungi uno yogurt a Open Food Facts",
        "view_query": "Vedi l'analisi live &rarr;",
        "bottom_cta_title": "🥛 Pronto a far parlare il banco frigo?",
        "bottom_cta_desc": "Trova una Scan Party vicino a te o contribuisci scansionando con l'app di Open Food Facts!",
    },
    "es": {
        "eyebrow": "🌍 Open Data Day 2014 • Campaña Global",
        "title": "¿Qué hay en mi yogur? (What's in my yogurt?)",
        "lead": "Lanzado en el Open Data Day (22 de febrero de 2014), el proyecto «What's in my yogurt?» movilizó a ciudadanos de más de 20 países para descifrar los lácteos: raciones de 125g frente a 180g, fruta real, aditivos en versiones 0% y niveles de azúcar en todo el mundo.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yogures analizados",
        "stat_yogurts_sub": "Natural, con frutas, batido, soja",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Países movilizados",
        "stat_countries_sub": "Equipos ciudadanos nacionales",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Disparidad de ración",
        "stat_formats_sub": "Francia vs Suiza y EE. UU.",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "El «Caballo de Troya» en el fondo de la nevera",
        "trojan_p1": "¿Por qué yogures tras los refrescos? Porque el yogur es un producto básico consumido a diario por familias y menores. Tras su aureola saludable, las etiquetas esconden contrastes notables: espesantes que sustituyen la grasa, jarabes de glucosa y marcadas diferencias geográficas.",
        "trojan_p2": "Al invitar a fotografiar los envases del hogar o de la tienda vecina, Open Food Facts empleó el yogur como caballo de Troya para introducir la cultura de datos abiertos en cada cocina.",
        "inq_title": "Hallazgos principales de la investigación sobre yogures",
        "squads_title": "Equipos internacionales y competición amistosa",
        "queries_title": "Explorar datos en directo (Consultas interactivas)",
        "queries_lead": "Gracias a los datos recopilados, diversas consultas y gráficos siguen orientando a los consumidores hoy en día:",
        "btn_scan_party": "Unirse a una Scan Party",
        "btn_add_yogurt": "Añadir un yogur a Open Food Facts",
        "view_query": "Ver consulta en vivo &rarr;",
        "bottom_cta_title": "🥛 ¿A punto para descifrar el lineal de frescos?",
        "bottom_cta_desc": "¡Encuentra una Scan Party cercana o escanea yogures con la app móvil de Open Food Facts!",
    },
    "nl": {
        "eyebrow": "🌍 Open Data Day 2014 • Wereldwijde Campagne",
        "title": "Wat zit er in mijn yoghurt? (What's in my yogurt?)",
        "lead": "Gelanceerd op de Internationale Open Data Dag (22 februari 2014), bracht het project «What's in my yogurt?» burgers in meer dan 20 landen op de been om het zuivelschap te ontcijferen: porties van 125g versus 180g, percentages echt fruit, additieven in magere producten en suikergehaltes wereldwijd.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yoghurts ontcijferd",
        "stat_yogurts_sub": "Naturel, fruit, roeryoghurt, soja",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Betrokken landen",
        "stat_countries_sub": "Nationale burgerteams",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Portieverschillen",
        "stat_formats_sub": "Frankrijk vs Zwitserland & VS",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "Het «Paard van Troje» in de koelkast",
        "trojan_p1": "Waarom yoghurt na frisdrank? Omdat yoghurt een dagelijks basisproduct is voor miljoenen gezinnen en kinderen. Achter het gezonde imago verbergen etiketten echter grote tegenstellingen: verdikkingsmiddelen ter vervanging van vet, glucose-fructosestroop en grote regionale receptuurverschillen.",
        "trojan_p2": "Door iedereen uit te nodigen de potjes in de koelkast of supermarkt te fotograferen, werd yoghurt een vriendelijk paard van Troje om voedseltransparantie in huis te halen.",
        "inq_title": "Belangrijkste inzichten van het wereldwijde yoghurt-onderzoek",
        "squads_title": "Internationale teams & vriendschappelijke competitie",
        "queries_title": "Verken live datasets (Interactieve zoekopdrachten)",
        "queries_lead": "Dankzij de verzamelde data helpen diverse live visualisaties en grafieken consumenten nog steeds dagelijks:",
        "btn_scan_party": "Doe mee aan een Scan Party",
        "btn_add_yogurt": "Voeg een yoghurt toe aan Open Food Facts",
        "view_query": "Bekijk live analyse &rarr;",
        "bottom_cta_title": "🥛 Klaar om het zuivelschap te ontcijferen?",
        "bottom_cta_desc": "Ontdek Scan Parties bij jou in de buurt of scan yoghurts met de Open Food Facts mobiele app!",
    },
    "en": {
        "eyebrow": "🌍 Open Data Day 2014 • Global Crowdsourcing Quest",
        "title": "What's in my yogurt?",
        "lead": "Launched on Open Data Day (February 22, 2014), 'What's in my yogurt?' mobilized citizen contributors in over 20 countries to scan dairy aisles: comparing 125g vs 180g portion sizes, real fruit percentages, additives in fat-free formulas, and sugar levels worldwide.",
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yogurts Mapped",
        "stat_yogurts_sub": "Plain, fruit, stirred, soy & Greek",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Countries Mobilized",
        "stat_countries_sub": "National contributor squads",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Portion Disparities",
        "stat_formats_sub": "France vs Switzerland & USA",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com",
        "trojan_title": "The 'Trojan Horse' into Everyday Refrigerators",
        "trojan_p1": "Why focus on yogurts after sodas? Because yogurt is a household staple enjoyed daily by hundreds of millions of children and families. Yet behind its innocent 'health food' halo, nutrition labels conceal staggering contrasts: synthetic thickeners masking fat-free textures, high-fructose corn syrups, deceptive fruit imagery, and extreme geographical variations.",
        "trojan_p2": "By inviting everyday shoppers to snap pictures of the yogurt cups in their kitchen or local co-op, Open Food Facts used yogurt as a friendly Trojan Horse to bring open data literacy into household routines.",
        "inq_title": "Key Discoveries of the Global Yogurt Inquiry",
        "squads_title": "Country Squads & Friendly Global Competition",
        "queries_title": "Explore Live Yogurt Datasets",
        "queries_lead": "Thanks to the crowdsourced data, several live queries and comparative scatter plots continue to empower consumers today:",
        "btn_scan_party": "Join a Scan Party",
        "btn_add_yogurt": "Add a yogurt to Open Food Facts",
        "view_query": "View live query &rarr;",
        "bottom_cta_title": "🥛 Ready to demystify yogurt aisles?",
        "bottom_cta_desc": "Find a scan party in your local community or scan yogurts with the Open Food Facts mobile app!",
    }
}


SHAMPOO_TRANSLATIONS = {
    "fr": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "Qu'y a-t-il dans mon shampooing ?",
        "lead": "Le 5 mars 2016, à l'occasion de l'Open Data Day, la communauté Open Food Facts a poussé la porte de la salle de bain pour donner naissance à Open Beauty Facts. Objectif : photographier et décrypter la nomenclature INCI en latin, identifier conservateurs, allergènes et silicones dans les shampooings du monde entier.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampooings Décryptés",
        "stat_shampoos_sub": "Classiques, bios, solides, antipelliculaires",
        "stat_comp_num": "10 à 42",
        "stat_comp_lbl": "Ingrédients par Flacon",
        "stat_comp_sub": "De l'ultra-court au cocktail chimique",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Latin Décodé en Clair",
        "stat_inci_sub": "Aqua = Eau, tensioactifs, silicones",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Jeu de Données Ouvert",
        "stat_gouv_sub": "Réutilisation citoyenne & recherche",
        "latin_title": "Pourquoi décrypter la salle de bain ?",
        "latin_p1": "Contrairement à l'alimentation où les ingrédients sont souvent formulés en langage courant (farine, sucre, huile), les cosmétiques imposent la nomenclature internationale INCI : un mélange de latin (pour les extraits végétaux) et de termes chimiques complexes. Sans formation scientifique poussée, il est presque impossible pour un citoyen de comprendre ce qu'il applique sur son cuir chevelu.",
        "latin_p2": "Open Beauty Facts a été bâti pour combler ce gouffre : traduire « Aqua » en eau, repérer le phénoxyéthanol, les parabènes, les sulfates décapants (SLS/SLES) et les 26 substances parfumantes allergènes à déclaration obligatoire en Europe.",
        "inq_title": "Les Révélations de l'Enquête Cosmétique",
        "goals_title": "Objectifs Mondiaux du Projet",
        "btn_obf": "Visiter Open Beauty Facts",
        "btn_scan": "Rejoindre une Scan Party",
        "bottom_cta_title": "🧴 Envie d'ouvrir les cosmétiques de votre salle de bain ?",
        "bottom_cta_desc": "Consultez la base de données ouverte Open Beauty Facts ou organisez un atelier de scan collaboratif !",
    },
    "de": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "Was ist in meinem Shampoo? (What's in my shampoo?)",
        "lead": "Am 5. März 2016 öffnete die Open Food Facts Community anlässlich des Open Data Day die Tür zum Badezimmer, um Open Beauty Facts ins Leben zu rufen. Das Ziel: die lateinische INCI-Nomenklatur entschlüsseln sowie Konservierungsstoffe, Allergene und Silikone in Shampoos weltweit erfassen.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampoos analysiert",
        "stat_shampoos_sub": "Klassisch, bio, fest, Anti-Schuppen",
        "stat_comp_num": "10 bis 42",
        "stat_comp_lbl": "Inhaltsstoffe pro Flasche",
        "stat_comp_sub": "Vom Minimalismus bis zum Chemiecocktail",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Latein verständlich übersetzt",
        "stat_inci_sub": "Aqua = Wasser, Tenside, Silikone",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Offener Datensatz",
        "stat_gouv_sub": "Bürgerwissenschaft & Forschung",
        "latin_title": "Warum das Badezimmer entschlüsseln?",
        "latin_p1": "Anders als bei Lebensmitteln, wo Zutaten meist in Alltagssprache formuliert sind, schreibt die Kosmetik die internationale INCI-Nomenklatur vor: ein Gemisch aus Latein und chemischen Bezeichnungen. Ohne Fachwissen ist es für Verbraucher kaum verständlich, was sie täglich auf ihre Kopfhaut auftragen.",
        "latin_p2": "Open Beauty Facts schließt diese Lücke: „Aqua“ als Wasser übersetzen, Phenoxyethanol, Parabene, aggressive Sulfate (SLS/SLES) und deklarationspflichtige Duftstoffallergene transparent machen.",
        "inq_title": "Wichtige Erkenntnisse der Kosmetik-Untersuchung",
        "goals_title": "Weltweite Meilensteine des Projekts",
        "btn_obf": "Open Beauty Facts besuchen",
        "btn_scan": "An einer Scan-Party teilnehmen",
        "bottom_cta_title": "🧴 Bereit, die Kosmetik im Badezimmer zu entschlüsseln?",
        "bottom_cta_desc": "Durchsuchen Sie die offene Datenbank von Open Beauty Facts oder organisieren Sie eine Scan-Party!",
    },
    "it": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "Cosa c'è nel mio shampoo? (What's in my shampoo?)",
        "lead": "Il 5 marzo 2016, in occasione dell'Open Data Day, la comunità di Open Food Facts ha aperto la porta del bagno per dare vita a Open Beauty Facts. Obiettivo: fotografare e decifrare la nomenclatura INCI in latino, identificando conservanti, allergeni e siliconi negli shampoo di tutto il mondo.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampoo decifrati",
        "stat_shampoos_sub": "Tradizionali, bio, solidi, antiforfora",
        "stat_comp_num": "10 a 42",
        "stat_comp_lbl": "Ingredienti per flacone",
        "stat_comp_sub": "Dal minimalismo al cocktail chimico",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Latino tradotto in chiaro",
        "stat_inci_sub": "Aqua = Acqua, tensioattivi, siliconi",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Dataset aperto",
        "stat_gouv_sub": "Scienza cittadina & ricerca",
        "latin_title": "Perché decifrare i prodotti del bagno?",
        "latin_p1": "A differenza del cibo in cui gli ingredienti sono espressi in linguaggio comune, i cosmetici impongono la nomenclatura internazionale INCI: una miscela di latino e codici chimici. Senza una formazione scientifica, è quasi impossibile per un consumatore comprendere cosa applica sui propri capelli.",
        "latin_p2": "Open Beauty Facts è nato per colmare questa distanza: tradurre «Aqua» in acqua, segnalare fenossietanolo, parabeni, solfati aggressivi (SLS/SLES) e i 26 allergeni dei profumi regolamentati a livello europeo.",
        "inq_title": "Rivelazioni chiave dell'indagine cosmetica",
        "goals_title": "Obiettivi globali del progetto",
        "btn_obf": "Visita Open Beauty Facts",
        "btn_scan": "Partecipa a una Scan Party",
        "bottom_cta_title": "🧴 Vuoi scoprire cosa c'è nei cosmetici del tuo bagno?",
        "bottom_cta_desc": "Consulta la banca dati aperta Open Beauty Facts o organizza un laboratorio di scansione collaborativo!",
    },
    "es": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "¿Qué hay en mi champú? (What's in my shampoo?)",
        "lead": "El 5 de marzo de 2016, con motivo del Open Data Day, la comunidad de Open Food Facts se adentró en el cuarto de baño para crear Open Beauty Facts. Meta: fotografiar y descifrar la nomenclatura INCI en latín, identificando conservantes, alérgenos y siliconas en champús de todo el mundo.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Champús analizados",
        "stat_shampoos_sub": "Convencionales, bio, sólidos, anticaspa",
        "stat_comp_num": "10 a 42",
        "stat_comp_lbl": "Ingredientes por botella",
        "stat_comp_sub": "De fórmulas cortas a cócteles químicos",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "El latín traducido en claro",
        "stat_inci_sub": "Aqua = Agua, sulfatos, siliconas",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Conjunto de datos abierto",
        "stat_gouv_sub": "Ciencia ciudadana & investigación",
        "latin_title": "¿Por qué descifrar los cosméticos del baño?",
        "latin_p1": "A diferencia de la alimentación, donde los ingredientes se expresan con palabras cotidianas, los cosméticos emplean la nomenclatura INCI: mezcla de botánica en latín y códigos químicos. Sin formación específica, resulta casi imposible entender qué nos aplicamos en la piel.",
        "latin_p2": "Open Beauty Facts nació para salvar esa brecha: traducir «Aqua» por agua, localizar fenoxietanol, parabenos, sulfatos agresivos (SLS/SLES) y los alérgenos de fragancias de declaración obligatoria.",
        "inq_title": "Conclusiones clave de la expedición cosmética",
        "goals_title": "Metas globales del proyecto",
        "btn_obf": "Visitar Open Beauty Facts",
        "btn_scan": "Unirse a una Scan Party",
        "bottom_cta_title": "🧴 ¿Quieres abrir los cosméticos de tu cuarto de baño?",
        "bottom_cta_desc": "¡Consulta la base de datos abierta Open Beauty Facts u organiza un taller colaborativo de escaneo!",
    },
    "nl": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "Wat zit er in mijn shampoo? (What's in my shampoo?)",
        "lead": "Op 5 maart 2016, ter gelegenheid van Open Data Day, stapte de Open Food Facts-gemeenschap de badkamer binnen om Open Beauty Facts op te richten. Het doel: de Latijnse INCI-nomenclatuur ontcijferen en conserveermiddelen, allergenen en siliconen in shampoos wereldwijd in kaart brengen.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampoos ontcijferd",
        "stat_shampoos_sub": "Klassiek, bio, solide, anti-roos",
        "stat_comp_num": "10 tot 42",
        "stat_comp_lbl": "Ingrediënten per fles",
        "stat_comp_sub": "Van minimalistisch tot chemische cocktail",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Latijn begrijpelijk vertaald",
        "stat_inci_sub": "Aqua = Water, sulfaten, siliconen",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Openbare dataset",
        "stat_gouv_sub": "Burgerwetenschap & onderzoek",
        "latin_title": "Waarom de badkamer ontcijferen?",
        "latin_p1": "In tegenstelling tot voeding, waar ingrediënten meestal in gewone taal op de verpakking staan, gebruikt cosmetica de internationale INCI-nomenclatuur: een mengeling van Latijn en ingewikkelde chemische termen. Zonder scheikundige achtergrond is het voor consumenten nagenoeg onmogelijk te begrijpen wat ze dagelijks gebruiken.",
        "latin_p2": "Open Beauty Facts overbrugt deze kloof: vertaalt «Aqua» naar water, signaleert fenoxyethanol, parabenen, agressieve sulfaten (SLS/SLES) en de wettelijk verplichte parfumallergenen.",
        "inq_title": "Belangrijkste inzichten van het shampoo-onderzoek",
        "goals_title": "Wereldwijde mijlpalen van het project",
        "btn_obf": "Bezoek Open Beauty Facts",
        "btn_scan": "Doe mee aan een Scan Party",
        "bottom_cta_title": "🧴 Wil je de verzorgingsproducten in je badkamer ontcijferen?",
        "bottom_cta_desc": "Raadpleeg de open database Open Beauty Facts of organiseer een gezamenlijke Scan Party!",
    },
    "en": {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "What's in my shampoo?",
        "lead": "On March 5, 2016, for Open Data Day, the Open Food Facts community opened the bathroom door to launch Open Beauty Facts. The mission: photograph and decipher complex Latin INCI cosmetic formulations, count chemicals, and identify preservatives, allergens, and silicones in shampoos worldwide.",
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampoos Decrypted",
        "stat_shampoos_sub": "Conventional, organic, solid, anti-dandruff",
        "stat_comp_num": "10 to 42",
        "stat_comp_lbl": "Ingredients per Bottle",
        "stat_comp_sub": "From minimalist to 40+ chemicals",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Plain English Translation",
        "stat_inci_sub": "Aqua = Water, sulfates, silicones",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Public Open Commons",
        "stat_gouv_sub": "Citizen science & academic reuse",
        "latin_title": "Why Decipher the Bathroom Cabinet?",
        "latin_p1": "Unlike food where ingredients are expressed in familiar words (wheat, sugar, olive oil), personal care items mandate INCI nomenclature: an obscure blend of Latin botanical names and chemical codes. Without a degree in chemistry, it is virtually impossible for shoppers to know what touches their scalp and hair every morning.",
        "latin_p2": "Open Beauty Facts was built to bridge this knowledge gap: translating 'Aqua' into water, highlighting phenoxyethanol, parabens, stripping sulfates (SLS/SLES), and the 26 mandatory fragrance allergens regulated under European consumer law.",
        "inq_title": "Core Insights from the Shampoo Expedition",
        "goals_title": "Worldwide Mission Milestones",
        "btn_obf": "Explore Open Beauty Facts",
        "btn_scan": "Join a Scan Party",
        "bottom_cta_title": "🧴 Ready to open the personal care products in your home?",
        "bottom_cta_desc": "Search the Open Beauty Facts public database or organize a collaborative scan party!",
    }
}

MISSIONS_DIR = os.path.join(DATA_DIR, "missions")

def load_mission(slug):
    fpath = os.path.join(MISSIONS_DIR, f"{slug}.yaml")
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Missing mission YAML file: {fpath}")
    with open(fpath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_standalone_wrapper(title, lang, content):
    nav_labels = {
        "fr": {"brand": "Campagnes & Missions", "contribute": "Contribuer", "footer_org": "Open Food Facts est une association citoyenne à but non lucratif (loi 1901).", "footer_odbl": "Données sous licence libre ODbL.", "footer_back": "&larr; Retour à l'annuaire des Scan Parties", "footer_site": "Site officiel Open Food Facts"},
        "de": {"brand": "Kampagnen & Missionen", "contribute": "Mitwirken", "footer_org": "Open Food Facts ist ein gemeinnütziger Verein von Bürgerinnen und Bürgern.", "footer_odbl": "Daten unter freier ODbL-Lizenz.", "footer_back": "&larr; Zurück zum Scan-Party-Verzeichnis", "footer_site": "Offizielle Open Food Facts Website"},
        "it": {"brand": "Campagne & Missioni", "contribute": "Contribuisci", "footer_org": "Open Food Facts è un'associazione di cittadini senza scopo di lucro.", "footer_odbl": "Dati con licenza libera ODbL.", "footer_back": "&larr; Torna alla directory delle Scan Party", "footer_site": "Sito ufficiale di Open Food Facts"},
        "es": {"brand": "Campañas & Misiones", "contribute": "Contribuir", "footer_org": "Open Food Facts es una asociación ciudadana sin ánimo de lucro.", "footer_odbl": "Datos bajo licencia libre ODbL.", "footer_back": "&larr; Volver al directorio de Scan Parties", "footer_site": "Sitio web oficial de Open Food Facts"},
        "nl": {"brand": "Campagnes & Missies", "contribute": "Bijdragen", "footer_org": "Open Food Facts is een vereniging van burgers zonder winstoogmerk.", "footer_odbl": "Gegevens onder vrije ODbL-licentie.", "footer_back": "&larr; Terug naar het overzicht van Scan Parties", "footer_site": "Officiële Open Food Facts-website"},
    }
    nl_nav = nav_labels.get(lang, {
        "brand": "Campaigns & Missions", "contribute": "Contribute", "footer_org": "Open Food Facts is a non-profit association of food citizens.", "footer_odbl": "Data released under the Open Database License (ODbL).", "footer_back": "&larr; Back to Scan Parties Directory", "footer_site": "Official Open Food Facts Website"
    })
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Open Food Facts</title>
  <meta name="description" content="{title} — Retrospective and interactive exploration by Open Food Facts.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      line-height: 1.6;
    }}
    .standalone-nav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.85rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .standalone-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #341100;
      font-weight: 800;
      font-size: 1.15rem;
    }}
    .standalone-brand img {{
      height: 32px;
      width: auto;
    }}
    .standalone-links {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.9rem;
    }}
    .standalone-links a {{
      color: #473526;
      text-decoration: none;
      font-weight: 600;
      transition: color 0.15s;
    }}
    .standalone-links a:hover,
    .standalone-links a.active {{
      color: #ed8857;
    }}
    .standalone-footer {{
      border-top: 1px solid #e2e8f0;
      background: #ffffff;
      padding: 2.5rem 1.5rem;
      text-align: center;
      font-size: 0.9rem;
      color: #64748b;
      margin-top: 4rem;
    }}
    .standalone-footer a {{
      color: #ea580c;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <nav class="standalone-nav">
    <a href="https://world.openfoodfacts.org" class="standalone-brand">
      <img src="https://static.openfoodfacts.org/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts Logo">
      <span>{nl_nav["brand"]}</span>
    </a>
    <div class="standalone-links">
      <a href="scan-parties.html">Scan Parties</a>
      <a href="operation-sodas.html">Opération Sodas</a>
      <a href="whats-in-my-yogurt.html">What's in my yogurt?</a>
      <a href="whats-in-my-shampoo.html">What's in my shampoo?</a>
      <a href="https://world.openfoodfacts.org/contribute">{nl_nav["contribute"]}</a>
      <a href="https://slack.openfoodfacts.org" target="_blank" rel="noopener">Slack</a>
    </div>
  </nav>

  {content}

  <footer class="standalone-footer">
    <p>
      {nl_nav["footer_org"]} 
      {nl_nav["footer_odbl"]}
    </p>
    <p>
      <a href="scan-parties.html">{nl_nav["footer_back"]}</a> • 
      <a href="https://world.openfoodfacts.org">{nl_nav["footer_site"]}</a>
    </p>
  </footer>
</body>
</html>"""

def generate_operation_sodas_html(data, lang="en"):
    t = SODAS_TRANSLATIONS.get(lang, SODAS_TRANSLATIONS["en"])
    

    
    questions = data.get("key_questions", [])
    press = data.get("press_coverage", [])
    
    questions_html = ""
    for q in questions:
        q_text = get_localized_field(q, "question", lang, default_lang="en")
        f_text = get_localized_field(q, "finding", lang, default_lang="en")
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">❓ {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    press_html = ""
    for p in press:
        outlet = p.get("outlet", "")
        p_title = p.get("title", "")
        author = p.get("author", "")
        date = p.get("date", "")
        link = p.get("link", "#")
        quote = p.get("quote", "")
        press_html += f"""
        <div class="off-card off-press-card">
          <div class="off-press-top">
            <span class="off-press-outlet">{outlet}</span>
            <span class="off-press-date">{date}</span>
          </div>
          <h4 class="off-press-title"><a href="{link}" target="_blank" rel="noopener noreferrer">{p_title}</a></h4>
          <div class="off-press-author">✍️ {author}</div>
          <blockquote class="off-press-quote">« {quote} »</blockquote>
        </div>
        """

    return f"""<style>
/* Operation Sodas Revamped Showcase Styles */
.off-op-wrap {{
  --off-espresso: #341100;
  --off-espresso-mid: #473526;
  --off-cream: #fdfaf7;
  --off-peach-tint: #f5ebe6;
  --off-orange: #ea580c;
  --off-orange-hover: #c2410c;
  --off-blue: #0284c7;
  --off-green: #16a34a;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-op-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-cream) 100%);
  border: 1px solid var(--off-peach-tint);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(52, 17, 0, 0.04);
}}

.off-badge-hero {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #fff7ed;
  color: var(--off-orange);
  border: 1px solid #fed7aa;
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-op-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-op-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: var(--off-espresso-mid);
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}}
.off-stat-num {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-orange);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: var(--off-espresso);
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: var(--off-espresso-mid);
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-inq-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}}
.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--off-espresso);
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #f8fafc;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-orange);
}}

.off-chart-box {{
  background: #ffffff;
  border: 1px solid var(--off-border);
  border-radius: 24px;
  padding: clamp(1.5rem, 3vw, 2.5rem);
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}}
.off-chart-img {{
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin: 1.5rem 0;
}}
.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-primary {{
  background: var(--off-orange);
  color: #ffffff;
}}
.off-btn-primary:hover {{
  background: var(--off-orange-hover);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: var(--off-espresso);
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
  border-color: #cbd5e1;
}}

.off-press-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 1.5rem;
}}
.off-press-card {{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.off-press-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}}
.off-press-outlet {{
  background: #f1f5f9;
  color: #0f172a;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
}}
.off-press-date {{
  font-size: 0.8rem;
  color: #64748b;
}}
.off-press-title {{
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}}
.off-press-title a {{
  color: var(--off-espresso);
  text-decoration: none;
}}
.off-press-title a:hover {{
  color: var(--off-orange);
}}
.off-press-author {{
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 0.75rem;
}}
.off-press-quote {{
  margin: 0;
  font-style: italic;
  font-size: 0.9rem;
  color: #475569;
  border-left: 2px solid #cbd5e1;
  padding-left: 0.75rem;
}}

.off-legacy-banner {{
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 1px solid #fed7aa;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #9a3412;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc {{
  font-size: 1.05rem;
  color: #7c2d12;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-op-wrap">
  <!-- Hero Section -->
  <div class="off-op-hero">
    <div class="off-badge-hero">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_sodas_num"]}</div>
        <div class="off-stat-lbl">{t["stat_sodas_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_sodas_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_contrib_num"]}</div>
        <div class="off-stat-lbl">{t["stat_contrib_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_contrib_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_viz_num"]}</div>
        <div class="off-stat-lbl">{t["stat_viz_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_viz_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_tax_num"]}</div>
        <div class="off-stat-lbl">{t["stat_tax_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_tax_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Historical Context -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; margin-top: 0;">{t["ctx_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["ctx_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["ctx_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://fr.openfoodfacts.org/images/misc/operation-soda.png" alt="Opération Sodas Badge" style="max-width: 220px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Citizen Questions Investigated -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div class="off-inq-grid">
      {questions_html}
    </div>
  </div>

  <!-- 3-Click Chart Feature Breakthrough -->
  <div class="off-section">
    <div class="off-chart-box">
      <h3 style="font-size: 1.6rem; font-weight: 800; margin: 0 0 0.5rem 0;">{t["chart_title"]}</h3>
      <p style="color: #475569; max-width: 750px; margin: 0 auto 1.25rem auto;">{t["chart_lead"]}</p>
      
      <a href="{data.get('scatter_plot_url')}" target="_blank" rel="noopener noreferrer">
        <img src="https://fr.blog.openfoodfacts.org/images/sucres_et_additifs_dans_les_sodas.png" alt="{t['chart_caption']}" class="off-chart-img">
      </a>
      <p style="font-size: 0.85rem; color: #64748b; font-style: italic; margin-bottom: 1.5rem;">{t["chart_caption"]}</p>
      
      <a href="{data.get('scatter_plot_url')}" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-primary">
        {t["chart_cta"]}
      </a>
    </div>
  </div>

  <!-- Media Coverage & Partners -->
  <div class="off-section">
    <h3 class="off-section-title">{t["media_title"]}</h3>
    <p class="off-section-lead">{t["media_lead"]}</p>
    <div class="off-press-grid">
      {press_html}
    </div>
  </div>

  <!-- Legacy & Future Call to Action -->
  <div class="off-legacy-banner">
    <div class="off-legacy-title">💡 {t["legacy_title"]}</div>
    <div class="off-legacy-desc">{t["legacy_desc"]}</div>
    <div class="off-legacy-actions">
      <a href="scan-parties.html" class="off-btn off-btn-primary">🎉 {t["btn_scan_party"]}</a>
      <a href="https://world.openfoodfacts.org/contribute" class="off-btn off-btn-secondary">📱 {t["btn_add_product"]}</a>
    </div>
  </div>
</div>
"""

def generate_whats_in_my_yogurt_html(data, lang="en"):
    t = YOGURT_TRANSLATIONS.get(lang, YOGURT_TRANSLATIONS["en"])
    

    
    questions = data.get("key_questions", [])
    squads = data.get("country_teams", [])
    queries = data.get("related_queries", [])
    
    questions_html = ""
    for q in questions:
        q_text = get_localized_field(q, "question", lang, default_lang="en")
        f_text = get_localized_field(q, "finding", lang, default_lang="en")
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">🥛 {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    squads_html = ""
    for s in squads:
        country = get_localized_field(s, "country", lang, default_lang="en")
        notes = get_localized_field(s, "notes", lang, default_lang="en")
        squads_html += f"""
        <div class="off-card" style="border-left: 4px solid var(--off-blue);">
          <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #0284c7;">🚩 {country}</h4>
          <p style="margin: 0; font-size: 0.9rem; color: #334155;">{notes}</p>
        </div>
        """

    queries_html = ""
    for q in queries:
        q_id = q.get("id", "")
        q_title = get_localized_field(q, "title", lang, default_lang="en")
        q_url = q.get("url", "#")
        queries_html += f"""
        <div class="off-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">📊 {q_title}</div>
            <div style="font-size: 0.8rem; color: #64748b; font-family: monospace;">query: {q_id}</div>
          </div>
          <a href="{q_url}" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-blue">
            {t["view_query"]}
          </a>
        </div>
        """

    return f"""<style>
/* What's In My Yogurt Revamped Showcase Styles */
.off-yg-wrap {{
  --off-espresso: #0f172a;
  --off-blue: #0284c7;
  --off-blue-dark: #0369a1;
  --off-blue-light: #f0f9ff;
  --off-blue-border: #bae6fd;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-yg-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-blue-light) 100%);
  border: 1px solid var(--off-blue-border);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(2, 132, 199, 0.06);
}}

.off-badge-blue {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #e0f2fe;
  color: var(--off-blue-dark);
  border: 1px solid var(--off-blue-border);
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-yg-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: #0c4a6e;
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-yg-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: #334155;
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.08);
}}
.off-stat-num-blue {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-blue);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: #0c4a6e;
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: #475569;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #0c4a6e;
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #f8fafc;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-blue);
}}

.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-blue {{
  background: var(--off-blue);
  color: #ffffff;
}}
.off-btn-blue:hover {{
  background: var(--off-blue-dark);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: #0f172a;
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
}}

.off-legacy-banner-blue {{
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title-blue {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #0369a1;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc-blue {{
  font-size: 1.05rem;
  color: #075985;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-yg-wrap">
  <!-- Hero Section -->
  <div class="off-yg-hero">
    <div class="off-badge-blue">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_yogurts_num"]}</div>
        <div class="off-stat-lbl">{t["stat_yogurts_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_yogurts_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_countries_num"]}</div>
        <div class="off-stat-lbl">{t["stat_countries_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_countries_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_formats_num"]}</div>
        <div class="off-stat-lbl">{t["stat_formats_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_formats_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_day_num"]}</div>
        <div class="off-stat-lbl">{t["stat_day_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_day_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Trojan Horse Concept -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; color: #0c4a6e; margin-top: 0;">{t["trojan_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["trojan_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["trojan_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://fr.openfoodfacts.org/images/misc/yogurt-400x300.png" alt="What's in my yogurt badge" style="max-width: 240px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Key Discoveries -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
      {questions_html}
    </div>
  </div>

  <!-- Country Squads -->
  <div class="off-section">
    <h3 class="off-section-title">{t["squads_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
      {squads_html}
    </div>
  </div>

  <!-- Live Queries Exploration -->
  <div class="off-section">
    <h3 class="off-section-title">{t["queries_title"]}</h3>
    <p class="off-section-lead">{t["queries_lead"]}</p>
    <div style="display: flex; flex-direction: column; gap: 1rem; max-width: 860px; margin: 0 auto;">
      {queries_html}
    </div>
  </div>

  <!-- Bottom CTA Banner -->
  <div class="off-legacy-banner-blue">
    <div class="off-legacy-title-blue">🥛 {t["bottom_cta_title"]}</div>
    <div class="off-legacy-desc-blue">
      {t["bottom_cta_desc"]}
    </div>
    <div class="off-legacy-actions">
      <a href="scan-parties.html" class="off-btn off-btn-blue">🎉 {t["btn_scan_party"]}</a>
      <a href="https://world.openfoodfacts.org/category/yogurts" class="off-btn off-btn-secondary">🔍 {t["btn_add_yogurt"]}</a>
    </div>
  </div>
</div>
"""

def generate_whats_in_my_shampoo_html(data, lang="en"):
    t = SHAMPOO_TRANSLATIONS.get(lang, SHAMPOO_TRANSLATIONS["en"])
    

    
    questions = data.get("key_questions", [])
    goals = data.get("global_goals", [])
    
    questions_html = ""
    for q in questions:
        q_text = get_localized_field(q, "question", lang, default_lang="en")
        f_text = get_localized_field(q, "finding", lang, default_lang="en")
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">🧴 {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    goals_html = ""
    for g in goals:
        g_text = get_localized_field(g, "goal", lang, default_lang="en")
        goals_html += f"""
        <div class="off-card" style="border-left: 4px solid var(--off-purple);">
          <div style="font-weight: 700; font-size: 1rem; color: #581c87;">🎯 {g_text}</div>
        </div>
        """

    return f"""<style>
/* What's In My Shampoo Revamped Showcase Styles */
.off-sh-wrap {{
  --off-espresso: #0f172a;
  --off-purple: #9333ea;
  --off-purple-dark: #7e22ce;
  --off-purple-light: #fdf4ff;
  --off-purple-border: #f0abfc;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-sh-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-purple-light) 100%);
  border: 1px solid var(--off-purple-border);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(147, 51, 234, 0.06);
}}

.off-badge-purple {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #fae8ff;
  color: var(--off-purple-dark);
  border: 1px solid var(--off-purple-border);
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-sh-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: #581c87;
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-sh-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: #334155;
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(147, 51, 234, 0.08);
}}
.off-stat-num-purple {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-purple);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: #581c87;
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: #475569;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #581c87;
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #faf5ff;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-purple);
}}

.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-purple {{
  background: var(--off-purple);
  color: #ffffff;
}}
.off-btn-purple:hover {{
  background: var(--off-purple-dark);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: #0f172a;
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
}}

.off-legacy-banner-purple {{
  background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%);
  border: 1px solid #f0abfc;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title-purple {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #701a75;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc-purple {{
  font-size: 1.05rem;
  color: #86198f;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-sh-wrap">
  <!-- Hero Section -->
  <div class="off-sh-hero">
    <div class="off-badge-purple">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_shampoos_num"]}</div>
        <div class="off-stat-lbl">{t["stat_shampoos_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_shampoos_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_comp_num"]}</div>
        <div class="off-stat-lbl">{t["stat_comp_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_comp_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_inci_num"]}</div>
        <div class="off-stat-lbl">{t["stat_inci_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_inci_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_gouv_num"]}</div>
        <div class="off-stat-lbl">{t["stat_gouv_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_gouv_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Why Bathroom / Deciphering Latin -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; color: #581c87; margin-top: 0;">{t["latin_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["latin_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["latin_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://world.openfoodfacts.org/images/misc/open-beauty-facts-logo.png" alt="Open Beauty Facts Logo" style="max-width: 220px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Key Discoveries -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
      {questions_html}
    </div>
  </div>

  <!-- Worldwide Goals -->
  <div class="off-section">
    <h3 class="off-section-title">{t["goals_title"]}</h3>
    <div style="display: flex; flex-direction: column; gap: 1rem; max-width: 860px; margin: 0 auto;">
      {goals_html}
    </div>
  </div>

  <!-- Bottom CTA Banner -->
  <div class="off-legacy-banner-purple">
    <div class="off-legacy-title-purple">🧴 {t["bottom_cta_title"]}</div>
    <div class="off-legacy-desc-purple">
      {t["bottom_cta_desc"]}
    </div>
    <div class="off-legacy-actions">
      <a href="https://world.openbeautyfacts.org" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-purple">🔍 {t["btn_obf"]}</a>
      <a href="scan-parties.html" class="off-btn off-btn-secondary">🎉 {t["btn_scan"]}</a>
    </div>
  </div>
</div>
"""

def compile_campaign_pages(verbose=True):
    if verbose:
        print("🚀 Compiling Campaign Pages from YAML...")

    # 1. Opération Sodas
    sodas_data = load_mission("operation-sodas")
    for lang in SUPPORTED_LANGUAGES:
        html = generate_operation_sodas_html(sodas_data, lang=lang)
        out_path = os.path.join(REPO_ROOT, "lang", lang, "texts", "operation-sodas.html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
    fr_sodas = generate_operation_sodas_html(sodas_data, lang="fr")
    root_sodas = render_standalone_wrapper("Opération Sodas", "fr", fr_sodas)
    with open(os.path.join(REPO_ROOT, "operation-sodas.html"), "w", encoding="utf-8") as f:
        f.write(root_sodas)
    if verbose:
        print(f"  ✅ Opération Sodas compiled ({', '.join(SUPPORTED_LANGUAGES)}, root)")

    # 2. What's in my yogurt?
    yogurt_data = load_mission("whats-in-my-yogurt")
    for lang in SUPPORTED_LANGUAGES:
        html = generate_whats_in_my_yogurt_html(yogurt_data, lang=lang)
        out_path = os.path.join(REPO_ROOT, "lang", lang, "texts", "whats-in-my-yogurt.html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
    en_yogurt = generate_whats_in_my_yogurt_html(yogurt_data, lang="en")
    root_yogurt = render_standalone_wrapper("What's in my yogurt?", "en", en_yogurt)
    with open(os.path.join(REPO_ROOT, "whats-in-my-yogurt.html"), "w", encoding="utf-8") as f:
        f.write(root_yogurt)
    if verbose:
        print(f"  ✅ What's in my yogurt? compiled ({', '.join(SUPPORTED_LANGUAGES)}, root)")

    # 3. What's in my shampoo?
    shampoo_data = load_mission("whats-in-my-shampoo")
    for lang in SUPPORTED_LANGUAGES:
        html = generate_whats_in_my_shampoo_html(shampoo_data, lang=lang)
        out_path = os.path.join(REPO_ROOT, "lang", "obf", lang, "texts", "whats-in-my-shampoo.html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
    en_shampoo = generate_whats_in_my_shampoo_html(shampoo_data, lang="en")
    root_shampoo = render_standalone_wrapper("What's in my shampoo?", "en", en_shampoo)
    with open(os.path.join(REPO_ROOT, "whats-in-my-shampoo.html"), "w", encoding="utf-8") as f:
        f.write(root_shampoo)
    if verbose:
        print(f"  ✅ What's in my shampoo? compiled (obf: {', '.join(SUPPORTED_LANGUAGES)}, root)")

    return True

def main():
    success = compile_campaign_pages(verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
