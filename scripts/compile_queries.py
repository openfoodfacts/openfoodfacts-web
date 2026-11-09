#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Useful Queries.
Reads individual YAML files from data/queries/*.yaml,
validates schemas, compiles data/queries.json, and generates modernized
interactive tutorial and showcase HTML pages in:
- lang/en/texts/graphs-in-3-clicks.html
- lang/fr/texts/graphs-in-3-clicks.html

Usage:
    python3 scripts/compile_queries.py          # Validate and compile
    python3 scripts/compile_queries.py --check  # Validate only (CI friendly)
"""

import os
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

import glob
import html
import json
import re
import yaml

REPO_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
QUERIES_DIR = os.path.join(DATA_DIR, "queries")
COMPILED_JSON = os.path.join(DATA_DIR, "queries.json")

VALID_TOPICS = {
    "beverages": {
        "en": "Beverages", "fr": "Boissons", "es": "Bebidas", "de": "Getränke", "it": "Bevande",
        "nl": "Dranken", "pt": "Bebidas", "pl": "Napoje", "ru": "Напитки", "ca": "Begudes",
        "ro": "Băuturi", "cs": "Nápoje", "sv": "Drycker", "da": "Drikkevarer", "fi": "Juomat",
        "el": "Ποτά", "hu": "Italok", "ja": "飲料", "zh": "饮料", "ar": "مشروبات",
        "uk": "Напої", "tr": "İçecekler", "id": "Minuman", "ko": "음료", "no": "Drikker", "he": "משקאות",
        "icon": "🥤"
    },
    "dairy": {
        "en": "Dairy & Cheeses", "fr": "Produits laitiers & Fromages", "es": "Lácteos y quesos", "de": "Milchprodukte & Käse", "it": "Latticini e formaggi",
        "nl": "Zuivel & Kazen", "pt": "Lacticínios e queijos", "pl": "Nabiał i sery", "ru": "Молочные продукты и сыры", "ca": "Lactis i formatges",
        "ro": "Lactate și brânzeturi", "cs": "Mléčné výrobky a sýry", "sv": "Mejeri & Ostar", "da": "Mejeri & Oste", "fi": "Maitotuotteet & Juustot",
        "el": "Γαλακτοκομικά & Τυριά", "hu": "Tejtermékek és sajtok", "ja": "乳製品・チーズ", "zh": "乳制品与奶酪", "ar": "منتجات الألبان والأجبان",
        "uk": "Молочні продукти та сири", "tr": "Süt Ürünleri ve Peynirler", "id": "Produk Susu & Keju", "ko": "유제품 및 치즈", "no": "Meieriprodukter & Oster", "he": "מוצרי חלב וגבינות",
        "icon": "🧀"
    },
    "breakfast": {
        "en": "Breakfast & Cereals", "fr": "Petit-déjeuner & Céréales", "es": "Desayuno y cereales", "de": "Frühstück & Zerealien", "it": "Colazione e cereali",
        "nl": "Ontbijt & Granen", "pt": "Pequeno-almoço e cereais", "pl": "Śniadanie i płatki", "ru": "Завтраки и хлопья", "ca": "Esmorzar i cereals",
        "ro": "Mic dejun și cereale", "cs": "Snídaně a cereálie", "sv": "Frukost & Flingor", "da": "Morgenmad & Kornprodukter", "fi": "Aamiainen & Murot",
        "el": "Πρωινό & Δημητριακά", "hu": "Reggeli és gabonafélék", "ja": "朝食・シリアル", "zh": "早餐与谷物", "ar": "إفطار وحبوب",
        "uk": "Сніданки та пластівці", "tr": "Kahvaltı ve Tahıllar", "id": "Sarapan & Sereal", "ko": "아침 식사 및 시리얼", "no": "Frokost & Frokostblandinger", "he": "ארוחת בוקר ודגנים",
        "icon": "🥣"
    },
    "sweets": {
        "en": "Sweets & Spreads", "fr": "Douceurs & Pâtes à tartiner", "es": "Dulces y untables", "de": "Süßigkeiten & Aufstriche", "it": "Dolci e creme spalmabili",
        "nl": "Zoetwaren & Broodbeleg", "pt": "Doces e pastas de barrar", "pl": "Słodycze i smarowidła", "ru": "Сладости и пасты", "ca": "Dolços i cremes per untar",
        "ro": "Dulciuri și creme tartinabile", "cs": "Sladkosti a pomazánky", "sv": "Sötsaker & Pålägg", "da": "Søde sager & Smørepålæg", "fi": "Makeiset & Levitteet",
        "el": "Γλυκά & Αλείμματα", "hu": "Édességek és kenhető krémek", "ja": "スイーツ・スプレッド", "zh": "甜食与抹酱", "ar": "حلويات ومواد للدهن",
        "uk": "Солодощі та пасти", "tr": "Tatlılar ve Sürülebilir Ürünler", "id": "Manisan & Selai", "ko": "과자 및 스프레드", "no": "Søtsaker & Pålegg", "he": "מתוקים וממרחים",
        "icon": "🍫"
    },
    "meat": {
        "en": "Meat & Charcuterie", "fr": "Viandes & Charcuterie", "es": "Carnes y embutidos", "de": "Fleisch & Wurstwaren", "it": "Carne e salumi",
        "nl": "Vlees & Vleeswaren", "pt": "Carnes e charcutaria", "pl": "Mięso i wędliny", "ru": "Мясо и мясные изделия", "ca": "Carn i xarcuteria",
        "ro": "Carne și mezeluri", "cs": "Maso a uzeniny", "sv": "Kött & Charkuterier", "da": "Kød & Pålæg", "fi": "Liha & Leikkeleet",
        "el": "Κρέας & Αλλαντικά", "hu": "Húsok és felvágottak", "ja": "肉類・加工肉", "zh": "肉类与冷盘", "ar": "لحوم ومصنعاتها",
        "uk": "М'ясо та ковбасні вироби", "tr": "Et ve Şarküteri", "id": "Daging & Olahan Daging", "ko": "육류 및 가공육", "no": "Kjøtt & Kjøttpålegg", "he": "בשר ונקניקים",
        "icon": "🥩"
    },
    "meals": {
        "en": "Ready Meals & Prepared", "fr": "Plats préparés", "es": "Platos preparados", "de": "Fertiggerichte", "it": "Piatti pronti",
        "nl": "Kant-en-klaarmaaltijden", "pt": "Refeições prontas", "pl": "Dania gotowe", "ru": "Готовые блюда", "ca": "Plats preparats",
        "ro": "Mâncăruri preparate", "cs": "Hotová jídla", "sv": "Färdigrätter", "da": "Færdigretter", "fi": "Valmisateriat",
        "el": "Έτοιμα γεύματα", "hu": "Készételek", "ja": "調理済み食品・レトルト", "zh": "方便食品与快餐", "ar": "وجبات جاهزة",
        "uk": "Готові страви", "tr": "Hazır Yemekler", "id": "Makanan Siap Saji", "ko": "간편식 및 밀키트", "no": "Ferdigmåltider", "he": "ארוחות מוכנות",
        "icon": "🍲"
    },
    "nutrition": {
        "en": "Nutrition & Scores", "fr": "Nutrition & Scores", "es": "Nutrición y puntuaciones", "de": "Ernährung & Scores", "it": "Nutrizione e punteggi",
        "nl": "Voeding & Scores", "pt": "Nutrição e pontuações", "pl": "Odżywianie i wskaźniki", "ru": "Питание и оценки", "ca": "Nutrició i puntuacions",
        "ro": "Nutriție și scoruri", "cs": "Výživa a skóre", "sv": "Näring & Poäng", "da": "Ernæring & Scores", "fi": "Ravitsemus & Pisteet",
        "el": "Διατροφή & Βαθμολογίες", "hu": "Táplálkozás és pontszámok", "ja": "栄養・スコア", "zh": "营养与评分", "ar": "التغذية والدرجات",
        "uk": "Харчування та оцінки", "tr": "Beslenme ve Skorlar", "id": "Nutrisi & Skor", "ko": "영양 및 점수", "no": "Ernæring & Skårer", "he": "תזונה ודירוגים",
        "icon": "🥗"
    },
    "quality": {
        "en": "Data Quality & Contributor Tools", "fr": "Qualité des données & Outils", "es": "Calidad de datos y herramientas", "de": "Datenqualität & Mitmach-Tools", "it": "Qualità dei dati e strumenti",
        "nl": "Gegevenskwaliteit & Tools", "pt": "Qualidade dos dados e ferramentas", "pl": "Jakość danych i narzędzia", "ru": "Качество данных и инструменты", "ca": "Qualitat de les dades i eines",
        "ro": "Calitatea datelor și instrumente", "cs": "Kvalita dat a nástroje", "sv": "Datakvalitet & Verktyg", "da": "Datakvalitet & Værktøjer", "fi": "Datan laatu & Työkalut",
        "el": "Ποιότητα δεδομένων & Εργαλεία", "hu": "Adatminőség és eszközök", "ja": "データ品質・ツール", "zh": "数据质量与贡献工具", "ar": "جودة البيانات والأدوات",
        "uk": "Якість даних та інструменти", "tr": "Veri Kalitesi ve Araçlar", "id": "Kualitas Data & Alat Kontributor", "ko": "데이터 품질 및 기여 도구", "no": "Datakvalitet & Verktøy", "he": "איכות נתונים וכלים",
        "icon": "🛠️"
    },
}

VALID_QUERY_TYPES = {
    "scatter_plot": {
        "en": "Scatter Plot", "fr": "Nuage de points", "es": "Diagrama de dispersión", "de": "Streudiagramm", "it": "Grafico a dispersione",
        "nl": "Spreidingsdiagram", "pt": "Gráfico de dispersão", "pl": "Wykres punktowy", "ru": "Диаграмма рассеяния", "ca": "Gràfic de dispersió",
        "ro": "Grafic de dispersie", "cs": "Bodový graf", "sv": "Spridningsdiagram", "da": "Spredningsdiagram", "fi": "Pistekaavio",
        "el": "Διάγραμμα διασποράς", "hu": "Pontdiagram", "ja": "散布図", "zh": "散点图", "ar": "مخطط مبعثر",
        "uk": "Діаграма розсіювання", "tr": "Dağılım Grafiği", "id": "Plot Sebar", "ko": "산점도", "no": "Spredningsplott", "he": "תרשים פיזור",
        "icon": "📈"
    },
    "bar_chart": {
        "en": "Bar Chart", "fr": "Histogramme", "es": "Gráfico de barras", "de": "Balkendiagramm", "it": "Grafico a barre",
        "nl": "Staafdiagram", "pt": "Gráfico de barras", "pl": "Wykres słupkowy", "ru": "Столбчатая диаграмма", "ca": "Gràfic de barres",
        "ro": "Grafic cu bare", "cs": "Sloupcový graf", "sv": "Stapeldiagram", "da": "Søjlediagram", "fi": "Pylväskaavio",
        "el": "Ραβδόγραμμα", "hu": "Oszlopdiagram", "ja": "棒グラフ", "zh": "柱状图", "ar": "مخطط شريطي",
        "uk": "Стовпчаста діаграма", "tr": "Çubuk Grafik", "id": "Grafik Batang", "ko": "막대그래프", "no": "Stolpediagram", "he": "תרשים עמודות",
        "icon": "📊"
    },
    "map": {
        "en": "Origins Map", "fr": "Carte d'origines", "es": "Mapa de orígenes", "de": "Herkunftskarte", "it": "Mappa delle origini",
        "nl": "Herkomstkaart", "pt": "Mapa de origens", "pl": "Mapa pochodzenia", "ru": "Карта происхождения", "ca": "Mapa d'orígens",
        "ro": "Hartă a originilor", "cs": "Mapa původu", "sv": "Ursprungskarta", "da": "Oprindelseskort", "fi": "Alkuperäkartta",
        "el": "Χάρτης προέλευσης", "hu": "Eredettérkép", "ja": "原産地マップ", "zh": "产地地图", "ar": "خريطة الأصول",
        "uk": "Карта походження", "tr": "Menşei Haritası", "id": "Peta Asal Usul", "ko": "원산지 지도", "no": "Opprinnelseskart", "he": "מפת מקורות",
        "icon": "🗺️"
    },
    "list": {
        "en": "Product List", "fr": "Liste de produits", "es": "Lista de productos", "de": "Produktliste", "it": "Elenco prodotti",
        "nl": "Productenlijst", "pt": "Lista de produtos", "pl": "Lista produktów", "ru": "Список продуктов", "ca": "Llista de productes",
        "ro": "Listă de produse", "cs": "Seznam produktů", "sv": "Produktlista", "da": "Produktliste", "fi": "Tuoteluettelo",
        "el": "Λίστα προϊόντων", "hu": "Terméklista", "ja": "商品リスト", "zh": "产品列表", "ar": "قائمة المنتجات",
        "uk": "Список продуктів", "tr": "Ürün Listesi", "id": "Daftar Produk", "ko": "제품 목록", "no": "Produktliste", "he": "רשימת מוצרים",
        "icon": "📋"
    },
    "facet": {
        "en": "Taxonomy Facet", "fr": "Facette taxonomique", "es": "Faceta taxonómica", "de": "Taxonomiefacette", "it": "Faccetta tassonomica",
        "nl": "Taxonomie-facet", "pt": "Faceta taxonómica", "pl": "Aspekt taksonomiczny", "ru": "Фасет таксономии", "ca": "Faceta taxonòmica",
        "ro": "Fațetă taxonomică", "cs": "Taxonomický aspekt", "sv": "Taxonomifasett", "da": "Taksonomifacet", "fi": "Taksonomiafasetti",
        "el": "Ταξινομική όψη", "hu": "Rendszertani vetület", "ja": "分類ファセット", "zh": "分类维度", "ar": "وجه تصنيفي",
        "uk": "Таксономічний фасет", "tr": "Taksonomi Yönü", "id": "Faset Taksonomi", "ko": "분류 패싯", "no": "Taksonomifasett", "he": "היבט טקסונומי",
        "icon": "🔍"
    },
}

GEO_NAMES = {
    "world": {
        "en": "Worldwide", "fr": "Monde", "es": "Mundial", "de": "Weltweit", "it": "Mondo",
        "nl": "Wereldwijd", "pt": "Mundial", "pl": "Świat", "ru": "Весь мир", "ca": "Mundial",
        "ro": "Global", "cs": "Celosvětově", "sv": "Globalt", "da": "Globalt", "fi": "Maailmanlaajuinen",
        "el": "Παγκοσμίως", "hu": "Világszerte", "ja": "世界", "zh": "全球", "ar": "عالمي",
        "uk": "Весь світ", "tr": "Dünya Çapında", "id": "Seluruh Dunia", "ko": "전 세계", "no": "Verden", "he": "כלל עולמי",
        "flag": "🌍"
    },
    "fr": {"en": "France", "fr": "France", "es": "Francia", "de": "Frankreich", "it": "Francia", "nl": "Frankrijk", "pt": "França", "pl": "Francja", "ru": "Франция", "flag": "🇫🇷"},
    "uk": {"en": "United Kingdom", "fr": "Royaume-Uni", "es": "Reino Unido", "de": "Vereinigtes Königreich", "it": "Regno Unito", "nl": "Verenigd Koninkrijk", "pt": "Reino Unido", "pl": "Wielka Brytania", "ru": "Великобритания", "flag": "🇬🇧"},
    "be": {"en": "Belgium", "fr": "Belgique", "es": "Bélgica", "de": "Belgien", "it": "Belgio", "nl": "België", "pt": "Bélgica", "pl": "Belgia", "ru": "Бельгия", "flag": "🇧🇪"},
    "de": {"en": "Germany", "fr": "Allemagne", "es": "Alemania", "de": "Deutschland", "it": "Germania", "nl": "Duitsland", "pt": "Alemanha", "pl": "Niemcy", "ru": "Германия", "flag": "🇩🇪"},
    "es": {"en": "Spain", "fr": "Espagne", "es": "España", "de": "Spanien", "it": "Spagna", "nl": "Spanje", "pt": "Espanha", "pl": "Hiszpania", "ru": "Испания", "flag": "🇪🇸"},
    "us": {"en": "United States", "fr": "États-Unis", "es": "Estados Unidos", "de": "Vereinigte Staaten", "it": "Stati Uniti", "nl": "Verenigde Staten", "pt": "Estados Unidos", "pl": "Stany Zjednoczone", "ru": "США", "flag": "🇺🇸"},
}

def validate_query(item, filepath):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    stem = filename[:-5] if filename.endswith(".yaml") else filename[:-4]

    # Required: id
    q_id = item.get("id")
    if not q_id:
        errors.append(f"{filename}: missing required field 'id'")
    elif q_id != stem:
        errors.append(f"{filename}: id '{q_id}' does not match filename stem '{stem}'")
    elif not re.match(r"^[a-zA-Z0-9_-]+$", str(q_id)):
        errors.append(f"{filename}: id '{q_id}' contains invalid characters (must be alphanumeric, hyphens, or underscores)")

    # Required: title (supports string, multilingual dict, or suffixed keys)
    errors.extend(validate_localized_field(item, "title", filename, required=True))

    # Required: description (supports string, multilingual dict, or suffixed keys)
    errors.extend(validate_localized_field(item, "description", filename, required=True))

    # Required: topic
    topic = item.get("topic")
    if not topic:
        errors.append(f"{filename}: missing required field 'topic'")
    elif topic not in VALID_TOPICS:
        errors.append(f"{filename}: invalid topic '{topic}', must be one of {sorted(list(VALID_TOPICS.keys()))}")

    # Required: query_type
    q_type = item.get("query_type")
    if not q_type:
        errors.append(f"{filename}: missing required field 'query_type'")
    elif q_type not in VALID_QUERY_TYPES:
        errors.append(f"{filename}: invalid query_type '{q_type}', must be one of {sorted(list(VALID_QUERY_TYPES.keys()))}")

    # Required: geographies
    geos = item.get("geographies")
    if not geos or not isinstance(geos, list):
        errors.append(f"{filename}: 'geographies' must be a non-empty list of country codes (e.g. ['world', 'fr'])")

    # Required: url
    url = item.get("url")
    if not url or not str(url).strip():
        errors.append(f"{filename}: missing required field 'url'")
    elif not (url.startswith("http://") or url.startswith("https://") or url.startswith("/")):
        errors.append(f"{filename}: url must start with http://, https://, or /")

    # Optional: tags_combined
    tags_combined = item.get("tags_combined")
    if tags_combined is not None and not isinstance(tags_combined, list):
        errors.append(f"{filename}: 'tags_combined' must be a list of strings")

    # Optional: featured
    featured = item.get("featured")
    if featured is not None and not isinstance(featured, bool):
        errors.append(f"{filename}: 'featured' must be a boolean (true/false)")

    return errors, warnings

def load_queries(directory=QUERIES_DIR, validate=True):
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
            errs, warns = validate_query(data, fpath)
            all_errors.extend(errs)
            all_warnings.extend(warns)

        items.append(data)

    # Sort: featured first, then case-insensitive by title
    items.sort(key=lambda x: (not x.get("featured", False), get_localized_field(x, "title", "en").lower()))

    return items, all_errors, all_warnings

def generate_css():
    return """
<style>
/* ==========================================================================
   Open Food Facts: Graphs in 3 Clicks & Useful Queries Modern Showcase
   ========================================================================== */

