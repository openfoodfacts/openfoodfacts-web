#!/usr/bin/env python3
"""
Enrich data/reuses.json with granular themes:
- pregnancy
- gluten
- lactose
- fodmap
- allergies
- vegan
- halal_kosher
- diabetes_keto
- additives
- environment
- tools
- research
- traceability
- education
- nutrition

Assigns both primary 'theme' and multi-theme array 'themes' to every app.
Adds verified pregnancy apps from submissions if not already present.
Ensures bilingual search keywords include the granular terms.
"""

import hashlib
import json
import os
import re
import subprocess
import urllib.request

DATA_PATH = "data/reuses.json"
ICONS_DIR = "html/images/reuses/icons"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# Granular regex patterns
PATTERNS = {
    "pregnancy": [
        r"\bpregnan",
        r"\bgrossesse\b",
        r"\benceinte\b",
        r"\bmatern",
        r"\bfetus\b",
        r"\bfoetus\b",
        r"\btoxoplasm",
        r"\blisteria\b",
        r"\bmama\b",
    ],
    "gluten": [
        r"\bgluten",
        r"\bceliac\b",
        r"\bcoeliac\b",
        r"\bcœliaque\b",
        r"\bcoeliaque\b",
        r"\bbezlepku\b",
        r"sans gluten",
        r"gluten-free",
    ],
    "lactose": [
        r"\blactose",
        r"\bdairy-free\b",
        r"sans lactose",
        r"lactose-free",
        r"\bsosmilk\b",
        r"intol[eé]ran.*lait",
        r"lait.*intol[eé]ran",
        r"dairy intolerance",
    ],
    "fodmap": [
        r"\bfodmap",
        r"\bibs\b",
        r"intestin irritable",
        r"colon irritable",
        r"irritable bowel",
    ],
    "vegan": [
        r"\bvegan",
        r"\bv[eé]g[eé]talien",
        r"\bplant-based\b",
        r"\bv[eé]g[eé]tarien",
        r"\bvegetarian\b",
    ],
    "halal_kosher": [
        r"\bhalal",
        r"\bkosher\b",
        r"\bcasher\b",
        r"\bkashrut\b",
        r"\bcacher\b",
    ],
    "diabetes_keto": [
        r"\bdiabet",
        r"\bdiab[eè]te",
        r"\bglycem",
        r"\bglyc[eé]m",
        r"\binsulin",
        r"\bketo\b",
        r"\bc[h]?eto\b",
        r"ch[eé]tog",
    ],
    "additives": [
        r"additif",
        r"additive",
        r"ultra-process",
        r"ultra-transform",
        r"\bnova\b",
        r"e-code",
        r"ecodes",
        r"microplastic",
        r"endocrine",
    ],
}

