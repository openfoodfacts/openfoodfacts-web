#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Scan Parties.
Reads individual YAML files from data/scan_parties/*.yaml,
validates schemas, compiles data/scan_parties.json,
and generates localized static HTML pages:
- lang/en/texts/scan-parties.html
- lang/fr/texts/scan-parties.html
"""

import glob
import json
import os
import re
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
SCAN_PARTIES_DIR = os.path.join(DATA_DIR, "scan_parties")
COMPILED_JSON = os.path.join(DATA_DIR, "scan_parties.json")

VALID_TYPES = {"upcoming", "past"}
VALID_STATUSES = {"upcoming", "completed", "cancelled"}

def validate_scan_party(item, filepath):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    stem = filename[:-5] if filename.endswith(".yaml") else filename[:-4]

    # Required: id
    r_id = item.get("id")
    if not r_id:
        errors.append(f"{filename}: missing required field 'id'")
    elif r_id != stem:
        errors.append(f"{filename}: id '{r_id}' does not match filename stem '{stem}'")
    elif not re.match(r"^[a-zA-Z0-9_-]+$", str(r_id)):
        errors.append(f"{filename}: id '{r_id}' contains invalid characters (must be alphanumeric, hyphens, or underscores)")

    # Required: title
    title = item.get("title")
    if not title or not str(title).strip():
        errors.append(f"{filename}: missing or empty required field 'title'")

    # Required: type
    evt_type = item.get("type")
    if not evt_type or evt_type not in VALID_TYPES:
        errors.append(f"{filename}: 'type' must be one of {sorted(VALID_TYPES)}, got '{evt_type}'")

    # Required: date
    date_str = item.get("date")
    if not date_str or not str(date_str).strip():
        errors.append(f"{filename}: missing required field 'date'")

    # Required: location
    location = item.get("location")
    if not location or not str(location).strip():
        errors.append(f"{filename}: missing required field 'location'")

    # Required: venue
    venue = item.get("venue")
    if not venue or not str(venue).strip():
        errors.append(f"{filename}: missing required field 'venue'")

    # Required: description
    description = item.get("description")
    if not description or not str(description).strip():
        errors.append(f"{filename}: missing required field 'description'")

    # Optional tags check
    tags = item.get("tags")
    if tags is not None and not isinstance(tags, list):
        errors.append(f"{filename}: 'tags' must be a list of strings")

    # Numeric fields check
    for num_field in ["products_scanned", "participants_count"]:
        val = item.get(num_field)
        if val is not None and not isinstance(val, (int, float)):
            errors.append(f"{filename}: '{num_field}' must be numeric or null, got {type(val).__name__}")

    return errors, warnings

def load_scan_parties(directory=SCAN_PARTIES_DIR, validate=True):
    yaml_files = sorted(glob.glob(os.path.join(directory, "*.yaml")) + glob.glob(os.path.join(directory, "*.yml")))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML files found in {directory}")

    items = []
    all_errors = []
    all_warnings = []

    for fpath in yaml_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            all_errors.append(f"Failed to parse {os.path.basename(fpath)}: {e}")
            continue

        if not isinstance(data, dict):
            all_errors.append(f"{os.path.basename(fpath)}: content must be a YAML mapping/dictionary")
            continue

        if validate:
            errs, warns = validate_scan_party(data, fpath)
            all_errors.extend(errs)
            all_warnings.extend(warns)

        items.append(data)

    upcoming_items = [i for i in items if i.get("type") == "upcoming"]
    past_items = [i for i in items if i.get("type") != "upcoming"]
    upcoming_items.sort(key=lambda x: (x.get("start_date") or "9999", x.get("title", "")))
    past_items.sort(key=lambda x: (x.get("start_date") or "0000", x.get("title", "")), reverse=True)

    sorted_items = upcoming_items + past_items
    return sorted_items, all_errors, all_warnings

def generate_html(events, lang="en"):
    is_fr = (lang == "fr")

    t = {
        "hero_badge": "Écosystème Open Food Facts • Science Citoyenne Participative" if is_fr else "Open Food Facts Ecosystem • Participatory Citizen Science",
        "hero_title_1": "Rassemblez-vous. Scannez." if is_fr else "Gather. Scan.",
        "hero_title_2": "Démocratisez les données alimentaires." if is_fr else "Democratize Food Data.",
        "hero_desc": (
            "Une <strong>Scan Party</strong> est un atelier collaboratif et chaleureux où citoyens, bénévoles et consommateurs se réunissent dans un supermarché, une épicerie coopérative ou un tiers-lieu pour photographier les codes-barres, ingrédients, tableaux nutritionnels et emballages des aliments afin de les ajouter à <strong>Open Food Facts</strong>."
            if is_fr else
            "A <strong>Scan Party</strong> is a collaborative, hands-on gathering where citizens, volunteers, and food advocates meet in local supermarkets, cooperative grocery stores, or community spaces to scan barcodes, capture ingredients, nutrition facts, and packaging specs directly for <strong>Open Food Facts</strong>."
        ),
        "btn_organize": "🚀 Déclarer / Organiser un atelier" if is_fr else "🚀 Submit / Host a Party",
        "btn_kit": "📦 Guide de l'hôte & Affiches Canva" if is_fr else "📦 Host Toolkit & Canva Flyers",
        "btn_workflows": "📱 2 façons de scanner" if is_fr else "📱 2 Ways to Scan",
        "btn_simulator": "🎮 Simulateur de scan" if is_fr else "🎮 Scan Playground",
        "btn_directory": "📅 Annuaire des ateliers" if is_fr else "📅 Events Directory",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Produits ouverts" if is_fr else "Open Products",
        "stat_products_sub": "Base de données citoyenne" if is_fr else "In public database",
        "stat_free_num": "100%",
        "stat_free_label": "Libre & ODbL" if is_fr else "Free & Open Source",
        "stat_free_sub": "Bien commun mondial" if is_fr else "Global public commons",
        "stat_countries_num": "180+",
        "stat_countries_label": "Pays touchés" if is_fr else "Countries Impacted",
        "stat_countries_sub": "À travers la planète" if is_fr else "Worldwide reach",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Contributeurs" if is_fr else "Citizen Contributors",
        "stat_volunteers_sub": "Qui s'engagent" if is_fr else "Active worldwide",
        
        "hero_photo_badge": "Photo historique" if is_fr else "Historical Gathering",
        "hero_photo_title": "1ère Assemblée Générale d'Open Food Facts à Paris" if is_fr else "1st OFF General Assembly in Paris",
        "hero_photo_desc": "Les contributeurs pionniers photographient et scannent des centaines de produits dès 2015." if is_fr else "Pioneering contributors scanning and cataloging products together in Paris back in 2015.",
        "hero_photo_loc": "Paris, France (2015)",

        "tribute_title": "❤️ Les visages et l'énergie de nos contributeurs" if is_fr else "❤️ Heart-Warming Energy: Yes They Scan!",
        "tribute_subtitle": (
            "Depuis les premiers jours d'Open Food Facts, l'énergie des scan parties repose sur des personnes bienveillantes, curieuses et déterminées à éclairer notre alimentation."
            if is_fr else
            "Since the earliest days of Open Food Facts, scan parties have been powered by kind, passionate people determined to bring food transparency to everyone."
        ),
        "tribute_c1_title": "1ère Assemblée Générale à Paris" if is_fr else "1st General Assembly in Paris",
        "tribute_c1_desc": "20 juin 2015 : Première scan party collective lors de l'assemblée générale de l'association Open Food Facts." if is_fr else "June 20, 2015: First collective scan gathering during the founding assembly of Open Food Facts in Paris.",
        "tribute_c2_title": "Scan Party à Lyon" if is_fr else "Impromptu Scan Party in Lyon",
        "tribute_c2_desc": "Juin 2015 : Expédition spontanée dans une épicerie asiatique pour décoder et indexer des dizaines de spécialités." if is_fr else "June 2015: Spontaneous expedition in an Asian grocery store to decode and index dozens of specialties.",
        "tribute_c3_title": "Marie-Claire, pionnière de la 1ère heure" if is_fr else "Marie-Claire, Pioneer Contributor",
        "tribute_c3_desc": "Chassant les codes-barres en Espagne après avoir ajouté plus de 200 produits avant même le lancement public !" if is_fr else "Hunting barcodes in Spain after cataloging over 200 products before the public launch of Open Food Facts!",
        "tribute_invitation_title": "Qui nous rejoint ensuite ?" if is_fr else "Joining us next...",
        "tribute_invitation_1": "Vous ? :-)" if is_fr else "You? :-)",
        "tribute_invitation_2": "Votre famille ? :-)" if is_fr else "Your family? :-)",
        "tribute_invitation_3": "Vos amis et collègues ? :-)" if is_fr else "Your friends? :-)",
        "tribute_cta": (
            "Partagez vos photos d'ateliers avec le hashtag <strong>#scanparty</strong> ou écrivez-nous à <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a> !"
            if is_fr else
            "Share your scan party photos with <strong>#scanparty</strong> or send them to <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>!"
        ),

        "concept_badge": "Concept & Mission",
        "concept_title": "Qu'est-ce qu'une Scan Party ?" if is_fr else "What is a Scan Party?",
        "concept_lead": (
            "C'est un événement convivial et formateur où l'on joint l'utile à l'agréable : découvrir l'envers des étiquettes alimentaires tout en enrichissant le plus grand bien commun mondial sur l'alimentation."
            if is_fr else
            "A fun, educational, and impactful workshop combining social teamwork with citizen science: decipher food labels while enriching the world's largest open food commons."
        ),
        "pillar_1_title": "Enrichir la base ouverte" if is_fr else "Enrich Open Food Facts",
        "pillar_1_desc": "Ajouter des produits inédits et mettre à jour ingrédients, tableaux nutritionnels et emballages recyclables." if is_fr else "Add new products and refresh ingredient lists, nutrition tables, and recyclable packaging specs.",
        "pillar_2_title": "Éclairer les consommateurs" if is_fr else "Empower Consumers",
        "pillar_2_desc": "Donner à chacun des informations claires et vérifiées pour choisir une alimentation plus saine et durable." if is_fr else "Provide verified, transparent facts to help everyone make healthier and more sustainable food choices.",
        "pillar_3_title": "Créer du lien social" if is_fr else "Promote Collaboration",
        "pillar_3_desc": "Partager un moment chaleureux entre voisins, collègues, étudiants ou coopérateurs autour de l'alimentation." if is_fr else "Connect neighbors, students, coworkers, and co-op members through engaging, collaborative teamwork.",
        "pillar_4_title": "Sensibiliser & Éduquer" if is_fr else "Raise Food Literacy",
        "pillar_4_desc": "Comprendre le Nutri-Score, l'Éco-Score, la classification NOVA des aliments ultra-transformés et les additifs." if is_fr else "Demystify Nutri-Score, Eco-Score, NOVA ultra-processing groups, and additive classifications.",

        "wf_badge": "2 Méthodes Disponibles" if is_fr else "2 Flexible Workflows",
        "wf_title": "Deux façons simples d'organiser votre atelier" if is_fr else "2 Ways to Run Your Scan Party",
        "wf_lead": (
            "Que vous disposiez d'un excellent Wi-Fi ou que vous soyez dans le sous-sol d'un magasin sans réseau, Open Food Facts s'adapte !"
            if is_fr else
            "Whether you have high-speed Wi-Fi in a classroom or zero cellular reception in a supermarket basement, Open Food Facts has you covered!"
        ),
        "wf1_badge": "Idéal avec Wi-Fi / 4G" if is_fr else "Best with Wi-Fi / 4G",
        "wf1_title": "Méthode 1 : Scan en direct via l'App Mobile" if is_fr else "Method 1: Live Mobile App Scanning",
        "wf1_desc": "Les participants téléchargent l'application gratuite Open Food Facts et ajoutent les produits en direct." if is_fr else "Participants install the free Open Food Facts mobile app, scan items, and add photos directly on their phones.",
        "wf1_step1_title": "Installer l'application gratuite" if is_fr else "Install Free App",
        "wf1_step1_desc": "Disponible sur iOS et Android sans publicité ni compte payant." if is_fr else "Available on iOS and Android without ads or paywalls.",
        "wf1_step2_title": "Former des binômes" if is_fr else "Pair Up Participants",
        "wf1_step2_desc": "L'un prend le produit en main, le second scanne le code-barres et prend les photos." if is_fr else "One person handles products, the second scans barcodes and captures labels.",
        "wf1_step3_title": "Photographier les 4 faces clés" if is_fr else "Capture 4 Key Angles",
        "wf1_step3_desc": "Face avant, ingrédients, tableau nutritionnel et informations d'emballage." if is_fr else "Front packaging, ingredients list, nutrition table, and recycling specs.",
        "wf1_step4_title": "Reconnaissance OCR & Scores immédiats" if is_fr else "Instant AI & Score Calculation",
        "wf1_step4_desc": "L'IA intégrée extrait le texte et calcule Nutri-Score et Éco-Score en direct !" if is_fr else "Built-in OCR extracts text and computes Nutri-Score & Eco-Score on the spot!",
        "wf1_btn": "📱 Télécharger l'App Open Food Facts" if is_fr else "📱 Download Open Food Facts App",

        "wf2_badge": "Sans Wi-Fi ni réseau !" if is_fr else "No Wi-Fi Needed!",
        "wf2_title": "Méthode 2 : Photos Hors-Ligne & Import Pro" if is_fr else "Method 2: Offline Photos & Producer Import",
        "wf2_desc": (
            "En sous-sol ou sans connexion, photographiez les produits avec l'appareil photo de votre smartphone en respectant la séquence d'ancrage, puis importez le dossier par lot sur la plateforme Pro !"
            if is_fr else
            "When scanning in basements with no Wi-Fi, take photos using standard camera phones following the barcode anchor sequence, then bulk upload the folder to the Producer Platform!"
        ),
        "wf2_step1_title": "Photos consécutives au smartphone" if is_fr else "Sequential Camera Photos",
        "wf2_step1_desc": "Utilisez simplement l'application appareil photo de vos smartphones." if is_fr else "Use standard camera phones to snap clear photos.",
        "wf2_step2_title": "Photo du code-barres en premier" if is_fr else "Barcode Photo First",
        "wf2_step2_desc": "Le code-barres sert de balise de séparation pour notre algorithme de regroupement." if is_fr else "The barcode photo serves as the separator delimiter for automatic pairing.",
        "wf2_step3_title": "Centraliser les photos" if is_fr else "Collect Photo Folders",
        "wf2_step3_desc": "Rassemblez les dossiers de photos sur l'ordinateur de l'hôte après l'atelier." if is_fr else "Gather photo folders onto the host laptop after the event.",
        "wf2_step4_title": "Glisser-déposer sur la plateforme Pro" if is_fr else "Drag & Drop Bulk Upload",
        "wf2_step4_desc": "Téléversez tout le dossier sur pro.openfoodfacts.org pour un traitement automatique !" if is_fr else "Upload the complete folder to pro.openfoodfacts.org for batch processing!",
        "wf2_btn": "🌐 Accéder à la Plateforme Producteur (pro.openfoodfacts.org)" if is_fr else "🌐 Visit Producer Platform (pro.openfoodfacts.org)",

        "seq_title": "La séquence de photos « Code-barres Ancre »" if is_fr else "The 'Barcode Anchor' Photo Sequence Protocol",
        "seq_desc": (
            "Pour la méthode hors-ligne, suivez scrupuleusement cet ordre pour chaque produit : le code-barres sert de point de départ pour rattacher les photos suivantes au bon produit."
            if is_fr else
            "For offline scanning, follow this strict sequence for each product: the barcode photo acts as the delimiter so the system correctly groups consecutive packaging photos."
        ),
        "seq_pill": "Étape 1 • Ancre" if is_fr else "Step 1 • Anchor",
        "seq_s1_title": "1. Code-barres" if is_fr else "1. Barcode Photo",
        "seq_s1_desc": "À plat, bien net avec chiffres visibles (sert de séparateur)." if is_fr else "Flat and sharp with visible digits (acts as delimiter).",
        "seq_s2_title": "2. Face avant" if is_fr else "2. Front Packaging",
        "seq_s2_desc": "Nom du produit, marque, logos officiels et poids net." if is_fr else "Product name, brand, logos, and net weight/volume.",
        "seq_s3_title": "3. Ingrédients" if is_fr else "3. Ingredients List",
        "seq_s3_desc": "Liste intégrale des ingrédients et mentions d'allergènes." if is_fr else "Full ingredients list and allergen statements.",
        "seq_s4_title": "4. Tableau nutritionnel" if is_fr else "4. Nutrition Table",
        "seq_s4_desc": "Valeurs pour 100g / 100ml (calories, sucres, sel, graisses)." if is_fr else "Values per 100g / 100ml (calories, sugars, fats, salt).",
        "seq_s5_title": "5. Emballage & Tri" if is_fr else "5. Packaging & Eco",
        "seq_s5_desc": "Consignes de tri (Triman), matières plastiques (PET, PEHD, etc.)." if is_fr else "Recycling symbols (Triman), material types (PET, HDPE, PP).",

        "sim_badge": "Simulateur Interactif" if is_fr else "Interactive Playground",
        "sim_title": "Simulateur de Scan Party" if is_fr else "Scan Party Simulator",
        "sim_lead": "Cliquez sur les produits du rayon pour observer comment l'analyse s'effectue en temps réel !" if is_fr else "Click items on the shelf to see barcode scanning and score calculation in real time!",
        "sim_shelf_title": "Rayon du magasin :" if is_fr else "Store Shelf Products:",
        "sim_card_title": "Fiche Open Food Facts en direct" if is_fr else "Live Open Food Facts Inspector",
        "sim_scan_btn": "Scanner ce produit &rarr;" if is_fr else "Scan this product &rarr;",
        "sim_goal_label": "Progression de l'atelier :" if is_fr else "Scan Party Goal Progress:",

        "kit_badge": "Ressources & Guides" if is_fr else "Host Resources & Kit",
        "kit_title": "La boîte à outils de l'organisateur" if is_fr else "Host Toolkit & Marketing Materials",
        "kit_lead": "Tout ce dont vous avez besoin pour préparer, animer et communiquer sur votre Scan Party :" if is_fr else "Everything you need to prepare, promote, and host your local Scan Party with ease:",
        "kit_canva_title": "Modèles d'affiches Canva" if is_fr else "Canva Poster Templates",
        "kit_canva_desc": "Affiches A4 personnalisables, bannières pour réseaux sociaux et fiches d'émargement prêtes à imprimer." if is_fr else "Customizable A4 posters, social media banners, and printable sign-up sheets in Canva.",
        "kit_canva_btn": "🎨 Ouvrir le dossier Canva" if is_fr else "🎨 Open Canva Design Folder",
        "kit_pdf_title": "Guide méthodologique PDF" if is_fr else "PDF Host Handbook",
        "kit_pdf_desc": "Le guide étape par étape de 12 pages pour préparer votre salle, contacter les magasins et animer les équipes." if is_fr else "A comprehensive 12-page step-by-step handbook covering store outreach, room setup, and team facilitation.",
        "kit_pdf_btn": "📥 Télécharger le Guide PDF" if is_fr else "📥 Download PDF Guide",
        "kit_blog_en_title": "Article méthodologique (EN)" if is_fr else "Workshop Guide Article (EN)",
        "kit_blog_en_desc": "Article de blog officiel détaillant l'organisation d'un atelier citoyen participatif." if is_fr else "Comprehensive blog post guide: 'Organise a scan party / participative workshop!'",
        "kit_blog_en_btn": "🌐 Lire l'article (EN)" if is_fr else "🌐 Read Article (EN)",
        "kit_blog_fr_title": "Article méthodologique (FR)" if is_fr else "French Workshop Article",
        "kit_blog_fr_desc": "Guide pratique en français : « Organisez une scan party emballages » avec retours d'expérience." if is_fr else "Official French announcement & guide: 'Organisez une scan party emballages'.",
        "kit_blog_fr_btn": "🌐 Lire l'article (FR)" if is_fr else "🌐 Read Article (FR)",

        "chk_badge": "Préparation" if is_fr else "Event Preparation",
        "chk_title": "La Checklist interactive de l'hôte" if is_fr else "Interactive Host Checklist",
        "chk_lead": "Cochez vos étapes pour ne rien oublier lors de l'organisation de votre atelier :" if is_fr else "Track your preparation progress step-by-step to ensure a smooth, rewarding workshop:",

        "dir_badge": "Réseau Mondial" if is_fr else "Global Network",
        "dir_title": "Annuaire des Scan Parties" if is_fr else "Scan Parties Directory",
        "dir_lead": "Découvrez les ateliers à venir et revivez les moments forts des scan parties passées :" if is_fr else "Explore upcoming gatherings and historical scan parties from around the world:",
        "filter_all": "Tous les ateliers" if is_fr else "All Events",
        "filter_upcoming": "À venir" if is_fr else "Upcoming",
        "filter_past": "Éditions passées" if is_fr else "Past Events",
        "search_placeholder": "🔍 Filtrer par ville, lieu, pays..." if is_fr else "🔍 Filter by city, venue, country...",
        "declare_banner_title": "Vous organisez une Scan Party ? Faites-la connaître !" if is_fr else "Hosting a Scan Party? Get it listed here!",
        "declare_banner_desc": (
            "Ajoutez votre atelier en 1 clic via un ticket GitHub ou une Pull Request, exactement comme pour les réutilisations et publications scientifiques."
            if is_fr else
            "Add your scan party in 1 click via a pre-filled GitHub issue or a Pull Request, just like reuses and scientific papers."
        ),
        "btn_declare_gh": "🚀 Déclarer via GitHub (1 clic)" if is_fr else "🚀 Submit via GitHub (1-Click)",
        "btn_declare_pr": "✏️ Proposer un fichier YAML (PR)" if is_fr else "✏️ Propose a YAML file (PR)",
        "btn_declare_drawer": "📋 Générateur YAML en ligne" if is_fr else "📋 Online YAML Generator",

        "comm_title": "Échanger avec la communauté" if is_fr else "Connect with the Community",
        "comm_lead": "Des questions sur l'organisation ou besoin d'aide pour animer votre groupe ?" if is_fr else "Need guidance, ideas, or venue advice? Connect directly with organizers and OFF staff:",
        "slack_global_title": "Canal Slack International",
        "slack_global_desc": "Rejoignez #scanparty pour échanger avec des organisateurs du monde entier." if is_fr else "Join #scanparty on the official Slack for global coordination and tips.",
        "slack_fr_title": "Canal Slack Francophone",
        "slack_fr_desc": "Rejoignez #scanparty_fr pour organiser des ateliers en France, Belgique, Suisse, etc." if is_fr else "Join #scanparty_fr to collaborate with French-speaking organizers.",
        "contact_lead_title": "Contact Équipe Communauté" if is_fr else "Community Lead Support",
        "contact_lead_desc": "Écrivez directement à Gala (chargée de communauté Open Food Facts) pour vous accompagner." if is_fr else "Reach out to Gala (Community Lead) for assistance, materials, or introductions.",

        "partner_badge": "Partenaire de Soutien" if is_fr else "Supporting Partner",
        "partner_title": "Avec le soutien de la Fondation de France" if is_fr else "Supported by Fondation de France",
        "partner_desc": (
            "Open Food Facts remercie chaleureusement la <strong>Fondation de France</strong> pour son soutien déterminant aux projets de science citoyenne, d'engagement participatif et d'ouverture des données pour une alimentation saine, transparente et durable accessible à tous."
            if is_fr else
            "Open Food Facts warmly thanks the <strong>Fondation de France</strong> for its generous support of citizen participatory science, civic engagement, and open food data democratization for healthier and more sustainable food systems."
        ),
        "partner_link_text": "En savoir plus sur la Fondation de France &rarr;" if is_fr else "Learn more about Fondation de France &rarr;",
    }

    hero_photos = [
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty-off-general-meeting-20150620.jpg",
            "title": "1ère Assemblée Générale d'Open Food Facts à Paris" if is_fr else "1st OFF General Assembly in Paris",
            "loc": "Paris, France (2015)",
            "tag": "Photo historique" if is_fr else "Historical Gathering",
            "desc": "Les contributeurs pionniers photographient et scannent des centaines de produits dès 2015." if is_fr else "Pioneering contributors scanning and cataloging products together in Paris back in 2015."
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty-lyon-20150601.jpg",
            "title": "Scan Party épicerie asiatique à Lyon" if is_fr else "Impromptu Asian Grocery Scan Party in Lyon",
            "loc": "Lyon, France (2015)",
            "tag": "Exploration" if is_fr else "Field Expedition",
            "desc": "Déchiffrage de produits internationaux et spécialités multilingues." if is_fr else "Deciphering international packaging, multilingual lists, and specialty food labels."
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/marie-claire-scan-spain.jpg",
            "title": "Marie-Claire en supermarché en Espagne" if is_fr else "Marie-Claire Hunting Barcodes in Spain",
            "loc": "Espagne (2015)" if is_fr else "Spain (2015)",
            "tag": "Pionnière OFF" if is_fr else "Pioneer Contributor",
            "desc": "Marie-Claire a ajouté plus de 200 produits avant le lancement public de la plateforme." if is_fr else "Marie-Claire added over 200 products before the public launch of Open Food Facts!"
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty.640x480.png",
            "title": "Yes They Scan! Bannière de ralliement" if is_fr else "Yes They Scan! Landmark Rallying Banner",
            "loc": "Mouvement mondial" if is_fr else "Global Movement",
            "tag": "Énergie bénévole" if is_fr else "Volunteer Spirit",
            "desc": "Le visuel iconique des premières scan parties mobilisant des milliers de citoyens." if is_fr else "The landmark visual celebrating the worldwide energy of citizen barcode scanners."
        },
        {
            "url": "https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=800&q=80",
            "title": "Atelier en Supermarché Coopératif" if is_fr else "Cooperative Supermarket Scan Workshop",
            "loc": "France",
            "tag": "Atelier Coop" if is_fr else "Co-op Workshop",
            "desc": "Les coopérateurs cartographient collectivement la composition de leurs rayons." if is_fr else "Shoppers collaboratively mapping nutritional values and environmental metrics in-store."
        }
    ]

    sample_products = [
        {
            "id": 1,
            "name": "Pâte à tartiner noisettes bio" if is_fr else "Organic Hazelnut Chocolate Spread",
            "brand": "Bio Terroir",
            "barcode": "3017620422003",
            "icon": "🌰",
            "nutri": "E",
            "nutriColor": "#ef4444",
            "nova": "4",
            "eco": "C",
            "packaging": "Pot en verre & couvercle alu" if is_fr else "Glass Jar & Aluminum Lid"
        },
        {
            "id": 2,
            "name": "Lait d'avoine sans sucre 1L" if is_fr else "Oat Milk Unsweetened 1L",
            "brand": "Green Harvest",
            "barcode": "7350041864009",
            "icon": "🥛",
            "nutri": "A",
            "nutriColor": "#22c55e",
            "nova": "1",
            "eco": "A",
            "packaging": "Brique Tetra Pak" if is_fr else "Tetra Pak Carton"
        },
        {
            "id": 3,
            "name": "Chocolat noir 85% équitable" if is_fr else "Artisan Dark Chocolate 85%",
            "brand": "Cacao Libre",
            "barcode": "7613035821102",
            "icon": "🍫",
            "nutri": "B",
            "nutriColor": "#84cc16",
            "nova": "2",
            "eco": "B",
            "packaging": "Papier recyclable & feuille alu" if is_fr else "Recycled Paper & Foil"
        },
        {
            "id": 4,
            "name": "Kombucha citron pétillant" if is_fr else "Sparkling Lemon Kombucha",
            "brand": "Pure Bubbles",
            "barcode": "3270190201104",
            "icon": "🍹",
            "nutri": "B",
            "nutriColor": "#84cc16",
            "nova": "3",
            "eco": "A",
            "packaging": "Bouteille en verre consignée" if is_fr else "Returnable Glass Bottle"
        }
    ]

    checklist_items = [
        {"id": 1, "text": "Contacter le magasin ou lieu d'accueil pour convenir de la date" if is_fr else "Contact the store or venue to agree on date and time"},
        {"id": 2, "text": "Télécharger les affiches Canva et imprimer la signalétique" if is_fr else "Download Canva flyers and print welcoming signage"},
        {"id": 3, "text": "Choisir votre méthode : App Mobile (Wi-Fi) ou Photos Hors-Ligne" if is_fr else "Select workflow: Live Mobile App or Offline Anchor Photos"},
        {"id": 4, "text": "Annoncer l'atelier sur Slack (#scanparty / #scanparty_fr) et vos réseaux" if is_fr else "Announce on Slack (#scanparty / #scanparty_fr) and social media"},
        {"id": 5, "text": "Former les binômes : un manipulateur de produit, un photographe" if is_fr else "Pair participants: one handles products, one scans/photographs"},
        {"id": 6, "text": "Après l'atelier : téléversement des photos sur pro.openfoodfacts.org et célébration !" if is_fr else "Post-event: bulk upload photos to pro.openfoodfacts.org and celebrate!"}
    ]

    events_json = json.dumps(events, ensure_ascii=False)
    hero_photos_json = json.dumps(hero_photos, ensure_ascii=False)
    sample_products_json = json.dumps(sample_products, ensure_ascii=False)
    checklist_json = json.dumps(checklist_items, ensure_ascii=False)

    return f"""<style>
/* Scoped styles for Scan Party page - adhering to Open Food Facts clean white/slate design system */
.sp-page {{
  max-width: 1200px;
  margin: 0 auto 3rem;
  font-family: inherit;
  color: #0f172a;
}}

