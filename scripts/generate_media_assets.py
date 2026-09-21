#!/usr/bin/env python3
import re, json, os

assets = []

projects = [
    ("Open Food Facts", "off", "🍊", "openfoodfacts"),
    ("Open Beauty Facts", "obf", "🧴", "openbeautyfacts"),
    ("Open Products Facts", "opf", "📸", "openproductsfacts"),
    ("Open Pet Food Facts", "opff", "🐾", "openpetfoodfacts"),
]

for project, code, emoji, topic in projects:
    with open(f"lang/en/texts/logo-{code}.html", "r", encoding="utf-8") as f:
        text = f.read()
    cards = re.findall(r'<div class="logo-card([^"]*)" data-color="([^"]*)" data-format="([^"]*)" data-bg="([^"]*)">(.*?)</div>\s*</div>', text, re.DOTALL)
    for dark_cls, color, fmt, bg, inner in cards:
        img_m = re.search(r'src="([^"]+)"', inner)
        title_m = re.search(r'<h3[^>]*>(.*?)</h3>', inner)
        if not img_m or not title_m: continue
        img_url = img_m.group(1).strip()
        title = title_m.group(1).strip()
        base = img_url.rsplit(".", 1)[0]
        
        if "screenshot" in img_url.lower(): continue
        if "nutriscore" in img_url.lower(): continue
        if "green-score" in img_url.lower() or "ecoscore" in img_url.lower(): continue
        
        assets.append({
            "title": title,
            "topic": topic,
            "topic_label": f"{emoji} {project}",
            "color": color,
            "format": "svg png",
            "bg": bg,
            "img": img_url,
            "svg": base + ".svg",
            "png": base + ".png",
            "keywords": f"{project} {code} {title} {color} {bg} logo brand cmyk rgb rvb cmjn vector"
        })

# Open Prices
assets.append({
    "title": "Open Prices Logo Vertical (Light)",
    "topic": "openprices",
    "topic_label": "🏷️ Open Prices",
    "color": "color",
    "format": "svg",
    "bg": "light",
    "img": "/images/logos/openprices/op-logo-vertical-light.svg",
    "svg": "/images/logos/openprices/op-logo-vertical-light.svg",
    "png": None,
    "keywords": "open prices logo vertical light brand vector svg prices food inflation"
})
assets.append({
    "title": "Open Prices Favicon & Icon",
    "topic": "openprices",
    "topic_label": "🏷️ Open Prices",
    "color": "color",
    "format": "svg",
    "bg": "light",
    "img": "/images/logos/openprices/op-favicon.svg",
    "svg": "/images/logos/openprices/op-favicon.svg",
    "png": None,
    "keywords": "open prices favicon icon tag brand vector svg"
})

# Nutri-Score
for grade in ["a", "b", "c", "d", "e"]:
    assets.append({
        "title": f"Nutri-Score Grade {grade.upper()} (Version 2)",
        "topic": "nutriscore",
        "topic_label": "🥗 Nutri-Score",
        "color": "color",
        "format": "svg",
        "bg": "light",
        "img": f"https://static.openfoodfacts.org/images/attributes/dist/nutriscore-{grade}.svg",
        "svg": f"https://static.openfoodfacts.org/images/attributes/dist/nutriscore-{grade}.svg",
        "png": None,
        "keywords": f"nutri-score nutriscore grade {grade} nutrition label score v2 vector svg"
    })

# Green-Score / Eco-Score
for grade in ["a", "b", "c", "d", "e"]:
    assets.append({
        "title": f"Green-Score Grade {grade.upper()}",
        "topic": "greenscore",
        "topic_label": "🌱 Green-Score",
        "color": "color",
        "format": "svg",
        "bg": "light",
        "img": f"https://static.openfoodfacts.org/images/attributes/dist/green-score-{grade}.svg",
        "svg": f"https://static.openfoodfacts.org/images/attributes/dist/green-score-{grade}.svg",
        "png": None,
        "keywords": f"green-score ecoscore eco-score grade {grade} environmental impact score leaf vector svg"
    })

assets.append({
    "title": "Eco-Score Leaf Icon",
    "topic": "greenscore",
    "topic_label": "🌱 Green-Score",
    "color": "color",
    "format": "svg",
    "bg": "light",
    "img": "https://static.openfoodfacts.org/images/icons/ecoscore-a.svg",
    "svg": "https://static.openfoodfacts.org/images/icons/ecoscore-a.svg",
    "png": None,
    "keywords": "ecoscore green-score leaf icon environment vector svg"
})