# Explicit curated overrides for key apps
EXPLICIT_OVERRIDES = {
    # Pregnancy
    "ask-hera": {
        "theme": "pregnancy",
        "themes": ["pregnancy", "nutrition"],
        "tagline": "Personalized nutrition & safe food guide for pregnant women",
        "description": "Helps pregnant women make informed, safe dietary choices by checking ingredients against toxoplasmosis, listeria, and gestation nutrition guidelines with Open Food Facts.",
    },
    "pregnancy-diet-food-recipes": {
        "theme": "pregnancy",
        "themes": ["pregnancy", "nutrition"],
        "tagline": "Nutritional guidance, meal plans & recipes for pregnant mothers",
        "description": "Comprehensive nutritional guide and trimester-specific meal planner for expectant mothers, verifying groceries against Open Food Facts open food data.",
    },
    "nutrimam": {
        "theme": "pregnancy",
        "themes": ["pregnancy", "nutrition"],
        "tagline": "Maternal nutrition & food safety guide during pregnancy",
        "description": "Web platform and mobile application for pregnant and breastfeeding women across France, Switzerland, and Belgium, analyzing grocery ingredients for maternal safety.",
    },
    # Gluten
    "cedulka": {
        "theme": "gluten",
        "themes": ["gluten", "allergies"],
    },
    "gluten-scan": {
        "theme": "gluten",
        "themes": ["gluten", "allergies"],
    },
    "gluto": {
        "theme": "gluten",
        "themes": ["gluten", "allergies"],
    },
    "glutapp": {
        "theme": "gluten",
        "themes": ["gluten", "allergies"],
    },
    "gluten-guardian": {
        "theme": "gluten",
        "themes": ["gluten", "allergies"],
        "tagline": "Barcode scanner & gluten detector for celiacs",
        "description": "Assists celiacs and gluten-sensitive individuals by scanning packaged food barcodes against the Open Food Facts database to detect wheat, barley, rye, and hidden gluten derivatives.",
    },
    # Lactose
    "lattosio-free": {
        "theme": "lactose",
        "themes": ["lactose", "allergies"],
    },
    "lactose-help": {
        "theme": "lactose",
        "themes": ["lactose", "allergies"],
        "tagline": "Lactose scanner & lactase dosage assistant",
        "description": "Scans food labels for lactose, milk powder, whey, and dairy derivatives using Open Food Facts to help users manage lactose intolerance.",
    },
    # FODMAP
    "fodmap-facile": {
        "theme": "fodmap",
        "themes": ["fodmap", "allergies"],
    },
    "intolerapp": {
        "theme": "fodmap",
        "themes": ["fodmap", "gluten", "lactose", "allergies"],
    },
    "the-fodmap-bot": {
        "theme": "fodmap",
        "themes": ["fodmap", "allergies"],
        "tagline": "Low-FODMAP diet assistant & ingredient scanner",
        "description": "Evaluates packaged food ingredients for fermentable oligosaccharides, disaccharides, monosaccharides, and polyols to help manage irritable bowel syndrome (IBS).",
    },
    "ibs-tracker": {
        "theme": "fodmap",
        "themes": ["fodmap", "allergies"],
        "tagline": "Low-FODMAP food tracker for irritable bowel syndrome (IBS)",
        "description": "Helps users track daily food intake and symptom flare-ups while scanning ingredients for high-FODMAP triggers using Open Food Facts.",
    },
    # Allergies & Multi-diet
    "allergobox": {
        "theme": "allergies",
        "themes": ["allergies", "gluten", "lactose"],
    },
    "can-i-eat-this": {
        "theme": "allergies",
        "themes": ["allergies", "gluten", "lactose"],
    },
    "frag-ingrid": {
        "theme": "allergies",
        "themes": ["allergies", "lactose", "gluten", "fodmap"],
        "tagline": "Food intolerance scanner for fructose, lactose, gluten & histamine",
        "description": "Helps people with multiple food intolerances check supermarket items for fructose, lactose, sorbitol, histamine, and gluten using Open Food Facts data.",
    },
    "insekten-warn-app": {
        "theme": "allergies",
        "themes": ["allergies", "additives"],
    },
    # Diabetes / Keto
    "verydiab": {
        "theme": "diabetes_keto",
        "themes": ["diabetes_keto", "nutrition"],
    },
    "glucideo": {
        "theme": "diabetes_keto",
        "themes": ["diabetes_keto", "nutrition"],
    },
    "calcul-glucides-insuline": {
        "theme": "diabetes_keto",
        "themes": ["diabetes_keto", "nutrition"],
        "tagline": "Carbohydrate calculator & insulin dose estimator for diabetics",
        "description": "Calculates precise carbohydrate content and assists with insulin dosage calculations for type 1 and type 2 diabetics using nutritional data from Open Food Facts.",
    },
    "glycemeal": {
        "theme": "diabetes_keto",
        "themes": ["diabetes_keto", "nutrition"],
        "tagline": "Glycemic index tracker & carbohydrate counter",
        "description": "Scans food barcodes to estimate glycemic index and glycemic load, helping users with diabetes or insulin resistance optimize meal choices.",
    },
    "logi-glycemic-index-tracker": {
        "theme": "diabetes_keto",
        "themes": ["diabetes_keto", "nutrition"],
        "tagline": "Low-glycemic diet companion & carbohydrate tracker",
        "description": "Guides consumers following the LOGI low-glycemic method by evaluating carbohydrates and blood sugar impact using Open Food Facts.",
    },
    # Additives / Ultra-Processing
    "el-coco": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
    },
    "yuka": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
    },
    "ya-quoi-dedans": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
    },
    "toxfox": {
        "theme": "additives",
        "themes": ["additives", "tools"],
    },
    "truthin": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
    },
    "additifs-alimentaires": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
        "tagline": "Food additives, E-numbers & toxicity risk decrypter",
        "description": "Scans and decodes chemical food additives, artificial colorings, preservatives, and E-numbers in packaged food using Open Food Facts open data.",
    },
    "additiveguard": {
        "theme": "additives",
        "themes": ["additives", "nutrition"],
        "tagline": "Ingredient additive analyzer & hazard level scanner",
        "description": "Flags harmful, controversial, or banned food additives in supermarket goods by cross-referencing ingredients with Open Food Facts.",
    },
    # Vegan
    "321-vegan": {
        "theme": "vegan",
        "themes": ["vegan", "nutrition"],
        "tagline": "Vegan & vegetarian barcode scanner",
        "description": "Instantly verifies whether packaged food products contain animal-derived ingredients, dairy, eggs, or animal byproducts using Open Food Facts data.",
    },
    "cactus-go-vegan": {
        "theme": "vegan",
        "themes": ["vegan", "nutrition"],
        "tagline": "Community guide & grocery scanner for vegans",
        "description": "Scans food items to check vegan and vegetarian suitability, highlighting animal-derived additives and gelatin with Open Food Facts.",
    },
    "vegan-scanner": {
        "theme": "vegan",
        "themes": ["vegan", "nutrition"],
        "tagline": "Vegan product detector & animal ingredient checker",
        "description": "Detects meat, dairy, honey, and animal derivatives in grocery products using Open Food Facts open ingredient database.",
    },
    "v-g-tarien-scanner": {
        "theme": "vegan",
        "themes": ["vegan", "nutrition"],
        "tagline": "Scanner végétarien et végétalien",
        "description": "Scanne les codes-barres alimentaires pour détecter les ingrédients d'origine animale (gélatine, carmin, présure) via Open Food Facts.",
    },
    # Halal / Kosher
    "halal-healthy": {
        "theme": "halal_kosher",
        "themes": ["halal_kosher", "nutrition"],
        "tagline": "Halal certification & healthy nutrition grocery scanner",
        "description": "Scans food barcodes to check halal status (flags pork, non-halal meat, and alcohol derivatives) alongside Nutri-Score using Open Food Facts.",
    },
    "halalsnap": {
        "theme": "halal_kosher",
        "themes": ["halal_kosher", "nutrition"],
        "tagline": "Halal ingredient detector & food scanner",
        "description": "Analyzes ingredients lists for alcohol, non-halal animal fats, and doubtful E-codes against Open Food Facts open data.",
    },
    "is-it-kosher-est-ce-cacher": {
        "theme": "halal_kosher",
        "themes": ["halal_kosher", "nutrition"],
        "tagline": "Kosher verification & certification scanner",
        "description": "Checks kosher certifications and ingredient lists against kosher dietary guidelines using Open Food Facts.",
    },
}

