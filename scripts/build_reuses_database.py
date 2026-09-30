#!/usr/bin/env python3
"""
Merge and enrich reusers database from existing reuses.json, CSV 2 (internal reusers DB),
and CSV 1 (community form submissions).
"""

import csv
import json
import os
import re
from urllib.parse import urlparse

EXISTING_PATH = "data/reuses.json"
CSV1_PATH = "/Users/pierre/.gemini/antigravity/brain/52ca4d29-a4b8-4f27-b5de-6a2a18ab2e76/.user_uploaded/media_1789124244690.csv"
CSV2_PATH = "/Users/pierre/.gemini/antigravity/brain/52ca4d29-a4b8-4f27-b5de-6a2a18ab2e76/.user_uploaded/media_1789124263103.csv"

VALID_TLDS = {
    'com', 'org', 'net', 'io', 'app', 'fr', 'de', 'eu', 'es', 'it', 'uk', 'co', 'me', 'dev',
    'ai', 'ch', 'be', 'nl', 'pl', 'cz', 'in', 'br', 'info', 'site', 'online', 'tech', 'xyz',
    'eco', 'world', 'link', 'page', 'pt', 'at', 'dk', 'se', 'no', 'fi', 'ca', 'au', 'nz'
}

JUNK_NAMES = {
    'test', 'test app', 'testing', 'asdf', 'n/a', 'none', 'no name', 'app', 'wip :)', 'not decided yet',
    'undefined', 'null', 'unknown', 'xxx', 'my app', 'demo', 'tbd', 'sample', 'web scrapping', 'wip',
    'foo', 'bar', 'test1', 'test2', 'aaa', 'bbb', 'idk', 'untitled'
}

def is_junk_name(name):
    if not name or len(name.strip()) < 2:
        return True
    n = name.strip().lower()
    if n in JUNK_NAMES:
        return True
    if re.match(r'^(test|demo|temp|wip|sample)\s*\d*$', n):
        return True
    return False

def parse_and_validate_url(val):
    if not val or not isinstance(val, str):
        return None, None
    val = val.strip()
    if ' ' in val or '\n' in val or '\t' in val:
        return None, None
        
    # Check if package id like com.example.app
    if re.match(r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)+$', val):
        parts = val.split('.')
        if parts[0] in ('com', 'org', 'net', 'de', 'fr', 'io', 'es', 'it') and len(parts) >= 3:
            return 'play', f'https://play.google.com/store/apps/details?id={val}'
            
    if not val.startswith(('http://', 'https://')):
        if '.' in val and not val.startswith('mailto:'):
            val = 'https://' + val
        else:
            return None, None
            
    try:
        p = urlparse(val)
        host = p.netloc.lower()
        if not host: return None, None
        if host.startswith('www.'): host = host[4:]
        if 'localhost' in host or '127.0.0.1' in host: return None, None
        parts = host.split('.')
        if len(parts) < 2: return None, None
        tld = parts[-1]
        if tld not in VALID_TLDS and len(tld) > 4: return None, None
        
        # Block generic domains without repo / subpath
        if host in ('google.com', 'github.com', 'gitlab.com', 'codeberg.org') and len(p.path.strip('/')) == 0:
            return None, None
            
        if 'play.google.com' in host:
            return 'play', val
        elif 'apps.apple.com' in host or 'itunes.apple.com' in host:
            return 'apple', val
        elif 'f-droid.org' in host:
            return 'fdroid', val
        elif 'github.com' in host or 'gitlab.com' in host or 'codeberg.org' in host:
            return 'github', val
        else:
            return 'web', val
    except:
        return None, None

def extract_play_id(url):
    if not url: return ''
    m = re.search(r'id=([a-zA-Z0-9._]+)', url)
    return m.group(1).lower() if m else ''

def extract_apple_id(url):
    if not url: return ''
    m = re.search(r'id(\d+)', url)
    return m.group(1) if m else ''

def norm_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def extract_domain(url):
    if not url: return ''
    if not url.startswith('http'): url = 'https://' + url
    try:
        h = urlparse(url).netloc.lower()
        if h.startswith('www.'): h = h[4:]
        return h
    except:
        return ''

