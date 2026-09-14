#!/usr/bin/env python3
"""
Fix outdated logos, broken/translated includes, and formatting in lang/*/texts/press.html.
"""
import os
import re
import glob

BUTTON_FLEX_CSS = """/* Ensure all download buttons and icon buttons across the entire page align vertically */
#app-landing-page .button,
.button,
a.button,
.download_image__button,
.homepage-greeter__button {
	display: inline-flex !important;
	align-items: center !important;
	justify-content: center !important;
	gap: 6px;
	vertical-align: middle;
}

#app-landing-page .button .material-icons,
.button .material-icons,
a.button .material-icons,
.download_image__button .material-icons,
.homepage-greeter__button .material-icons {
	display: inline-flex !important;
	align-items: center !important;
	justify-content: center !important;
	vertical-align: middle !important;
	font-size: 18px;
	line-height: 1 !important;
	margin: 0 !important;
}"""

def get_nutri_lang(lang_code):
    if lang_code in ('fr', 'fr_FR', 'fr_BE', 'fr_CH'):
        return 'fr'
    elif lang_code in ('de', 'de_DE', 'de_CH', 'de_AT'):
        return 'de'
    elif lang_code in ('nl', 'nl_BE', 'nl_NL'):
        return 'nl'
    elif lang_code in ('lb', 'lu'):
        return 'lu'
    return 'en'

def get_mobile_img(lang_code):
    if lang_code in ('fr', 'fr_FR', 'fr_BE', 'fr_CH'):
        return '/images/misc/mobileapp/new_openfoodfacts_app_fr_light_3_screenshots.png'
    return '/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png'