.sp-header {{
  margin: 1.5rem 0 1.25rem;
  text-align: center;
}}
.sp-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 1rem;
}}
.sp-badge-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ea580c;
  animation: spPulse 2s infinite;
}}
@keyframes spPulse {{
  0%, 100% {{ opacity: 1; transform: scale(1); }}
  50% {{ opacity: 0.4; transform: scale(0.85); }}
}}

.sp-title {{
  font-size: 2.3rem;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.2;
  margin: 0 0 0.85rem;
}}
.sp-title-highlight {{
  color: #ea580c;
}}
.sp-lead {{
  font-size: 1.05rem;
  color: #475569;
  line-height: 1.6;
  max-width: 860px;
  margin: 0 auto 1.5rem;
}}

.sp-actions-bar {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  margin: 1.25rem 0 1.75rem;
}}
.sp-btn {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
  padding: 0.55rem 1.15rem !important;
  border-radius: 10px !important;
  text-decoration: none !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
  margin: 0 !important;
}}
.sp-btn-primary {{
  background: #ea580c !important;
  color: #ffffff !important;
  border: 1px solid #ea580c !important;
}}
.sp-btn-primary:hover {{
  background: #c2410c !important;
  border-color: #c2410c !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25) !important;
}}
.sp-btn-secondary {{
  background: #ffffff !important;
  color: #1e293b !important;
  border: 1px solid #cbd5e1 !important;
}}
.sp-btn-secondary:hover {{
  background: #f8fafc !important;
  border-color: #94a3b8 !important;
  color: #0f172a !important;
}}
.sp-btn-emerald {{
  background: #16a34a !important;
  color: #ffffff !important;
  border: 1px solid #16a34a !important;
}}
.sp-btn-emerald:hover {{
  background: #15803d !important;
  border-color: #15803d !important;
  color: #ffffff !important;
}}