# UN SDG
sdgs = [
    (3, "Good Health and Well-being"),
    (12, "Responsible Consumption and Production"),
    (13, "Climate Action"),
    (14, "Life Below Water"),
    (15, "Life on Land"),
    (17, "Partnerships for the Goals"),
]
for num, name in sdgs:
    s_num = f"{num:02d}"
    assets.append({
        "title": f"UN SDG #{num} – {name}",
        "topic": "sdg",
        "topic_label": "🇺🇳 UN SDG",
        "color": "color",
        "format": "png",
        "bg": "light",
        "img": f"https://world.openfoodfacts.org/images/illustrations/un-sdg-logos/EN_SDG_Goals_{s_num}.png",
        "svg": None,
        "png": f"https://world.openfoodfacts.org/images/illustrations/un-sdg-logos/EN_SDG_Goals_{s_num}.png",
        "keywords": f"un sdg goal {num} {name} sustainable development goals united nations"
    })

# Mobile App
assets.append({
    "title": "Open Food Facts Mobile App Screenshots (English, Light Mode)",
    "topic": "app",
    "topic_label": "📱 Mobile App",
    "color": "color",
    "format": "png",
    "bg": "light",
    "img": "/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png",
    "svg": None,
    "png": "/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png",
    "keywords": "open food facts mobile app screenshots english light mode scanner iphone android"
})
assets.append({
    "title": "Open Food Facts Mobile App Screenshots (French, Light Mode)",
    "topic": "app",
    "topic_label": "📱 Mobile App",
    "color": "color",
    "format": "png",
    "bg": "light",
    "img": "/images/misc/mobileapp/new_openfoodfacts_app_fr_light_3_screenshots.png",
    "svg": None,
    "png": "/images/misc/mobileapp/new_openfoodfacts_app_fr_light_3_screenshots.png",
    "keywords": "open food facts application mobile captures ecran francais light mode"
})
for icon_name, icon_title in [
    ("barcodereader.svg", "Barcode Scanner Icon"),
    ("eating-for-the-planet.svg", "Eating for the Planet Icon"),
    ("equivalents.svg", "Product Equivalents Icon"),
    ("ultra-processing.svg", "Ultra-Processing NOVA Icon"),
    ("privacy-by-design.svg", "Privacy by Design Icon"),
]:
    assets.append({
        "title": f"App Feature: {icon_title}",
        "topic": "app",
        "topic_label": "📱 Mobile App",
        "color": "color",
        "format": "svg",
        "bg": "light",
        "img": f"/images/misc/mobileapp/features/{icon_name}",
        "svg": f"/images/misc/mobileapp/features/{icon_name}",
        "png": None,
        "keywords": f"app feature {icon_title} {icon_name} mobile smooth vector svg"
    })

# Podcast
assets.append({
    "title": "Listen on Spotify Vector Badge",
    "topic": "podcast",
    "topic_label": "🎙️ Podcast",
    "color": "color",
    "format": "svg",
    "bg": "dark",
    "img": "/images/cop26/podcast/spotify.svg",
    "svg": "/images/cop26/podcast/spotify.svg",
    "png": None,
    "keywords": "listen on spotify badge vector svg podcast audio music green-score"
})
assets.append({
    "title": "Green-Score Podcast Cover (English)",
    "topic": "podcast",
    "topic_label": "🎙️ Podcast",
    "color": "color",
    "format": "png",
    "bg": "light",
    "img": "https://static.openfoodfacts.org/images/cop26/podcast/podcast-thumbnail-en.jpg",
    "svg": None,
    "png": "https://static.openfoodfacts.org/images/cop26/podcast/podcast-thumbnail-en.jpg",
    "keywords": "green-score podcast cover english cop26 audio interview planet progress"
})
assets.append({
    "title": "Green-Score Podcast Cover (French)",
    "topic": "podcast",
    "topic_label": "🎙️ Podcast",
    "color": "color",
    "format": "png",
    "bg": "light",
    "img": "https://static.openfoodfacts.org/images/cop26/podcast/podcast-thumbnail-fr.jpg",
    "svg": None,
    "png": "https://static.openfoodfacts.org/images/cop26/podcast/podcast-thumbnail-fr.jpg",
    "keywords": "green-score podcast couverture francais cop26 audio interview"
})

assets_json = json.dumps(assets, ensure_ascii=False)