def fix_standard_press_file(content, lang_code):
    nutri_lang = get_nutri_lang(lang_code)
    mobile_img = get_mobile_img(lang_code)

    # 1. Top style CSS
    if '/* Ensure all download buttons' not in content:
        content = content.replace('#app-landing-page .button {', BUTTON_FLEX_CSS + '\n\n#app-landing-page .button {')

    # 2. Material icons: restore 'download' inside class="material-icons"
    content = re.sub(r'<span class=([\'"])material-icons\1>[^<]*</span>', r'<span class="material-icons">download</span>', content)

    # 3. Block 3 Key facts include
    def fix_block_3(m):
        block = m.group(0)
        # replace any [[...]] inside with [[texts/keyfacts.html]]
        block = re.sub(r'\[\[.*?\]\]', '[[texts/keyfacts.html]]', block)
        return block
    content = re.sub(r'<div class="block block-seashell" id="block-3">.*?</div>\s*</div>\s*</div>', fix_block_3, content, flags=re.DOTALL)

    # 4. Block 4 Numbers include
    def fix_block_4(m):
        part = m.group(0)
        part = re.sub(r'\[\[.*?\]\]', '[[texts/numbers-selected.html]]', part)
        return part
    content = re.sub(r'<div id="numbers"></div>.*?<div class="block block-light-green" id="block-5">', fix_block_4, content, flags=re.DOTALL)

    # 5. Block 5 Press releases include (end of block 5)
    def fix_block_5(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]\s*</div>\s*<div class="block block-blue" id="block-6">', '[[texts/presskit_other_languages.html]]\n</div>\n\n<div class="block block-blue" id="block-6">', block)
        return block
    content = re.sub(r'<div class="block block-light-green" id="block-5">.*?<div class="block block-blue" id="block-6">', fix_block_5, content, flags=re.DOTALL)

    # 6. Block 6 Media kit
    def fix_block_6(m):
        block = m.group(0)
        # Add media assets button if not present
        if '/media-assets' not in block:
            media_btn = '\n\t<div style="margin: 15px 0 20px;">\n\t\t<a class="button" href="/media-assets" style="background-color: #2e7d32 !important; color: #ffffff !important; font-size: 1.05rem; padding: 10px 22px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">✨ All Media Assets (Search &amp; Filter Browser)</a>\n\t</div>\n'
            block = block.replace('<div id="openfoodfacts-logos"></div>', '<div id="openfoodfacts-logos"></div>' + media_btn)

        # Fix ecoscore include under #ecoscore-logos
        ecoscore_pattern = r'(<div id="ecoscore-logos"></div>\s*(?:<!--.*?-->\s*)?<div class="text-center">)\[\[.*?\]\](</div>)'
        block = re.sub(ecoscore_pattern, r'\1[[texts/cop26/blocks/new-ecoscore-presskit.html]]\2', block, flags=re.DOTALL)

        # Fix UN SDG include under #un-sdg
        sdg_pattern = r'(<div id="un-sdg"></div>\s*<div class="text-center">)\[\[.*?\]\](</div>)'
        block = re.sub(sdg_pattern, r'\1[[texts/cop26/blocks/un-sustainable-development-goals.html]]\2', block, flags=re.DOTALL)

        # Fix nutriscore section under #nutriscore-logos
        nutri_replacement = f'''<div id="nutriscore-logos"></div>
	<div class="text-center">[[texts/presskit-nutriscore-logos.html]]
	
	[[texts/presskit-nutriscore-logos-horizontal-color.html]]
[[texts/presskit-nutriscore-logos-{nutri_lang}.html]]
	</div>'''
        nutri_pattern = r'<div id="nutriscore-logos"></div>\s*<div class="text-center">.*?</div>\s*</div>\s*</div>'
        block = re.sub(nutri_pattern, nutri_replacement + '\n</div>\n</div>', block, flags=re.DOTALL)

        return block
    content = re.sub(r'<div class="block block-blue" id="block-6">.*?<div class="block block-seashell" id="block-7">', fix_block_6, content, flags=re.DOTALL)

    # 7. Block 7 Newsletter
    def fix_block_7(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]', '[[texts/sendinblue.html]]', block)
        return block
    content = re.sub(r'<div class="block block-seashell" id="block-7">.*?<div class="block block-yellow" id="block-8">', fix_block_7, content, flags=re.DOTALL)

    # 8. Block 8 Selection
    def fix_block_8(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]\s*(<br>\s*<style>)', r'[[texts/presskit_selection.html]]\n\1', block)
        return block
    content = re.sub(r'<div class="block block-yellow" id="block-8">.*?<div class="block block-light-green" id="block-9">', fix_block_8, content, flags=re.DOTALL)

    # 9. Block 9 Contacts
    def fix_block_9(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]', '[[texts/contacts.html]]', block, count=1)
        return block
    content = re.sub(r'<div class="block block-light-green" id="block-9">.*?<div class="block block-blue" id="block-10">', fix_block_9, content, flags=re.DOTALL)

    # 10. Block 11 Screenshots
    def fix_block_11(m):
        block = m.group(0)
        title_m = re.search(r'<h2 class="title-2 emphasized-title">([^<]*)</h2>', block)
        title = title_m.group(1) if title_m else "Screenshots of the Open Food Facts mobile app"
        subheader_m = re.search(r'<h4 class="subheader">([^<]+)</h4>', block)
        subheader = subheader_m.group(1).strip() if subheader_m and subheader_m.group(1).strip() else "Visuals showcasing the modern mobile app on iOS and Android."

        new_block = f'''<div class="block block-white" id="block-11">
<!-- Block 11 -->
<div id="mobile-screenshots"></div>
<div class="row text-center">
	<div class="large-12 columns">
		<h2 class="title-2 emphasized-title">{title}</h2>
		<h4 class="subheader">{subheader}</h4>
	</div>
</div>

<div class="row text-center" style="margin: 20px 0;">
	<div class="large-12 columns">
		<a href="{mobile_img}" target="_blank" rel="noopener noreferrer">
			<img src="{mobile_img}" alt="{title}" style="max-width: 900px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
		</a>
	</div>
</div>

<div class="row text-center" style="margin-top: 15px;">
	<div class="large-12 columns">
		<a class="button small" href="{mobile_img}" download><span class="material-icons" style="vertical-align: middle; font-size: 18px;">download</span> Download 3-screen showcase (PNG)</a>&nbsp;
		<a class="button small" href="/open-food-facts-mobile-app">📱 Open Food Facts Mobile App</a>&nbsp;
		<a class="button small" href="https://github.com/openfoodfacts/smooth-app" target="_blank" rel="noopener noreferrer">💻 Mobile App on GitHub</a>&nbsp;
		<a class="button small" href="/media-assets?topic=mobileapp">📁 View all mobile app assets</a>
	</div>
</div>
</div>'''
        return new_block
    content = re.sub(r'<div class="block block-white" id="block-11">.*?</div>\s*<div class="block block-blue" id="block-12">', lambda m: fix_block_11(m) + '\n<div class="block block-blue" id="block-12">', content, flags=re.DOTALL)

    # 11. Block 12 Green-Score
    def fix_block_12(m):
        block = m.group(0)
        title_m = re.search(r'<h2 class="title-2 emphasized-title">([^<]*)</h2>', block)
        title = title_m.group(1) if title_m else "Green-Score resources"
        subheader_m = re.search(r'<h4 class="subheader">([^<]+)</h4>', block)
        subheader = subheader_m.group(1).strip() if subheader_m and subheader_m.group(1).strip() else "Visuals, data, and information on the environmental impact score."

        new_block = f'''<div class="block block-blue" id="block-12">
<!-- Block 12 -->
<div id="greenscore"></div>
<div class="row text-center">
	<div class="large-12 columns">
		<h2 class="title-2 emphasized-title">{title}</h2>
		<h4 class="subheader">{subheader}</h4>
	</div>
</div>

[[texts/presskit-greenscore.html]]
</div>'''
        return new_block
    content = re.sub(r'<div class="block block-blue" id="block-12">.*?</div>\s*<div class="block block-seashell" id="block-13">', lambda m: fix_block_12(m) + '\n<div class="block block-seashell" id="block-13">', content, flags=re.DOTALL)

    # 12. Block 13 Podcast
    def fix_block_13(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]', '[[texts/cop26/blocks/google-podcast.html]]', block)
        return block
    content = re.sub(r'<div class="block block-seashell" id="block-13">.*?<div class="block block-yellow" id="block-14">', fix_block_13, content, flags=re.DOTALL)

    # 13. Block 14 Blog
    def fix_block_14(m):
        block = m.group(0)
        rss_centered = '''<div style="display: flex; justify-content: center; align-items: center; margin: 1.5rem auto; text-align: center;">
[[texts/presskit-rss.html]]
</div>
</div>'''
        block = re.sub(r'(?:<div[^>]*>)?\s*\[\[.*?\]\][^<]*?(?:</div>)?\s*</div>\s*<div class="block block-light-green" id="block-15">', rss_centered + '\n\n<div class="block block-light-green" id="block-15">', block)
        return block
    content = re.sub(r'<div class="block block-yellow" id="block-14">.*?<div class="block block-light-green" id="block-15">', fix_block_14, content, flags=re.DOTALL)

    # 14. Block 15 App visuals
    def fix_block_15(m):
        block = m.group(0)
        block = re.sub(r'\[\[.*?\]\]', '[[texts/app-visuals.html]]', block)
        return block
    content = re.sub(r'<div class="block block-light-green" id="block-15">.*', fix_block_15, content, flags=re.DOTALL)

    return content