.sp-impact-hero {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  margin: 1.25rem auto 2.25rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-around;
  gap: 1.25rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}}
.sp-stat-item {{
  text-align: center;
  flex: 1 1 150px;
}}
.sp-stat-number {{
  font-size: 2.1rem;
  font-weight: 900;
  color: #ea580c;
  line-height: 1.1;
  margin-bottom: 0.2rem;
  font-family: system-ui, -apple-system, sans-serif;
}}
.sp-stat-label {{
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.15rem;
}}
.sp-stat-sub {{
  font-size: 0.78rem;
  color: #64748b;
}}
.sp-stat-divider {{
  width: 1px;
  height: 44px;
  background: #e2e8f0;
  display: none;
}}
@media (min-width: 768px) {{
  .sp-stat-divider {{
    display: block;
  }}
}}

.sp-hero-photo-wrap {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 1.25rem;
  margin: 1.5rem auto 2.5rem;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}}
.sp-main-photo-frame {{
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  background: #0f172a;
  aspect-ratio: 16 / 9;
  max-height: 480px;
}}
.sp-main-photo-img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}}
.sp-main-photo-frame:hover .sp-main-photo-img {{
  transform: scale(1.02);
}}
.sp-photo-overlay-top {{
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(15, 23, 42, 0.82);
  backdrop-filter: blur(6px);
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}}
.sp-photo-overlay-bottom {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.6) 60%, transparent 100%);
  padding: 1.5rem 1.25rem 1rem;
  color: #ffffff;
  text-align: left;
}}
.sp-photo-overlay-tag {{
  color: #fb923c;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.25rem;
}}
.sp-photo-overlay-title {{
  font-size: 1.2rem;
  font-weight: 800;
  margin: 0 0 0.35rem;
  color: #ffffff;
}}
.sp-photo-overlay-desc {{
  font-size: 0.85rem;
  color: #cbd5e1;
  margin: 0;
  line-height: 1.45;
}}
.sp-thumbs-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.65rem;
  margin-top: 0.85rem;
}}
.sp-thumb-btn {{
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid transparent;
  padding: 0;
  background: #0f172a;
  cursor: pointer;
  height: 64px;
  transition: all 0.2s ease;
  position: relative;
}}
.sp-thumb-btn img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.75;
  transition: opacity 0.2s ease;
}}
.sp-thumb-btn.active {{
  border-color: #ea580c;
  box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.35);
}}
.sp-thumb-btn.active img, .sp-thumb-btn:hover img {{
  opacity: 1;
}}