html = f"""<style>
.media-assets-header {{
  margin: 1.5rem 0 2rem;
}}
.topic-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin: 1.5rem 0;
}}
.chip-btn {{
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}}
.chip-btn:hover, .chip-btn.active {{
  background: #341100;
  color: #ffffff;
  border-color: #341100;
}}
.media-filter-bar {{
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: center;
  margin: 1.5rem 0 2rem;
  padding: 1.25rem;
  background: #f8fafc;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}}
.media-search-input {{
  min-width: 260px;
  flex: 1 1 260px;
  margin: 0 !important;
  padding: 0.5rem 0.9rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  font-size: 0.95rem !important;
}}
.media-filter-group {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}
.media-filter-group label {{
  font-weight: 600;
  margin: 0;
  color: #334155;
  font-size: 0.9rem;
  white-space: nowrap;
}}
.media-filter-group select {{
  margin: 0 !important;
  padding: 0.45rem 0.8rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  background-color: #fff !important;
  font-size: 0.9rem !important;
  cursor: pointer;
}}
.media-stats {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}}
.media-count {{
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
}}
.media-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}}
.media-card {{
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #ffffff;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.media-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}}
.media-card.dark-card {{
  background: #18181b;
  border-color: #27272a;
  color: #f4f4f5;
}}
.media-card.dark-card .media-title {{
  color: #f4f4f5;
}}
.media-topic-tag {{
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  background: #e2e8f0;
  color: #475569;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.media-card.dark-card .media-topic-tag {{
  background: #27272a;
  color: #a1a1aa;
}}
.media-preview-box {{
  width: 100%;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  border-radius: 10px;
  background: #f8fafc;
  margin-bottom: 1rem;
}}
.media-card.dark-card .media-preview-box {{
  background: #09090b;
}}
.media-preview-box img {{
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}}
.media-title {{
  font-size: 0.92rem;
  font-weight: 600;
  margin: 0 0 1rem;
  line-height: 1.35;
  min-height: 2.7em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.media-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: auto;
}}
.media-download-btn {{
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px;
  margin: 0 !important;
  font-size: 0.85rem !important;
  padding: 0.4rem 0.8rem !important;
  border-radius: 8px !important;
  vertical-align: middle;
}}
.media-download-btn .material-icons {{
  font-size: 1.1rem;
  vertical-align: middle;
}}
</style>

<div class="media-assets-header text-center">
  <h1 class="title-2 emphasized-title">📁 Open Food Facts Media Assets Library</h1>
  <h4 class="subheader">Search, filter, and download brand assets, logos, and visuals across all Open Food Facts projects</h4>
</div>

<div class="topic-chips">
  <button type="button" class="chip-btn active" onclick="selectChip(this, 'all')">All Assets</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'openfoodfacts')">🍊 Open Food Facts</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'openbeautyfacts')">🧴 Open Beauty Facts</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'openpetfoodfacts')">🐾 Open Pet Food Facts</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'openproductsfacts')">📸 Open Products Facts</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'openprices')">🏷️ Open Prices</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'nutriscore')">🥗 Nutri-Score</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'greenscore')">🌱 Green-Score</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'sdg')">🇺🇳 UN SDG</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'app')">📱 Mobile App</button>
  <button type="button" class="chip-btn" onclick="selectChip(this, 'podcast')">🎙️ Podcast</button>
</div>

<div class="media-filter-bar">
  <input type="search" id="searchInput" class="media-search-input" placeholder="🔍 Search assets by keyword, brand, format..." oninput="applyFilters()">
  
  <div class="media-filter-group">
    <label for="topicSelect">Topic:</label>
    <select id="topicSelect" onchange="onTopicSelectChange()">
      <option value="all">All Topics</option>
      <option value="openfoodfacts">Open Food Facts</option>
      <option value="openbeautyfacts">Open Beauty Facts</option>
      <option value="openpetfoodfacts">Open Pet Food Facts</option>
      <option value="openproductsfacts">Open Products Facts</option>
      <option value="openprices">Open Prices</option>
      <option value="nutriscore">Nutri-Score</option>
      <option value="greenscore">Green-Score / Eco-Score</option>
      <option value="sdg">UN SDG</option>
      <option value="app">Mobile App</option>
      <option value="podcast">Podcast</option>
    </select>
  </div>

  <div class="media-filter-group">
    <label for="colorSelect">Color:</label>
    <select id="colorSelect" onchange="applyFilters()">
      <option value="all">All Colors</option>
      <option value="color">Full Color</option>
      <option value="bw">Black & White / Monochrome</option>
    </select>
  </div>

  <div class="media-filter-group">
    <label for="formatSelect">Format:</label>
    <select id="formatSelect" onchange="applyFilters()">
      <option value="all">All Formats</option>
      <option value="svg">SVG (Vector)</option>
      <option value="png">PNG / JPG (Raster)</option>
    </select>
  </div>

  <div class="media-filter-group">
    <label for="sortSelect">Sort:</label>
    <select id="sortSelect" onchange="applyFilters()">
      <option value="default">Topic (Default)</option>
      <option value="az">Name (A-Z)</option>
      <option value="za">Name (Z-A)</option>
    </select>
  </div>
</div>

<div class="media-stats">
  <div class="media-count" id="mediaCount">Showing {len(assets)} of {len(assets)} assets</div>
  <button type="button" class="button secondary small" onclick="resetFilters()" style="margin: 0;">Reset Filters</button>
</div>

<div class="media-grid" id="mediaGrid"></div>

<div class="row text-center" style="margin: 3rem 0;">
  <div class="large-12 columns">
    <a href="/press" class="button secondary small">← Back to Press Page</a>
  </div>
</div>

<script>
const ALL_ASSETS = {assets_json};

function renderCards(list) {{
  const grid = document.getElementById("mediaGrid");
  if (!list.length) {{
    grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem;">No assets found matching your criteria. Try resetting filters.</div>';
    return;
  }}

  grid.innerHTML = list.map(item => {{
    const isDark = item.bg === "dark";
    const darkClass = isDark ? " dark-card" : "";
    const fname = item.title.replace(/[^a-zA-Z0-9_-]/g, "_");
    
    const btns = [];
    if (item.svg) {{
      btns.push('<a class="button round small media-download-btn" download="' + fname + '.svg" href="' + item.svg + '" target="_blank" rel="noopener noreferrer"><span class="material-icons">download</span> SVG</a>');
    }}
    if (item.png) {{
      btns.push('<a class="button round secondary small media-download-btn" download="' + fname + '.png" href="' + item.png + '" target="_blank" rel="noopener noreferrer"><span class="material-icons">download</span> PNG</a>');
    }}

    return '<div class="media-card' + darkClass + '">' +
      '<span class="media-topic-tag">' + item.topic_label + '</span>' +
      '<div class="media-preview-box">' +
        '<img src="' + item.img + '" alt="' + item.title + '" loading="lazy">' +
      '</div>' +
      '<h3 class="media-title">' + item.title + '</h3>' +
      '<div class="media-actions">' +
        btns.join(" ") +
      '</div>' +
    '</div>';
  }}).join("");
}}

function applyFilters() {{
  const query = document.getElementById("searchInput").value.toLowerCase().trim();
  const topic = document.getElementById("topicSelect").value;
  const color = document.getElementById("colorSelect").value;
  const format = document.getElementById("formatSelect").value;
  const sort = document.getElementById("sortSelect").value;

  let filtered = ALL_ASSETS.filter(item => {{
    if (topic !== "all" && item.topic !== topic) return false;
    if (color !== "all" && item.color !== color) return false;
    if (format !== "all" && !item.format.includes(format)) return false;
    if (query) {{
      const matchText = (item.title + " " + item.keywords + " " + item.topic_label).toLowerCase();
      if (!matchText.includes(query)) return false;
    }}
    return true;
  }});

  if (sort === "az") {{
    filtered.sort((a, b) => a.title.localeCompare(b.title));
  }} else if (sort === "za") {{
    filtered.sort((a, b) => b.title.localeCompare(a.title));
  }}

  renderCards(filtered);
  document.getElementById("mediaCount").textContent = 'Showing ' + filtered.length + ' of ' + ALL_ASSETS.length + ' assets';
}}

function selectChip(btn, topic) {{
  document.querySelectorAll(".chip-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  document.getElementById("topicSelect").value = topic;
  applyFilters();
}}

function onTopicSelectChange() {{
  const topic = document.getElementById("topicSelect").value;
  document.querySelectorAll(".chip-btn").forEach(b => {{
    const onclickVal = b.getAttribute("onclick") || "";
    if (onclickVal.includes("'" + topic + "'")) {{
      b.classList.add("active");
    }} else {{
      b.classList.remove("active");
    }}
  }});
  applyFilters();
}}

function resetFilters() {{
  document.getElementById("searchInput").value = "";
  document.getElementById("topicSelect").value = "all";
  document.getElementById("colorSelect").value = "all";
  document.getElementById("formatSelect").value = "all";
  document.getElementById("sortSelect").value = "default";
  document.querySelectorAll(".chip-btn").forEach(b => {{
    if (b.getAttribute("onclick").includes("'all'")) b.classList.add("active");
    else b.classList.remove("active");
  }});
  applyFilters();
}}

document.addEventListener("DOMContentLoaded", () => renderCards(ALL_ASSETS));
if (document.readyState !== "loading") renderCards(ALL_ASSETS);
</script>
"""

with open("lang/en/texts/media-assets.html", "w", encoding="utf-8") as f:
    f.write(html.strip() + "\n")

print(f"Generated lang/en/texts/media-assets.html with {len(assets)} assets!")