:root {
  --off-green-900: #064e3b;
  --off-green-800: #065f46;
  --off-green-700: #047857;
  --off-green-600: #059669;
  --off-green-500: #10b981;
  --off-green-100: #d1fae5;
  --off-green-50: #ecfdf5;
  --off-surface: #ffffff;
  --off-bg: #f8fafc;
  --off-border: #e2e8f0;
  --off-border-hover: #cbd5e1;
  --off-text-primary: #0f172a;
  --off-text-secondary: #475569;
  --off-text-muted: #64748b;
  --off-accent: #2563eb;
  --off-accent-bg: #eff6ff;
  --off-warn-bg: #fffbeb;
  --off-warn-border: #fde68a;
  --off-warn-text: #92400e;
  --off-shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --off-shadow-md: 0 4px 14px rgba(0,0,0,0.06);
  --off-shadow-hover: 0 10px 25px rgba(4, 120, 87, 0.10);
  --off-radius-card: 16px;
  --off-radius-pill: 9999px;
  --off-radius-sm: 8px;
}

.g3c-container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
  color: var(--off-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  line-height: 1.6;
}

/* Hero Section */
.g3c-hero {
  text-align: center;
  padding: 2.5rem 1.5rem 2rem;
  background: linear-gradient(135deg, var(--off-green-50) 0%, #ffffff 100%);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  margin-bottom: 2.5rem;
  box-shadow: var(--off-shadow-sm);
}

.g3c-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--off-green-100);
  color: var(--off-green-900);
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.35rem 0.85rem;
  border-radius: var(--off-radius-pill);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.g3c-hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.75rem;
  line-height: 1.2;
  letter-spacing: -0.025em;
}

.g3c-hero-subtitle {
  font-size: 1.2rem;
  color: var(--off-text-secondary);
  max-width: 760px;
  margin: 0 auto 1.5rem;
}

.g3c-quote-card {
  display: inline-block;
  background: var(--off-surface);
  border-left: 4px solid var(--off-green-600);
  padding: 0.75rem 1.25rem;
  border-radius: 0 var(--off-radius-sm) var(--off-radius-sm) 0;
  font-style: italic;
  color: var(--off-green-800);
  font-weight: 500;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 1.75rem;
}

.g3c-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  align-items: center;
}

.g3c-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1.35rem;
  border-radius: var(--off-radius-pill);
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.g3c-btn-primary {
  background: var(--off-green-700);
  color: #ffffff !important;
  box-shadow: 0 2px 6px rgba(4, 120, 87, 0.25);
}
.g3c-btn-primary:hover {
  background: var(--off-green-800);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(4, 120, 87, 0.35);
}

.g3c-btn-secondary {
  background: var(--off-surface);
  color: var(--off-green-800) !important;
  border-color: var(--off-border);
}
.g3c-btn-secondary:hover {
  border-color: var(--off-green-600);
  background: var(--off-green-50);
}

/* 3 Clicks Visual Workflow */
.g3c-workflow {
  margin-bottom: 3.5rem;
}

.g3c-section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.g3c-section-title {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.5rem;
}

.g3c-section-subtitle {
  color: var(--off-text-secondary);
  font-size: 1.05rem;
  max-width: 680px;
  margin: 0 auto;
}

.g3c-steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.g3c-step-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.75rem 1.5rem;
  box-shadow: var(--off-shadow-sm);
  transition: all 0.25s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.g3c-step-card:hover {
  border-color: var(--off-green-600);
  box-shadow: var(--off-shadow-hover);
  transform: translateY(-2px);
}

.g3c-step-number {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  font-size: 2.2rem;
  font-weight: 900;
  color: var(--off-green-100);
  line-height: 1;
}

.g3c-step-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.g3c-step-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.65rem;
}

.g3c-step-desc {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  margin: 0 0 1rem;
  flex-grow: 1;
}

.g3c-step-features {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.88rem;
  color: var(--off-text-muted);
}

.g3c-step-features li {
  margin-bottom: 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* Callout Box */
.g3c-callout {
  background: var(--off-warn-bg);
  border: 1px solid var(--off-warn-border);
  border-radius: var(--off-radius-card);
  padding: 1.25rem 1.5rem;
  margin-bottom: 2.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.g3c-callout-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.g3c-callout-body h4 {
  margin: 0 0 0.35rem;
  color: var(--off-warn-text);
  font-size: 1.05rem;
}

.g3c-callout-body p {
  margin: 0;
  color: #78350f;
  font-size: 0.92rem;
  line-height: 1.5;
}

/* Showcase & Filters Section */
.g3c-showcase-section {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 2rem 1.5rem;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 3rem;
}

.g3c-controls-wrap {
  background: var(--off-bg);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.g3c-search-bar {
  position: relative;
  margin-bottom: 1.25rem;
}

.g3c-search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.85rem 1rem 0.85rem 2.75rem;
  font-size: 1rem;
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-pill);
  background: var(--off-surface);
  color: var(--off-text-primary);
  outline: none;
  transition: all 0.2s ease;
}

.g3c-search-input:focus {
  border-color: var(--off-green-600);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.g3c-search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--off-text-muted);
  font-size: 1.1rem;
  pointer-events: none;
}

/* Filter Groups */
.g3c-filter-group {
  margin-bottom: 1rem;
}

.g3c-filter-group:last-child {
  margin-bottom: 0;
}

.g3c-filter-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--off-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}

.g3c-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.g3c-pill-btn {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-pill);
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  color: var(--off-text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  user-select: none;
}

.g3c-pill-btn:hover {
  border-color: var(--off-green-600);
  color: var(--off-green-900);
}

.g3c-pill-btn.active {
  background: var(--off-green-700);
  border-color: var(--off-green-700);
  color: #ffffff;
  font-weight: 600;
}

/* Secondary Filters Row */
.g3c-secondary-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--off-border);
  align-items: center;
  justify-content: space-between;
}

.g3c-select-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.g3c-select {
  padding: 0.45rem 0.85rem;
  border-radius: var(--off-radius-sm);
  border: 1px solid var(--off-border);
  background: var(--off-surface);
  font-size: 0.88rem;
  color: var(--off-text-primary);
  outline: none;
}

