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

# Ensure scripts directory and vendor are on path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from i18n_utils import (
    ensure_vendor_path,
    get_localized_field,
    validate_localized_field,
    SUPPORTED_LANGUAGES,
)
ensure_vendor_path()

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

    # Required: title (supports string or localized dict)
    errors.extend(validate_localized_field(item, "title", filename, required=True))

    # Required: type
    evt_type = item.get("type")
    if not evt_type or evt_type not in VALID_TYPES:
        errors.append(f"{filename}: 'type' must be one of {sorted(VALID_TYPES)}, got '{evt_type}'")

    # Required: date
    date_str = item.get("date")
    if not date_str or not str(date_str).strip():
        errors.append(f"{filename}: missing required field 'date'")

    # Required: location (supports string or localized dict)
    errors.extend(validate_localized_field(item, "location", filename, required=True))

    # Required: venue (supports string or localized dict)
    errors.extend(validate_localized_field(item, "venue", filename, required=True))

    # Required: description (supports string or localized dict)
    errors.extend(validate_localized_field(item, "description", filename, required=True))

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


SP_STRINGS = {
    "fr": {
        "hero_badge": "Écosystème Open Food Facts • Science Citoyenne Participative",
        "hero_title_1": "Rassemblez-vous. Scannez.",
        "hero_title_2": "Démocratisez les données alimentaires.",
        "hero_desc": "Une <strong>Scan Party</strong> est un atelier collaboratif et chaleureux où citoyens, bénévoles et consommateurs se réunissent dans un supermarché, une épicerie coopérative ou un tiers-lieu pour photographier les codes-barres, ingrédients, tableaux nutritionnels et emballages des aliments afin de les ajouter à <strong>Open Food Facts</strong>.",
        "btn_organize": "🚀 Déclarer / Organiser un atelier",
        "btn_kit": "📦 Guide de l'hôte & Affiches Canva",
        "btn_workflows": "📱 2 façons de scanner",
        "btn_simulator": "🎮 Simulateur de scan",
        "btn_directory": "📅 Annuaire des ateliers",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Produits ouverts",
        "stat_products_sub": "Base de données citoyenne",
        "stat_free_num": "100%",
        "stat_free_label": "Libre & ODbL",
        "stat_free_sub": "Bien commun mondial",
        "stat_countries_num": "180+",
        "stat_countries_label": "Pays touchés",
        "stat_countries_sub": "À travers la planète",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Contributeurs",
        "stat_volunteers_sub": "Qui s'engagent",
        "hero_photo_badge": "Photo historique",
        "hero_photo_title": "1ère Assemblée Générale d'Open Food Facts à Paris",
        "hero_photo_desc": "Les contributeurs pionniers photographient et scannent des centaines de produits dès 2015.",
        "hero_photo_loc": "Paris, France (2015)",
        "tribute_title": "❤️ Les visages et l'énergie de nos contributeurs",
        "tribute_subtitle": "Depuis les premiers jours d'Open Food Facts, l'énergie des scan parties repose sur des personnes bienveillantes, curieuses et déterminées à éclairer notre alimentation.",
        "tribute_c1_title": "1ère Assemblée Générale à Paris",
        "tribute_c1_desc": "20 juin 2015 : Première scan party collective lors de l'assemblée générale de l'association Open Food Facts.",
        "tribute_c2_title": "Scan Party à Lyon",
        "tribute_c2_desc": "Juin 2015 : Expédition spontanée dans une épicerie asiatique pour décoder et indexer des dizaines de spécialités.",
        "tribute_c3_title": "Marie-Claire, pionnière de la 1ère heure",
        "tribute_c3_desc": "Chassant les codes-barres en Espagne après avoir ajouté plus de 200 produits avant même le lancement public !",
        "tribute_invitation_title": "Qui nous rejoint ensuite ?",
        "tribute_invitation_1": "Vous ? :-)",
        "tribute_invitation_2": "Votre famille ? :-)",
        "tribute_invitation_3": "Vos amis et collègues ? :-)",
        "tribute_cta": "Partagez vos photos d'ateliers avec le hashtag <strong>#scanparty</strong> ou écrivez-nous à <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a> !",
        "concept_badge": "Concept & Mission",
        "concept_title": "Qu'est-ce qu'une Scan Party ?",
        "concept_lead": "C'est un événement convivial et formateur où l'on joint l'utile à l'agréable : découvrir l'envers des étiquettes alimentaires tout en enrichissant le plus grand bien commun mondial sur l'alimentation.",
        "pillar_1_title": "Enrichir la base ouverte",
        "pillar_1_desc": "Ajouter des produits inédits et mettre à jour ingrédients, tableaux nutritionnels et emballages recyclables.",
        "pillar_2_title": "Éclairer les consommateurs",
        "pillar_2_desc": "Donner à chacun des informations claires et vérifiées pour choisir une alimentation plus saine et durable.",
        "pillar_3_title": "Créer du lien social",
        "pillar_3_desc": "Partager un moment chaleureux entre voisins, collègues, étudiants ou coopérateurs autour de l'alimentation.",
        "pillar_4_title": "Sensibiliser & Éduquer",
        "pillar_4_desc": "Comprendre le Nutri-Score, l'Éco-Score, la classification NOVA des aliments ultra-transformés et les additifs.",
        "wf_badge": "2 Méthodes Disponibles",
        "wf_title": "Deux façons simples d'organiser votre atelier",
        "wf_lead": "Que vous disposiez d'un excellent Wi-Fi ou que vous soyez dans le sous-sol d'un magasin sans réseau, Open Food Facts s'adapte !",
        "wf1_badge": "Idéal avec Wi-Fi / 4G",
        "wf1_title": "Méthode 1 : Scan en direct via l'App Mobile",
        "wf1_desc": "Les participants téléchargent l'application gratuite Open Food Facts et ajoutent les produits en direct.",
        "wf1_step1_title": "Installer l'application gratuite",
        "wf1_step1_desc": "Disponible sur iOS et Android sans publicité ni compte payant.",
        "wf1_step2_title": "Former des binômes",
        "wf1_step2_desc": "L'un prend le produit en main, le second scanne le code-barres et prend les photos.",
        "wf1_step3_title": "Photographier les 4 faces clés",
        "wf1_step3_desc": "Face avant, ingrédients, tableau nutritionnel et informations d'emballage.",
        "wf1_step4_title": "Reconnaissance OCR & Scores immédiats",
        "wf1_step4_desc": "L'IA intégrée extrait le texte et calcule Nutri-Score et Éco-Score en direct !",
        "wf1_btn": "📱 Télécharger l'App Open Food Facts",
        "wf2_badge": "Sans Wi-Fi ni réseau !",
        "wf2_title": "Méthode 2 : Photos Hors-Ligne & Import Pro",
        "wf2_desc": "En sous-sol ou sans connexion, photographiez les produits avec l'appareil photo de votre smartphone en respectant la séquence d'ancrage, puis importez le dossier par lot sur la plateforme Pro !",
        "wf2_step1_title": "Photos consécutives au smartphone",
        "wf2_step1_desc": "Utilisez simplement l'application appareil photo de vos smartphones.",
        "wf2_step2_title": "Photo du code-barres en premier",
        "wf2_step2_desc": "Le code-barres sert de balise de séparation pour notre algorithme de regroupement.",
        "wf2_step3_title": "Centraliser les photos",
        "wf2_step3_desc": "Rassemblez les dossiers de photos sur l'ordinateur de l'hôte après l'atelier.",
        "wf2_step4_title": "Glisser-déposer sur la plateforme Pro",
        "wf2_step4_desc": "Téléversez tout le dossier sur pro.openfoodfacts.org pour un traitement automatique !",
        "wf2_btn": "🌐 Accéder à la Plateforme Producteur (pro.openfoodfacts.org)",
        "seq_title": "La séquence de photos « Code-barres Ancre »",
        "seq_desc": "Pour la méthode hors-ligne, suivez scrupuleusement cet ordre pour chaque produit : le code-barres sert de point de départ pour rattacher les photos suivantes au bon produit.",
        "seq_pill": "Étape 1 • Ancre",
        "seq_s1_title": "1. Code-barres",
        "seq_s1_desc": "À plat, bien net avec chiffres visibles (sert de séparateur).",
        "seq_s2_title": "2. Face avant",
        "seq_s2_desc": "Nom du produit, marque, logos officiels et poids net.",
        "seq_s3_title": "3. Ingrédients",
        "seq_s3_desc": "Liste intégrale des ingrédients et mentions d'allergènes.",
        "seq_s4_title": "4. Tableau nutritionnel",
        "seq_s4_desc": "Valeurs pour 100g / 100ml (calories, sucres, sel, graisses).",
        "seq_s5_title": "5. Emballage & Tri",
        "seq_s5_desc": "Consignes de tri (Triman), matières plastiques (PET, PEHD, etc.).",
        "sim_badge": "Simulateur Interactif",
        "sim_title": "Simulateur de Scan Party",
        "sim_lead": "Cliquez sur les produits du rayon pour observer comment l'analyse s'effectue en temps réel !",
        "sim_shelf_title": "Rayon du magasin :",
        "sim_card_title": "Fiche Open Food Facts en direct",
        "sim_scan_btn": "Scanner ce produit &rarr;",
        "sim_goal_label": "Progression de l'atelier :",
        "kit_badge": "Ressources & Guides",
        "kit_title": "La boîte à outils de l'organisateur",
        "kit_lead": "Tout ce dont vous avez besoin pour préparer, animer et communiquer sur votre Scan Party :",
        "kit_canva_title": "Modèles d'affiches Canva",
        "kit_canva_desc": "Affiches A4 personnalisables, bannières pour réseaux sociaux et fiches d'émargement prêtes à imprimer.",
        "kit_canva_btn": "🎨 Ouvrir le dossier Canva",
        "kit_pdf_title": "Guide méthodologique PDF",
        "kit_pdf_desc": "Le guide étape par étape de 12 pages pour préparer votre salle, contacter les magasins et animer les équipes.",
        "kit_pdf_btn": "📥 Télécharger le Guide PDF",
        "kit_blog_en_title": "Article méthodologique (EN)",
        "kit_blog_en_desc": "Article de blog officiel détaillant l'organisation d'un atelier citoyen participatif.",
        "kit_blog_en_btn": "🌐 Lire l'article (EN)",
        "kit_blog_fr_title": "Article méthodologique (FR)",
        "kit_blog_fr_desc": "Guide pratique en français : « Organisez une scan party emballages » avec retours d'expérience.",
        "kit_blog_fr_btn": "🌐 Lire l'article (FR)",
        "chk_badge": "Préparation",
        "chk_title": "La Checklist interactive de l'hôte",
        "chk_lead": "Cochez vos étapes pour ne rien oublier lors de l'organisation de votre atelier :",
        "dir_badge": "Réseau Mondial",
        "dir_title": "Annuaire des Scan Parties",
        "dir_lead": "Découvrez les ateliers à venir et revivez les moments forts des scan parties passées :",
        "filter_all": "Tous les ateliers",
        "filter_upcoming": "À venir",
        "filter_past": "Éditions passées",
        "search_placeholder": "🔍 Filtrer par ville, lieu, pays...",
        "declare_banner_title": "Vous organisez une Scan Party ? Faites-la connaître !",
        "declare_banner_desc": "Ajoutez votre atelier en 1 clic via un ticket GitHub ou une Pull Request, exactement comme pour les réutilisations et publications scientifiques.",
        "btn_declare_gh": "🚀 Déclarer un atelier (1 clic)",
        "btn_declare_pr": "✏️ Proposer un fichier YAML (PR)",
        "comm_title": "Échanger avec la communauté",
        "comm_lead": "Des questions sur l'organisation ou besoin d'aide pour animer votre groupe ?",
        "slack_global_title": "Canal Slack International",
        "slack_global_desc": "Rejoignez #scanparty pour échanger avec des organisateurs du monde entier.",
        "slack_fr_title": "Canal Slack Francophone",
        "slack_fr_desc": "Rejoignez #scanparty_fr pour organiser des ateliers en France, Belgique, Suisse, etc.",
        "contact_lead_title": "Contact Équipe Communauté",
        "contact_lead_desc": "Écrivez directement à Gala (chargée de communauté Open Food Facts) pour vous accompagner.",
        "partner_badge": "Partenaire de Soutien",
        "partner_title": "Avec le soutien de la Fondation de France",
        "partner_desc": "Open Food Facts remercie chaleureusement la <strong>Fondation de France</strong> pour son soutien déterminant aux projets de science citoyenne, d'engagement participatif et d'ouverture des données pour une alimentation saine, transparente et durable accessible à tous.",
        "partner_link_text": "En savoir plus sur la Fondation de France &rarr;",
        "js_upcoming": "À venir",
        "js_past": "Édition passée",
        "js_read_more": "Lire le dossier &rarr;",
        "js_community_event": "Atelier communautaire",
        "js_products_word": "produits",
    },
    "de": {
        "hero_badge": "Open Food Facts Ökosystem • Partizipative Bürgerwissenschaft",
        "hero_title_1": "Zusammenkommen. Scannen.",
        "hero_title_2": "Lebensmitteldaten demokratisieren.",
        "hero_desc": "Eine <strong>Scan-Party</strong> ist ein kollaborativer, geselliger Workshop, bei dem Bürger, Freiwillige und Verbraucher in Supermärkten, Biomärkten oder Gemeinschaftsorten zusammenkommen, um Barcodes, Zutatenlisten, Nährwerttabellen und Verpackungen direkt für <strong>Open Food Facts</strong> zu erfassen.",
        "btn_organize": "🚀 Workshop melden / veranstalten",
        "btn_kit": "📦 Gastgeber-Leitfaden & Canva-Flyer",
        "btn_workflows": "📱 2 Methoden zum Scannen",
        "btn_simulator": "🎮 Scan-Simulator",
        "btn_directory": "📅 Workshop-Verzeichnis",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Offene Produkte",
        "stat_products_sub": "In der Bürgerdatenbank",
        "stat_free_num": "100%",
        "stat_free_label": "Frei & ODbL",
        "stat_free_sub": "Weltweites Gemeingut",
        "stat_countries_num": "180+",
        "stat_countries_label": "Erreichte Länder",
        "stat_countries_sub": "Auf der ganzen Welt",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Mitwirkende",
        "stat_volunteers_sub": "Weltweit engagiert",
        "hero_photo_badge": "Historisches Foto",
        "hero_photo_title": "1. Open Food Facts Mitgliederversammlung in Paris",
        "hero_photo_desc": "Pioniere scannen und erfassen gemeinsam Hunderte Produkte bereits im Jahr 2015.",
        "hero_photo_loc": "Paris, Frankreich (2015)",
        "tribute_title": "❤️ Gesichter und Begeisterung unserer Mitwirkenden",
        "tribute_subtitle": "Seit den ersten Tagen von Open Food Facts leben die Scan-Parties von engagierten, neugierigen Menschen, die für mehr Transparenz bei Lebensmitteln sorgen.",
        "tribute_c1_title": "1. Mitgliederversammlung in Paris",
        "tribute_c1_desc": "20. Juni 2015: Erste gemeinsame Scan-Party während der Gründungsversammlung in Paris.",
        "tribute_c2_title": "Spontane Scan-Party in Lyon",
        "tribute_c2_desc": "Juni 2015: Spontane Expedition in einen asiatischen Supermarkt, um Dutzende Spezialitäten zu erfassen.",
        "tribute_c3_title": "Marie-Claire, Pionierin der ersten Stunde",
        "tribute_c3_desc": "Barcode-Jagd in Spanien, nachdem sie schon vor dem öffentlichen Start über 200 Produkte erfasst hatte!",
        "tribute_invitation_title": "Wer macht als Nächstes mit?",
        "tribute_invitation_1": "Sie? :-)",
        "tribute_invitation_2": "Ihre Familie? :-)",
        "tribute_invitation_3": "Ihre Freunde & Kollegen? :-)",
        "tribute_cta": "Teilen Sie Ihre Workshop-Fotos mit dem Hashtag <strong>#scanparty</strong> oder schreiben Sie an <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>!",
        "concept_badge": "Konzept & Mission",
        "concept_title": "Was ist eine Scan-Party?",
        "concept_lead": "Ein unterhaltsamer und lehrreicher Workshop, der Teamarbeit mit Bürgerwissenschaft verbindet: Lebensmittelkennzeichnungen entschlüsseln und gleichzeitig das weltweit größte offene Lebensmittel-Gemeingut bereichern.",
        "pillar_1_title": "Offene Datenbank bereichern",
        "pillar_1_desc": "Neue Produkte hinzufügen und Zutatenlisten, Nährwerte und Recyclingangaben aktualisieren.",
        "pillar_2_title": "Verbraucher stärken",
        "pillar_2_desc": "Allen Menschen transparente, verlässliche Fakten für eine gesündere und nachhaltigere Ernährung an die Hand geben.",
        "pillar_3_title": "Gemeinschaft stiften",
        "pillar_3_desc": "Nachbarn, Studierende, Kollegen und Genossenschaftsmitglieder bei einem gemeinsamen Ziel zusammenbringen.",
        "pillar_4_title": "Aufklären & Bilden",
        "pillar_4_desc": "Nutri-Score, Eco-Score, NOVA-Klassifikation und Zusatzstoffe praxisnah verstehen.",
        "wf_badge": "2 Flexible Methoden",
        "wf_title": "Zwei einfache Methoden für Ihren Workshop",
        "wf_lead": "Egal ob schnelles WLAN im Seminarraum oder kein Empfang im Untergeschoss: Open Food Facts funktioniert überall!",
        "wf1_badge": "Ideal mit WLAN / 4G",
        "wf1_title": "Methode 1: Live-Scan über die mobile App",
        "wf1_desc": "Teilnehmende laden die kostenlose Open Food Facts App herunter und fügen Produkte direkt vor Ort hinzu.",
        "wf1_step1_title": "Kostenlose App installieren",
        "wf1_step1_desc": "Verfügbar für iOS und Android – werbefrei und ohne Bezahlschranken.",
        "wf1_step2_title": "Zweierteams bilden",
        "wf1_step2_desc": "Eine Person handhabt die Produkte, die zweite scannt den Barcode und fotografiert die Etiketten.",
        "wf1_step3_title": "4 wichtige Seiten fotografieren",
        "wf1_step3_desc": "Vorderseite, Zutatenliste, Nährwerttabelle und Verpackungsangaben.",
        "wf1_step4_title": "Sofortige OCR & Score-Berechnung",
        "wf1_step4_desc": "Die integrierte Texterkennung extrahiert Daten und berechnet Nutri-Score & Eco-Score in Echtzeit!",
        "wf1_btn": "📱 Open Food Facts App herunterladen",
        "wf2_badge": "Ohne WLAN & Empfang!",
        "wf2_title": "Methode 2: Offline-Fotos & Pro-Import",
        "wf2_desc": "Im Untergeschoss ohne Netz fotografieren Sie die Produkte einfach mit der normalen Smartphone-Kamera nach dem Anker-Protokoll und laden den Ordner später gesammelt hoch!",
        "wf2_step1_title": "Fotos nacheinander mit Smartphone",
        "wf2_step1_desc": "Nutzen Sie einfach die Standard-Kamera-App Ihres Smartphones.",
        "wf2_step2_title": "Barcode-Foto zuerst",
        "wf2_step2_desc": "Das Barcode-Foto dient unserem Algorithmus als Trennzeichen zwischen den Produkten.",
        "wf2_step3_title": "Fotos zentral sammeln",
        "wf2_step3_desc": "Sammeln Sie nach dem Workshop die Fotoordner auf dem Laptop des Gastgebers.",
        "wf2_step4_title": "Per Drag & Drop auf die Pro-Plattform",
        "wf2_step4_desc": "Laden Sie den kompletten Ordner auf pro.openfoodfacts.org zur automatischen Verarbeitung hoch!",
        "wf2_btn": "🌐 Zur Produzenten-Plattform (pro.openfoodfacts.org)",
        "seq_title": "Das Foto-Protokoll „Anker-Barcode“",
        "seq_desc": "Befolgen Sie bei der Offline-Methode für jedes Produkt diese feste Reihenfolge: Das Barcode-Foto dient als Anker für alle Folgeaufnahmen.",
        "seq_pill": "Schritt 1 • Anker",
        "seq_s1_title": "1. Barcode-Foto",
        "seq_s1_desc": "Flach und scharf mit sichtbaren Ziffern (dient als Trenner).",
        "seq_s2_title": "2. Vorderseite",
        "seq_s2_desc": "Produktname, Marke, Siegel und Nettofüllmenge.",
        "seq_s3_title": "3. Zutatenliste",
        "seq_s3_desc": "Vollständiges Zutatenverzeichnis und Allergenhinweise.",
        "seq_s4_title": "4. Nährwerttabelle",
        "seq_s4_desc": "Werte pro 100g / 100ml (Energie, Zucker, Fett, Salz).",
        "seq_s5_title": "5. Verpackung & Recycling",
        "seq_s5_desc": "Recyclingsymbole, Trennhinweise und Kunststoffarten (PET, HDPE usw.).",
        "sim_badge": "Interaktiver Simulator",
        "sim_title": "Scan-Party-Simulator",
        "sim_lead": "Klicken Sie auf Produkte im Regal, um Barcode-Scan und Score-Berechnung live zu erleben!",
        "sim_shelf_title": "Supermarktregal:",
        "sim_card_title": "Live Open Food Facts Produktinspektor",
        "sim_scan_btn": "Dieses Produkt scannen &rarr;",
        "sim_goal_label": "Workshop-Fortschritt:",
        "kit_badge": "Ressourcen & Leitfäden",
        "kit_title": "Die Werkzeugkiste für Gastgeber",
        "kit_lead": "Alles, was Sie zur Vorbereitung, Durchführung und Bewerbung Ihrer Scan-Party benötigen:",
        "kit_canva_title": "Canva-Plakatvorlagen",
        "kit_canva_desc": "Anpassbare A4-Poster, Social-Media-Banner und ausdruckbare Teilnehmerlisten in Canva.",
        "kit_canva_btn": "🎨 Canva-Designordner öffnen",
        "kit_pdf_title": "Methodischer PDF-Leitfaden",
        "kit_pdf_desc": "Der 12-seitige Schritt-für-Schritt-Leitfaden für Raumplanung, Supermarktkontakt und Gruppenleitung.",
        "kit_pdf_btn": "📥 PDF-Leitfaden herunterladen",
        "kit_blog_en_title": "Leitfaden-Artikel (EN)",
        "kit_blog_en_desc": "Offizieller Blogbeitrag zur Organisation partizipativer Bürgerworkshops.",
        "kit_blog_en_btn": "🌐 Artikel lesen (EN)",
        "kit_blog_fr_title": "Praxisbericht (FR)",
        "kit_blog_fr_desc": "Erfahrungsbericht auf Französisch: «Organisez une scan party emballages».",
        "kit_blog_fr_btn": "🌐 Artikel lesen (FR)",
        "chk_badge": "Vorbereitung",
        "chk_title": "Interaktive Checkliste für Gastgeber",
        "chk_lead": "Haken Sie die Schritte ab, um bei der Organisation an alles zu denken:",
        "dir_badge": "Weltweites Netzwerk",
        "dir_title": "Scan-Party-Verzeichnis",
        "dir_lead": "Entdecken Sie bevorstehende Workshops und blicken Sie auf vergangene Veranstaltungen zurück:",
        "filter_all": "Alle Workshops",
        "filter_upcoming": "Bevorstehend",
        "filter_past": "Vergangene Events",
        "search_placeholder": "🔍 Nach Stadt, Ort, Land filtern...",
        "declare_banner_title": "Sie veranstalten eine Scan-Party? Tragen Sie sie ein!",
        "declare_banner_desc": "Fügen Sie Ihren Workshop mit einem Klick über ein GitHub-Ticket oder eine Pull Request hinzu.",
        "btn_declare_gh": "🚀 Workshop melden (1 Klick)",
        "btn_declare_pr": "✏️ YAML-Datei vorschlagen (PR)",
        "comm_title": "Austausch mit der Community",
        "comm_lead": "Fragen zur Organisation oder Unterstützung bei der Gruppenleitung gewünscht?",
        "slack_global_title": "Internationaler Slack-Kanal",
        "slack_global_desc": "Treten Sie #scanparty auf Slack bei, um sich weltweit auszutauschen.",
        "slack_fr_title": "Frankophoner Slack-Kanal",
        "slack_fr_desc": "Treten Sie #scanparty_fr für Workshops im französischsprachigen Raum bei.",
        "contact_lead_title": "Kontakt Community-Team",
        "contact_lead_desc": "Schreiben Sie direkt an Gala (Community Lead) für Begleitung und Materialien.",
        "partner_badge": "Förderpartner",
        "partner_title": "Mit Unterstützung der Fondation de France",
        "partner_desc": "Open Food Facts dankt der <strong>Fondation de France</strong> herzlich für ihre entscheidende Unterstützung von Bürgerwissenschaft und offener Lebensmitteltransparenz.",
        "partner_link_text": "Mehr über die Fondation de France erfahren &rarr;",
        "js_upcoming": "Bevorstehend",
        "js_past": "Vergangenes Event",
        "js_read_more": "Dossier lesen &rarr;",
        "js_community_event": "Community-Workshop",
        "js_products_word": "Produkte",
    },
    "it": {
        "hero_badge": "Ecosistema Open Food Facts • Scienza Cittadina Partecipativa",
        "hero_title_1": "Incontratevi. Scansionate.",
        "hero_title_2": "Democratizzate i dati alimentari.",
        "hero_desc": "Una <strong>Scan Party</strong> è un laboratorio collaborativo e conviviale in cui cittadini, volontari e consumatori si incontrano in supermercati, cooperative o spazi comunitari per fotografare codici a barre, ingredienti, tabelle nutrizionali e imballaggi per <strong>Open Food Facts</strong>.",
        "btn_organize": "🚀 Segnala / Organizza un evento",
        "btn_kit": "📦 Kit per l'organizzatore & Volantini Canva",
        "btn_workflows": "📱 2 modi di scansionare",
        "btn_simulator": "🎮 Simulatore di scansione",
        "btn_directory": "📅 Elenco degli eventi",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Prodotti aperti",
        "stat_products_sub": "Nel database pubblico",
        "stat_free_num": "100%",
        "stat_free_label": "Libero & ODbL",
        "stat_free_sub": "Bene comune globale",
        "stat_countries_num": "180+",
        "stat_countries_label": "Paesi coinvolti",
        "stat_countries_sub": "In tutto il mondo",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Contributori",
        "stat_volunteers_sub": "Attivi nel mondo",
        "hero_photo_badge": "Foto storica",
        "hero_photo_title": "1ª Assemblea Generale di Open Food Facts a Parigi",
        "hero_photo_desc": "I primi contributori fotografano e scansionano centinaia di prodotti insieme già nel 2015.",
        "hero_photo_loc": "Parigi, Francia (2015)",
        "tribute_title": "❤️ I volti e l'energia dei nostri contributori",
        "tribute_subtitle": "Fin dai primi giorni di Open Food Facts, le scan party si basano su persone curiose e determinate a portare trasparenza nell'alimentazione.",
        "tribute_c1_title": "1ª Assemblea Generale a Parigi",
        "tribute_c1_desc": "20 giugno 2015: Prima scan party collettiva durante l'assemblea fondativa di Open Food Facts.",
        "tribute_c2_title": "Scan Party improvvisata a Lione",
        "tribute_c2_desc": "Giugno 2015: Spedizione spontanea in un negozio di alimentari asiatico per mappare decine di prodotti.",
        "tribute_c3_title": "Marie-Claire, pioniera della prima ora",
        "tribute_c3_desc": "A caccia di codici a barre in Spagna dopo aver aggiunto oltre 200 prodotti prima del lancio pubblico!",
        "tribute_invitation_title": "Chi si unisce dopo?",
        "tribute_invitation_1": "Tu? :-)",
        "tribute_invitation_2": "La tua famiglia? :-)",
        "tribute_invitation_3": "I tuoi amici e colleghi? :-)",
        "tribute_cta": "Condividi le foto dei tuoi laboratori con l'hashtag <strong>#scanparty</strong> o scrivici a <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>!",
        "concept_badge": "Concetto & Missione",
        "concept_title": "Cos'è una Scan Party?",
        "concept_lead": "Un evento conviviale ed educativo che unisce lavoro di squadra e scienza partecipativa: decifrare le etichette alimentari arricchendo il più grande bene comune alimentare al mondo.",
        "pillar_1_title": "Arricchire il database aperto",
        "pillar_1_desc": "Aggiungere nuovi prodotti e aggiornare ingredienti, tabelle nutrizionali e dettagli sul riciclo.",
        "pillar_2_title": "Informare i consumatori",
        "pillar_2_desc": "Fornire informazioni chiare e verificate per compiere scelte alimentari più sane e sostenibili.",
        "pillar_3_title": "Creare legami sociali",
        "pillar_3_desc": "Condividere un momento stimolante tra vicini, colleghi, studenti o soci cooperativi attorno al cibo.",
        "pillar_4_title": "Sensibilizzare & Educare",
        "pillar_4_desc": "Comprendere il Nutri-Score, l'Eco-Score, la classificazione NOVA dei cibi ultra-processati e gli additivi.",
        "wf_badge": "2 Metodi Flessibili",
        "wf_title": "Due modi semplici per organizzare il tuo laboratorio",
        "wf_lead": "Che tu abbia un ottimo Wi-Fi o che ti trovi nel seminterrato di un negozio senza rete, Open Food Facts si adatta!",
        "wf1_badge": "Ideale con Wi-Fi / 4G",
        "wf1_title": "Metodo 1: Scansione live tramite App Mobile",
        "wf1_desc": "I partecipanti scaricano l'app gratuita Open Food Facts e inseriscono i prodotti direttamente dal telefono.",
        "wf1_step1_title": "Installa l'app gratuita",
        "wf1_step1_desc": "Disponibile su iOS e Android senza pubblicità né abbonamenti.",
        "wf1_step2_title": "Forma coppie di partecipanti",
        "wf1_step2_desc": "Una persona manipola il prodotto, la seconda scansiona il codice a barre e scatta le foto.",
        "wf1_step3_title": "Fotografa i 4 lati chiave",
        "wf1_step3_desc": "Fronte della confezione, ingredienti, tabella nutrizionale e istruzioni di riciclo.",
        "wf1_step4_title": "Riconoscimento OCR e calcolo immediato",
        "wf1_step4_desc": "L'OCR integrato estrae il testo e calcola Nutri-Score ed Eco-Score in tempo reale!",
        "wf1_btn": "📱 Scarica l'App Open Food Facts",
        "wf2_badge": "Senza Wi-Fi né rete!",
        "wf2_title": "Metodo 2: Foto offline & Importazione Pro",
        "wf2_desc": "Senza connessione, fotografa i prodotti con la fotocamera dello smartphone seguendo la sequenza ancora, poi carica la cartella sulla piattaforma Pro!",
        "wf2_step1_title": "Foto consecutive con lo smartphone",
        "wf2_step1_desc": "Usa semplicemente l'app fotocamera standard del telefono.",
        "wf2_step2_title": "Foto del codice a barre per prima",
        "wf2_step2_desc": "Il codice a barre funge da separatore per il nostro algoritmo di raggruppamento.",
        "wf2_step3_title": "Raccogli le cartelle di foto",
        "wf2_step3_desc": "Raccogli le cartelle di foto sul computer dell'organizzatore dopo l'evento.",
        "wf2_step4_title": "Trascina sulla piattaforma Pro",
        "wf2_step4_desc": "Carica l'intera cartella su pro.openfoodfacts.org per l'elaborazione automatica!",
        "wf2_btn": "🌐 Accedi alla Piattaforma Produttori (pro.openfoodfacts.org)",
        "seq_title": "La sequenza di foto «Codice a barre ancora»",
        "seq_desc": "Per il metodo offline, segui scrupolosamente questo ordine: il codice a barre funge da punto di riferimento per raggruppare le foto successive.",
        "seq_pill": "Fase 1 • Ancora",
        "seq_s1_title": "1. Codice a barre",
        "seq_s1_desc": "Ben piatto e a fuoco con cifre leggibili (funge da separatore).",
        "seq_s2_title": "2. Fronte confezione",
        "seq_s2_desc": "Nome del prodotto, marca, loghi ufficiali e peso netto.",
        "seq_s3_title": "3. Lista ingredienti",
        "seq_s3_desc": "Elenco integrale degli ingredienti e indicazioni sugli allergeni.",
        "seq_s4_title": "4. Tabella nutrizionale",
        "seq_s4_desc": "Valori per 100g / 100ml (calorie, zuccheri, sale, grassi).",
        "seq_s5_title": "5. Imballaggio & Riciclo",
        "seq_s5_desc": "Simboli di smaltimento e tipo di materiale (PET, HDPE, ecc.).",
        "sim_badge": "Simulatore Interattivo",
        "sim_title": "Simulatore di Scan Party",
        "sim_lead": "Clicca sui prodotti sullo scaffale per vedere la scansione e il calcolo dei punteggi in tempo reale!",
        "sim_shelf_title": "Scaffale del negozio:",
        "sim_card_title": "Scheda Open Food Facts in tempo reale",
        "sim_scan_btn": "Scansiona questo prodotto &rarr;",
        "sim_goal_label": "Progresso del laboratorio:",
        "kit_badge": "Risorse & Guide",
        "kit_title": "La cassetta degli attrezzi dell'organizzatore",
        "kit_lead": "Tutto ciò di cui hai bisogno per preparare, animare e promuovere la tua Scan Party:",
        "kit_canva_title": "Modelli di locandine Canva",
        "kit_canva_desc": "Locandine A4 personalizzabili, banner social e fogli presenze pronti da stampare.",
        "kit_canva_btn": "🎨 Apri la cartella Canva",
        "kit_pdf_title": "Guida metodologica in PDF",
        "kit_pdf_desc": "Guida dettagliata di 12 pagine per organizzare gli spazi, contattare i negozi e facilitare i gruppi.",
        "kit_pdf_btn": "📥 Scarica la Guida in PDF",
        "kit_blog_en_title": "Articolo metodologico (EN)",
        "kit_blog_en_desc": "Articolo di blog che spiega come organizzare un laboratorio partecipativo.",
        "kit_blog_en_btn": "🌐 Leggi l'articolo (EN)",
        "kit_blog_fr_title": "Guida pratica (FR)",
        "kit_blog_fr_desc": "Guida pratica in francese: «Organisez une scan party emballages».",
        "kit_blog_fr_btn": "🌐 Leggi l'articolo (FR)",
        "chk_badge": "Preparazione",
        "chk_title": "Checklist interattiva dell'organizzatore",
        "chk_lead": "Spunta i passaggi per non dimenticare nulla durante l'organizzazione:",
        "dir_badge": "Rete Globale",
        "dir_title": "Elenco delle Scan Party",
        "dir_lead": "Scopri i prossimi laboratori ed esplora gli eventi passati in tutto il mondo:",
        "filter_all": "Tutti gli eventi",
        "filter_upcoming": "In programma",
        "filter_past": "Eventi passati",
        "search_placeholder": "🔍 Filtra per città, luogo, paese...",
        "declare_banner_title": "Organizzi una Scan Party? Falla conoscere!",
        "declare_banner_desc": "Aggiungi il tuo evento con 1 clic tramite una issue GitHub o una Pull Request.",
        "btn_declare_gh": "🚀 Registra un evento (1 clic)",
        "btn_declare_pr": "✏️ Proponi un file YAML (PR)",
        "comm_title": "Connettiti con la community",
        "comm_lead": "Domande sull'organizzazione o supporto per animare il gruppo?",
        "slack_global_title": "Canale Slack Internazionale",
        "slack_global_desc": "Unisciti a #scanparty su Slack per confrontarti con organizzatori di tutto il mondo.",
        "slack_fr_title": "Canale Slack Francofono",
        "slack_fr_desc": "Unisciti a #scanparty_fr per laboratori nei paesi francofoni.",
        "contact_lead_title": "Contatto Team Community",
        "contact_lead_desc": "Scrivi direttamente a Gala (Community Lead) per supporto e materiali.",
        "partner_badge": "Partner di Sostegno",
        "partner_title": "Con il sostegno della Fondation de France",
        "partner_desc": "Open Food Facts ringrazia calorosamente la <strong>Fondation de France</strong> per il suo prezioso supporto alla scienza civica partecipativa e all'apertura dei dati alimentari.",
        "partner_link_text": "Scopri di più sulla Fondation de France &rarr;",
        "js_upcoming": "In programma",
        "js_past": "Evento passato",
        "js_read_more": "Leggi la scheda &rarr;",
        "js_community_event": "Laboratorio comunitario",
        "js_products_word": "prodotti",
    },
    "es": {
        "hero_badge": "Ecosistema Open Food Facts • Ciencia Ciudadana Participativa",
        "hero_title_1": "Reúnete. Escanea.",
        "hero_title_2": "Democratiza los datos alimentarios.",
        "hero_desc": "Una <strong>Scan Party</strong> es un taller colaborativo y dinámico donde ciudadanos, voluntarios y consumidores se reúnen en supermercados, cooperativas o centros comunitarios para fotografiar códigos de barras, ingredientes, tablas nutricionales y envases directamente para <strong>Open Food Facts</strong>.",
        "btn_organize": "🚀 Proponer / Organizar un taller",
        "btn_kit": "📦 Guía del anfitrión & Carteles Canva",
        "btn_workflows": "📱 2 formas de escanear",
        "btn_simulator": "🎮 Simulador de escaneo",
        "btn_directory": "📅 Directorio de talleres",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Productos abiertos",
        "stat_products_sub": "En la base pública",
        "stat_free_num": "100%",
        "stat_free_label": "Libre & ODbL",
        "stat_free_sub": "Bien común global",
        "stat_countries_num": "180+",
        "stat_countries_label": "Países alcanzados",
        "stat_countries_sub": "En todo el planeta",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Colaboradores",
        "stat_volunteers_sub": "Activos en el mundo",
        "hero_photo_badge": "Foto histórica",
        "hero_photo_title": "1ª Asamblea General de Open Food Facts en París",
        "hero_photo_desc": "Los primeros colaboradores fotografían y catalogan cientos de productos juntos ya en 2015.",
        "hero_photo_loc": "París, Francia (2015)",
        "tribute_title": "❤️ Las caras y la energía de nuestros colaboradores",
        "tribute_subtitle": "Desde los primeros días de Open Food Facts, las scan parties se apoyan en personas apasionadas y comprometidas con la transparencia alimentaria.",
        "tribute_c1_title": "1ª Asamblea General en París",
        "tribute_c1_desc": "20 de junio de 2015: Primera scan party colectiva durante la asamblea constituyente de Open Food Facts.",
        "tribute_c2_title": "Scan Party improvisada en Lyon",
        "tribute_c2_desc": "Junio de 2015: Expedición espontánea a una tienda de ultramarinos asiática para registrar decenas de especialidades.",
        "tribute_c3_title": "Marie-Claire, pionera de la primera hora",
        "tribute_c3_desc": "Cazando códigos de barras en España tras haber subido más de 200 productos antes del lanzamiento público.",
        "tribute_invitation_title": "¿Quién se une ahora?",
        "tribute_invitation_1": "¿Tú? :-)",
        "tribute_invitation_2": "¿Tu familia? :-)",
        "tribute_invitation_3": "¿Tus amistades y colegas? :-)",
        "tribute_cta": "Comparte las fotos de tus talleres con el hashtag <strong>#scanparty</strong> o escríbenos a <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>.",
        "concept_badge": "Concepto & Misión",
        "concept_title": "¿Qué es una Scan Party?",
        "concept_lead": "Un evento ameno y formativo que aúna trabajo en equipo y ciencia ciudadana: descifrar las etiquetas de los alimentos mientras se enriquece el mayor bien común alimentario del planeta.",
        "pillar_1_title": "Enriquecer la base abierta",
        "pillar_1_desc": "Añadir nuevos productos y actualizar listas de ingredientes, tablas nutricionales e información de reciclaje.",
        "pillar_2_title": "Empoderar a los consumidores",
        "pillar_2_desc": "Ofrecer datos verificados para que cualquier persona pueda elegir alimentos más saludables y sostenibles.",
        "pillar_3_title": "Fomentar lazos comunitarios",
        "pillar_3_desc": "Compartir un momento enriquecedor entre vecinos, estudiantes, compañeros de trabajo o socios cooperativistas.",
        "pillar_4_title": "Sensibilizar & Educar",
        "pillar_4_desc": "Comprender el Nutri-Score, el Eco-Score, la clasificación NOVA de alimentos ultraprocesados y los aditivos.",
        "wf_badge": "2 Métodos Flexibles",
        "wf_title": "Dos formas sencillas de organizar tu taller",
        "wf_lead": "Tanto si tienes buena cobertura Wi-Fi como si estás en el sótano de una tienda sin señal: ¡Open Food Facts se adapta!",
        "wf1_badge": "Ideal con Wi-Fi / 4G",
        "wf1_title": "Método 1: Escaneo en directo con la App Móvil",
        "wf1_desc": "Los participantes instalan la app gratuita Open Food Facts e introducen los productos directamente desde sus teléfonos.",
        "wf1_step1_title": "Instalar la app gratuita",
        "wf1_step1_desc": "Disponible para iOS y Android sin anuncios ni muros de pago.",
        "wf1_step2_title": "Formar parejas de trabajo",
        "wf1_step2_desc": "Una persona manipula el producto y la otra escanea el código de barras y toma las fotos.",
        "wf1_step3_title": "Fotografiar los 4 ángulos clave",
        "wf1_step3_desc": "Frontal del envase, ingredientes, tabla nutricional y datos de reciclaje.",
        "wf1_step4_title": "OCR y cálculo inmediato de puntuaciones",
        "wf1_step4_desc": "El OCR integrado extrae el texto y calcula el Nutri-Score y el Eco-Score en tiempo real.",
        "wf1_btn": "📱 Descargar la App Open Food Facts",
        "wf2_badge": "¡Sin necesidad de Wi-Fi!",
        "wf2_title": "Método 2: Fotos sin conexión e Importación Pro",
        "wf2_desc": "En lugares sin red, toma fotos con la cámara de tu smartphone respetando la secuencia ancla y sube la carpeta al llegar a casa a la plataforma Pro.",
        "wf2_step1_title": "Fotos consecutivas con el smartphone",
        "wf2_step1_desc": "Utiliza la app de cámara predeterminada de tu teléfono móvil.",
        "wf2_step2_title": "Foto del código de barras en primer lugar",
        "wf2_step2_desc": "La foto del código de barras sirve de delimitador para nuestro algoritmo de emparejamiento.",
        "wf2_step3_title": "Reunir las fotos en una carpeta",
        "wf2_step3_desc": "Reúne las fotos de todos los equipos en el ordenador del anfitrión al finalizar el taller.",
        "wf2_step4_title": "Arrastrar y soltar en la plataforma Pro",
        "wf2_step4_desc": "Sube la carpeta a pro.openfoodfacts.org para que se procese automáticamente.",
        "wf2_btn": "🌐 Ir a la Plataforma de Productores (pro.openfoodfacts.org)",
        "seq_title": "Protocolo de fotos «Código de barras ancla»",
        "seq_desc": "Para el método sin conexión, sigue estrictamente este orden: la foto del código de barras es el ancla para agrupar las imágenes siguientes.",
        "seq_pill": "Paso 1 • Ancla",
        "seq_s1_title": "1. Código de barras",
        "seq_s1_desc": "Bien enfocado y plano, con los números visibles (actúa como separador).",
        "seq_s2_title": "2. Parte frontal",
        "seq_s2_desc": "Nombre del producto, marca, sellos oficiales y cantidad neta.",
        "seq_s3_title": "3. Lista de ingredientes",
        "seq_s3_desc": "Listado completo de ingredientes y menciones de alérgenos.",
        "seq_s4_title": "4. Tabla nutricional",
        "seq_s4_desc": "Valores por 100g / 100ml (calorías, azúcares, grasas, sal).",
        "seq_s5_title": "5. Envase & Reciclaje",
        "seq_s5_desc": "Símbolos de reciclaje e identificación de materiales plásticos (PET, PEAD, etc.).",
        "sim_badge": "Simulador Interactivo",
        "sim_title": "Simulador de Scan Party",
        "sim_lead": "Haz clic en los productos del estante para ver el escaneo y el cálculo de puntuaciones en tiempo real.",
        "sim_shelf_title": "Estantería de tienda:",
        "sim_card_title": "Ficha en vivo de Open Food Facts",
        "sim_scan_btn": "Escanear este producto &rarr;",
        "sim_goal_label": "Progreso del taller:",
        "kit_badge": "Recursos & Guías",
        "kit_title": "Caja de herramientas del anfitrión",
        "kit_lead": "Todo lo que necesitas para preparar, dinamizar y difundir tu Scan Party:",
        "kit_canva_title": "Plantillas de carteles en Canva",
        "kit_canva_desc": "Pósteres A4 personalizables, banners para redes sociales y hojas de registro listas para imprimir.",
        "kit_canva_btn": "🎨 Abrir carpeta de diseños en Canva",
        "kit_pdf_title": "Guía metodológica en PDF",
        "kit_pdf_desc": "Manual paso a paso de 12 páginas para acondicionar el espacio, contactar con tiendas y coordinar equipos.",
        "kit_pdf_btn": "📥 Descargar Guía en PDF",
        "kit_blog_en_title": "Artículo metodológico (EN)",
        "kit_blog_en_desc": "Artículo oficial de blog que detalla cómo organizar un taller ciudadano participativo.",
        "kit_blog_en_btn": "🌐 Leer artículo (EN)",
        "kit_blog_fr_title": "Guía práctica (FR)",
        "kit_blog_fr_desc": "Guía práctica en francés: «Organisez une scan party emballages».",
        "kit_blog_fr_btn": "🌐 Leer artículo (FR)",
        "chk_badge": "Preparación",
        "chk_title": "Lista interactiva de preparativos",
        "chk_lead": "Marca cada paso para tenerlo todo a punto en tu taller:",
        "dir_badge": "Red Mundial",
        "dir_title": "Directorio de Scan Parties",
        "dir_lead": "Descubre los próximos talleres y revive las ediciones pasadas en todo el mundo:",
        "filter_all": "Todos los talleres",
        "filter_upcoming": "Próximos",
        "filter_past": "Ediciones pasadas",
        "search_placeholder": "🔍 Filtrar por ciudad, lugar, país...",
        "declare_banner_title": "¿Organizas una Scan Party? ¡Compártela aquí!",
        "declare_banner_desc": "Registra tu taller en 1 clic a través de un ticket de GitHub o una Pull Request.",
        "btn_declare_gh": "🚀 Registrar taller (1 clic)",
        "btn_declare_pr": "✏️ Proponer archivo YAML (PR)",
        "comm_title": "Conecta con la comunidad",
        "comm_lead": "¿Tienes dudas sobre la organización o necesitas apoyo para coordinar tu grupo?",
        "slack_global_title": "Canal Slack Internacional",
        "slack_global_desc": "Únete a #scanparty en Slack para coordinarte con organizadores de todo el mundo.",
        "slack_fr_title": "Canal Slack Francófono",
        "slack_fr_desc": "Únete a #scanparty_fr para talleres en países de habla francesa.",
        "contact_lead_title": "Contacto del Equipo de Comunidad",
        "contact_lead_desc": "Escribe directamente a Gala (Responsable de Comunidad) para recibir asistencia y materiales.",
        "partner_badge": "Entidad Colaboradora",
        "partner_title": "Con el apoyo de la Fondation de France",
        "partner_desc": "Open Food Facts agradece sinceramente a la <strong>Fondation de France</strong> su apoyo continuado a la ciencia ciudadana participativa y a la apertura de datos alimentarios.",
        "partner_link_text": "Más información sobre la Fondation de France &rarr;",
        "js_upcoming": "Próximo",
        "js_past": "Edición pasada",
        "js_read_more": "Ver ficha completa &rarr;",
        "js_community_event": "Taller comunitario",
        "js_products_word": "productos",
    },
    "nl": {
        "hero_badge": "Open Food Facts Ecosysteem • Participatieve Burgerwetenschap",
        "hero_title_1": "Kom samen. Scan.",
        "hero_title_2": "Democratiseer voedseldata.",
        "hero_desc": "Een <strong>Scan Party</strong> is een gezellige en interactieve workshop waar burgers, vrijwilligers en consumenten samenkomen in supermarkten, coöperaties of ontmoetingsplekken om streepjescodes, ingrediënten, voedingstabellen en verpakkingen vast te leggen voor <strong>Open Food Facts</strong>.",
        "btn_organize": "🚀 Workshop aanmelden / organiseren",
        "btn_kit": "📦 Handleiding & Canva-posters",
        "btn_workflows": "📱 2 manieren om te scannen",
        "btn_simulator": "🎮 Scan-simulator",
        "btn_directory": "📅 Overzicht van workshops",
        "stat_products_num": "3,8M+",
        "stat_products_label": "Open producten",
        "stat_products_sub": "In de openbare database",
        "stat_free_num": "100%",
        "stat_free_label": "Vrij & ODbL",
        "stat_free_sub": "Wereldwijd publiek goed",
        "stat_countries_num": "180+",
        "stat_countries_label": "Bereikte landen",
        "stat_countries_sub": "Wereldwijd bereik",
        "stat_volunteers_num": "15 000+",
        "stat_volunteers_label": "Vrijwilligers",
        "stat_volunteers_sub": "Wereldwijd actief",
        "hero_photo_badge": "Historische foto",
        "hero_photo_title": "1e Algemene Ledenvergadering van Open Food Facts in Parijs",
        "hero_photo_desc": "Pioniers fotograferen en scannen samen honderden producten in 2015.",
        "hero_photo_loc": "Parijs, Frankrijk (2015)",
        "tribute_title": "❤️ De gezichten en energie van onze vrijwilligers",
        "tribute_subtitle": "Sinds de begindagen van Open Food Facts draaien scan parties om nieuwsgierige, betrokken mensen die voedseltransparantie voor iedereen bereikbaar maken.",
        "tribute_c1_title": "1e Algemene Vergadering in Parijs",
        "tribute_c1_desc": "20 juni 2015: Eerste gezamenlijke scan party tijdens de oprichtingsvergadering in Parijs.",
        "tribute_c2_title": "Spontane Scan Party in Lyon",
        "tribute_c2_desc": "Juni 2015: Spontane expeditie in een Aziatische supermarkt om tientallen specialiteiten te indexeren.",
        "tribute_c3_title": "Marie-Claire, pionier van het eerste uur",
        "tribute_c3_desc": "Streepjescodes scannen in Spanje nadat ze al vóór de officiële lancering meer dan 200 producten toevoegde!",
        "tribute_invitation_title": "Wie doet er de volgende keer mee?",
        "tribute_invitation_1": "Jij? :-)",
        "tribute_invitation_2": "Je familie? :-)",
        "tribute_invitation_3": "Je vrienden en collega's? :-)",
        "tribute_cta": "Deel je workshopfoto's met hashtag <strong>#scanparty</strong> of stuur ze naar <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>!",
        "concept_badge": "Concept & Missie",
        "concept_title": "Wat is een Scan Party?",
        "concept_lead": "Een gezellige en leerzame bijeenkomst die teamwerk en burgerwetenschap combineert: ontcijfer voedseletiketten en help het grootste open voedselbestand ter wereld uit te breiden.",
        "pillar_1_title": "De open database verrijken",
        "pillar_1_desc": "Nieuwe producten toevoegen en ingrediëntenlijsten, voedingstabellen en recycle-instructies bijwerken.",
        "pillar_2_title": "Consumenten informeren",
        "pillar_2_desc": "Iedereen voorzien van duidelijke, geverifieerde feiten om gezondere en duurzamere keuzes te maken.",
        "pillar_3_title": "Samenhorigheid stimuleren",
        "pillar_3_desc": "Buurtbewoners, studenten, collega's en coöperatieleden samenbrengen rondom gezonde voeding.",
        "pillar_4_title": "Bewustmaken & Leren",
        "pillar_4_desc": "De Nutri-Score, Eco-Score, NOVA-classificatie voor ultra-bewerkte voeding en additieven ontrafelen.",
        "wf_badge": "2 Handige Werkwijzen",
        "wf_title": "Twee eenvoudige manieren om je workshop te organiseren",
        "wf_lead": "Of je nu supersnel Wi-Fi hebt of in de kelder van een winkel staat zonder bereik: Open Food Facts werkt overal!",
        "wf1_badge": "Ideaal met Wi-Fi / 4G",
        "wf1_title": "Methode 1: Live scannen via de mobiele app",
        "wf1_desc": "Deelnemers installeren de gratis Open Food Facts app en voegen producten rechtstreeks toe via hun telefoon.",
        "wf1_step1_title": "Installeer de gratis app",
        "wf1_step1_desc": "Beschikbaar voor iOS en Android – advertentievrij en zonder betaalmuren.",
        "wf1_step2_title": "Vorm tweetallen",
        "wf1_step2_desc": "Eén persoon pakt het product beet, de tweede scant de streepjescode en maakt duidelijke foto's.",
        "wf1_step3_title": "Fotografeer 4 belangrijke zijden",
        "wf1_step3_desc": "Voorzijde verpakking, ingrediëntenlijst, voedingstabel en recycle-instructies.",
        "wf1_step4_title": "Directe OCR-herkenning & scores",
        "wf1_step4_desc": "De ingebouwde OCR extraheert tekst en berekent de Nutri-Score en Eco-Score direct ter plekke!",
        "wf1_btn": "📱 Download de Open Food Facts App",
        "wf2_badge": "Geen Wi-Fi nodig!",
        "wf2_title": "Methode 2: Offline foto's & Import via Pro",
        "wf2_desc": "Geen mobiel netwerk? Maak foto's met de normale camera van je smartphone volgens het anker-protocol en upload de map later in één keer op het Pro-platform!",
        "wf2_step1_title": "Achtereenvolgende foto's met smartphone",
        "wf2_step1_desc": "Gebruik gewoon de standaard camera-app op je telefoon.",
        "wf2_step2_title": "Foto van de streepjescode eerst",
        "wf2_step2_desc": "De foto van de streepjescode fungeert als scheidingsteken voor ons groeperingsalgoritme.",
        "wf2_step3_title": "Verzamel de fotomappen",
        "wf2_step3_desc": "Breng alle fotomappen na de bijeenkomst samen op de laptop van de organisator.",
        "wf2_step4_title": "Sleep naar het Pro-platform",
        "wf2_step4_desc": "Upload de complete map naar pro.openfoodfacts.org voor automatische verwerking!",
        "wf2_btn": "🌐 Naar het Producentenplatform (pro.openfoodfacts.org)",
        "seq_title": "Het fotoprotocol «Anker-streepjescode»",
        "seq_desc": "Volg bij offline scannen nauwgezet deze vaste volgorde: de streepjescodefoto is het startpunt om volgende foto's aan het juiste product te koppelen.",
        "seq_pill": "Stap 1 • Anker",
        "seq_s1_title": "1. Streepjescode",
        "seq_s1_desc": "Plat en haarscherp met leesbare cijfers (dient als scheiding).",
        "seq_s2_title": "2. Voorzijde",
        "seq_s2_desc": "Productnaam, merk, officiële keurmerken en netto-inhoud.",
        "seq_s3_title": "3. Ingrediëntenlijst",
        "seq_s3_desc": "Volledige lijst met ingrediënten en allergeenvermeldingen.",
        "seq_s4_title": "4. Voedingstabel",
        "seq_s4_desc": "Waarden per 100g / 100ml (energie, suikers, vetten, zout).",
        "seq_s5_title": "5. Verpakking & Recycling",
        "seq_s5_desc": "Recyclesymbolen, sorteerinstructies en type kunststof (PET, HDPE, enz.).",
        "sim_badge": "Interactieve Simulator",
        "sim_title": "Scan Party simulator",
        "sim_lead": "Klik op producten in het schap om streepjescode-scans en scoreberekeningen live te zien gebeuren!",
        "sim_shelf_title": "Winkelschap:",
        "sim_card_title": "Live Open Food Facts productweergave",
        "sim_scan_btn": "Scan dit product &rarr;",
        "sim_goal_label": "Voortgang workshop:",
        "kit_badge": "Materialen & Handleidingen",
        "kit_title": "De gereedschapskist voor organisatoren",
        "kit_lead": "Alles wat je nodig hebt om je Scan Party voor te bereiden, te begeleiden en bekend te maken:",
        "kit_canva_title": "Canva-postersjablonen",
        "kit_canva_desc": "Aanpasbare A4-posters, banners voor sociale media en printklare presentielijsten in Canva.",
        "kit_canva_btn": "🎨 Open de Canva-map",
        "kit_pdf_title": "Methodische PDF-handleiding",
        "kit_pdf_desc": "Stapsgewijze handleiding van 12 pagina's voor ruimteplanning, winkelcontact en groepsbegeleiding.",
        "kit_pdf_btn": "📥 Download de PDF-handleiding",
        "kit_blog_en_title": "Handleiding-artikel (EN)",
        "kit_blog_en_desc": "Officieel blogartikel met uitleg over het organiseren van participatieve burgerworkshops.",
        "kit_blog_en_btn": "🌐 Lees artikel (EN)",
        "kit_blog_fr_title": "Praktijkgids (FR)",
        "kit_blog_fr_desc": "Praktijkervaring in het Frans: «Organisez une scan party emballages».",
        "kit_blog_fr_btn": "🌐 Lees artikel (FR)",
        "chk_badge": "Voorbereiding",
        "chk_title": "Interactieve checklist voor de organisatie",
        "chk_lead": "Vink de stappen af om niets te vergeten tijdens de organisatie:",
        "dir_badge": "Wereldwijd Netwerk",
        "dir_title": "Overzicht van Scan Parties",
        "dir_lead": "Ontdek aankomende workshops en bekijk eerdere evenementen wereldwijd:",
        "filter_all": "Alle workshops",
        "filter_upcoming": "Binnenkort",
        "filter_past": "Eerdere edities",
        "search_placeholder": "🔍 Filter op stad, locatie, land...",
        "declare_banner_title": "Organiseer je een Scan Party? Laat het weten!",
        "declare_banner_desc": "Voeg je workshop in 1 klik toe via een GitHub issue of Pull Request.",
        "btn_declare_gh": "🚀 Meld een workshop aan (1 klik)",
        "btn_declare_pr": "✏️ Stel een YAML-bestand voor (PR)",
        "comm_title": "In gesprek met de gemeenschap",
        "comm_lead": "Vragen over de organisatie of hulp nodig bij het opzetten van je groep?",
        "slack_global_title": "Internationaal Slack-kanaal",
        "slack_global_desc": "Word lid van #scanparty op Slack om ideeën uit te wisselen met organisatoren wereldwijd.",
        "slack_fr_title": "Franstalig Slack-kanaal",
        "slack_fr_desc": "Word lid van #scanparty_fr voor workshops in Franstalige gebieden.",
        "contact_lead_title": "Contact Community-team",
        "contact_lead_desc": "Neem rechtstreeks contact op met Gala (Community Lead) voor ondersteuning en materialen.",
        "partner_badge": "Ondersteunende Partner",
        "partner_title": "Met steun van de Fondation de France",
        "partner_desc": "Open Food Facts bedankt de <strong>Fondation de France</strong> hartelijk voor de steun aan participatieve burgerwetenschap en open voedseltransparantie voor iedereen.",
        "partner_link_text": "Meer informatie over de Fondation de France &rarr;",
        "js_upcoming": "Binnenkort",
        "js_past": "Eerdere editie",
        "js_read_more": "Bekijk verslag &rarr;",
        "js_community_event": "Community-workshop",
        "js_products_word": "producten",
    },
    "en": {
        "hero_badge": "Open Food Facts Ecosystem • Participatory Citizen Science",
        "hero_title_1": "Gather. Scan.",
        "hero_title_2": "Democratize Food Data.",
        "hero_desc": "A <strong>Scan Party</strong> is a collaborative, hands-on gathering where citizens, volunteers, and food advocates meet in local supermarkets, cooperative grocery stores, or community spaces to scan barcodes, capture ingredients, nutrition facts, and packaging specs directly for <strong>Open Food Facts</strong>.",
        "btn_organize": "🚀 Submit / Host a Party",
        "btn_kit": "📦 Host Toolkit & Canva Flyers",
        "btn_workflows": "📱 2 Ways to Scan",
        "btn_simulator": "🎮 Scan Playground",
        "btn_directory": "📅 Events Directory",
        "stat_products_num": "3.8M+",
        "stat_products_label": "Open Products",
        "stat_products_sub": "In public database",
        "stat_free_num": "100%",
        "stat_free_label": "Free & Open Source",
        "stat_free_sub": "Global public commons",
        "stat_countries_num": "180+",
        "stat_countries_label": "Countries Impacted",
        "stat_countries_sub": "Worldwide reach",
        "stat_volunteers_num": "15,000+",
        "stat_volunteers_label": "Citizen Contributors",
        "stat_volunteers_sub": "Active worldwide",
        "hero_photo_badge": "Historical Gathering",
        "hero_photo_title": "1st OFF General Assembly in Paris",
        "hero_photo_desc": "Pioneering contributors scanning and cataloging products together in Paris back in 2015.",
        "hero_photo_loc": "Paris, France (2015)",
        "tribute_title": "❤️ Heart-Warming Energy: Yes They Scan!",
        "tribute_subtitle": "Since the earliest days of Open Food Facts, scan parties have been powered by kind, passionate people determined to bring food transparency to everyone.",
        "tribute_c1_title": "1st General Assembly in Paris",
        "tribute_c1_desc": "June 20, 2015: First collective scan gathering during the founding assembly of Open Food Facts in Paris.",
        "tribute_c2_title": "Impromptu Scan Party in Lyon",
        "tribute_c2_desc": "June 2015: Spontaneous expedition in an Asian grocery store to decode and index dozens of specialties.",
        "tribute_c3_title": "Marie-Claire, Pioneer Contributor",
        "tribute_c3_desc": "Hunting barcodes in Spain after cataloging over 200 products before the public launch of Open Food Facts!",
        "tribute_invitation_title": "Joining us next...",
        "tribute_invitation_1": "You? :-)",
        "tribute_invitation_2": "Your family? :-)",
        "tribute_invitation_3": "Your friends? :-)",
        "tribute_cta": "Share your scan party photos with <strong>#scanparty</strong> or send them to <a href='mailto:scanparty@openfoodfacts.org'>scanparty@openfoodfacts.org</a>!",
        "concept_badge": "Concept & Mission",
        "concept_title": "What is a Scan Party?",
        "concept_lead": "A fun, educational, and impactful workshop combining social teamwork with citizen science: decipher food labels while enriching the world's largest open food commons.",
        "pillar_1_title": "Enrich Open Food Facts",
        "pillar_1_desc": "Add new products and refresh ingredient lists, nutrition tables, and recyclable packaging specs.",
        "pillar_2_title": "Empower Consumers",
        "pillar_2_desc": "Provide verified, transparent facts to help everyone make healthier and more sustainable food choices.",
        "pillar_3_title": "Promote Collaboration",
        "pillar_3_desc": "Connect neighbors, students, coworkers, and co-op members through engaging, collaborative teamwork.",
        "pillar_4_title": "Raise Food Literacy",
        "pillar_4_desc": "Demystify Nutri-Score, Eco-Score, NOVA ultra-processing groups, and additive classifications.",
        "wf_badge": "2 Flexible Workflows",
        "wf_title": "2 Ways to Run Your Scan Party",
        "wf_lead": "Whether you have high-speed Wi-Fi in a classroom or zero cellular reception in a supermarket basement, Open Food Facts has you covered!",
        "wf1_badge": "Best with Wi-Fi / 4G",
        "wf1_title": "Method 1: Live Mobile App Scanning",
        "wf1_desc": "Participants install the free Open Food Facts mobile app, scan items, and add photos directly on their phones.",
        "wf1_step1_title": "Install Free App",
        "wf1_step1_desc": "Available on iOS and Android without ads or paywalls.",
        "wf1_step2_title": "Pair Up Participants",
        "wf1_step2_desc": "One person handles products, the second scans barcodes and captures labels.",
        "wf1_step3_title": "Capture 4 Key Angles",
        "wf1_step3_desc": "Front packaging, ingredients list, nutrition table, and recycling specs.",
        "wf1_step4_title": "Instant AI & Score Calculation",
        "wf1_step4_desc": "Built-in OCR extracts text and computes Nutri-Score & Eco-Score on the spot!",
        "wf1_btn": "📱 Download Open Food Facts App",
        "wf2_badge": "No Wi-Fi Needed!",
        "wf2_title": "Method 2: Offline Photos & Producer Import",
        "wf2_desc": "When scanning in basements with no Wi-Fi, take photos using standard camera phones following the barcode anchor sequence, then bulk upload the folder to the Producer Platform!",
        "wf2_step1_title": "Sequential Camera Photos",
        "wf2_step1_desc": "Use standard camera phones to snap clear photos.",
        "wf2_step2_title": "Barcode Photo First",
        "wf2_step2_desc": "The barcode photo serves as the separator delimiter for automatic pairing.",
        "wf2_step3_title": "Collect Photo Folders",
        "wf2_step3_desc": "Gather photo folders onto the host laptop after the event.",
        "wf2_step4_title": "Drag & Drop Bulk Upload",
        "wf2_step4_desc": "Upload the complete folder to pro.openfoodfacts.org for batch processing!",
        "wf2_btn": "🌐 Visit Producer Platform (pro.openfoodfacts.org)",
        "seq_title": "The 'Barcode Anchor' Photo Sequence Protocol",
        "seq_desc": "For offline scanning, follow this strict sequence for each product: the barcode photo acts as the delimiter so the system correctly groups consecutive packaging photos.",
        "seq_pill": "Step 1 • Anchor",
        "seq_s1_title": "1. Barcode Photo",
        "seq_s1_desc": "Flat and sharp with visible digits (acts as delimiter).",
        "seq_s2_title": "2. Front Packaging",
        "seq_s2_desc": "Product name, brand, logos, and net weight/volume.",
        "seq_s3_title": "3. Ingredients List",
        "seq_s3_desc": "Full ingredients list and allergen statements.",
        "seq_s4_title": "4. Nutrition Table",
        "seq_s4_desc": "Values per 100g / 100ml (calories, sugars, fats, salt).",
        "seq_s5_title": "5. Packaging & Eco",
        "seq_s5_desc": "Recycling symbols (Triman), material types (PET, HDPE, PP).",
        "sim_badge": "Interactive Playground",
        "sim_title": "Scan Party Simulator",
        "sim_lead": "Click items on the shelf to see barcode scanning and score calculation in real time!",
        "sim_shelf_title": "Store Shelf Products:",
        "sim_card_title": "Live Open Food Facts Inspector",
        "sim_scan_btn": "Scan this product &rarr;",
        "sim_goal_label": "Scan Party Goal Progress:",
        "kit_badge": "Host Resources & Kit",
        "kit_title": "Host Toolkit & Marketing Materials",
        "kit_lead": "Everything you need to prepare, promote, and host your local Scan Party with ease:",
        "kit_canva_title": "Canva Poster Templates",
        "kit_canva_desc": "Customizable A4 posters, social media banners, and printable sign-up sheets in Canva.",
        "kit_canva_btn": "🎨 Open Canva Design Folder",
        "kit_pdf_title": "PDF Host Handbook",
        "kit_pdf_desc": "A comprehensive 12-page step-by-step handbook covering store outreach, room setup, and team facilitation.",
        "kit_pdf_btn": "📥 Download PDF Guide",
        "kit_blog_en_title": "Workshop Guide Article (EN)",
        "kit_blog_en_desc": "Comprehensive blog post guide: 'Organise a scan party / participative workshop!'",
        "kit_blog_en_btn": "🌐 Read Article (EN)",
        "kit_blog_fr_title": "French Workshop Article",
        "kit_blog_fr_desc": "Official French announcement & guide: 'Organisez une scan party emballages'.",
        "kit_blog_fr_btn": "🌐 Read Article (FR)",
        "chk_badge": "Event Preparation",
        "chk_title": "Interactive Host Checklist",
        "chk_lead": "Track your preparation progress step-by-step to ensure a smooth, rewarding workshop:",
        "dir_badge": "Global Network",
        "dir_title": "Scan Parties Directory",
        "dir_lead": "Explore upcoming gatherings and historical scan parties from around the world:",
        "filter_all": "All Events",
        "filter_upcoming": "Upcoming",
        "filter_past": "Past Events",
        "search_placeholder": "🔍 Filter by city, venue, country...",
        "declare_banner_title": "Hosting a Scan Party? Get it listed here!",
        "declare_banner_desc": "Add your scan party in 1 click via a pre-filled GitHub issue or a Pull Request, just like reuses and scientific papers.",
        "btn_declare_gh": "🚀 Submit an Event (1-Click)",
        "btn_declare_pr": "✏️ Propose a YAML file (PR)",
        "comm_title": "Connect with the Community",
        "comm_lead": "Need guidance, ideas, or venue advice? Connect directly with organizers and OFF staff:",
        "slack_global_title": "International Slack Channel",
        "slack_global_desc": "Join #scanparty on the official Slack for global coordination and tips.",
        "slack_fr_title": "French-Speaking Slack Channel",
        "slack_fr_desc": "Join #scanparty_fr to collaborate with French-speaking organizers.",
        "contact_lead_title": "Community Lead Support",
        "contact_lead_desc": "Reach out to Gala (Community Lead) for assistance, materials, or introductions.",
        "partner_badge": "Supporting Partner",
        "partner_title": "Supported by Fondation de France",
        "partner_desc": "Open Food Facts warmly thanks the <strong>Fondation de France</strong> for its generous support of citizen participatory science, civic engagement, and open food data democratization for healthier and more sustainable food systems.",
        "partner_link_text": "Learn more about Fondation de France &rarr;",
        "js_upcoming": "Upcoming",
        "js_past": "Past Event",
        "js_read_more": "Read full dossier &rarr;",
        "js_community_event": "Community workshop",
        "js_products_word": "products",
    }
}