.sp-tribute-box {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.75rem 1.5rem;
  margin: 2rem 0;
  box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}}
.sp-tribute-header {{
  text-align: center;
  margin-bottom: 1.5rem;
}}
.sp-tribute-header h3 {{
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-tribute-header p {{
  font-size: 0.95rem;
  color: #475569;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.5;
}}
.sp-tribute-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}}
.sp-tribute-card {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}
.sp-tribute-img-wrap {{
  height: 180px;
  background: #e2e8f0;
  overflow: hidden;
}}
.sp-tribute-img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}}
.sp-tribute-card:hover .sp-tribute-img {{
  transform: scale(1.03);
}}
.sp-tribute-body {{
  padding: 1rem;
  flex: 1;
}}
.sp-tribute-body h4 {{
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.35rem;
}}
.sp-tribute-body p {{
  font-size: 0.84rem;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}}
.sp-tribute-invite {{
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
}}
.sp-tribute-invite-grid {{
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  font-size: 1.15rem;
  font-weight: 800;
  color: #ea580c;
  margin: 0.65rem 0;
}}

.sp-section {{
  margin: 3rem 0;
  text-align: left;
}}
.sp-section-center {{
  text-align: center;
  margin-bottom: 1.75rem;
}}
.sp-section-title {{
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-section-subtitle {{
  font-size: 1rem;
  color: #475569;
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.55;
}}
.sp-pillars-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}}
.sp-pillar-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  transition: border-color 0.2s ease, transform 0.2s ease;
}}
.sp-pillar-card:hover {{
  border-color: #cbd5e1;
  transform: translateY(-2px);
}}
.sp-pillar-icon {{
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  margin-bottom: 1rem;
}}
.sp-icon-orange {{ background: #fff7ed; color: #ea580c; }}
.sp-icon-emerald {{ background: #f0fdf4; color: #16a34a; }}
.sp-icon-blue {{ background: #eff6ff; color: #0284c7; }}
.sp-icon-purple {{ background: #faf5ff; color: #7c3aed; }}
.sp-pillar-card h4 {{
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-pillar-card p {{
  font-size: 0.88rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}}

.sp-workflows-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}}
.sp-wf-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}}
.sp-wf-card.highlight {{
  border-color: #cbd5e1;
}}
.sp-wf-top-badge {{
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 0.75rem;
}}
.sp-badge-live {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
.sp-badge-offline {{ background: #eff6ff; color: #0369a1; border: 1px solid #bae6fd; }}
.sp-wf-title {{
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-wf-desc {{
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}}
.sp-wf-steps {{
  margin: 0 0 1.5rem;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}}
.sp-wf-step {{
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  font-size: 0.85rem;
}}
.sp-wf-num {{
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ea580c;
  color: #ffffff;
  font-weight: 800;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}}
.sp-wf-num-blue {{
  background: #0284c7;
}}
.sp-wf-step strong {{
  color: #0f172a;
  display: block;
}}
.sp-wf-step span {{
  color: #64748b;
  font-size: 0.8rem;
}}

.sp-seq-box {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1.75rem 0 2.5rem;
}}
.sp-seq-header {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}}
.sp-seq-header h4 {{
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}}
.sp-seq-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.85rem;
}}
.sp-seq-card {{
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 1rem;
  position: relative;
  text-align: left;
}}
.sp-seq-card.primary-anchor {{
  border: 2px solid #ea580c;
}}
.sp-seq-pill {{
  position: absolute;
  top: -9px;
  left: 10px;
  background: #ea580c;
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: 4px;
}}
.sp-seq-card h5 {{
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0.4rem 0 0.25rem;
}}
.sp-seq-card p {{
  font-size: 0.76rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}}

.sp-sim-box {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 1.75rem;
  margin: 2rem 0;
  box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}}
.sp-sim-layout {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.25rem;
}}
.sp-shelf-items {{
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}}
.sp-prod-card {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}}
.sp-prod-card:hover, .sp-prod-card.active {{
  background: #fff7ed;
  border-color: #ea580c;
  transform: translateX(4px);
}}
.sp-prod-emoji {{
  font-size: 1.8rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
}}
.sp-prod-info h5 {{
  margin: 0 0 0.15rem;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}}
.sp-prod-info p {{
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  color: #64748b;
}}
.sp-prod-ean {{
  font-family: monospace;
  font-size: 0.72rem;
  background: #e2e8f0;
  padding: 1px 6px;
  border-radius: 4px;
  color: #334155;
}}

.sp-inspector {{
  background: #0f172a;
  color: #ffffff;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.sp-inspector-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}}
.sp-inspector-title {{
  font-size: 0.95rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.sp-inspector-prod-title {{
  font-size: 1.2rem;
  font-weight: 800;
  margin: 0 0 0.25rem;
  color: #ffffff;
}}
.sp-inspector-scores {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.65rem;
  margin: 1rem 0;
}}
.sp-score-box {{
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.65rem 0.35rem;
  text-align: center;
}}
.sp-score-label {{
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  display: block;
  margin-bottom: 0.25rem;
}}
.sp-score-val {{
  font-size: 1.15rem;
  font-weight: 900;
}}
.sp-progress-box {{
  margin-top: 1rem;
  border-top: 1px solid #334155;
  padding-top: 0.85rem;
}}
.sp-progress-labels {{
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  margin-bottom: 0.45rem;
  color: #cbd5e1;
}}
.sp-progress-bar-bg {{
  width: 100%;
  height: 8px;
  background: #334155;
  border-radius: 9999px;
  overflow: hidden;
}}
.sp-progress-bar-fill {{
  height: 100%;
  background: #ea580c;
  width: 0%;
  transition: width 0.3s ease;
}}

.sp-kit-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0;
}}
.sp-kit-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}}
.sp-kit-card h4 {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-kit-card p {{
  font-size: 0.84rem;
  color: #64748b;
  margin: 0 0 1rem;
  line-height: 1.45;
}}

.sp-checklist-wrap {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  margin: 2rem 0;
}}
.sp-check-items {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.65rem;
  margin-top: 1rem;
}}
.sp-check-label {{
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
  transition: all 0.15s ease;
}}
.sp-check-label:hover {{
  border-color: #ea580c;
  background: #fff7ed;
}}
.sp-check-label input {{
  width: 18px;
  height: 18px;
  accent-color: #ea580c;
  cursor: pointer;
}}
.sp-check-label.done {{
  text-decoration: line-through;
  color: #94a3b8;
  background: #f1f5f9;
}}

.sp-dir-controls {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  margin: 1.5rem 0;
}}
.sp-filter-tabs {{
  display: inline-flex;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 3px;
  gap: 3px;
}}
.sp-filter-tab {{
  border: none;
  background: transparent;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.sp-filter-tab.active {{
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 5px rgba(0,0,0,0.06);
}}
.sp-search-input {{
  padding: 0.5rem 0.85rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  font-size: 0.88rem !important;
  max-width: 280px;
  margin: 0 !important;
}}

.sp-events-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0;
}}
.sp-event-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  transition: transform 0.2s ease, border-color 0.2s ease;
}}
.sp-event-card:hover {{
  transform: translateY(-2px);
  border-color: #cbd5e1;
}}
.sp-event-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.65rem;
}}
.sp-event-badge {{
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}}
.sp-badge-upcoming {{ background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; }}
.sp-badge-past {{ background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}
.sp-event-date {{
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 600;
}}
.sp-event-title {{
  font-size: 1.12rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.35rem;
}}
.sp-event-loc {{
  font-size: 0.84rem;
  color: #475569;
  font-weight: 600;
  margin-bottom: 0.65rem;
}}
.sp-event-desc {{
  font-size: 0.84rem;
  color: #64748b;
  margin-bottom: 0.85rem;
  line-height: 1.45;
}}
.sp-event-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
}}
.sp-event-tag {{
  font-size: 0.68rem;
  background: #f8fafc;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}}
.sp-event-footer {{
  border-top: 1px solid #f1f5f9;
  padding-top: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.sp-declare-banner {{
  background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
  border: 1px solid #bbf7d0;
  border-radius: 16px;
  padding: 1.5rem;
  margin: 2rem 0;
  text-align: left;
}}
.sp-declare-banner h3 {{
  font-size: 1.25rem;
  font-weight: 800;
  color: #166534;
  margin: 0 0 0.35rem;
}}
.sp-declare-banner p {{
  font-size: 0.92rem;
  color: #14532d;
  margin: 0 0 1rem;
}}
.sp-declare-drawer {{
  display: none;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 1.5rem;
  margin-top: 1rem;
}}
.sp-declare-drawer.open {{
  display: block;
}}

.sp-partner-section {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.75rem;
  margin: 2.5rem 0 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}}
.sp-partner-badge-col {{
  flex: 0 0 auto;
}}
.sp-partner-logo-box {{
  width: 140px;
  height: 80px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0.5rem;
}}
.sp-partner-logo-text {{
  font-weight: 900;
  font-size: 1rem;
  color: #b91c1c;
  letter-spacing: -0.02em;
  line-height: 1.1;
}}
.sp-partner-logo-sub {{
  font-size: 0.65rem;
  color: #475569;
  font-weight: 600;
}}
.sp-partner-text-col {{
  flex: 1 1 300px;
}}
.sp-partner-tag {{
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #ea580c;
  letter-spacing: 0.04em;
  display: block;
  margin-bottom: 0.25rem;
}}
.sp-partner-title {{
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem;
}}
.sp-partner-desc {{
  font-size: 0.88rem;
  color: #475569;
  line-height: 1.55;
  margin: 0 0 0.65rem;
}}
.sp-partner-link {{
  font-size: 0.84rem;
  font-weight: 700;
  color: #ea580c;
  text-decoration: none;
}}
.sp-partner-link:hover {{
  text-decoration: underline;
}}

.sp-community-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0 2.5rem;
}}
.sp-comm-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.35rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.sp-comm-card h4 {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.35rem;
}}
.sp-comm-card p {{
  font-size: 0.82rem;
  color: #64748b;
  margin: 0 0 1rem;
}}
</style>