.g3c-select:focus {
  border-color: var(--off-green-600);
}

.g3c-stats-and-reset {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
}

.g3c-count-badge {
  background: var(--off-green-100);
  color: var(--off-green-900);
  padding: 0.25rem 0.65rem;
  border-radius: var(--off-radius-pill);
  font-weight: 700;
}

.g3c-reset-btn {
  background: none;
  border: none;
  color: var(--off-text-muted);
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.2rem 0.4rem;
}
.g3c-reset-btn:hover {
  color: var(--off-green-900);
}

/* Cards Grid */
.g3c-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.g3c-query-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.25rem;
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  position: relative;
}

.g3c-query-card:hover {
  border-color: var(--off-green-600);
  box-shadow: var(--off-shadow-hover);
  transform: translateY(-2px);
}

.g3c-query-card.featured {
  border-left: 4px solid var(--off-green-600);
}

.g3c-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.6rem;
  gap: 0.5rem;
}

.g3c-card-tags-top {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.g3c-type-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: var(--off-radius-pill);
  background: #f1f5f9;
  color: var(--off-text-secondary);
}

.g3c-type-badge.scatter_plot { background: #eff6ff; color: #1d4ed8; }
.g3c-type-badge.bar_chart { background: #fdf2f8; color: #be185d; }
.g3c-type-badge.map { background: #ecfdf5; color: #047857; }
.g3c-type-badge.list { background: #fefce8; color: #a16207; }
.g3c-type-badge.facet { background: #faf5ff; color: #7e22ce; }

.g3c-geo-badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--off-radius-pill);
  background: #f8fafc;
  border: 1px solid var(--off-border);
  color: var(--off-text-secondary);
}

.g3c-featured-star {
  color: #f59e0b;
  font-size: 0.9rem;
  cursor: help;
}

.g3c-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.45rem;
  line-height: 1.35;
}

.g3c-card-desc {
  font-size: 0.9rem;
  color: var(--off-text-secondary);
  line-height: 1.45;
  margin: 0 0 0.85rem;
  flex-grow: 1;
}

.g3c-author-line {
  font-size: 0.78rem;
  color: var(--off-text-muted);
  margin-bottom: 0.75rem;
  font-style: italic;
}

/* Combined Tags Chips */
.g3c-chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.g3c-chip {
  font-size: 0.74rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  padding: 0.15rem 0.5rem;
  border-radius: var(--off-radius-sm);
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.g3c-chip.category { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.g3c-chip.axis { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.g3c-chip.label { background: #fef3c7; border-color: #fde68a; color: #92400e; }
.g3c-chip.ingredient { background: #faf5ff; border-color: #e9d5ff; color: #6b21a8; }
.g3c-chip.state { background: #f8fafc; border-color: #e2e8f0; color: #475569; }

/* Card Actions */
.g3c-card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--off-border);
}

.g3c-run-btn {
  flex-grow: 1;
  text-align: center;
  padding: 0.5rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--off-radius-sm);
  background: var(--off-green-700);
  color: #ffffff !important;
  text-decoration: none;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.g3c-run-btn:hover {
  background: var(--off-green-800);
}

.g3c-copy-btn {
  padding: 0.5rem 0.65rem;
  font-size: 0.85rem;
  border: 1px solid var(--off-border);
  background: var(--off-surface);
  border-radius: var(--off-radius-sm);
  cursor: pointer;
  color: var(--off-text-secondary);
  transition: all 0.15s ease;
}

.g3c-copy-btn:hover {
  border-color: var(--off-green-600);
  color: var(--off-green-900);
  background: var(--off-green-50);
}

/* Expandable Params */
.g3c-params-details {
  margin-top: 0.5rem;
  font-size: 0.78rem;
  color: var(--off-text-muted);
}

.g3c-params-details summary {
  cursor: pointer;
  user-select: none;
  color: var(--off-text-secondary);
  padding: 0.2rem 0;
}

.g3c-params-details summary:hover {
  color: var(--off-green-700);
}

.g3c-params-pre {
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: var(--off-radius-sm);
  border: 1px solid var(--off-border);
  overflow-x: auto;
  margin: 0.35rem 0 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

/* Spotlight Example */
.g3c-spotlight-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.75rem;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 2.5rem;
}
.g3c-spotlight-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
  align-items: center;
}
.g3c-spotlight-img {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  border: 1px solid var(--off-border);
  box-shadow: var(--off-shadow-sm);
  display: block;
}
.g3c-spotlight-content h3 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.5rem;
}
.g3c-spotlight-content p {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 1rem;
}

/* Formats Grid */
.g3c-formats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}
.g3c-format-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.35rem;
  box-shadow: var(--off-shadow-sm);
}
.g3c-format-card h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.g3c-format-card p {
  font-size: 0.9rem;
  color: var(--off-text-secondary);
  margin: 0;
  line-height: 1.45;
}

@media (max-width: 768px) {
  .g3c-spotlight-grid {
    grid-template-columns: 1fr;
  }
}

/* Empty State */
.g3c-no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem 1.5rem;
  color: var(--off-text-muted);
}
.g3c-no-results-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

/* Contribute Banner */
.g3c-contribute-box {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border: 1px solid var(--off-green-100);
  border-radius: var(--off-radius-card);
  padding: 1.75rem;
  text-align: center;
  margin-top: 2.5rem;
}
.g3c-contribute-title {
  color: var(--off-green-900);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}
.g3c-contribute-desc {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  max-width: 650px;
  margin: 0 auto 1.25rem;
}

/* Toast Notification */
.g3c-toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  background: var(--off-green-900);
  color: #ffffff;
  padding: 0.75rem 1.25rem;
  border-radius: var(--off-radius-pill);
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  opacity: 0;
  pointer-events: none;
  transform: translateY(12px);
  transition: all 0.25s ease;
  z-index: 9999;
}
.g3c-toast.show {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 768px) {
  .g3c-hero-title { font-size: 1.85rem; }
  .g3c-hero-subtitle { font-size: 1rem; }
  .g3c-cards-grid { grid-template-columns: 1fr; }
  .g3c-secondary-filters { flex-direction: column; align-items: stretch; }
}
</style>
"""

UI_STRINGS = {
    "en": {
        "page_title": "Advanced Search & Visualizations: Graphs in 3 Clicks",
        "hero_badge": "Open Data Visualizations",
        "hero_subtitle": "Explore millions of open food products with interactive scatter plots, origin maps, comparison bar charts, and custom data exports in seconds.",
        "hero_quote": "If a picture is worth 1,000 words, it is also worth 1,000 digits!",
        "btn_search": "🚀 Launch Advanced Search",
        "btn_showcase": "✨ Explore Useful Queries",
        "btn_propose_query": "🚀 Propose a Query",
        "btn_skip": "Skip Tutorial",
        "workflow_title": "How to Create a Graph in 3 Clicks",
        "workflow_sub": "The Open Food Facts advanced search engine lets you filter and correlate any segment of the global food database.",
        "step1_title": "1. Scope & Filter Products",
        "step1_desc": "Combine up to 5 simultaneous criteria: category (e.g. cereals, cheeses), country of sale, brand, labels (Organic, Fair Trade), or Nutri-Score grades.",
        "step1_f1": "Categories, brands, ingredients",
        "step1_f2": "Country of sale & quality labels",
        "step1_f3": "Multi-criteria Boolean filtering",
        "step2_title": "2. Select Axes & Visualization",
        "step2_desc": "Choose your X and Y axes (sugars vs additives, calories vs fats, sodium vs Nutri-Score). Enable visual markers for organic products or sweeteners.",
        "step2_f1": "2-Axis Scatter plots",
        "step2_f2": "Distribution bar charts",
        "step2_f3": "Geospatial maps & CSV exports",
        "step3_title": "3. Inspect, Verify & Share",
        "step3_desc": "Hover over data points to preview product sheets. Spot nutritional outliers, audit input errors, and share your persistent graph URL with the world.",
        "step3_f1": "Dynamic interactive data points",
        "step3_f2": "Visual outlier identification",
        "step3_f3": "Permanent URL for papers & sharing",
        "spotlight_badge": "Iconic Case Study",
        "spotlight_title": "Sugars & Additives in Sodas (The Sodas Operation)",
        "spotlight_desc": "This iconic scatter plot correlates sugar content (X axis) with food additives count (Y axis) across sodas collected by the community. Green dots highlight certified organic sodas, while specific markers identify formulations containing intense artificial sweeteners.",
        "spotlight_btn": "Explore this Live Graph ↗",
        "format1_title": "2-Axis Scatter Plots",
        "format1_desc": "Correlate any two nutrients or metrics with interactive hover tooltips.",
        "format2_title": "Geospatial & Origins Maps",
        "format2_desc": "Map manufacturing sites and ingredient provenance (Protected Origins, Fair Trade).",
        "format3_title": "Custom Lists & Data Exports",
        "format3_desc": "Download filtered datasets as CSV or Excel for in-depth data analysis (R, Python, LibreOffice).",
        "callout_title": "Community Data Validation Tip",
        "callout_desc": "Before publishing or referencing a graph in an article or study, double-check products at extreme outlier points. Input errors can occur: if a value seems unusually high or low, check the original packaging photo on Open Food Facts and edit it directly!",
        "showcase_title": "Curated Useful Queries & Community Graphs Showcase",
        "showcase_sub": "Explore curated searches and visualizations crafted by the Open Food Facts community: nutritional analyses, civic investigations, and contributor workflows.",
        "search_placeholder": "🔍 Search by keyword, food, nutrient, contributor (e.g. sodas, Tacite, salt, bio...)",
        "label_topics": "Topics:",
        "all_topics": "All Topics",
        "label_type": "Visualization Type:",
        "all_types": "All Types",
        "label_geo": "Geography:",
        "all_geos": "All Geographies",
        "label_sort": "Sort by:",
        "sort_featured": "Featured & Curated",
        "sort_title": "Title (A-Z)",
        "sort_topic": "Topic",
        "results_count": "queries shown",
        "reset": "Reset Filters",
        "no_results": "No curated queries match your selected filters.",
        "contrib_title": "💡 Created an Insightful Query or Graph?",
        "contrib_desc": "Add your search or chart to this open library! Simply submit our 1-click form to automatically generate a Pull Request.",
        "btn_propose": "🚀 Propose a Query",
        "btn_browse_yaml": "📁 Browse YAML Files",
        "btn_run_text": "Open Query",
        "btn_copy_title": "Copy link",
        "btn_edit_title": "Edit this query",
        "params_summary_text": "🔍 Inspect parameters",
        "copied_text": "Search link copied to clipboard!"
    },
    "fr": {
        "page_title": "Recherche avancée et Graphiques en 3 clics",
        "hero_badge": "Visualisation de Données Ouvertes",
        "hero_subtitle": "Explorez la base mondiale d'Open Food Facts sous forme de nuages de points interactifs, cartes d'origines, histogrammes comparatifs et exports sur-mesure.",
        "hero_quote": "Si une image vaut 1000 mots, elle vaut aussi 1000 chiffres !",
        "btn_search": "🚀 Lancer la Recherche Avancée",
        "btn_showcase": "✨ Découvrir les Requêtes Utiles",
        "btn_propose_query": "🚀 Proposer une Requête",
        "btn_skip": "Passer le tutoriel",
        "workflow_title": "Comment créer un graphique en 3 clics",
        "workflow_sub": "Le moteur de recherche avancée d'Open Food Facts vous permet d'analyser n'importe quel segment du marché alimentaire.",
        "step1_title": "1. Définir filtres et périmètre",
        "step1_desc": "Choisissez jusqu'à 5 critères simultanés : catégorie (ex: céréales, fromages), pays de vente, marque, labels (Bio, Commerce équitable) ou notes Nutri-Score.",
        "step1_f1": "Catégories, marques, ingrédients",
        "step1_f2": "Filtrage par pays et labels qualité",
        "step1_f3": "Critères cumulatifs (ET / OU)",
        "step2_title": "2. Choisir vos axes d'analyse",
        "step2_desc": "Sélectionnez l'axe X et l'axe Y (sucre vs additifs, énergie vs lipides, sodium vs Nutri-Score). Activez des séries visuelles (produits bio, édulcorants).",
        "step2_f1": "Nuages de points (Scatter plots)",
        "step2_f2": "Histogrammes de distribution",
        "step2_f3": "Cartes géographiques & exports CSV",
        "step3_title": "3. Analyser, vérifier et partager",
        "step3_desc": "Survolez les points pour afficher la fiche produit complète. Repérez les anomalies ou valeurs extrêmes, puis partagez l'URL persistante du graphique !",
        "step3_f1": "Graphiques dynamiques et interactifs",
        "step3_f2": "Détection visuelle des valeurs aberrantes",
        "step3_f3": "URL pérenne pour partage et publications",
        "spotlight_badge": "Cas d'étude emblématique",
        "spotlight_title": "Sucres et additifs dans les boissons sucrées (Opération Sodas)",
        "spotlight_desc": "Ce graphique croise la teneur en sucre (axe X) et le nombre d'additifs (axe Y) des sodas collectés par la communauté. Les points verts mettent en valeur les produits certifiés biologiques, tandis que les marqueurs spécifiques signalent les boissons avec édulcorants intenses.",
        "spotlight_btn": "Explorer ce graphique en direct ↗",
        "format1_title": "Nuages de points (Scatter plots)",
        "format1_desc": "Corrélez deux nutriments ou métriques au choix avec infobulles interactives au survol.",
        "format2_title": "Cartes des terroirs & origines",
        "format2_desc": "Visualisez les lieux de fabrication et l'origine des ingrédients (AOP, AOC, bio).",
        "format3_title": "Listes personnalisées & Exports",
        "format3_desc": "Téléchargez les données filtrées en CSV ou Excel pour vos analyses approfondies (R, Python, LibreOffice).",
        "callout_title": "Conseil de validation citoyenne",
        "callout_desc": "Avant de publier ou citer un graphique dans un article ou une étude, vérifiez les produits situés aux points extrêmes. Une coquille de saisie est toujours possible : si une valeur nutritionnelle semble démesurée, vérifiez l'emballage original sur Open Food Facts et corrigez-la en un clic !",
        "showcase_title": "Bibliothèque de Requêtes Utiles & Graphiques Remarquables",
        "showcase_sub": "Découvrez les requêtes et visualisations conçues par la communauté Open Food Facts : analyses nutritionnelles, enquêtes citoyennes et requêtes de contribution.",
        "search_placeholder": "🔍 Rechercher par mot-clé, aliment, nutriment, auteur (ex: sodas, Tacite, sel, bio...)",
        "label_topics": "Thématiques :",
        "all_topics": "Toutes les thématiques",
        "label_type": "Format d'affichage :",
        "all_types": "Tous les formats",
        "label_geo": "Géographie :",
        "all_geos": "Toutes zones",
        "label_sort": "Trier par :",
        "sort_featured": "En vedette & populaires",
        "sort_title": "Titre (A-Z)",
        "sort_topic": "Thématique",
        "results_count": "requêtes affichées",
        "reset": "Réinitialiser les filtres",
        "no_results": "Aucune requête ne correspond à vos critères.",
        "contrib_title": "💡 Vous avez conçu une requête ou un graphique utile ?",
        "contrib_desc": "Ajoutez votre requête à notre bibliothèque ouverte ! Soumettez simplement un formulaire en 1 clic pour générer automatiquement une Pull Request.",
        "btn_propose": "🚀 Proposer une requête",
        "btn_browse_yaml": "📁 Fichiers YAML",
        "btn_run_text": "Ouvrir la requête",
        "btn_copy_title": "Copier le lien",
        "btn_edit_title": "Modifier cette requête",
        "params_summary_text": "🔍 Voir les paramètres",
        "copied_text": "Lien copié dans le presse-papiers !"
    },
    "es": {
        "page_title": "Búsqueda avanzada y Gráficos en 3 clics",
        "hero_badge": "Visualización de Datos Abiertos",
        "hero_subtitle": "Explore millones de alimentos abiertos con diagramas de dispersión interactivos, mapas de orígenes, gráficos comparativos y exportaciones personalizadas.",
        "hero_quote": "Si una imagen vale más que mil palabras, ¡también vale más que mil cifras!",
        "btn_search": "🚀 Iniciar Búsqueda Avanzada",
        "btn_showcase": "✨ Explorar Consultas Útiles",
        "btn_propose_query": "🚀 Proponer una Consulta",
        "btn_skip": "Omitir tutorial",
        "workflow_title": "Cómo crear un gráfico en 3 clics",
        "workflow_sub": "El motor de búsqueda avanzada de Open Food Facts le permite filtrar y correlacionar cualquier segmento de la base de datos alimentaria.",
        "step1_title": "1. Definir filtros y alcance",
        "step1_desc": "Combine hasta 5 criterios simultáneos: categoría, país de venta, marca, sellos de calidad o calificaciones Nutri-Score.",
        "step1_f1": "Categorías, marcas, ingredientes",
        "step1_f2": "Filtrado por país y sellos de calidad",
        "step1_f3": "Criterios booleanos acumulativos",
        "step2_title": "2. Elegir ejes y visualización",
        "step2_desc": "Seleccione los ejes X e Y (azúcar vs aditivos, energía vs grasas). Active marcadores visuales para productos ecológicos o edulcorantes.",
        "step2_f1": "Diagramas de dispersión",
        "step2_f2": "Histogramas de distribución",
        "step2_f3": "Mapas geográficos y exportación CSV",
        "step3_title": "3. Analizar, verificar y compartir",
        "step3_desc": "Pase el cursor sobre los puntos para ver el producto completo. Detecte valores atípicos y comparta el enlace permanente.",
        "step3_f1": "Puntos de datos dinámicos e interactivos",
        "step3_f2": "Identificación visual de valores atípicos",
        "step3_f3": "URL permanente para estudios y difusión",
        "spotlight_badge": "Caso de estudio emblemático",
        "spotlight_title": "Azúcares y aditivos en refrescos (Operación Refrescos)",
        "spotlight_desc": "Este gráfico correlaciona el contenido de azúcar con la cantidad de aditivos en refrescos recopilados por la comunidad.",
        "spotlight_btn": "Explorar este gráfico en directo ↗",
        "format1_title": "Diagramas de dispersión",
        "format1_desc": "Correlacione dos nutrientes o métricas con información interactiva al pasar el cursor.",
        "format2_title": "Mapas de orígenes",
        "format2_desc": "Visualice lugares de fabricación y procedencia de ingredientes (DOP, comercio justo).",
        "format3_title": "Listas personalizadas y exportación",
        "format3_desc": "Descargue datos filtrados en CSV o Excel para análisis avanzados.",
        "callout_title": "Consejo de validación comunitaria",
        "callout_desc": "Antes de citar un gráfico en un artículo, compruebe los productos situados en los extremos para verificar errores tipográficos.",
        "showcase_title": "Biblioteca de Consultas Útiles y Gráficos Destacados",
        "showcase_sub": "Descubra búsquedas y visualizaciones creadas por la comunidad de Open Food Facts.",
        "search_placeholder": "🔍 Buscar por palabra clave, alimento, nutriente o autor...",
        "label_topics": "Temáticas:",
        "all_topics": "Todas las temáticas",
        "label_type": "Tipo de visualización:",
        "all_types": "Todos los formatos",
        "label_geo": "Geografía:",
        "all_geos": "Todas las zonas",
        "label_sort": "Ordenar por:",
        "sort_featured": "Destacadas y populares",
        "sort_title": "Título (A-Z)",
        "sort_topic": "Temática",
        "results_count": "consultas mostradas",
        "reset": "Restablecer filtros",
        "no_results": "Ninguna consulta coincide con sus filtros seleccionados.",
        "contrib_title": "💡 ¿Ha creado una consulta o gráfico útil?",
        "contrib_desc": "¡Añada su búsqueda a nuestra biblioteca abierta mediante un sencillo formulario!",
        "btn_propose": "🚀 Proponer una consulta",
        "btn_browse_yaml": "📁 Archivos YAML",
        "btn_run_text": "Abrir consulta",
        "btn_copy_title": "Copiar enlace",
        "btn_edit_title": "Modificar esta consulta",
        "params_summary_text": "🔍 Ver parámetros",
        "copied_text": "¡Enlace copiado al portapapeles!"
    },
    "de": {
        "page_title": "Erweiterte Suche & Visualisierungen: Diagramme in 3 Klicks",
        "hero_badge": "Open-Data-Visualisierungen",
        "hero_subtitle": "Erkunden Sie Millionen von Lebensmitteln mit interaktiven Streudiagrammen, Herkunftskarten und benutzerdefinierten Datenexporten.",
        "hero_quote": "Wenn ein Bild mehr als 1.000 Worte sagt, sagt es auch mehr als 1.000 Zahlen!",
        "btn_search": "🚀 Erweiterte Suche starten",
        "btn_showcase": "✨ Nützliche Abfragen entdecken",
        "btn_propose_query": "🚀 Abfrage vorschlagen",
        "btn_skip": "Tutorial überspringen",
        "workflow_title": "In 3 Klicks ein Diagramm erstellen",
        "workflow_sub": "Mit der erweiterten Suche von Open Food Facts können Sie jedes Segment der globalen Datenbank analysieren.",
        "step1_title": "1. Filter & Bereich definieren",
        "step1_desc": "Kombinieren Sie bis zu 5 Kriterien: Kategorie, Land, Marke, Bio-Siegel oder Nutri-Score.",
        "step1_f1": "Kategorien, Marken, Zutaten",
        "step1_f2": "Filter nach Land und Gütesiegeln",
        "step1_f3": "Boolesche Mehrfachfilterung",
        "step2_title": "2. Achsen & Visualisierung wählen",
        "step2_desc": "Wählen Sie X- und Y-Achse (Zucker vs. Zusatzstoffe, Kalorien vs. Fett).",
        "step2_f1": "Streudiagramme (Scatter plots)",
        "step2_f2": "Verteilungsbalkendiagramme",
        "step2_f3": "Geografische Karten & CSV-Exporte",
        "step3_title": "3. Prüfen, analysieren & teilen",
        "step3_desc": "Fahren Sie mit der Maus über Punkte, um Produktdetails anzuzeigen und teilen Sie die dauerhafte URL.",
        "step3_f1": "Interaktive Datenpunkte",
        "step3_f2": "Visuelle Ausreißererkennung",
        "step3_f3": "Dauerhafter Link zum Teilen",
        "spotlight_badge": "Klassische Fallstudie",
        "spotlight_title": "Zucker und Zusatzstoffe in Limonaden (Aktion Sodas)",
        "spotlight_desc": "Dieses Diagramm vergleicht den Zuckergehalt mit der Anzahl der Lebensmittelzusatzstoffe in Limonaden.",
        "spotlight_btn": "Live-Diagramm erkunden ↗",
        "format1_title": "Streudiagramme",
        "format1_desc": "Vergleichen Sie zwei Nährwerte oder Kennzahlen mit interaktiven Tooltips.",
        "format2_title": "Herkunftskarten",
        "format2_desc": "Visualisieren Sie Herkunftsorte und Zutatenherkunft.",
        "format3_title": "Individuelle Listen & Exporte",
        "format3_desc": "Laden Sie gefilterte Daten als CSV oder Excel für eigene Analysen herunter.",
        "callout_title": "Tipp zur Datenüberprüfung",
        "callout_desc": "Überprüfen Sie Ausreißerpunkte vor der Veröffentlichung, um Eingabefehler direkt auf Open Food Facts zu korrigieren.",
        "showcase_title": "Bibliothek nützlicher Abfragen & Diagramme",
        "showcase_sub": "Entdecken Sie von der Community erstellte Suchabfragen und Auswertungen.",
        "search_placeholder": "🔍 Nach Stichwort, Lebensmittel, Nährwert oder Autor suchen...",
        "label_topics": "Themen:",
        "all_topics": "Alle Themen",
        "label_type": "Format:",
        "all_types": "Alle Formate",
        "label_geo": "Geografie:",
        "all_geos": "Alle Regionen",
        "label_sort": "Sortieren nach:",
        "sort_featured": "Hervorgehoben & Beliebt",
        "sort_title": "Titel (A-Z)",
        "sort_topic": "Thema",
        "results_count": "angezeigte Abfragen",
        "reset": "Filter zurücksetzen",
        "no_results": "Keine Abfragen entsprechen Ihren Filterkriterien.",
        "contrib_title": "💡 Haben Sie eine nützliche Abfrage erstellt?",
        "contrib_desc": "Fügen Sie Ihre Abfrage dieser offenen Sammlung hinzu!",
        "btn_propose": "🚀 Abfrage einreichen",
        "btn_browse_yaml": "📁 YAML-Dateien ansehen",
        "btn_run_text": "Abfrage öffnen",
        "btn_copy_title": "Link kopieren",
        "btn_edit_title": "Abfrage bearbeiten",
        "params_summary_text": "🔍 Parameter anzeigen",
        "copied_text": "Link in die Zwischenablage kopiert!"
    },
    "it": {
        "page_title": "Ricerca avanzata e Grafici in 3 clic",
        "hero_badge": "Visualizzazione di Dati Aperti",
        "hero_subtitle": "Esplora milioni di prodotti alimentari aperti con grafici a dispersione interattivi, mappe delle origini e tabelle di confronto.",
        "hero_quote": "Se un'immagine vale più di 1000 parole, vale anche più di 1000 numeri!",
        "btn_search": "🚀 Avvia Ricerca Avanzata",
        "btn_showcase": "✨ Esplora Query Utili",
        "btn_propose_query": "🚀 Proponi una Query",
        "btn_skip": "Salta tutorial",
        "workflow_title": "Come creare un grafico in 3 clic",
        "workflow_sub": "Il motore di ricerca avanzata di Open Food Facts consente di filtrare e analizzare qualunque segmento del mercato alimentare.",
        "step1_title": "1. Definisci filtri e perimetro",
        "step1_desc": "Combina fino a 5 criteri: categoria, paese di vendita, marca, etichette o punteggi Nutri-Score.",
        "step1_f1": "Categorie, marche, ingredienti",
        "step1_f2": "Filtri per paese ed etichette",
        "step1_f3": "Filtri booleani cumulativi",
        "step2_title": "2. Scegli assi e visualizzazione",
        "step2_desc": "Seleziona gli assi X e Y (zuccheri vs additivi, calorie vs lipidi). Attiva indicatori per prodotti bio o dolcificanti.",
        "step2_f1": "Grafici a dispersione",
        "step2_f2": "Istogrammi di distribuzione",
        "step2_f3": "Mappe geografiche ed esportazione CSV",
        "step3_title": "3. Analizza, verifica e condividi",
        "step3_desc": "Passa sopra i punti per visualizzare la scheda completa, rileva anomalie e condividi l'URL persistente.",
        "step3_f1": "Punti dati dinamici e interattivi",
        "step3_f2": "Rilevamento visivo dei valori anomali",
        "step3_f3": "URL persistente per pubblicazioni e condivisione",
        "spotlight_badge": "Caso studio iconico",
        "spotlight_title": "Zuccheri e additivi nelle bibite (Operazione Bibite)",
        "spotlight_desc": "Questo grafico confronta la quantità di zucchero con il numero di additivi nelle bevande analizzate dalla comunità.",
        "spotlight_btn": "Esplora questo grafico in tempo reale ↗",
        "format1_title": "Grafici a dispersione",
        "format1_desc": "Metti in relazione due nutrienti o metriche con descrizioni interattive.",
        "format2_title": "Mappe delle origini",
        "format2_desc": "Visualizza i luoghi di produzione e la provenienza degli ingredienti (DOP, commercio equo).",
        "format3_title": "Liste personalizzate ed esportazioni",
        "format3_desc": "Scarica i dati filtrati in CSV o Excel per analisi approfondite.",
        "callout_title": "Consiglio di verifica comunitaria",
        "callout_desc": "Prima di citare un grafico, controlla i prodotti ai punti estremi per verificare eventuali errori di digitazione.",
        "showcase_title": "Catalogo di Query Utili e Grafici della Comunità",
        "showcase_sub": "Scopri le ricerche e visualizzazioni create dalla comunità di Open Food Facts.",
        "search_placeholder": "🔍 Cerca per parola chiave, alimento, nutriente, autore...",
        "label_topics": "Temi:",
        "all_topics": "Tutti i temi",
        "label_type": "Formato visualizzazione:",
        "all_types": "Tutti i formati",
        "label_geo": "Geografia:",
        "all_geos": "Tutte le aree",
        "label_sort": "Ordina per:",
        "sort_featured": "In evidenza e popolari",
        "sort_title": "Titolo (A-Z)",
        "sort_topic": "Tema",
        "results_count": "query mostrate",
        "reset": "Reimposta filtri",
        "no_results": "Nessuna query corrisponde ai filtri selezionati.",
        "contrib_title": "💡 Hai creato una query o un grafico utile?",
        "contrib_desc": "Aggiungi la tua ricerca alla nostra libreria aperta!",
        "btn_propose": "🚀 Proponi una query",
        "btn_browse_yaml": "📁 Visualizza file YAML",
        "btn_run_text": "Apri query",
        "btn_copy_title": "Copia link",
        "btn_edit_title": "Modifica questa query",
        "params_summary_text": "🔍 Mostra parametri",
        "copied_text": "Link copiato negli appunti!"
    },
    "nl": {
        "page_title": "Geavanceerd zoeken & visualisaties: Grafieken in 3 klikken",
        "hero_badge": "Open data visualisaties",
        "hero_subtitle": "Verken miljoenen open voedselproducten met interactieve spreidingsdiagrammen, herkomstkaarten, vergelijkende staafdiagrammen en aangepaste gegevensexports.",
        "hero_quote": "Als een beeld meer zegt dan 1.000 woorden, zegt het ook meer dan 1.000 cijfers!",
        "btn_search": "🚀 Start geavanceerd zoeken",
        "btn_showcase": "✨ Ontdek nuttige zoekopdrachten",
        "btn_propose_query": "🚀 Stel een zoekopdracht voor",
        "btn_skip": "Tutorial overslaan",
        "workflow_title": "Hoe maak je een grafiek in 3 klikken",
        "workflow_sub": "Met de geavanceerde zoekmachine van Open Food Facts kunt u elk segment van de wereldwijde voedseldatabank filteren en correleren.",
        "step1_title": "1. Definieer filters en bereik",
        "step1_desc": "Combineer tot 5 gelijktijdige criteria: categorie (bijv. granen, kazen), land van verkoop, merk, keurmerken (Bio, Fair Trade) of Nutri-Score.",
        "step1_f1": "Categorieën, merken, ingrediënten",
        "step1_f2": "Filteren op land en kwaliteitslabels",
        "step1_f3": "Cumulatieve zoekcriteria",
        "step2_title": "2. Kies analyse-assen",
        "step2_desc": "Kies uw X- en Y-as (suikers vs toevoegingen, energie vs vetten). Schakel visuele markeringen in voor biologische producten of zoetstoffen.",
        "step2_f1": "Spreidingsdiagrammen (Scatter plots)",
        "step2_f2": "Verdelingsstaafdiagrammen",
        "step2_f3": "Geografische kaarten & CSV-exports",
        "step3_title": "3. Inspecteer, verifieer en deel",
        "step3_desc": "Beweeg over gegevenspunten voor een productvoorbeeld. Herken uitschieters en deel uw permanente grafiek-URL met de wereld.",
        "step3_f1": "Dynamische interactieve gegevenspunten",
        "step3_f2": "Visuele herkenning van uitschieters",
        "step3_f3": "Permanente URL voor artikelen en delen",
        "spotlight_badge": "Iconische casestudy",
        "spotlight_title": "Suikers & toevoegingen in frisdranken (Operatie Frisdrank)",
        "spotlight_desc": "Dit diagram vergelijkt het suikergehalte met het aantal additieven in frisdranken die door de gemeenschap zijn verzameld.",
        "spotlight_btn": "Bekijk deze live grafiek ↗",
        "format1_title": "Spreidingsdiagrammen",
        "format1_desc": "Correleer twee voedingsstoffen of statistieken met interactieve tooltips.",
        "format2_title": "Herkomstkaarten",
        "format2_desc": "Breng productielocaties en herkomst van ingrediënten in kaart.",
        "format3_title": "Aangepaste lijsten & gegevensexports",
        "format3_desc": "Download gefilterde datasets als CSV of Excel voor diepgaande analyse.",
        "callout_title": "Tip voor gemeenschapsverificatie",
        "callout_desc": "Controleer bij extreme uitschieters altijd de verpakking op eventuele typefouten voordat u een grafiek publiceert.",
        "showcase_title": "Overzicht van nuttige zoekopdrachten en grafieken",
        "showcase_sub": "Ontdek analyses en visualisaties gemaakt door de Open Food Facts-gemeenschap.",
        "search_placeholder": "🔍 Zoek op trefwoord, voedingsmiddel, voedingsstof, auteur...",
        "label_topics": "Onderwerpen:",
        "all_topics": "Alle onderwerpen",
        "label_type": "Visualisatietype:",
        "all_types": "Alle typen",
        "label_geo": "Geografie:",
        "all_geos": "Alle gebieden",
        "label_sort": "Sorteren op:",
        "sort_featured": "Uitgelicht & aanbevolen",
        "sort_title": "Titel (A-Z)",
        "sort_topic": "Onderwerp",
        "results_count": "zoekopdrachten getoond",
        "reset": "Filters resetten",
        "no_results": "Geen zoekopdrachten gevonden voor de geselecteerde filters.",
        "contrib_title": "💡 Heeft u een interessante zoekopdracht gemaakt?",
        "contrib_desc": "Voeg uw zoekopdracht of grafiek toe aan deze open bibliotheek!",
        "btn_propose": "🚀 Stel een zoekopdracht voor",
        "btn_browse_yaml": "📁 Bekijk YAML-bestanden",
        "btn_run_text": "Open zoekopdracht",
        "btn_copy_title": "Kopieer link",
        "btn_edit_title": "Bewerk deze zoekopdracht",
        "params_summary_text": "🔍 Parameters bekijken",
        "copied_text": "Zoeklink gekopieerd naar klembord!"
    },
    "pt": {
        "page_title": "Pesquisa avançada e visualizações: Gráficos em 3 cliques",
        "hero_badge": "Visualizações de Dados Abertos",
        "hero_subtitle": "Explore milhões de produtos alimentares abertos com gráficos de dispersão interativos, mapas de origem, gráficos de barras e exportações de dados personalizadas.",
        "hero_quote": "Se uma imagem vale por 1.000 palavras, também vale por 1.000 números!",
        "btn_search": "🚀 Iniciar Pesquisa Avançada",
        "btn_showcase": "✨ Explorar Consultas Úteis",
        "btn_propose_query": "🚀 Propor uma Consulta",
        "btn_skip": "Ignorar tutorial",
        "workflow_title": "Como criar um gráfico em 3 cliques",
        "workflow_sub": "O motor de busca avançada do Open Food Facts permite filtrar e correlacionar qualquer segmento da base de dados alimentar.",
        "step1_title": "1. Definir filtros e âmbito",
        "step1_desc": "Combine até 5 critérios simultâneos: categoria (ex: cereais, queijos), país de venda, marca, rótulos (Biológico, Comércio Justo) ou Nutri-Score.",
        "step1_f1": "Categorias, marcas, ingredientes",
        "step1_f2": "Filtragem por país e selos de qualidade",
        "step1_f3": "Critérios de filtragem múltiplos",
        "step2_title": "2. Escolher eixos de análise",
        "step2_desc": "Selecione os eixos X e Y (açúcares vs aditivos, calorias vs gorduras). Ative marcadores visuais para produtos biológicos ou adoçantes.",
        "step2_f1": "Gráficos de dispersão (Scatter plots)",
        "step2_f2": "Gráficos de barras de distribuição",
        "step2_f3": "Mapas geoespaciais e exportações CSV",
        "step3_title": "3. Inspecionar, verificar e partilhar",
        "step3_desc": "Passe o cursor sobre os pontos de dados para pré-visualizar o produto. Identifique valores atípicos e partilhe o URL persistente.",
        "step3_f1": "Pontos de dados dinâmicos e interativos",
        "step3_f2": "Identificação visual de valores atípicos",
        "step3_f3": "URL permanente para partilha e estudos",
        "spotlight_badge": "Estudo de caso icónico",
        "spotlight_title": "Açúcares e aditivos em refrigerantes (Operação Refrigerantes)",
        "spotlight_desc": "Este gráfico correlaciona o teor de açúcar com o número de aditivos em refrigerantes catalogados pela comunidade.",
        "spotlight_btn": "Explorar este gráfico em direto ↗",
        "format1_title": "Gráficos de dispersão",
        "format1_desc": "Correlacione dois nutrientes ou métricas com legendas interativas.",
        "format2_title": "Mapas de origens",
        "format2_desc": "Mapeie locais de fabrico e proveniência dos ingredientes.",
        "format3_title": "Listas personalizadas e exportações",
        "format3_desc": "Descarregue conjuntos de dados filtrados em CSV ou Excel para análise.",
        "callout_title": "Dica de validação comunitária",
        "callout_desc": "Antes de publicar ou referenciar um gráfico, verifique sempre os produtos nos extremos para confirmar eventuais erros de digitação.",
        "showcase_title": "Catálogo de Consultas Úteis e Gráficos da Comunidade",
        "showcase_sub": "Explore análises e visualizações criadas pela comunidade Open Food Facts.",
        "search_placeholder": "🔍 Pesquisar por palavra-chave, alimento, nutriente, autor...",
        "label_topics": "Tópicos:",
        "all_topics": "Todos os tópicos",
        "label_type": "Tipo de visualização:",
        "all_types": "Todos os formatos",
        "label_geo": "Geografia:",
        "all_geos": "Todas as regiões",
        "label_sort": "Ordenar por:",
        "sort_featured": "Em destaque e selecionados",
        "sort_title": "Título (A-Z)",
        "sort_topic": "Tópico",
        "results_count": "consultas apresentadas",
        "reset": "Repor filtros",
        "no_results": "Nenhuma consulta corresponde aos filtros selecionados.",
        "contrib_title": "💡 Criou uma consulta ou gráfico interessante?",
        "contrib_desc": "Adicione a sua pesquisa a esta biblioteca aberta!",
        "btn_propose": "🚀 Propor uma consulta",
        "btn_browse_yaml": "📁 Ver ficheiros YAML",
        "btn_run_text": "Abrir consulta",
        "btn_copy_title": "Copiar ligação",
        "btn_edit_title": "Editar esta consulta",
        "params_summary_text": "🔍 Inspecionar parâmetros",
        "copied_text": "Ligação copiada para a área de transferência!"
    },
    "pl": {
        "page_title": "Zaawansowane wyszukiwanie i wizualizacje: Wykresy w 3 kliknięciach",
        "hero_badge": "Wizualizacje Otwartych Danych",
        "hero_subtitle": "Przeglądaj miliony otwartych produktów spożywczych za pomocą interaktywnych wykresów punktowych, map pochodzenia i wykresów słupkowych.",
        "hero_quote": "Jeśli obraz jest wart 1000 słów, jest również wart 1000 liczb!",
        "btn_search": "🚀 Uruchom zaawansowane wyszukiwanie",
        "btn_showcase": "✨ Odkryj przydatne zapytania",
        "btn_propose_query": "🚀 Zaproponuj zapytanie",
        "btn_skip": "Pomiń samouczek",
        "workflow_title": "Jak stworzyć wykres w 3 kliknięciach",
        "workflow_sub": "Zaawansowana wyszukiwarka Open Food Facts pozwala filtrować i korelować dowolny segment bazy danych żywności.",
        "step1_title": "1. Określ filtry i zakres",
        "step1_desc": "Połącz do 5 jednoczesnych kryteriów: kategoria (np. płatki, sery), kraj sprzedaży, marka, etykiety (Eko, Fair Trade) lub Nutri-Score.",
        "step1_f1": "Kategorie, marki, składniki",
        "step1_f2": "Kraj sprzedaży i etykiety jakości",
        "step1_f3": "Wielokryterialne filtrowanie logiczne",
        "step2_title": "2. Wybierz osie analizy",
        "step2_desc": "Wybierz oś X i Y (cukry vs dodatki, kalorie vs tłuszcze). Włącz znaczniki dla produktów ekologicznych lub słodzików.",
        "step2_f1": "Wykresy punktowe (Scatter plots)",
        "step2_f2": "Wykresy słupkowe rozkładu",
        "step2_f3": "Mapy geograficzne i eksport do CSV",
        "step3_title": "3. Badaj, weryfikuj i udostępniaj",
        "step3_desc": "Najedź kursorem na punkty danych, aby podejrzeć kartę produktu. Wskazuj anomalie i udostępniaj trwały adres URL wykresu.",
        "step3_f1": "Dynamiczne interaktywne punkty danych",
        "step3_f2": "Wizualna identyfikacja wartości odstających",
        "step3_f3": "Trwały adres URL do publikacji i udostępniania",
        "spotlight_badge": "Kultowe studium przypadku",
        "spotlight_title": "Cukry i dodatki w napojach gazowanych (Operacja Napoje)",
        "spotlight_desc": "Ten wykres zestawia zawartość cukru z liczbą dodatków do żywności w napojach zgromadzonych przez społeczność.",
        "spotlight_btn": "Zobacz ten wykres na żywo ↗",
        "format1_title": "Wykresy punktowe",
        "format1_desc": "Koreluj dowolne dwa składniki odżywcze z interaktywnymi podpowiedziami.",
        "format2_title": "Mapy pochodzenia",
        "format2_desc": "Mapuj miejsca produkcji i pochodzenie składników.",
        "format3_title": "Niestandardowe listy i eksport danych",
        "format3_desc": "Pobieraj przefiltrowane dane w formacie CSV lub Excel do dogłębnej analizy.",
        "callout_title": "Wskazówka dotycząca weryfikacji danych",
        "callout_desc": "Przed zacytowaniem wykresu sprawdź produkty w punktach skrajnych pod kątem ewentualnych błędów wprowadzania.",
        "showcase_title": "Katalog przydatnych zapytań i wykresów społeczności",
        "showcase_sub": "Przeglądaj analizy żywieniowe i wizualizacje stworzone przez społeczność Open Food Facts.",
        "search_placeholder": "🔍 Szukaj według słowa kluczowego, żywności, składnika odżywczego, autora...",
        "label_topics": "Tematy:",
        "all_topics": "Wszystkie tematy",
        "label_type": "Typ wizualizacji:",
        "all_types": "Wszystkie formaty",
        "label_geo": "Geografia:",
        "all_geos": "Wszystkie regiony",
        "label_sort": "Sortuj według:",
        "sort_featured": "Wyróżnione i polecane",
        "sort_title": "Tytuł (A-Z)",
        "sort_topic": "Temat",
        "results_count": "wyświetlonych zapytań",
        "reset": "Zresetuj filtry",
        "no_results": "Brak zapytań pasujących do wybranych filtrów.",
        "contrib_title": "💡 Stworzyłeś ciekawe zapytanie lub wykres?",
        "contrib_desc": "Dodaj swoje wyszukiwanie do tej otwartej biblioteki!",
        "btn_propose": "🚀 Zaproponuj zapytanie",
        "btn_browse_yaml": "📁 Przeglądaj pliki YAML",
        "btn_run_text": "Otwórz zapytanie",
        "btn_copy_title": "Kopiuj link",
        "btn_edit_title": "Edytuj to zapytanie",
        "params_summary_text": "🔍 Pokaż parametry",
        "copied_text": "Link do wyszukiwania skopiowany do schowka!"
    },
    "ca": {
        "page_title": "Cerca avançada i visualitzacions: Gràfics en 3 clics",
        "hero_badge": "Visualitzacions de Dades Obertes",
        "hero_subtitle": "Exploreu milions de productes alimentaris oberts amb gràfics de dispersió interactius, mapes d'orígens, gràfics de barres i exportacions de dades personalitzades.",
        "hero_quote": "Si una imatge val més que 1.000 paraules, també val més que 1.000 xifres!",
        "btn_search": "🚀 Iniciar la Cerca Avançada",
        "btn_showcase": "✨ Explorar Consultes Útils",
        "btn_propose_query": "🚀 Proposar una Consulta",
        "btn_skip": "Ometre el tutorial",
        "workflow_title": "Com crear un gràfic en 3 clics",
        "workflow_sub": "El motor de cerca avançada d'Open Food Facts us permet filtrar i correlacionar qualsevol segment de la base de dades alimentària mundial.",
        "step1_title": "1. Definir filtres i abast",
        "step1_desc": "Combineu fins a 5 criteris simultanis: categoria (ex: cereals, formatges), país de venda, marca, segells (Ecològic, Comerç Just) o Nutri-Score.",
        "step1_f1": "Categories, marques, ingredients",
        "step1_f2": "Filtratge per país i segells de qualitat",
        "step1_f3": "Criteris de cerca booleans",
        "step2_title": "2. Triar els eixos d'anàlisi",
        "step2_desc": "Trieu els eixos X i Y (sucres vs additius, energia vs greixos). Activeu marcadors per a productes ecològics o edulcorants.",
        "step2_f1": "Gràfics de dispersió (Scatter plots)",
        "step2_f2": "Gràfics de barres de distribució",
        "step2_f3": "Mapes geoespacials i exportacions CSV",
        "step3_title": "3. Inspeccionar, verificar i compartir",
        "step3_desc": "Passeu el cursor per sobre dels punts per veure la fitxa del producte. Detecteu valors atípics i compartiu l'URL permanent del gràfic.",
        "step3_f1": "Punts de dades dinàmics i interactius",
        "step3_f2": "Identificació visual de valors atípics",
        "step3_f3": "URL permanent per a estudis i compartició",
        "spotlight_badge": "Cas d'estudi icònic",
        "spotlight_title": "Sucres i additius en refrescos (Operació Refrescos)",
        "spotlight_desc": "Aquest gràfic correlaciona el contingut de sucre amb el nombre d'additius en refrescos recollits per la comunitat.",
        "spotlight_btn": "Explorar aquest gràfic en directe ↗",
        "format1_title": "Gràfics de dispersió",
        "format1_desc": "Correlacioneu dos nutrients o mètriques amb consells interactius.",
        "format2_title": "Mapes d'orígens",
        "format2_desc": "Mapegeu llocs de fabricació i procedència dels ingredients.",
        "format3_title": "Llistes personalitzades i exportacions",
        "format3_desc": "Descarregueu conjunts de dades filtrats en CSV o Excel per a anàlisis a fons.",
        "callout_title": "Consell de validació comunitària",
        "callout_desc": "Abans de citar un gràfic, comproveu sempre els productes als punts extrems per verificar possibles errors d'escriptura.",
        "showcase_title": "Catàleg de Consultes Útils i Gràfics de la Comunitat",
        "showcase_sub": "Exploreu anàlisis i visualitzacions creades per la comunitat d'Open Food Facts.",
        "search_placeholder": "🔍 Cerca per paraula clau, aliment, nutrient, autor...",
        "label_topics": "Temes:",
        "all_topics": "Tots els temes",
        "label_type": "Tipus de visualització:",
        "all_types": "Tots els formats",
        "label_geo": "Geografia:",
        "all_geos": "Totes les regions",
        "label_sort": "Ordena per:",
        "sort_featured": "Destacats i seleccionats",
        "sort_title": "Títol (A-Z)",
        "sort_topic": "Tema",
        "results_count": "consultes mostrades",
        "reset": "Restablir filtres",
        "no_results": "Cap consulta coincideix amb els filtres seleccionats.",
        "contrib_title": "💡 Heu creat una consulta o gràfic interessant?",
        "contrib_desc": "Afegiu la vostra cerca a aquesta biblioteca oberta!",
        "btn_propose": "🚀 Proposar una consulta",
        "btn_browse_yaml": "📁 Veure fitxers YAML",
        "btn_run_text": "Obrir consulta",
        "btn_copy_title": "Copiar enllaç",
        "btn_edit_title": "Modificar aquesta consulta",
        "params_summary_text": "🔍 Inspeccionar paràmetres",
        "copied_text": "Enllaç copiat al porta-retalls!"
    },
    "ru": {
        "page_title": "Расширенный поиск и визуализация: Графики в 3 клика",
        "hero_badge": "Визуализация открытых данных",
        "hero_subtitle": "Исследуйте миллионы продуктов с интерактивными диаграммами рассеяния, картами происхождения, гистограммами и экспортом данных.",
        "hero_quote": "Если картинка стоит тысячи слов, она также стоит тысячи цифр!",
        "btn_search": "🚀 Расширенный поиск",
        "btn_showcase": "✨ Полезные запросы",
        "btn_propose_query": "🚀 Предложить запрос",
        "btn_skip": "Пропустить руководство",
        "workflow_title": "Как создать график за 3 клика",
        "workflow_sub": "Расширенный поиск Open Food Facts позволяет фильтровать и сопоставлять любые сегменты мировой базы данных продуктов питания.",
        "step1_title": "1. Задайте фильтры и область",
        "step1_desc": "Объединяйте до 5 критериев одновременно: категория (хлопья, сыры), страна продажи, бренд, маркировки (Органик, Fair Trade) или Nutri-Score.",
        "step1_f1": "Категории, бренды, ингредиенты",
        "step1_f2": "Страна продажи и знаки качества",
        "step1_f3": "Многокритериальная фильтрация",
        "step2_title": "2. Выберите оси анализа",
        "step2_desc": "Выберите оси X и Y (сахар и добавки, калории и жиры). Включите визуальные маркеры для органических продуктов или подсластителей.",
        "step2_f1": "Диаграммы рассеяния (Scatter plots)",
        "step2_f2": "Гистограммы распределения",
        "step2_f3": "Географические карты и экспорт в CSV",
        "step3_title": "3. Исследуйте, проверяйте и делитесь",
        "step3_desc": "Наведите курсор на точки данных для просмотра карточки товара. Находите аномалии и делитесь постоянной ссылкой на график.",
        "step3_f1": "Интерактивные точки данных",
        "step3_f2": "Визуальное выявление аномалий",
        "step3_f3": "Постоянная ссылка для публикаций и обмена",
        "spotlight_badge": "Знаковое исследование",
        "spotlight_title": "Сахар и добавки в газировке (Операция Газировка)",
        "spotlight_desc": "Этот график сопоставляет содержание сахара с количеством добавок в газированных напитках, собранных сообществом.",
        "spotlight_btn": "Открыть этот график в реальном времени ↗",
        "format1_title": "Диаграммы рассеяния",
        "format1_desc": "Сопоставляйте любые два питательных вещества с интерактивными подсказками.",
        "format2_title": "Карты происхождения",
        "format2_desc": "Карта мест производства и происхождения ингредиентов.",
        "format3_title": "Списки и экспорт данных",
        "format3_desc": "Скачивайте отфильтрованные данные в CSV или Excel для детального анализа.",
        "callout_title": "Совет по проверке данных",
        "callout_desc": "Перед публикацией графика проверьте крайние точки, чтобы убедиться в отсутствии опечаток при вводе.",
        "showcase_title": "Каталог полезных запросов и графиков сообщества",
        "showcase_sub": "Исследуйте подборку запросов и визуализаций, созданных сообществом Open Food Facts.",
        "search_placeholder": "🔍 Поиск по ключевому слову, продукту, автору...",
        "label_topics": "Темы:",
        "all_topics": "Все темы",
        "label_type": "Тип визуализации:",
        "all_types": "Все форматы",
        "label_geo": "География:",
        "all_geos": "Все регионы",
        "label_sort": "Сортировка:",
        "sort_featured": "Популярные и избранные",
        "sort_title": "Название (А-Я)",
        "sort_topic": "Тема",
        "results_count": "показано запросов",
        "reset": "Сбросить фильтры",
        "no_results": "По выбранным фильтрам запросы не найдены.",
        "contrib_title": "💡 Создали интересный запрос или график?",
        "contrib_desc": "Добавьте его в открытую библиотеку запросов!",
        "btn_propose": "🚀 Предложить запрос",
        "btn_browse_yaml": "📁 Файлы YAML",
        "btn_run_text": "Открыть запрос",
        "btn_copy_title": "Скопировать ссылку",
        "btn_edit_title": "Редактировать запрос",
        "params_summary_text": "🔍 Параметры запроса",
        "copied_text": "Ссылка скопирована в буфер обмена!"
    }
}

def t_query(key, lang="en"):
    """Lookup UI string with fallback to English."""
    return UI_STRINGS.get(lang, {}).get(key) or UI_STRINGS.get("en", {}).get(key, "")

def generate_js(lang="en"):
    copied_text = t_query("copied_text", lang)
    return f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{

  const searchInput = document.getElementById('g3c-search');
  const topicPills = document.querySelectorAll('.g3c-topic-pill');
  const typeSelect = document.getElementById('g3c-type-select');
  const geoSelect = document.getElementById('g3c-geo-select');
  const sortSelect = document.getElementById('g3c-sort-select');
  const resetBtn = document.getElementById('g3c-reset');
  const cards = Array.from(document.querySelectorAll('.g3c-query-card'));
  const countBadge = document.getElementById('g3c-count');
  const noResults = document.getElementById('g3c-no-results');
  const cardsContainer = document.getElementById('g3c-cards-grid');

  let activeTopic = 'all';

  function filterCards() {{
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const selectedType = typeSelect ? typeSelect.value : 'all';
    const selectedGeo = geoSelect ? geoSelect.value : 'all';

    let visibleCount = 0;

    cards.forEach(card => {{
      const topic = card.getAttribute('data-topic') || '';
      const type = card.getAttribute('data-type') || '';
      const geos = (card.getAttribute('data-geos') || '').split(',');
      const searchTarget = (card.getAttribute('data-search') || '').toLowerCase();

      let matchTopic = (activeTopic === 'all') || (topic === activeTopic);
      let matchType = (selectedType === 'all') || (type === selectedType);
      let matchGeo = (selectedGeo === 'all') || geos.includes(selectedGeo);
      let matchQuery = !query || searchTarget.includes(query);

      if (matchTopic && matchType && matchGeo && matchQuery) {{
        card.style.display = 'flex';
        visibleCount++;
      }} else {{
        card.style.display = 'none';
      }}
    }});

    if (countBadge) {{
      countBadge.textContent = visibleCount;
    }}
    if (noResults) {{
      noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }}
  }}

  // Topic pills click
  topicPills.forEach(pill => {{
    pill.addEventListener('click', function() {{
      topicPills.forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      activeTopic = this.getAttribute('data-topic') || 'all';
      filterCards();
    }});
  }});

  // Search input with debounce
  let debounceTimeout;
  if (searchInput) {{
    searchInput.addEventListener('input', function() {{
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(filterCards, 150);
    }});
  }}

  if (typeSelect) typeSelect.addEventListener('change', filterCards);
  if (geoSelect) geoSelect.addEventListener('change', filterCards);

  // Sorting
  if (sortSelect) {{
    sortSelect.addEventListener('change', function() {{
      const sortVal = this.value;
      cards.sort((a, b) => {{
        if (sortVal === 'featured') {{
          const aFeat = a.classList.contains('featured') ? 0 : 1;
          const bFeat = b.classList.contains('featured') ? 0 : 1;
          if (aFeat !== bFeat) return aFeat - bFeat;
          return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
        }} else if (sortVal === 'title') {{
          return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
        }} else if (sortVal === 'topic') {{
          return a.getAttribute('data-topic').localeCompare(b.getAttribute('data-topic'));
        }}
        return 0;
      }});
      cards.forEach(card => cardsContainer.appendChild(card));
      filterCards();
    }});
  }}

  // Reset button
  if (resetBtn) {{
    resetBtn.addEventListener('click', function(e) {{
      e.preventDefault();
      if (searchInput) searchInput.value = '';
      if (typeSelect) typeSelect.value = 'all';
      if (geoSelect) geoSelect.value = 'all';
      if (sortSelect) sortSelect.value = 'featured';
      topicPills.forEach(p => p.classList.remove('active'));
      const allPill = document.querySelector('.g3c-topic-pill[data-topic=\"all\"]');
      if (allPill) allPill.classList.add('active');
      activeTopic = 'all';
      filterCards();
    }});
  }}

  // Copy buttons & Toast
  const toast = document.getElementById('g3c-toast');
  function showToast(msg) {{
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }}

  document.querySelectorAll('.g3c-copy-btn').forEach(btn => {{
    btn.addEventListener('click', function() {{
      const url = this.getAttribute('data-url');
      if (!url) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(url).then(() => {{
          showToast('{copied_text}');
        }}).catch(() => {{
          promptCopy(url);
        }});
      }} else {{
        promptCopy(url);
      }}
    }});
  }});

  function promptCopy(text) {{
    window.prompt('Copy query URL:', text);
  }}

  filterCards();
}});
</script>
"""