def generate_html(events, lang="en"):
    t = SP_STRINGS.get(lang, SP_STRINGS["en"])

    hero_photos = [
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty-off-general-meeting-20150620.jpg",
            "title": t["hero_photo_title"],
            "loc": t["hero_photo_loc"],
            "tag": t["hero_photo_badge"],
            "desc": t["hero_photo_desc"]
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty-lyon-20150601.jpg",
            "title": t["tribute_c2_title"],
            "loc": "Lyon (2015)",
            "tag": "Scan Party",
            "desc": t["tribute_c2_desc"]
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/marie-claire-scan-spain.jpg",
            "title": t["tribute_c3_title"],
            "loc": "Spain (2015)",
            "tag": "Pioneer",
            "desc": t["tribute_c3_desc"]
        },
        {
            "url": "https://world.openfoodfacts.org/images/misc/scanparty.640x480.png",
            "title": "Yes They Scan!",
            "loc": "World",
            "tag": "Scan Party",
            "desc": t["hero_desc"]
        }
    ]

    sample_products = [
        {
            "id": 1,
            "name": {"fr": "Pâte à tartiner noisettes bio", "de": "Bio-Haselnusscreme", "it": "Crema di nocciole bio", "es": "Crema de avellanas bio", "nl": "Bio hazelnootpasta"}.get(lang, "Organic Hazelnut Chocolate Spread"),
            "brand": "Bio Terroir",
            "barcode": "3017620422003",
            "icon": "🌰",
            "nutri": "E",
            "nutriColor": "#ef4444",
            "nova": "4",
            "eco": "C",
            "packaging": {"fr": "Pot en verre & couvercle alu", "de": "Glas & Aludeckel", "it": "Vasetto in vetro & coperchio alluminio", "es": "Tarro de vidrio y tapa aluminio", "nl": "Glazen pot & aluminium deksel"}.get(lang, "Glass Jar & Aluminum Lid")
        },
        {
            "id": 2,
            "name": {"fr": "Lait d'avoine sans sucre 1L", "de": "Hafermilch ungesüßt 1L", "it": "Latte d'avena senza zucchero 1L", "es": "Bebida de avena sin azúcar 1L", "nl": "Havermelk ongezoet 1L"}.get(lang, "Oat Milk Unsweetened 1L"),
            "brand": "Green Harvest",
            "barcode": "7350041864009",
            "icon": "🥛",
            "nutri": "A",
            "nutriColor": "#22c55e",
            "nova": "1",
            "eco": "A",
            "packaging": "Tetra Pak"
        },
        {
            "id": 3,
            "name": {"fr": "Chocolat noir 85% équitable", "de": "Zartbitterschokolade 85%", "it": "Cioccolato fondente 85%", "es": "Chocolate negro 85%", "nl": "Puur chocolade 85%"}.get(lang, "Artisan Dark Chocolate 85%"),
            "brand": "Cacao Libre",
            "barcode": "7613035821102",
            "icon": "🍫",
            "nutri": "B",
            "nutriColor": "#84cc16",
            "nova": "2",
            "eco": "B",
            "packaging": {"fr": "Papier recyclable & alu", "de": "Recyclingpapier & Folie", "it": "Carta riciclabile & foglio alluminio", "es": "Papel reciclable y aluminio", "nl": "Recyclebaar papier & folie"}.get(lang, "Recycled Paper & Foil")
        },
        {
            "id": 4,
            "name": {"fr": "Kombucha citron pétillant", "de": "Zitronen-Kombucha spritzig", "it": "Kombucha limone frizzante", "es": "Kombucha de limón con gas", "nl": "Kombucha citroen sprankelend"}.get(lang, "Sparkling Lemon Kombucha"),
            "brand": "Pure Bubbles",
            "barcode": "3270190201104",
            "icon": "🍹",
            "nutri": "B",
            "nutriColor": "#84cc16",
            "nova": "3",
            "eco": "A",
            "packaging": {"fr": "Bouteille en verre consignée", "de": "Mehrweg-Glasflasche", "it": "Bottiglia di vetro a rendere", "es": "Botella de vidrio retornable", "nl": "Statiegeld glazen fles"}.get(lang, "Returnable Glass Bottle")
        }
    ]

    checklist_items = [
        {"id": 1, "text": {"fr": "Contacter le magasin ou lieu d'accueil pour convenir de la date", "de": "Geschäft oder Veranstaltungsort für Termin anfragen", "it": "Contattare il negozio o luogo per concordare la data", "es": "Contactar con la tienda o espacio para fijar la fecha", "nl": "Winkel of locatie contacteren voor de datum"}.get(lang, "Contact the store or venue to agree on date and time")},
        {"id": 2, "text": {"fr": "Télécharger les affiches Canva et imprimer la signalétique", "de": "Canva-Plakate herunterladen und Beschilderung drucken", "it": "Scaricare le locandine Canva e stampare i cartelli", "es": "Descargar los carteles de Canva e imprimir señalética", "nl": "Canva-posters downloaden en bewegwijzering printen"}.get(lang, "Download Canva flyers and print welcoming signage")},
        {"id": 3, "text": {"fr": "Choisir votre méthode : App Mobile (Wi-Fi) ou Photos Hors-Ligne", "de": "Methode wählen: Mobile App (WLAN) oder Offline-Fotos", "it": "Scegliere il metodo: App Mobile (Wi-Fi) o Foto Offline", "es": "Elegir el método: App Móvil (Wi-Fi) o Fotos sin conexión", "nl": "Kies je methode: Mobiele App (Wi-Fi) of Offline Foto's"}.get(lang, "Select workflow: Live Mobile App or Offline Anchor Photos")},
        {"id": 4, "text": {"fr": "Annoncer l'atelier sur Slack (#scanparty / #scanparty_fr) et vos réseaux", "de": "Workshop auf Slack (#scanparty) und sozialen Medien ankündigen", "it": "Annunciare il laboratorio su Slack (#scanparty) e sui social", "es": "Anunciar el taller en Slack (#scanparty) y redes sociales", "nl": "Kondig de workshop aan op Slack (#scanparty) en sociale media"}.get(lang, "Announce on Slack (#scanparty / #scanparty_fr) and social media")},
        {"id": 5, "text": {"fr": "Former les binômes : un manipulateur de produit, un photographe", "de": "Zweierteams bilden: einer handhabt Produkte, einer fotografiert", "it": "Formare le coppie: uno manipola il prodotto, uno fotografa", "es": "Formar parejas: una persona manipula el producto, la otra fotografía", "nl": "Vorm tweetallen: één pakt producten vast, één fotografeert"}.get(lang, "Pair participants: one handles products, one scans/photographs")},
        {"id": 6, "text": {"fr": "Après l'atelier : téléversement des photos sur pro.openfoodfacts.org et célébration !", "de": "Nach dem Workshop: Fotos auf pro.openfoodfacts.org hochladen und feiern!", "it": "Dopo il laboratorio: caricamento foto su pro.openfoodfacts.org e festeggiamenti!", "es": "Tras el taller: subir fotos a pro.openfoodfacts.org y ¡celebrar!", "nl": "Na de workshop: foto's uploaden naar pro.openfoodfacts.org en vieren!"}.get(lang, "Post-event: bulk upload photos to pro.openfoodfacts.org and celebrate!")}
    ]

    localized_events = []
    for e in events:
        ec = dict(e)
        ec["title"] = get_localized_field(e, "title", lang=lang)
        ec["description"] = get_localized_field(e, "description", lang=lang)
        ec["location"] = get_localized_field(e, "location", lang=lang)
        ec["venue"] = get_localized_field(e, "venue", lang=lang)
        localized_events.append(ec)
    events_json = json.dumps(localized_events, ensure_ascii=False)
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
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-scan-party.yml" 
           target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-primary">
          {t["btn_declare_gh"]}
        </a>
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/scan_parties" 
           target="_blank" rel="noopener noreferrer" class="sp-btn sp-btn-secondary" style="border-color: #16a34a; color: #16a34a;">
          {t["btn_declare_pr"]}
        </a>
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
            ${{e.type === 'upcoming' ? '{t["js_upcoming"]}' : '{t["js_past"]}'}}
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
            {t["js_read_more"]}
          </a>
        ` : `
          <span style="font-size: 0.78rem; color: #94a3b8;">{t["js_community_event"]}</span>
        `}}
        ${{e.products_scanned ? `<span style="font-size: 0.78rem; font-weight: 700; color: #16a34a;">✨ ` + e.products_scanned + ` {t["js_products_word"]}</span>` : ''}}
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
    en_html = ""
    for target_lang in SUPPORTED_LANGUAGES:
        lang_html = generate_html(items, lang=target_lang)
        if target_lang == "en":
            en_html = lang_html
        lang_path = os.path.join(REPO_ROOT, "lang", target_lang, "texts", "scan-parties.html")
        os.makedirs(os.path.dirname(lang_path), exist_ok=True)
        try:
            with open(lang_path, "w", encoding="utf-8") as f:
                f.write(lang_html)
            if verbose:
                print(f"Wrote {lang_path}")
        except (PermissionError, OSError) as e:
            if verbose:
                print(f"  [WARN] Could not write {lang_path}: {e}")

    # 3. Generate standalone root page
    root_path = os.path.join(REPO_ROOT, "scan-parties.html")
    root_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Open Food Facts — Scan Parties & Community Workshops</title>
  <meta name="description" content="Organize and join Open Food Facts Scan Parties: collaborative community workshops to scan barcodes, capture ingredients, nutrition facts, and packaging specs.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
      color: #0f172a;
    }}
    .standalone-nav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.75rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .standalone-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #341100;
      font-weight: 800;
      font-size: 1.1rem;
    }}
    .standalone-brand img {{
      height: 32px;
      width: auto;
    }}
    .standalone-links {{
      display: flex;
      align-items: center;
      gap: 1rem;
      font-size: 0.9rem;
    }}
    .standalone-links a {{
      color: #473526;
      text-decoration: none;
      font-weight: 600;
    }}
    .standalone-links a:hover {{
      color: #ed8857;
    }}
  </style>
</head>
<body>
  <nav class="standalone-nav">
    <a href="https://world.openfoodfacts.org" class="standalone-brand">
      <img src="https://static.openfoodfacts.org/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts Logo">
      <span>Scan Parties</span>
    </a>
    <div class="standalone-links">
      <a href="operation-sodas.html">Opération Sodas</a>
      <a href="whats-in-my-yogurt.html">What's in my yogurt?</a>
      <a href="whats-in-my-shampoo.html">What's in my shampoo?</a>
      <a href="https://world.openfoodfacts.org/contribute">Contribute</a>
      <a href="https://slack.openfoodfacts.org" target="_blank" rel="noopener">Slack</a>
    </div>
  </nav>
  {en_html}
</body>
</html>"""
    try:
        with open(root_path, "w", encoding="utf-8") as f:
            f.write(root_html)
        if verbose:
            print(f"Wrote {root_path}")
    except (PermissionError, OSError) as e:
        if verbose:
            print(f"  [WARN] Could not write {root_path}: {e}")

    return True

def main():
    check_mode = "--check" in sys.argv
    success = compile_scan_parties(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