<div class="sp-page">
  
  <canvas id="sp-confetti-canvas" style="position: fixed; inset: 0; pointer-events: none; z-index: 99999; width: 100%; height: 100%;"></canvas>

  <!-- Top Hero Header -->
  <div class="sp-header">
    <div class="sp-badge">
      <span class="sp-badge-dot"></span>
      <span>{t["hero_badge"]}</span>
    </div>
    
    <h1 class="sp-title">
      {t["hero_title_1"]}<br/>
      <span class="sp-title-highlight">{t["hero_title_2"]}</span>
    </h1>

    <p class="sp-lead">
      {t["hero_desc"]}
    </p>

    <!-- Quick action links -->
    <div class="sp-actions-bar">
      <a href="#events" class="sp-btn sp-btn-primary">
        {t["btn_organize"]}
      </a>
      <a href="#marketing" class="sp-btn sp-btn-secondary">
        {t["btn_kit"]}
      </a>
      <a href="#workflows" class="sp-btn sp-btn-secondary">
        {t["btn_workflows"]}
      </a>
      <a href="#simulator" class="sp-btn sp-btn-secondary">
        {t["btn_simulator"]}
      </a>
      <a href="#events" class="sp-btn sp-btn-secondary">
        {t["btn_directory"]}
      </a>
    </div>
  </div>

  <!-- Impact Statistics Hero Bar -->
  <div class="sp-impact-hero">
    <div class="sp-stat-item">
      <div class="sp-stat-number">{t["stat_products_num"]}</div>
      <div class="sp-stat-label">{t["stat_products_label"]}</div>
      <div class="sp-stat-sub">{t["stat_products_sub"]}</div>
    </div>
    <div class="sp-stat-divider"></div>
    <div class="sp-stat-item">
      <div class="sp-stat-number">{t["stat_free_num"]}</div>
      <div class="sp-stat-label">{t["stat_free_label"]}</div>
      <div class="sp-stat-sub">{t["stat_free_sub"]}</div>
    </div>
    <div class="sp-stat-divider"></div>
    <div class="sp-stat-item">
      <div class="sp-stat-number">{t["stat_countries_num"]}</div>
      <div class="sp-stat-label">{t["stat_countries_label"]}</div>
      <div class="sp-stat-sub">{t["stat_countries_sub"]}</div>
    </div>
    <div class="sp-stat-divider"></div>
    <div class="sp-stat-item">
      <div class="sp-stat-number">{t["stat_volunteers_num"]}</div>
      <div class="sp-stat-label">{t["stat_volunteers_label"]}</div>
      <div class="sp-stat-sub">{t["stat_volunteers_sub"]}</div>
    </div>
  </div>

  <!-- Interactive Hero Contributor Photo Showcase -->
  <div class="sp-hero-photo-wrap">
    <div class="sp-main-photo-frame">
      <img id="sp-hero-photo-img" 
           src="https://world.openfoodfacts.org/images/misc/scanparty-off-general-meeting-20150620.jpg" 
           alt="Open Food Facts Scan Party Gathering" 
           class="sp-main-photo-img" />
      
      <div class="sp-photo-overlay-top">
        <span style="color: #22c55e;">●</span>
        <span id="sp-hero-photo-loc">{t["hero_photo_loc"]}</span>
      </div>

      <div class="sp-photo-overlay-bottom">
        <span class="sp-photo-overlay-tag" id="sp-hero-photo-tag">{t["hero_photo_badge"]}</span>
        <h4 class="sp-photo-overlay-title" id="sp-hero-photo-title">{t["hero_photo_title"]}</h4>
        <p class="sp-photo-overlay-desc" id="sp-hero-photo-desc">{t["hero_photo_desc"]}</p>
      </div>
    </div>

    <!-- Switcher Thumbnails -->
    <div class="sp-thumbs-row">
      <button type="button" onclick="switchSpHeroPhoto(0)" class="sp-thumb-btn active" id="sp-thumb-0" title="Paris Assembly 2015">
        <img src="https://world.openfoodfacts.org/images/misc/scanparty-off-general-meeting-20150620.jpg" alt="Paris Assembly 2015" />
      </button>
      <button type="button" onclick="switchSpHeroPhoto(1)" class="sp-thumb-btn" id="sp-thumb-1" title="Lyon Asian Market 2015">
        <img src="https://world.openfoodfacts.org/images/misc/scanparty-lyon-20150601.jpg" alt="Lyon Asian Market 2015" />
      </button>
      <button type="button" onclick="switchSpHeroPhoto(2)" class="sp-thumb-btn" id="sp-thumb-2" title="Marie-Claire in Spain 2015">
        <img src="https://world.openfoodfacts.org/images/misc/marie-claire-scan-spain.jpg" alt="Marie-Claire Spain" />
      </button>
      <button type="button" onclick="switchSpHeroPhoto(3)" class="sp-thumb-btn" id="sp-thumb-3" title="Yes They Scan Banner">
        <img src="https://world.openfoodfacts.org/images/misc/scanparty.640x480.png" alt="Scan Party Banner" />
      </button>
      <button type="button" onclick="switchSpHeroPhoto(4)" class="sp-thumb-btn" id="sp-thumb-4" title="Coop Supermarket Workshop">
        <img src="https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=400&q=80" alt="Coop Workshop" />
      </button>
    </div>
  </div>

  <!-- Historical Contributors Tribute Box (Preserving Heart-Warming Photos) -->
  <div class="sp-tribute-box">
    <div class="sp-tribute-header">
      <h3>{t["tribute_title"]}</h3>
      <p>{t["tribute_subtitle"]}</p>
    </div>

    <div class="sp-tribute-cards">
      <div class="sp-tribute-card">
        <div class="sp-tribute-img-wrap">
          <img src="https://world.openfoodfacts.org/images/misc/scanparty-off-general-meeting-20150620.jpg" alt="1st Assembly Paris" class="sp-tribute-img" />
        </div>
        <div class="sp-tribute-body">
          <h4>{t["tribute_c1_title"]}</h4>
          <p>{t["tribute_c1_desc"]}</p>
        </div>
      </div>

      <div class="sp-tribute-card">
        <div class="sp-tribute-img-wrap">
          <img src="https://world.openfoodfacts.org/images/misc/scanparty-lyon-20150601.jpg" alt="Lyon Chinese store" class="sp-tribute-img" />
        </div>
        <div class="sp-tribute-body">
          <h4>{t["tribute_c2_title"]}</h4>
          <p>{t["tribute_c2_desc"]}</p>
        </div>
      </div>

      <div class="sp-tribute-card">
        <div class="sp-tribute-img-wrap">
          <img src="https://world.openfoodfacts.org/images/misc/marie-claire-scan-spain.jpg" alt="Marie-Claire Spain" class="sp-tribute-img" />
        </div>
        <div class="sp-tribute-body">
          <h4>{t["tribute_c3_title"]}</h4>
          <p>{t["tribute_c3_desc"]}</p>
        </div>
      </div>
    </div>

    <div class="sp-tribute-invite">
      <div style="font-weight: 700; color: #9a3412;">{t["tribute_invitation_title"]}</div>
      <div class="sp-tribute-invite-grid">
        <span>{t["tribute_invitation_1"]}</span>
        <span>{t["tribute_invitation_2"]}</span>
        <span>{t["tribute_invitation_3"]}</span>
      </div>
      <p style="font-size: 0.88rem; color: #7c2d12; margin: 0.35rem 0 0;">
        {t["tribute_cta"]}
      </p>
    </div>
  </div>

  <!-- Concept & Mission -->
  <div class="sp-section" id="about">
    <div class="sp-section-center">
      <div class="sp-badge">{t["concept_badge"]}</div>
      <h2 class="sp-section-title">{t["concept_title"]}</h2>
      <p class="sp-section-subtitle">{t["concept_lead"]}</p>
    </div>

    <div class="sp-pillars-grid">
      <div class="sp-pillar-card">
        <div class="sp-pillar-icon sp-icon-orange">📊</div>
        <h4>{t["pillar_1_title"]}</h4>
        <p>{t["pillar_1_desc"]}</p>
      </div>

      <div class="sp-pillar-card">
        <div class="sp-pillar-icon sp-icon-emerald">🛡️</div>
        <h4>{t["pillar_2_title"]}</h4>
        <p>{t["pillar_2_desc"]}</p>
      </div>

      <div class="sp-pillar-card">
        <div class="sp-pillar-icon sp-icon-blue">🤝</div>
        <h4>{t["pillar_3_title"]}</h4>
        <p>{t["pillar_3_desc"]}</p>
      </div>

      <div class="sp-pillar-card">
        <div class="sp-pillar-icon sp-icon-purple">🌱</div>
        <h4>{t["pillar_4_title"]}</h4>
        <p>{t["pillar_4_desc"]}</p>
      </div>
    </div>
  </div>

  <!-- 2 Scanning Workflows -->
  <div class="sp-section" id="workflows">
    <div class="sp-section-center">
      <div class="sp-badge">{t["wf_badge"]}</div>
      <h2 class="sp-section-title">{t["wf_title"]}</h2>
      <p class="sp-section-subtitle">{t["wf_lead"]}</p>
    </div>

    <div class="sp-workflows-grid">
      <!-- Workflow 1 -->
      <div class="sp-wf-card highlight">
        <div>
          <span class="sp-wf-top-badge sp-badge-live">{t["wf1_badge"]}</span>
          <h3 class="sp-wf-title">{t["wf1_title"]}</h3>
          <p class="sp-wf-desc">{t["wf1_desc"]}</p>

          <ul class="sp-wf-steps">
            <li class="sp-wf-step">
              <span class="sp-wf-num">1</span>
              <div>
                <strong>{t["wf1_step1_title"]}</strong>
                <span>{t["wf1_step1_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num">2</span>
              <div>
                <strong>{t["wf1_step2_title"]}</strong>
                <span>{t["wf1_step2_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num">3</span>
              <div>
                <strong>{t["wf1_step3_title"]}</strong>
                <span>{t["wf1_step3_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num">4</span>
              <div>
                <strong>{t["wf1_step4_title"]}</strong>
                <span>{t["wf1_step4_desc"]}</span>
              </div>
            </li>
          </ul>
        </div>

        <a href="https://world.openfoodfacts.org/open-food-facts-mobile-app" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-primary" style="width: 100%;">
          {t["wf1_btn"]}
        </a>
      </div>

      <!-- Workflow 2 -->
      <div class="sp-wf-card">
        <div>
          <span class="sp-wf-top-badge sp-badge-offline">{t["wf2_badge"]}</span>
          <h3 class="sp-wf-title">{t["wf2_title"]}</h3>
          <p class="sp-wf-desc">{t["wf2_desc"]}</p>

          <ul class="sp-wf-steps">
            <li class="sp-wf-step">
              <span class="sp-wf-num sp-wf-num-blue">1</span>
              <div>
                <strong>{t["wf2_step1_title"]}</strong>
                <span>{t["wf2_step1_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num sp-wf-num-blue">2</span>
              <div>
                <strong>{t["wf2_step2_title"]}</strong>
                <span>{t["wf2_step2_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num sp-wf-num-blue">3</span>
              <div>
                <strong>{t["wf2_step3_title"]}</strong>
                <span>{t["wf2_step3_desc"]}</span>
              </div>
            </li>
            <li class="sp-wf-step">
              <span class="sp-wf-num sp-wf-num-blue">4</span>
              <div>
                <strong>{t["wf2_step4_title"]}</strong>
                <span>{t["wf2_step4_desc"]}</span>
              </div>
            </li>
          </ul>
        </div>

        <a href="https://pro.openfoodfacts.org" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #0284c7; color: #0284c7;">
          {t["wf2_btn"]}
        </a>
      </div>
    </div>

    <!-- Barcode Anchor Sequence Diagram -->
    <div class="sp-seq-box">
      <div class="sp-seq-header">
        <h4>{t["seq_title"]}</h4>
        <span style="font-size: 0.78rem; font-weight: 700; color: #ea580c; background: #fff7ed; padding: 0.25rem 0.65rem; border-radius: 6px; border: 1px solid #fed7aa;">
          Ordre strict obligatoire
        </span>
      </div>
      <p style="font-size: 0.86rem; color: #64748b; margin: 0 0 1rem; line-height: 1.45;">
        {t["seq_desc"]}
      </p>

      <div class="sp-seq-grid">
        <div class="sp-seq-card primary-anchor">
          <span class="sp-seq-pill">{t["seq_pill"]}</span>
          <div style="font-size: 1.4rem; color: #ea580c; margin-bottom: 0.2rem;">📶</div>
          <h5>{t["seq_s1_title"]}</h5>
          <p>{t["seq_s1_desc"]}</p>
        </div>

        <div class="sp-seq-card">
          <div style="font-size: 1.4rem; color: #0284c7; margin-bottom: 0.2rem;">📦</div>
          <h5>{t["seq_s2_title"]}</h5>
          <p>{t["seq_s2_desc"]}</p>
        </div>

        <div class="sp-seq-card">
          <div style="font-size: 1.4rem; color: #16a34a; margin-bottom: 0.2rem;">📋</div>
          <h5>{t["seq_s3_title"]}</h5>
          <p>{t["seq_s3_desc"]}</p>
        </div>

        <div class="sp-seq-card">
          <div style="font-size: 1.4rem; color: #7c3aed; margin-bottom: 0.2rem;">🥗</div>
          <h5>{t["seq_s4_title"]}</h5>
          <p>{t["seq_s4_desc"]}</p>
        </div>

        <div class="sp-seq-card">
          <div style="font-size: 1.4rem; color: #eab308; margin-bottom: 0.2rem;">♻️</div>
          <h5>{t["seq_s5_title"]}</h5>
          <p>{t["seq_s5_desc"]}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Interactive Playground Simulator -->
  <div class="sp-section" id="simulator">
    <div class="sp-section-center">
      <div class="sp-badge">{t["sim_badge"]}</div>
      <h2 class="sp-section-title">{t["sim_title"]}</h2>
      <p class="sp-section-subtitle">{t["sim_lead"]}</p>
    </div>

    <div class="sp-sim-box">
      <div class="sp-sim-layout">
        <!-- Store Shelf -->
        <div>
          <h4 style="font-size: 0.95rem; font-weight: 700; color: #64748b; margin: 0 0 0.75rem; text-transform: uppercase;">
            {t["sim_shelf_title"]}
          </h4>

          <div class="sp-shelf-items" id="sp-shelf-container">
            <!-- Rendered by JS -->
          </div>
        </div>

        <!-- Live Database Inspector -->
        <div class="sp-inspector">
          <div>
            <div class="sp-inspector-header">
              <span class="sp-inspector-title">
                <span>🚀</span> {t["sim_card_title"]}
              </span>
              <span id="sp-sim-time" style="font-size: 0.75rem; color: #94a3b8; font-family: monospace;">Ready</span>
            </div>

            <div style="display: flex; align-items: center; gap: 0.85rem; margin-bottom: 1rem;">
              <span id="sp-sim-icon" style="font-size: 2.2rem; background: #1e293b; padding: 0.35rem 0.65rem; border-radius: 8px;">🛒</span>
              <div>
                <h3 class="sp-inspector-prod-title" id="sp-sim-title">Sélectionnez un produit</h3>
                <p id="sp-sim-brand" style="margin: 0; font-size: 0.84rem; color: #94a3b8;">Cliquez sur un article à gauche pour tester le scan</p>
              </div>
            </div>

            <div class="sp-inspector-scores">
              <div class="sp-score-box">
                <span class="sp-score-label">Nutri-Score</span>
                <span class="sp-score-val" id="sp-sim-nutri" style="color: #22c55e;">--</span>
              </div>
              <div class="sp-score-box">
                <span class="sp-score-label">Groupe NOVA</span>
                <span class="sp-score-val" id="sp-sim-nova" style="color: #fb923c;">--</span>
              </div>
              <div class="sp-score-box">
                <span class="sp-score-label">Éco-Score</span>
                <span class="sp-score-val" id="sp-sim-eco" style="color: #4ade80;">--</span>
              </div>
            </div>

            <div style="background: #1e293b; border-radius: 8px; padding: 0.75rem; font-size: 0.78rem; space-y: 0.35rem; color: #cbd5e1;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                <span style="color: #94a3b8;">Code-barres (EAN) :</span>
                <span id="sp-sim-code" style="font-family: monospace; color: #ffffff;">--</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #94a3b8;">Emballage :</span>
                <span id="sp-sim-pkg" style="color: #ffffff;">--</span>
              </div>
            </div>
          </div>

          <!-- Progress goal -->
          <div class="sp-progress-box">
            <div class="sp-progress-labels">
              <span>{t["sim_goal_label"]}</span>
              <strong id="sp-sim-counter" style="color: #ea580c;">0 / 50 scans</strong>
            </div>
            <div class="sp-progress-bar-bg">
              <div id="sp-sim-progress" class="sp-progress-bar-fill"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Host Toolkit & Marketing Resources -->
  <div class="sp-section" id="marketing">
    <div class="sp-section-center">
      <div class="sp-badge">{t["kit_badge"]}</div>
      <h2 class="sp-section-title">{t["kit_title"]}</h2>
      <p class="sp-section-subtitle">{t["kit_lead"]}</p>
    </div>

    <div class="sp-kit-grid">
      <div class="sp-kit-card">
        <div>
          <div style="font-size: 1.8rem; margin-bottom: 0.75rem;">🎨</div>
          <h4>{t["kit_canva_title"]}</h4>
          <p>{t["kit_canva_desc"]}</p>
        </div>
        <a href="https://www.canva.com/folder/FAFOYPM6xn8" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #7c3aed; color: #7c3aed;">
          {t["kit_canva_btn"]}
        </a>
      </div>

      <div class="sp-kit-card">
        <div>
          <div style="font-size: 1.8rem; margin-bottom: 0.75rem;">📕</div>
          <h4>{t["kit_pdf_title"]}</h4>
          <p>{t["kit_pdf_desc"]}</p>
        </div>
        <a href="https://drive.google.com/file/d/1xqtjqvJrwuqxZYQ_8Zd5EQXp0n1PrjFs/view?usp=drive_link" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #dc2626; color: #dc2626;">
          {t["kit_pdf_btn"]}
        </a>
      </div>

      <div class="sp-kit-card">
        <div>
          <div style="font-size: 1.8rem; margin-bottom: 0.75rem;">📰</div>
          <h4>{t["kit_blog_en_title"]}</h4>
          <p>{t["kit_blog_en_desc"]}</p>
        </div>
        <a href="https://blog.openfoodfacts.org/en/news/organise-a-scan-party-participative-workshop" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #ea580c; color: #ea580c;">
          {t["kit_blog_en_btn"]}
        </a>
      </div>

      <div class="sp-kit-card">
        <div>
          <div style="font-size: 1.8rem; margin-bottom: 0.75rem;">🇫🇷</div>
          <h4>{t["kit_blog_fr_title"]}</h4>
          <p>{t["kit_blog_fr_desc"]}</p>
        </div>
        <a href="https://blog.openfoodfacts.org/fr/news/organisez-une-scan-party-emballages" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #0284c7; color: #0284c7;">
          {t["kit_blog_fr_btn"]}
        </a>
      </div>
    </div>
  </div>

  <!-- Interactive Host Organizer Checklist -->
  <div class="sp-checklist-wrap">
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
      <div>
        <h3 style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 0.25rem;">
          📋 {t["chk_title"]}
        </h3>
        <p style="font-size: 0.88rem; color: #64748b; margin: 0;">{t["chk_lead"]}</p>
      </div>
      <span id="sp-checklist-status" style="font-weight: 800; font-size: 0.84rem; color: #ea580c; background: #fff7ed; padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid #fed7aa;">
        0 / 6 complétées
      </span>
    </div>

    <div class="sp-check-items" id="sp-checklist-items">
      <!-- Injected by JS -->
    </div>
  </div>

  <!-- Events Directory & Declare Your Own -->
  <div class="sp-section" id="events">
    <div class="sp-section-center">
      <div class="sp-badge">{t["dir_badge"]}</div>
      <h2 class="sp-section-title">{t["dir_title"]}</h2>
      <p class="sp-section-subtitle">{t["dir_lead"]}</p>
    </div>

    <!-- Declare Your Own Scan Party Callout Banner -->
    <div class="sp-declare-banner">
      <h3>📢 {t["declare_banner_title"]}</h3>
      <p>{t["declare_banner_desc"]}</p>
      
      <div style="display: flex; flex-wrap: wrap; gap: 0.65rem;">
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?title=%5BScan+Party%5D+New+Event%3A+&labels=scan-party%2Cevent&body=%23%23%23+%F0%9F%8E%89+Scan+Party+Title%0A%3C%21--+Enter+event+title+--%3E%0A%0A%23%23%23+%F0%9F%93%85+Date+%26+Time%0A-+Date%3A+%0A-+Start+Time%3A+%0A%0A%23%23%23+%F0%9F%93%8D+Location+%26+Venue%0A-+Venue+Name%3A+%0A-+City%3A+%0A-+Country%3A+%0A%0A%23%23%23+%F0%9F%91%A4+Organizer%0A-+Organizer+Name+%2F+Organization%3A+%0A-+Contact+Email+%2F+Slack+handle%3A+%0A%0A%23%23%23+%F0%9F%93%9D+Description%0A%3C%21--+Describe+the+scan+party%2C+target+store%2C+or+focus+--%3E%0A%0A%23%23%23+%F0%9F%94%97+Registration+%2F+Recap+Link%0A-+Link%3A+%0A" 
           target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-primary">
          {t["btn_declare_gh"]}
        </a>
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/scan_parties" 
           target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="border-color: #16a34a; color: #16a34a;">
          {t["btn_declare_pr"]}
        </a>
        <button type="button" onclick="toggleSpDeclareDrawer()" class="sp-btn sp-btn-secondary">
          {t["btn_declare_drawer"]}
        </button>
      </div>

      <!-- Generator Drawer -->
      <div class="sp-declare-drawer" id="sp-declare-drawer">
        <h4 style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin: 0 0 0.85rem;">
          Générer une fiche d'atelier YAML
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.85rem; margin-bottom: 1rem;">
          <input type="text" id="gen-title" placeholder="Titre de la Scan Party" style="padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem;">
          <input type="text" id="gen-city" placeholder="Ville & Pays (ex: Lyon, France)" style="padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem;">
          <input type="text" id="gen-venue" placeholder="Lieu / Magasin (ex: Biomonde Rennes)" style="padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem;">
          <input type="text" id="gen-date" placeholder="Date (ex: Novembre 2024)" style="padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem;">
        </div>
        <textarea id="gen-desc" placeholder="Courte description de l'atelier..." style="width: 100%; height: 70px; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem; margin-bottom: 0.85rem;"></textarea>
        
        <div style="display: flex; gap: 0.65rem;">
          <button type="button" onclick="generateSpYaml()" class="sp-btn sp-btn-primary">
            📋 Générer & Copier le YAML
          </button>
          <button type="button" onclick="toggleSpDeclareDrawer()" class="sp-btn sp-btn-secondary">
            Fermer
          </button>
        </div>
        <pre id="gen-output" style="display: none; background: #0f172a; color: #a5f3fc; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.78rem; overflow-x: auto;"></pre>
      </div>
    </div>

    <!-- Filter Controls -->
    <div class="sp-dir-controls">
      <div class="sp-filter-tabs">
        <button type="button" class="sp-filter-tab active" id="tab-all" onclick="filterSpEvents('all')">{t["filter_all"]}</button>
        <button type="button" class="sp-filter-tab" id="tab-upcoming" onclick="filterSpEvents('upcoming')">{t["filter_upcoming"]}</button>
        <button type="button" class="sp-filter-tab" id="tab-past" onclick="filterSpEvents('past')">{t["filter_past"]}</button>
      </div>

      <input type="search" id="sp-event-search" class="sp-search-input" placeholder="{t["search_placeholder"]}" oninput="searchSpEvents()">
    </div>

    <!-- Dynamic Events Grid -->
    <div class="sp-events-grid" id="sp-events-container">
      <!-- Populated by JS -->
    </div>
  </div>

  <!-- Community & Slack Section -->
  <div class="sp-section" id="community">
    <div class="sp-section-center">
      <h2 class="sp-section-title">{t["comm_title"]}</h2>
      <p class="sp-section-subtitle">{t["comm_lead"]}</p>
    </div>

    <div class="sp-community-grid">
      <div class="sp-comm-card">
        <div>
          <div style="font-size: 2rem; color: #16a34a; margin-bottom: 0.5rem;">💬</div>
          <h4>{t["slack_global_title"]}</h4>
          <p>{t["slack_global_desc"]}</p>
        </div>
        <a href="https://openfoodfacts.slack.com/messages/C037DFCLU/" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-emerald" style="width: 100%;">
          Rejoindre #scanparty
        </a>
      </div>

      <div class="sp-comm-card">
        <div>
          <div style="font-size: 2rem; color: #0284c7; margin-bottom: 0.5rem;">🇫🇷</div>
          <h4>{t["slack_fr_title"]}</h4>
          <p>{t["slack_fr_desc"]}</p>
        </div>
        <a href="https://openfoodfacts.slack.com/messages/C1C8216TF/" target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="width: 100%; border-color: #0284c7; color: #0284c7;">
          Rejoindre #scanparty_fr
        </a>
      </div>

      <div class="sp-comm-card">
        <div>
          <div style="font-size: 2rem; color: #ea580c; margin-bottom: 0.5rem;">✉️</div>
          <h4>{t["contact_lead_title"]}</h4>
          <p>{t["contact_lead_desc"]}</p>
        </div>
        <a href="mailto:gala@openfoodfacts.org" class="sp-btn sp-btn-primary" style="width: 100%;">
          Contacter Gala (Communauté)
        </a>
      </div>
    </div>
  </div>

  <!-- Dedicated Supporting Partner Section: Fondation de France -->
  <div class="sp-partner-section">
    <div class="sp-partner-badge-col">
      <a href="https://www.fondationdefrance.org/" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
        <div class="sp-partner-logo-box">
          <span class="sp-partner-logo-text">Fondation<br/>de France</span>
          <span class="sp-partner-logo-sub">Toutes les envies d'agir</span>
        </div>
      </a>
    </div>

    <div class="sp-partner-text-col">
      <span class="sp-partner-tag">{t["partner_badge"]}</span>
      <h3 class="sp-partner-title">{t["partner_title"]}</h3>
      <p class="sp-partner-desc">
        {t["partner_desc"]}
      </p>
      <a href="https://www.fondationdefrance.org/" target="_blank" rel="noopener noreferrer" class="sp-partner-link">
        {t["partner_link_text"]}
      </a>
    </div>
  </div>

</div>

<!-- Client-Side Runtime for Interactive Features -->
<script>
const SP_EVENTS = {events_json};
const SP_HERO_PHOTOS = {hero_photos_json};
const SP_SAMPLE_PRODUCTS = {sample_products_json};
const SP_CHECKLIST = {checklist_json};

let spCurrentFilter = "all";
let spSimScans = 0;
let spCheckedTasks = new Set();

function switchSpHeroPhoto(index) {{
  const photo = SP_HERO_PHOTOS[index];
  if (!photo) return;

  const img = document.getElementById("sp-hero-photo-img");
  const loc = document.getElementById("sp-hero-photo-loc");
  const tag = document.getElementById("sp-hero-photo-tag");
  const title = document.getElementById("sp-hero-photo-title");
  const desc = document.getElementById("sp-hero-photo-desc");

  if (img) img.src = photo.url;
  if (loc) loc.innerText = photo.loc;
  if (tag) tag.innerText = photo.tag;
  if (title) title.innerText = photo.title;
  if (desc) desc.innerText = photo.desc;

  [0, 1, 2, 3, 4].forEach(i => {{
    const thumb = document.getElementById("sp-thumb-" + i);
    if (thumb) {{
      if (i === index) thumb.classList.add("active");
      else thumb.classList.remove("active");
    }}
  }});
}}

function renderSpSimulator() {{
  const container = document.getElementById("sp-shelf-container");
  if (!container) return;

  container.innerHTML = SP_SAMPLE_PRODUCTS.map(p => `
    <div class="sp-prod-card" onclick="scanSpProduct(${{p.id}})" id="sp-prod-${{p.id}}">
      <span class="sp-prod-emoji">${{p.icon}}</span>
      <div class="sp-prod-info">
        <h5>${{p.name}}</h5>
        <p>${{p.brand}}</p>
        <span class="sp-prod-ean">${{p.barcode}}</span>
      </div>
      <span style="margin-left: auto; font-size: 0.78rem; font-weight: 700; color: #ea580c;">
        {t["sim_scan_btn"]}
      </span>
    </div>
  `).join("");

  scanSpProduct(1);
}}

function scanSpProduct(id) {{
  const item = SP_SAMPLE_PRODUCTS.find(p => p.id === id);
  if (!item) return;

  spSimScans++;

  SP_SAMPLE_PRODUCTS.forEach(p => {{
    const el = document.getElementById("sp-prod-" + p.id);
    if (el) {{
      if (p.id === id) el.classList.add("active");
      else el.classList.remove("active");
    }}
  }});

  document.getElementById("sp-sim-icon").innerText = item.icon;
  document.getElementById("sp-sim-title").innerText = item.name;
  document.getElementById("sp-sim-brand").innerText = item.brand;
  document.getElementById("sp-sim-code").innerText = item.barcode;
  document.getElementById("sp-sim-pkg").innerText = item.packaging;
  
  const nutriEl = document.getElementById("sp-sim-nutri");
  nutriEl.innerText = item.nutri;
  nutriEl.style.color = item.nutriColor;

  document.getElementById("sp-sim-nova").innerText = "Groupe " + item.nova;
  document.getElementById("sp-sim-eco").innerText = "Classe " + item.eco;

  const now = new Date();
  document.getElementById("sp-sim-time").innerText = now.toLocaleTimeString();

  const target = 50;
  const current = Math.min(spSimScans * 10, target);
  const pct = Math.min((current / target) * 100, 100);

  document.getElementById("sp-sim-counter").innerText = current + " / " + target + " scans";
  document.getElementById("sp-sim-progress").style.width = pct + "%";

  triggerSpConfetti();
}}

function renderSpChecklist() {{
  const container = document.getElementById("sp-checklist-items");
  if (!container) return;

  container.innerHTML = SP_CHECKLIST.map(item => `
    <label class="sp-check-label ${{spCheckedTasks.has(item.id) ? 'done' : ''}}" id="chk-lbl-${{item.id}}">
      <input type="checkbox" ${{spCheckedTasks.has(item.id) ? 'checked' : ''}} onchange="toggleSpChecklistItem(${{item.id}})" />
      <span>${{item.text}}</span>
    </label>
  `).join("");

  updateSpChecklistProgress();
}}

function toggleSpChecklistItem(id) {{
  if (spCheckedTasks.has(id)) {{
    spCheckedTasks.delete(id);
  }} else {{
    spCheckedTasks.add(id);
  }}
  renderSpChecklist();
}}

function updateSpChecklistProgress() {{
  const el = document.getElementById("sp-checklist-status");
  if (el) {{
    el.innerText = spCheckedTasks.size + " / " + SP_CHECKLIST.length + " complétées";
  }}
  if (spCheckedTasks.size === SP_CHECKLIST.length && SP_CHECKLIST.length > 0) {{
    triggerSpConfetti();
  }}
}}

function renderSpEvents(filter = "all", searchQuery = "") {{
  const container = document.getElementById("sp-events-container");
  if (!container) return;

  const q = (searchQuery || "").toLowerCase().trim();

  const filtered = SP_EVENTS.filter(e => {{
    if (filter === "upcoming" && e.type !== "upcoming") return false;
    if (filter === "past" && e.type !== "past") return false;
    if (q) {{
      const haystack = (e.title + " " + e.location + " " + (e.city || "") + " " + e.venue + " " + e.description).toLowerCase();
      if (!haystack.includes(q)) return false;
    }}
    return true;
  }});

  if (filtered.length === 0) {{
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 2rem; text-align: center; color: #64748b; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1;">
        Aucun atelier ne correspond à votre recherche. Vous pouvez déclarer le vôtre dès maintenant !
      </div>
    `;
    return;
  }}

  container.innerHTML = filtered.map(e => `
    <div class="sp-event-card">
      <div>
        <div class="sp-event-top">
          <span class="sp-event-badge ${{e.type === 'upcoming' ? 'sp-badge-upcoming' : 'sp-badge-past'}}">
            ${{e.type === 'upcoming' ? 'À venir' : 'Édition passée'}}
          </span>
          <span class="sp-event-date">📅 ${{e.date}}</span>
        </div>

        <h4 class="sp-event-title">${{e.title}}</h4>
        <div class="sp-event-loc">📍 ${{e.location}} — ${{e.venue}}</div>
        <p class="sp-event-desc">${{e.description}}</p>

        ${{e.tags && e.tags.length ? `
          <div class="sp-event-tags">
            ${{e.tags.map(t => `<span class="sp-event-tag">#` + t + `</span>`).join('')}}
          </div>
        ` : ''}}
      </div>

      <div class="sp-event-footer">
        ${{e.link ? `
          <a href="${{e.link}}" target="_blank" rel="noopener noreferrer" style="font-size: 0.82rem; font-weight: 700; color: #ea580c; text-decoration: none;">
            Lire le compte-rendu &rarr;
          </a>
        ` : `
          <span style="font-size: 0.78rem; color: #94a3b8;">Atelier communautaire</span>
        `}}
        ${{e.products_scanned ? `<span style="font-size: 0.78rem; font-weight: 700; color: #16a34a;">✨ ` + e.products_scanned + ` produits</span>` : ''}}
      </div>
    </div>
  `).join("");
}}

function filterSpEvents(tab) {{
  spCurrentFilter = tab;
  ['all', 'upcoming', 'past'].forEach(t => {{
    const el = document.getElementById("tab-" + t);
    if (el) {{
      if (t === tab) el.classList.add('active');
      else el.classList.remove('active');
    }}
  }});
  const search = document.getElementById("sp-event-search");
  renderSpEvents(tab, search ? search.value : "");
}}

function searchSpEvents() {{
  const search = document.getElementById("sp-event-search");
  renderSpEvents(spCurrentFilter, search ? search.value : "");
}}

function toggleSpDeclareDrawer() {{
  const el = document.getElementById("sp-declare-drawer");
  if (el) el.classList.toggle("open");
}}

function generateSpYaml() {{
  const title = (document.getElementById("gen-title").value || "Mon atelier Scan Party").trim();
  const city = (document.getElementById("gen-city").value || "Paris, France").trim();
  const venue = (document.getElementById("gen-venue").value || "Supermarché local").trim();
  const date = (document.getElementById("gen-date").value || "Novembre 2024").trim();
  const desc = (document.getElementById("gen-desc").value || "Atelier citoyen de scan d'aliments.").trim();

  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

  const yamlContent = "id: " + (slug || "nouvelle-scan-party") + "\\n" +
"title: " + title + "\\n" +
"type: upcoming\\n" +
"status: upcoming\\n" +
"date: \\"" + date + "\\"\\n" +
"start_date: \\"" + new Date().toISOString().split('T')[0] + "\\"\\n" +
"location: \\"" + city + "\\"\\n" +
"city: \\"" + city.split(',')[0].trim() + "\\"\\n" +
"country: \\"fra\\"\\n" +
"venue: \\"" + venue + "\\"\\n" +
"organizer: \\"Collectif citoyen\\"\\n" +
"description: \\"" + desc + "\\"\\n" +
"image: null\\n" +
"image_caption: null\\n" +
"products_scanned: null\\n" +
"participants_count: null\\n" +
"link: null\\n" +
"tags:\\n" +
"  - scanparty\\n" +
"  - citizen-science\\n";

  const pre = document.getElementById("gen-output");
  if (pre) {{
    pre.style.display = "block";
    pre.innerText = yamlContent;
  }}

  if (navigator.clipboard) {{
    navigator.clipboard.writeText(yamlContent).then(() => {{
      alert("YAML généré et copié dans le presse-papiers ! Vous pouvez le coller dans une Pull Request sur data/scan_parties/.");
    }}).catch(() => {{
      alert("YAML généré ci-dessous !");
    }});
  }} else {{
    alert("YAML généré ci-dessous !");
  }}
}}

function triggerSpConfetti() {{
  const canvas = document.getElementById('sp-confetti-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const width = window.innerWidth;
  const height = window.innerHeight;

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  const particles = [];
  const colors = ['#ea580c', '#16a34a', '#0284c7', '#7c3aed', '#f59e0b'];

  for (let i = 0; i < 25; i++) {{
    particles.push({{
      x: width * 0.7 + (Math.random() - 0.5) * 80,
      y: height * 0.6 + (Math.random() - 0.5) * 40,
      vx: (Math.random() - 0.5) * 8,
      vy: Math.random() * -6 - 3,
      size: Math.random() * 7 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 1
    }});
  }}

  function animate() {{
    ctx.clearRect(0, 0, width, height);
    let active = false;

    particles.forEach(p => {{
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.25;
      p.alpha -= 0.02;

      if (p.alpha > 0) {{
        active = true;
        ctx.save();
        ctx.globalAlpha = Math.max(0, p.alpha);
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
        ctx.restore();
      }}
    }});

    if (active) requestAnimationFrame(animate);
    else ctx.clearRect(0, 0, width, height);
  }}

  animate();
}}

// Initialize
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', () => {{
    renderSpSimulator();
    renderSpChecklist();
    renderSpEvents('all');
  }});
}} else {{
  renderSpSimulator();
  renderSpChecklist();
  renderSpEvents('all');
}}
</script>
"""

def compile_scan_parties(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating scan parties from {SCAN_PARTIES_DIR}...")

    items, errors, warnings = load_scan_parties(SCAN_PARTIES_DIR, validate=True)

    if warnings and verbose:
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s) in scan parties YAMLs:")
        for e in errors:
            print(f"  - {e}")
        return False

    upcoming_count = sum(1 for e in items if e.get("type") == "upcoming")
    past_count = sum(1 for e in items if e.get("type") == "past")

    if verbose:
        print(f"✅ Validated {len(items)} scan parties (Upcoming: {upcoming_count}, Past: {past_count})")

    if check_only:
        return True

    # 1. Write compiled data/scan_parties.json
    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"Wrote compiled {COMPILED_JSON} ({len(items)} items)")

    # 2. Generate localized HTML pages
    en_html = generate_html(items, lang="en")
    fr_html = generate_html(items, lang="fr")

    en_path = os.path.join(REPO_ROOT, "lang", "en", "texts", "scan-parties.html")
    fr_path = os.path.join(REPO_ROOT, "lang", "fr", "texts", "scan-parties.html")

    with open(en_path, "w", encoding="utf-8") as f:
        f.write(en_html)
    if verbose:
        print(f"Wrote {en_path}")

    with open(fr_path, "w", encoding="utf-8") as f:
        f.write(fr_html)
    if verbose:
        print(f"Wrote {fr_path}")

    return True

def main():
    check_mode = "--check" in sys.argv
    success = compile_scan_parties(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