def generate_page_html(queries, lang="en"):
    t = lambda k: t_query(k, lang)

    # Titles & UI strings
    t_page_title = t("page_title")
    t_hero_badge = t("hero_badge")
    t_hero_subtitle = t("hero_subtitle")
    t_hero_quote = t("hero_quote")
    t_btn_search = t("btn_search")
    t_btn_showcase = t("btn_showcase")
    t_btn_skip = t("btn_skip")

    # 3 Clicks Section
    t_workflow_title = t("workflow_title")
    t_workflow_sub = t("workflow_sub")

    t_step1_title = t("step1_title")
    t_step1_desc = t("step1_desc")
    t_step1_f1 = t("step1_f1")
    t_step1_f2 = t("step1_f2")
    t_step1_f3 = t("step1_f3")

    t_step2_title = t("step2_title")
    t_step2_desc = t("step2_desc")
    t_step2_f1 = t("step2_f1")
    t_step2_f2 = t("step2_f2")
    t_step2_f3 = t("step2_f3")

    t_step3_title = t("step3_title")
    t_step3_desc = t("step3_desc")
    t_step3_f1 = t("step3_f1")
    t_step3_f2 = t("step3_f2")
    t_step3_f3 = t("step3_f3")

    # Spotlight Case Study
    t_spotlight_badge = t("spotlight_badge")
    t_spotlight_title = t("spotlight_title")
    t_spotlight_desc = t("spotlight_desc")
    t_spotlight_btn = t("spotlight_btn")

    # Formats Cards
    t_format1_title = t("format1_title")
    t_format1_desc = t("format1_desc")
    t_format2_title = t("format2_title")
    t_format2_desc = t("format2_desc")
    t_format3_title = t("format3_title")
    t_format3_desc = t("format3_desc")

    # Callout
    t_callout_title = t("callout_title")
    t_callout_desc = t("callout_desc")

    # Showcase Header
    t_showcase_title = t("showcase_title")
    t_showcase_sub = t("showcase_sub")
    t_search_placeholder = t("search_placeholder")
    t_label_topics = t("label_topics")
    t_all_topics = t("all_topics")
    t_label_type = t("label_type")
    t_all_types = t("all_types")
    t_label_geo = t("label_geo")
    t_all_geos = t("all_geos")
    t_label_sort = t("label_sort")
    t_sort_featured = t("sort_featured")
    t_sort_title = t("sort_title")
    t_sort_topic = t("sort_topic")
    t_results_count = t("results_count")
    t_reset = t("reset")
    t_no_results = t("no_results")

    # Contribute section
    t_contrib_title = t("contrib_title")
    t_contrib_desc = t("contrib_desc")
    t_btn_propose = t("btn_propose")
    t_btn_browse_yaml = t("btn_browse_yaml")

    # Build topic pill buttons
    topic_pills_html = [f'<button type="button" class="g3c-pill-btn g3c-topic-pill active" data-topic="all">🌐 {t_all_topics}</button>']
    for t_key, t_info in VALID_TOPICS.items():
        t_label = t_info.get(lang) or t_info.get("en", t_key)
        topic_pills_html.append(
            f'<button type="button" class="g3c-pill-btn g3c-topic-pill" data-topic="{t_key}">{t_info["icon"]} {t_label}</button>'
        )

    # Build type options
    type_options_html = [f'<option value="all">{t_all_types}</option>']
    for type_key, type_info in VALID_QUERY_TYPES.items():
        type_label = type_info.get(lang) or type_info.get("en", type_key)
        type_options_html.append(f'<option value="{type_key}">{type_info["icon"]} {type_label}</option>')

    # Build geo options
    geo_options_html = [f'<option value="all">{t_all_geos}</option>']
    for geo_key, geo_info in GEO_NAMES.items():
        geo_label = geo_info.get(lang) or geo_info.get("en", geo_key)
        geo_options_html.append(f'<option value="{geo_key}">{geo_info["flag"]} {geo_label}</option>')

    # Build cards HTML
    cards_html = []
    for q in queries:
        qid = html.escape(str(q.get("id", "")))
        title = html.escape(get_localized_field(q, "title", lang=lang))
        desc = html.escape(get_localized_field(q, "description", lang=lang))
        author = html.escape(str(q.get("author", "Open Food Facts Community")))
        topic = q.get("topic", "nutrition")
        q_type = q.get("query_type", "scatter_plot")
        geos = q.get("geographies", ["world"])
        url = html.escape(str(q.get("url", "")))
        featured = q.get("featured", False)
        tags_combined = q.get("tags_combined", [])
        params = q.get("parameters", {})
        keywords = q.get("keywords", [])

        # Search index string
        search_target = " ".join([
            title, desc, author, topic, q_type,
            " ".join(geos),
            " ".join(tags_combined),
            " ".join(keywords)
        ]).lower()
        search_attr = html.escape(search_target)

        # Type badge
        type_meta = VALID_QUERY_TYPES.get(q_type, {})
        type_label = type_meta.get(lang) or type_meta.get("en", q_type)
        type_icon = type_meta.get("icon", "📈")
        type_badge_html = f'<span class="g3c-type-badge {q_type}">{type_icon} {type_label}</span>'

        # Geo badges
        geo_badges_html = []
        for g in geos:
            g_meta = GEO_NAMES.get(g, {})
            flag = g_meta.get("flag", "📍")
            g_label = g_meta.get(lang) or g_meta.get("en", g.upper())
            geo_badges_html.append(f'<span class="g3c-geo-badge">{flag} {g_label}</span>')
        geo_badges_str = " ".join(geo_badges_html)

        # Chips for combined tags
        chips_html = []
        for tag in tags_combined[:6]:
            tag_escaped = html.escape(str(tag))
            tag_class = "state"
            if tag_escaped.startswith("category:"): tag_class = "category"
            elif tag_escaped.startswith("axis_") or tag_escaped.startswith("nutriment:"): tag_class = "axis"
            elif tag_escaped.startswith("label:") or tag_escaped.startswith("series:"): tag_class = "label"
            elif tag_escaped.startswith("ingredient:"): tag_class = "ingredient"
            chips_html.append(f'<span class="g3c-chip {tag_class}">{tag_escaped}</span>')
        chips_str = "".join(chips_html)

        # Formatted params
        params_str = html.escape(yaml.dump(params, default_flow_style=False, sort_keys=False))

        featured_class = "featured" if featured else ""
        featured_star = '⭐ <span style="font-size:0.75rem;font-weight:600;color:#d97706;">Featured</span>' if featured else ""

        btn_run_text = t("btn_run_text")
        btn_copy_title = t("btn_copy_title")
        btn_edit_title = t("btn_edit_title")
        params_summary_text = t("params_summary_text")

        card = f"""
        <article class="g3c-query-card {featured_class}"
                 data-id="{qid}"
                 data-title="{title}"
                 data-topic="{topic}"
                 data-type="{q_type}"
                 data-geos="{','.join(geos)}"
                 data-search="{search_attr}">
          <div class="g3c-card-header">
            <div class="g3c-card-tags-top">
              {type_badge_html}
              {geo_badges_str}
            </div>
            {f'<div class="g3c-featured-star">{featured_star}</div>' if featured else ''}
          </div>
          <h3 class="g3c-card-title">{title}</h3>
          <p class="g3c-card-desc">{desc}</p>
          <div class="g3c-author-line">👤 {author}</div>
          <div class="g3c-chips-wrap">{chips_str}</div>
          <div class="g3c-card-footer">
            <a href="{url}" target="_blank" rel="noopener noreferrer" class="g3c-run-btn">
              {btn_run_text} ↗
            </a>
            <button type="button" class="g3c-copy-btn" data-url="{url}" title="{btn_copy_title}">
              📋
            </button>
            <a href="https://github.com/openfoodfacts/openfoodfacts-web/edit/main/data/queries/{qid}.yaml" target="_blank" rel="noopener noreferrer" class="g3c-copy-btn" title="{btn_edit_title}" style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center;">
              ✏️
            </a>
          </div>
          <details class="g3c-params-details">
            <summary>{params_summary_text}</summary>
            <pre class="g3c-params-pre">{params_str}</pre>
          </details>
        </article>
        """
        cards_html.append(card)

    cards_str = "\n".join(cards_html)
    pills_str = "\n".join(topic_pills_html)
    types_str = "\n".join(type_options_html)
    geos_str = "\n".join(geo_options_html)

    css_block = generate_css()
    js_block = generate_js(lang)

    html_page = f"""
{css_block}

<div class="g3c-container">

  <!-- Hero Section -->
  <header class="g3c-hero">
    <div class="g3c-badge">📊 {t_hero_badge}</div>
    <h1 class="g3c-hero-title">{t_page_title}</h1>
    <p class="g3c-hero-subtitle">{t_hero_subtitle}</p>
    
    <div class="g3c-quote-card">
      &ldquo;{t_hero_quote}&rdquo;
    </div>

    <div class="g3c-hero-actions">
      <a href="https://world.openfoodfacts.org/cgi/search.pl?graph=1" class="g3c-btn g3c-btn-primary">
        {t_btn_search}
      </a>
      <a href="#g3c-showcase" class="g3c-btn g3c-btn-secondary">
        {t_btn_showcase}
      </a>
      <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-graph-query.yml" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-secondary">
        {t_btn_propose}
      </a>
      <a href="https://world.openfoodfacts.org/cgi/search.pl" class="g3c-btn g3c-btn-secondary" title="{t_btn_skip}">
        {t_btn_skip} ➔
      </a>
    </div>
  </header>

  <!-- 3-Click Visual Workflow Guide -->
  <section class="g3c-workflow" id="g3c-workflow">
    <div class="g3c-section-header">
      <h2 class="g3c-section-title">{t_workflow_title}</h2>
      <p class="g3c-section-subtitle">{t_workflow_sub}</p>
    </div>

    <div class="g3c-steps-grid">
      <!-- Step 1 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">1</div>
        <div class="g3c-step-icon">🎯</div>
        <h3 class="g3c-step-title">{t_step1_title}</h3>
        <p class="g3c-step-desc">{t_step1_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step1_f1}</li>
          <li>✔ {t_step1_f2}</li>
          <li>✔ {t_step1_f3}</li>
        </ul>
      </div>

      <!-- Step 2 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">2</div>
        <div class="g3c-step-icon">📐</div>
        <h3 class="g3c-step-title">{t_step2_title}</h3>
        <p class="g3c-step-desc">{t_step2_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step2_f1}</li>
          <li>✔ {t_step2_f2}</li>
          <li>✔ {t_step2_f3}</li>
        </ul>
      </div>

      <!-- Step 3 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">3</div>
        <div class="g3c-step-icon">🚀</div>
        <h3 class="g3c-step-title">{t_step3_title}</h3>
        <p class="g3c-step-desc">{t_step3_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step3_f1}</li>
          <li>✔ {t_step3_f2}</li>
          <li>✔ {t_step3_f3}</li>
        </ul>
      </div>
    </div>

    <!-- Spotlight Example Card -->
    <div class="g3c-spotlight-card">
      <div class="g3c-spotlight-grid">
        <a href="https://world.openfoodfacts.org/cgi/search.pl?action=process&amp;tagtype_0=categories&amp;tag_contains_0=contains&amp;tag_0=sodas&amp;sort_by=product_name&amp;page_size=20&amp;axis_x=sugars&amp;axis_y=additives_n&amp;graph_title=Sugars%20and%20additives%20in%20sodas&amp;series_organic=on&amp;series_fairtrade=on&amp;series_with_sweeteners=on&amp;generate_graph_scatter_plot=1" target="_blank" rel="noopener noreferrer">
          <img src="https://fr.blog.openfoodfacts.org/images/sucres_et_additifs_dans_les_sodas.png" alt="Sugars and additives in sodas scatter plot" class="g3c-spotlight-img" loading="lazy">
        </a>
        <div class="g3c-spotlight-content">
          <span class="g3c-badge">💡 {t_spotlight_badge}</span>
          <h3>{t_spotlight_title}</h3>
          <p>{t_spotlight_desc}</p>
          <a href="https://world.openfoodfacts.org/cgi/search.pl?action=process&amp;tagtype_0=categories&amp;tag_contains_0=contains&amp;tag_0=sodas&amp;sort_by=product_name&amp;page_size=20&amp;axis_x=sugars&amp;axis_y=additives_n&amp;graph_title=Sugars%20and%20additives%20in%20sodas&amp;series_organic=on&amp;series_fairtrade=on&amp;series_with_sweeteners=on&amp;generate_graph_scatter_plot=1" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-primary">
            {t_spotlight_btn}
          </a>
        </div>
      </div>
    </div>

    <!-- Available Visualization Formats Grid -->
    <div class="g3c-formats-grid">
      <div class="g3c-format-card">
        <h4>📈 {t_format1_title}</h4>
        <p>{t_format1_desc}</p>
      </div>
      <div class="g3c-format-card">
        <h4>🗺️ {t_format2_title}</h4>
        <p>{t_format2_desc}</p>
      </div>
      <div class="g3c-format-card">
        <h4>📥 {t_format3_title}</h4>
        <p>{t_format3_desc}</p>
      </div>
    </div>

    <!-- Outlier Validation Callout -->
    <div class="g3c-callout">
      <div class="g3c-callout-icon">💡</div>
      <div class="g3c-callout-body">
        <h4>{t_callout_title}</h4>
        <p>{t_callout_desc}</p>
      </div>
    </div>
  </section>

  <!-- Interactive Useful Queries Showcase -->
  <section class="g3c-showcase-section" id="g3c-showcase">
    <div class="g3c-section-header">
      <h2 class="g3c-section-title">{t_showcase_title}</h2>
      <p class="g3c-section-subtitle">{t_showcase_sub}</p>
    </div>

    <!-- Filter & Search Controls -->
    <div class="g3c-controls-wrap">
      <!-- Search Input -->
      <div class="g3c-search-bar">
        <span class="g3c-search-icon">🔍</span>
        <input type="text" id="g3c-search" class="g3c-search-input" placeholder="{t_search_placeholder}" aria-label="Search curated queries">
      </div>

      <!-- Topic Pills -->
      <div class="g3c-filter-group">
        <span class="g3c-filter-label">{t_label_topics}</span>
        <div class="g3c-pills-row">
          {pills_str}
        </div>
      </div>

      <!-- Secondary Filters & Sort -->
      <div class="g3c-secondary-filters">
        <div class="g3c-select-wrap">
          <div>
            <label class="g3c-filter-label" for="g3c-type-select">{t_label_type}</label>
            <select id="g3c-type-select" class="g3c-select">
              {types_str}
            </select>
          </div>

          <div>
            <label class="g3c-filter-label" for="g3c-geo-select">{t_label_geo}</label>
            <select id="g3c-geo-select" class="g3c-select">
              {geos_str}
            </select>
          </div>

          <div>
            <label class="g3c-filter-label" for="g3c-sort-select">{t_label_sort}</label>
            <select id="g3c-sort-select" class="g3c-select">
              <option value="featured">{t_sort_featured}</option>
              <option value="title">{t_sort_title}</option>
              <option value="topic">{t_sort_topic}</option>
            </select>
          </div>
        </div>

        <div class="g3c-stats-and-reset">
          <span class="g3c-count-badge" id="g3c-count">{len(queries)}</span> {t_results_count}
          <button type="button" class="g3c-reset-btn" id="g3c-reset">{t_reset}</button>
        </div>
      </div>
    </div>

    <!-- Cards Grid -->
    <div class="g3c-cards-grid" id="g3c-cards-grid">
      {cards_str}

      <div class="g3c-no-results" id="g3c-no-results" style="display:none;">
        <div class="g3c-no-results-icon">🔎</div>
        <p>{t_no_results}</p>
      </div>
    </div>

    <!-- Contribute Callout -->
    <div class="g3c-contribute-box">
      <h3 class="g3c-contribute-title">{t_contrib_title}</h3>
      <p class="g3c-contribute-desc">{t_contrib_desc}</p>
      <div style="display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap;">
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-graph-query.yml" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-primary">
          {t_btn_propose} ↗
        </a>
        <a href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/queries" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-secondary">
          {t_btn_browse_yaml} ↗
        </a>
      </div>
    </div>
  </section>

  <!-- Toast Notification element -->
  <div class="g3c-toast" id="g3c-toast"></div>

</div>

{js_block}
"""
    return html_page