def fix_ancient_press_file(lang_code, en_template):
    nutri_lang = get_nutri_lang(lang_code)
    mobile_img = get_mobile_img(lang_code)
    content = en_template
    if nutri_lang != 'en':
        content = content.replace('[[texts/presskit-nutriscore-logos-en.html]]', f'[[texts/presskit-nutriscore-logos-{nutri_lang}.html]]')
    if mobile_img != '/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png':
        content = content.replace('/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png', mobile_img)
    return content

def main():
    with open('lang/en/texts/press.html', 'r', encoding='utf-8') as f:
        en_template = f.read()

    press_files = sorted(glob.glob('lang/*/texts/press.html'))
    print(f"Total files to inspect: {len(press_files)}")

    updated = 0
    ancient_upgraded = 0

    for pf in press_files:
        lang = pf.split('/')[1]
        if lang in ('en', 'fr'):  # en and fr already updated and hand-crafted
            continue

        with open(pf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        line_count = len(content.splitlines())
        if line_count < 300:
            new_content = fix_ancient_press_file(lang, en_template)
            ancient_upgraded += 1
        else:
            new_content = fix_standard_press_file(content, lang)

        if new_content != content:
            with open(pf, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated += 1

    print(f"Done! Updated {updated} files (including {ancient_upgraded} ancient files upgraded).")

if __name__ == '__main__':
    main()