def map_theme(topic_str, text_str=''):
    s = (topic_str + ' ' + text_str).lower()
    if any(w in s for w in ['allergi', 'allergen', 'gluten', 'intoleran', 'celiac', 'lactose', 'fodmap']):
        return 'allergies'
    if any(w in s for w in ['ecolog', 'waste', 'gaspillage', 'climat', 'carbon', 'planet', 'recycl', 'packag']):
        return 'environment'
    if any(w in s for w in ['cosmetic', 'beauty', 'peau', 'ingredient', 'inci']):
        return 'nutrition'
    if any(w in s for w in ['research', 'scien', 'study', 'etude', 'inrae', 'inserm', 'university', 'stat']):
        return 'research'
    if any(w in s for w in ['trace', 'origin', 'local', 'provenance', 'geography', 'terroir']):
        return 'traceability'
    if any(w in s for w in ['pantry', 'frigo', 'fridge', 'inventory', 'stock', 'supply', 'shop', 'list', 'tool', 'barcode', 'ean', 'scanner']):
        return 'tools'
    return 'nutrition'

def map_project(name, topic_str, text_str=''):
    s = (name + ' ' + topic_str + ' ' + text_str).lower()
    if any(w in s for w in ['beauty', 'cosmetic', 'cosmétique', 'maquillage', 'shampoo', 'inci']):
        return 'openbeautyfacts'
    if any(w in s for w in ['pet', 'dog', 'cat', 'croquette', 'chien', 'chat', 'animal']):
        return 'openpetfoodfacts'
    if any(w in s for w in ['hardware', 'gadget', 'product', 'produit non alimentaire']):
        return 'openproductsfacts'
    return 'openfoodfacts'

def map_country(area_str):
    s = area_str.lower().strip()
    if not s or s in ('no', 'non', 'n/a', 'global', 'worldwide', 'all', 'world', 'everywhere'):
        return 'global', 'Worldwide'
    if any(w in s for w in ['france', 'fr', 'français']):
        return 'fra', 'France'
    if any(w in s for w in ['united states', 'usa', 'us', 'america']):
        return 'usa', 'United States'
    if any(w in s for w in ['germany', 'deutschland', 'de']):
        return 'deu', 'Germany'
    if any(w in s for w in ['spain', 'españa', 'es']):
        return 'esp', 'Spain'
    if any(w in s for w in ['united kingdom', 'uk', 'great britain', 'england']):
        return 'gbr', 'United Kingdom'
    if any(w in s for w in ['italy', 'italia', 'it']):
        return 'ita', 'Italy'
    if any(w in s for w in ['india', 'in']):
        return 'ind', 'India'
    if any(w in s for w in ['brazil', 'brasil', 'br']):
        return 'bra', 'Brazil'
    if any(w in s for w in ['poland', 'polska', 'pl']):
        return 'pol', 'Poland'
    if any(w in s for w in ['czech', 'cesko', 'cz']):
        return 'cze', 'Czech Republic'
    if any(w in s for w in ['switzerland', 'suisse', 'schweiz', 'ch']):
        return 'che', 'Switzerland'
    if any(w in s for w in ['belgium', 'belgique', 'belgie', 'be']):
        return 'bel', 'Belgium'
    if any(w in s for w in ['netherlands', 'holland', 'nl']):
        return 'nld', 'Netherlands'
    if any(w in s for w in ['europe', 'eu']):
        return 'global', 'Europe & Worldwide'
    return 'global', 'Worldwide'

def clean_name(name):
    name = name.strip()
    name = re.sub(r'^[\'"\s\-_.]+|[\'"\s\-_.]+$', '', name)
    if name.islower():
        name = name.title()
    return name

def generate_tagline(name, theme, project, desc=''):
    if desc and len(desc) < 80 and not desc.startswith('http'):
        return desc.strip()
    
    theme_taglines = {
        'nutrition': 'Food scanner & nutritional guide powered by Open Food Facts data',
        'environment': 'Eco-friendly assistant & environmental impact tracking for food',
        'allergies': 'Barcode scanner & ingredient checker for allergies and diets',
        'traceability': 'Product origin & traceability information tool',
        'research': 'Academic research and data analysis platform',
        'tools': 'Inventory, pantry, and shopping management application',
        'education': 'Educational tool and game exploring food transparency'
    }
    if project == 'openbeautyfacts':
        return 'Cosmetics & beauty product scanner using Open Beauty Facts data'
    if project == 'openpetfoodfacts':
        return 'Pet food nutrition & ingredients analyzer'
    return theme_taglines.get(theme, 'Innovative application reusing Open Food Facts data')