def compile_queries(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating queries from {QUERIES_DIR}...")

    items, errors, warnings = load_queries(QUERIES_DIR, validate=True)

    if warnings and verbose:
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s) in query YAMLs:")
        for e in errors:
            print(f"  - {e}")
        return False

    if verbose:
        featured_count = sum(1 for q in items if q.get("featured"))
        topics_count = len(set(q.get("topic") for q in items))
        print(f"✅ Validated {len(items)} curated queries (Featured: {featured_count}, Topics: {topics_count})")

    if check_only:
        return True

    # 1. Compile structured queries dataset into data/queries.json
    dataset = {
        "count": len(items),
        "topics": list(VALID_TOPICS.keys()),
        "query_types": list(VALID_QUERY_TYPES.keys()),
        "geographies": list(GEO_NAMES.keys()),
        "queries": items
    }

    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"Wrote compiled {COMPILED_JSON} ({len(items)} items)")

    # 2. Generate localized graphs-in-3-clicks.html for all supported languages
    for target_lang in SUPPORTED_LANGUAGES:
        target_dir = os.path.join(REPO_ROOT, "lang", target_lang, "texts")
        os.makedirs(target_dir, exist_ok=True)
        html_path = os.path.join(target_dir, "graphs-in-3-clicks.html")
        content = generate_page_html(items, lang=target_lang)
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            if verbose:
                print(f"Generated {html_path}")
        except PermissionError:
            fallback_path = os.path.join(DATA_DIR, f"graphs-in-3-clicks.{target_lang}.html")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(content)
            if verbose:
                print(f"Generated fallback {fallback_path} (sandbox prevented write to {html_path})")

    # 3. Ensure French legacy symlink exists: graphes-en-3-clics.html -> graphs-in-3-clicks.html
    fr_symlink_path = os.path.join(REPO_ROOT, "lang", "fr", "texts", "graphes-en-3-clics.html")
    try:
        if not os.path.exists(fr_symlink_path) and not os.path.islink(fr_symlink_path):
            os.symlink("graphs-in-3-clicks.html", fr_symlink_path)
            if verbose:
                print(f"Created symlink {fr_symlink_path} -> graphs-in-3-clicks.html")
    except Exception as e:
        if verbose:
            print(f"Notice: could not create symlink {fr_symlink_path}: {e}")

    return True

def main():
    check_only = "--check" in sys.argv
    success = compile_queries(check_only=check_only, verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