KEYWORDS_ADDITIONS = {
    "pregnancy": "pregnancy pregnant gestation maternal maternity grossesses enceinte femme enceinte maternite toxoplasmose listeria bebe baby",
    "gluten": "gluten celiac coeliac coeliaque bezlepku sans gluten gluten-free ble wheat orge seigle",
    "lactose": "lactose dairy-free sans lactose lactose-free lait milk derive laitier lactase",
    "fodmap": "fodmap ibs intestin irritable colon irritable irritable bowel digestif ballonnement",
    "vegan": "vegan vegetalien plant-based vegetarien vegetarian vegetal sans viande",
    "halal_kosher": "halal kosher casher cacher kashrut porc alcool certification",
    "diabetes_keto": "diabete diabetes glycemic glycemique insuline insulin keto cetogene cheto carbs glucides",
    "additives": "additifs additives nova ultra-transforme ultra-processed e-numbers colorants conservateurs",
}


def download_icon(artwork_url, target_png):
    temp_file = target_png + ".tmp"
    try:
        req = urllib.request.Request(artwork_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            with open(temp_file, "wb") as f:
                f.write(resp.read())

        conv = subprocess.run(
            ["sips", "-s", "format", "png", "-Z", "128", temp_file, "--out", target_png],
            capture_output=True,
            text=True,
        )
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if conv.returncode == 0 and os.path.exists(target_png) and os.path.getsize(target_png) > 200:
            return True
    except Exception:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    return False


def main():
    os.makedirs(ICONS_DIR, exist_ok=True)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reuses = json.load(f)

    existing_ids = {r["id"]: r for r in reuses}

    # 1. Add missing pregnancy apps if needed
    if "pregnancy-diet-food-recipes" not in existing_ids:
        app_entry = {
            "id": "pregnancy-diet-food-recipes",
            "name": "Pregnancy Diet: Food & Recipes",
            "tagline": "Nutritional guidance, meal plans & recipes for pregnant mothers",
            "description": "Comprehensive nutritional guide and trimester-specific meal planner for expectant mothers, verifying groceries against Open Food Facts open food data.",
            "theme": "pregnancy",
            "themes": ["pregnancy", "nutrition"],
            "project": "openfoodfacts",
            "country": "global",
            "country_label": "Worldwide",
            "domain": "redsky-labs.com",
            "website": "https://www.redsky-labs.com/",
            "play_store": "https://play.google.com/store/apps/details?id=com.pregnancyrecipes",
            "app_store": None,
            "fdroid": None,
            "github": None,
            "contributes_data": False,
            "contributes_photos": False,
            "odbl_compliant": True,
            "open_source": False,
            "special_badge": None,
            "featured": False,
            "keywords": "pregnancy diet food recipes pregnant gestation trimester maternal grossesses enceinte baby",
            "cached_icon": "/images/reuses/icons/pregnancy-diet-food-recipes.png",
            "donates_to_ngo": False,
            "installs": "100K+",
            "installs_numeric": 100000,
            "rating": 4.5,
        }
        reuses.append(app_entry)
        existing_ids["pregnancy-diet-food-recipes"] = app_entry
        print("Added 'pregnancy-diet-food-recipes' to reuses.")

        # Download icon
        icon_url = "https://play-lh.googleusercontent.com/rIfwL-k3mYpqE7qD1erJ0c4f1yGzGAPzBY8d0U3ugbwB5kCUkGLSxTIlptOYu0tbSuX3Csl1_cGce1-5CxiY=s512"
        target_icon = os.path.join(ICONS_DIR, "pregnancy-diet-food-recipes.png")
        if download_icon(icon_url, target_icon):
            print("  Successfully downloaded icon for pregnancy-diet-food-recipes.")

    if "nutrimam" not in existing_ids:
        app_entry = {
            "id": "nutrimam",
            "name": "NutriMam",
            "tagline": "Maternal nutrition & food safety guide during pregnancy",
            "description": "Web platform and mobile application for pregnant and breastfeeding women across France, Switzerland, and Belgium, analyzing grocery ingredients for maternal safety.",
            "theme": "pregnancy",
            "themes": ["pregnancy", "nutrition"],
            "project": "openfoodfacts",
            "country": "fra",
            "country_label": "France, Switzerland & Belgium",
            "domain": "nutrimam.com",
            "website": "https://nutrimam.com/",
            "play_store": None,
            "app_store": None,
            "fdroid": None,
            "github": None,
            "contributes_data": True,
            "contributes_photos": False,
            "odbl_compliant": True,
            "open_source": False,
            "special_badge": None,
            "featured": False,
            "keywords": "nutrimam pregnancy nutrition pregnant gestation grossesses enceinte maternite toxoplasmose listeria allaitement baby",
            "cached_icon": "/images/reuses/default-app-icon.png",
            "donates_to_ngo": False,
        }
        reuses.append(app_entry)
        existing_ids["nutrimam"] = app_entry
        print("Added 'nutrimam' to reuses.")

    # 2. Classify and enrich all apps
    theme_distribution = {}
    for r in reuses:
        app_id = r["id"]

        if app_id in EXPLICIT_OVERRIDES:
            ov = EXPLICIT_OVERRIDES[app_id]
            r["theme"] = ov["theme"]
            r["themes"] = list(ov["themes"])
            if "tagline" in ov:
                r["tagline"] = ov["tagline"]
            if "description" in ov:
                r["description"] = ov["description"]
        else:
            # Pattern matching
            blob = f"{r['id']} {r['name']} {r.get('tagline', '')} {r.get('description', '')} {r.get('keywords', '')}".lower()
            matched_themes = []
            for t_name, regexes in PATTERNS.items():
                if any(re.search(rgx, blob) for rgx in regexes):
                    matched_themes.append(t_name)

            # Link gluten, lactose, and fodmap to allergies as parent
            if any(t in matched_themes for t in ["gluten", "lactose", "fodmap"]):
                if "allergies" not in matched_themes:
                    matched_themes.append("allergies")

            # Preserve base theme
            base_t = r.get("theme", "nutrition")

            # Determine primary granular theme
            priority_themes = [
                "pregnancy",
                "gluten",
                "lactose",
                "fodmap",
                "allergies",
                "diabetes_keto",
                "vegan",
                "halal_kosher",
                "additives",
                "environment",
                "tools",
                "research",
                "traceability",
                "education",
            ]

            primary = base_t
            for pt in priority_themes:
                if pt in matched_themes:
                    primary = pt
                    break

            if primary not in matched_themes:
                matched_themes.insert(0, primary)

            r["theme"] = primary
            r["themes"] = matched_themes

        # Append granular keywords for improved text searching
        current_kws = r.get("keywords", "")
        for t in r["themes"]:
            extra_kws = KEYWORDS_ADDITIONS.get(t, "")
            if extra_kws:
                for kw in extra_kws.split():
                    if kw not in current_kws.lower():
                        current_kws += f" {kw}"
        r["keywords"] = current_kws.strip()

        # Count primary and all themes
        for t in r["themes"]:
            theme_distribution[t] = theme_distribution.get(t, 0) + 1

    print("\nTotal themes distribution across all reusers:")
    for t, count in sorted(theme_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"  {t:16s}: {count}")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(reuses, f, indent=2, ensure_ascii=False)

    print(f"\nSaved updated reuses with granular themes to {DATA_PATH}.")


if __name__ == "__main__":
    main()