def run_build():
    with open(EXISTING_PATH, 'r', encoding='utf-8') as f:
        existing_list = json.load(f)
        
    master = {}
    for item in existing_list:
        k = norm_name(item['name'])
        master[k] = dict(item)
        
    print(f"Loaded {len(master)} existing verified entries.")

    # 2. Process CSV 2 (internal reusers DB)
    csv2_added = 0
    csv2_updated = 0
    if os.path.exists(CSV2_PATH):
        with open(CSV2_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for r in csv.DictReader(f):
                name = clean_name(r.get('Name', ''))
                if is_junk_name(name):
                    continue
                status = r.get('status', '').strip().lower()
                if status in ('down', 'dead', 'abandoned', 'deprecated'):
                    continue
                    
                links = {}
                for fld in ['website', 'google_store_link', 'apple_store_url']:
                    val = r.get(fld, '').strip()
                    if val:
                        t, u = parse_and_validate_url(val)
                        if t and u:
                            links[t] = u
                if not links:
                    continue
                    
                p_id = extract_play_id(links.get('play'))
                a_id = extract_apple_id(links.get('apple'))
                n_key = norm_name(name)
                
                match_k = None
                if n_key in master:
                    match_k = n_key
                elif p_id:
                    for k, it in master.items():
                        if extract_play_id(it.get('play_store')) == p_id:
                            match_k = k
                            break
                elif a_id:
                    for k, it in master.items():
                        if extract_apple_id(it.get('app_store')) == a_id:
                            match_k = k
                            break
                            
                if match_k:
                    csv2_updated += 1
                    it = master[match_k]
                    if links.get('web') and not it.get('website'): it['website'] = links['web']
                    if links.get('play') and not it.get('play_store'): it['play_store'] = links['play']
                    if links.get('apple') and not it.get('app_store'): it['app_store'] = links['apple']
                    if links.get('github') and not it.get('github'): it['github'] = links['github']
                    if r.get('url_icon') and not it.get('icon_url'): it['icon_url'] = r['url_icon'].strip()
                    if r.get('contributor (y/n)', '').strip().lower() == 'y':
                        it['contributes_data'] = True
                    if r.get('Photographer', '').strip() in ('Link', 'Checked'):
                        it['contributes_photos'] = True
                else:
                    csv2_added += 1
                    theme = map_theme(r.get('topic', ''), r.get('description', ''))
                    project = map_project(name, r.get('topic', ''), r.get('description', ''))
                    c_code, c_label = map_country(r.get('main_market', ''))
                    web_url = links.get('web')
                    play_url = links.get('play')
                    apple_url = links.get('apple')
                    gh_url = links.get('github')
                    
                    domain = extract_domain(web_url or play_url or apple_url or '')
                    desc = r.get('description', '').strip()
                    tagline = generate_tagline(name, theme, project, desc)
                    full_desc = desc if desc else f"{name} is an application helping consumers evaluate food products using Open Food Facts open database."
                    
                    is_contrib_data = r.get('contributor (y/n)', '').strip().lower() == 'y'
                    is_contrib_photos = r.get('Photographer', '').strip() in ('Link', 'Checked')
                    is_odbl = r.get('odbl_ok', '').strip().lower() in ('yes', 'y')
                    is_foss = bool(gh_url)
                    
                    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                    if not slug: slug = f'app-{len(master)}'
                    
                    master[n_key] = {
                        'id': slug,
                        'name': name,
                        'tagline': tagline,
                        'description': full_desc,
                        'theme': theme,
                        'project': project,
                        'country': c_code,
                        'country_label': c_label,
                        'domain': domain,
                        'icon_url': r.get('url_icon', '').strip() or None,
                        'website': web_url,
                        'play_store': play_url,
                        'app_store': apple_url,
                        'fdroid': None,
                        'github': gh_url,
                        'contributes_data': is_contrib_data,
                        'contributes_photos': is_contrib_photos,
                        'odbl_compliant': is_odbl,
                        'open_source': is_foss,
                        'special_badge': None,
                        'featured': False,
                        'keywords': f"{name.lower()} {theme} {project} {c_label.lower()} {domain}"
                    }

    print(f"CSV 2: Added {csv2_added}, updated {csv2_updated}.")

    # 3. Process CSV 1 (form submissions)
    csv1_added = 0
    csv1_updated = 0
    if os.path.exists(CSV1_PATH):
        with open(CSV1_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for r in csv.DictReader(f):
                name = clean_name(r.get('What is the name of your app ?', ''))
                if is_junk_name(name):
                    continue
                    
                links = {}
                for fld in ['(If applicable) What is the URL of your Android app ?', '(If applicable) What is the URL of your iOS app ?']:
                    val = r.get(fld, '').strip()
                    if val:
                        t, u = parse_and_validate_url(val)
                        if t and u:
                            links[t] = u
                if not links:
                    continue
                    
                p_id = extract_play_id(links.get('play'))
                a_id = extract_apple_id(links.get('apple'))
                n_key = norm_name(name)
                
                match_k = None
                if n_key in master:
                    match_k = n_key
                elif p_id:
                    for k, it in master.items():
                        if extract_play_id(it.get('play_store')) == p_id:
                            match_k = k
                            break
                elif a_id:
                    for k, it in master.items():
                        if extract_apple_id(it.get('app_store')) == a_id:
                            match_k = k
                            break
                            
                contrib_photos_str = r.get('Users can currently contribute photos', '').strip()
                contrib_data_str = r.get('Users can currently contribute data', '').strip()
                has_contrib_photos = bool(contrib_photos_str and contrib_photos_str.lower() != 'no')
                has_contrib_data = bool(contrib_data_str and contrib_data_str.lower() != 'no')
                
                if match_k:
                    csv1_updated += 1
                    it = master[match_k]
                    if links.get('play') and not it.get('play_store'): it['play_store'] = links['play']
                    if links.get('apple') and not it.get('app_store'): it['app_store'] = links['apple']
                    if links.get('web') and not it.get('website'): it['website'] = links['web']
                    if has_contrib_photos: it['contributes_photos'] = True
                    if has_contrib_data: it['contributes_data'] = True
                else:
                    csv1_added += 1
                    topic = r.get('What topic does your app tackle ?', '')
                    theme = map_theme(topic, '')
                    project = map_project(name, topic, '')
                    c_code, c_label = map_country(r.get('Are you targeting a geographic area in particular ?', ''))
                    
                    web_url = links.get('web')
                    play_url = links.get('play')
                    apple_url = links.get('apple')
                    gh_url = links.get('github')
                    domain = extract_domain(web_url or play_url or apple_url or '')
                    
                    tagline = generate_tagline(name, theme, project, '')
                    full_desc = f"{name} is a mobile application ({c_label}) that reuses Open Food Facts data for {theme} and product evaluation."
                    
                    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                    if not slug: slug = f'app-{len(master)}'
                    
                    master[n_key] = {
                        'id': slug,
                        'name': name,
                        'tagline': tagline,
                        'description': full_desc,
                        'theme': theme,
                        'project': project,
                        'country': c_code,
                        'country_label': c_label,
                        'domain': domain,
                        'icon_url': None,
                        'website': web_url,
                        'play_store': play_url,
                        'app_store': apple_url,
                        'fdroid': None,
                        'github': gh_url,
                        'contributes_data': has_contrib_data,
                        'contributes_photos': has_contrib_photos,
                        'odbl_compliant': False,
                        'open_source': bool(gh_url),
                        'special_badge': None,
                        'featured': False,
                        'keywords': f"{name.lower()} {theme} {project} {c_label.lower()} {domain}"
                    }

    print(f"CSV 1: Added {csv1_added}, updated {csv1_updated}.")
    print(f"Total unified entries: {len(master)}")

    # Specific override for Yuka
    yuka_key = norm_name("Yuka")
    if yuka_key in master:
        yuka = master[yuka_key]
        yuka["special_badge"] = "yuka"
        yuka["odbl_compliant"] = False
        yuka["contributes_data"] = True
        yuka["contributes_photos"] = True
        yuka["tagline"] = "Scan food & cosmetics to decipher their health impact"
        yuka["description"] = (
            "Historically one of the earliest and most well-known reusers of Open Food Facts. "
            "Yuka scans food and cosmetic items to decipher their health impact. While they now maintain their own "
            "independent database and no longer use Open Food Facts ODbL data, they continue to contribute packaging photos "
            "and select product data back to Open Food Facts."
        )
        yuka["featured"] = True
        print("Updated Yuka entry with dedicated special_badge='yuka', odbl_compliant=False, and photo/data contribution flags.")

    # Sort entries: featured first, then name
    final_list = list(master.values())
    final_list.sort(key=lambda x: (not x.get('featured', False), x['name'].lower()))

    # Ensure unique IDs
    seen_ids = set()
    for item in final_list:
        base_id = item['id']
        counter = 1
        curr_id = base_id
        while curr_id in seen_ids:
            curr_id = f"{base_id}-{counter}"
            counter += 1
        item['id'] = curr_id
        seen_ids.add(curr_id)

    with open(EXISTING_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    print(f"Successfully wrote {len(final_list)} reusers to {EXISTING_PATH}")

if __name__ == '__main__':
    run_build()
