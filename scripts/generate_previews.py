#!/usr/bin/env python3
import os
import re
import base64

def get_base64_data_uri(file_path):
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    if file_path.endswith('.svg'):
        mime = 'image/svg+xml'
    elif file_path.endswith('.png'):
        mime = 'image/png'
    elif file_path.endswith('.webp'):
        mime = 'image/webp'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        mime = 'image/jpeg'
    else:
        mime = 'application/octet-stream'
    return f"data:{mime};base64,{encoded}"

PAGES = [
    ('contribute', 'lang/en/texts/contribute.html', 'Open Food Facts — Contribute Preview'),
    ('discover', 'lang/en/texts/discover.html', 'Open Food Facts — Discover Preview'),
    ('contact', 'lang/en/texts/contact.html', 'Open Food Facts — Contact Page Preview'),
    ('obf-discover', 'lang/obf/en/texts/discover.html', 'Open Beauty Facts — Discover Preview'),
    ('obf-contribute', 'lang/obf/en/texts/contribute.html', 'Open Beauty Facts — Contribute Preview'),
    ('opff-discover', 'lang/opff/en/texts/discover.html', 'Open Pet Food Facts — Discover Preview'),
    ('opff-contribute', 'lang/opff/en/texts/contribute.html', 'Open Pet Food Facts — Contribute Preview'),
    ('opf-discover', 'lang/opf/en/texts/discover.html', 'Open Products Facts — Discover Preview'),
    ('opf-contribute', 'lang/opf/en/texts/contribute.html', 'Open Products Facts — Contribute Preview'),
]

def build_preview(page_key, src_file, title):
    with open(src_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inline all animated SVG img tags directly as <svg> elements into the HTML DOM.
    # This allows CSS animation-play-state: paused/running to work 100% reliably on hover in browsers!
    def inline_animated_svg(match):
        img_tag = match.group(0)
        src_match = re.search(r'src="(/images/[^"]+)"', img_tag)
        if not src_match:
            return img_tag
        src = src_match.group(1)
        if 'animated' not in src or not src.endswith('.svg'):
            return img_tag

        local_path = "html" + src
        if not os.path.exists(local_path):
            print(f"Warning: {local_path} not found for inlining")
            return img_tag

        with open(local_path, 'r', encoding='utf-8') as sf:
            svg_text = sf.read()

        svg_text = re.sub(r'<\?xml[^>]*\?>\s*', '', svg_text)
        svg_text = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg_text)

        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        alt_val = alt_match.group(1) if alt_match else ""
        class_match = re.search(r'class="([^"]*)"', img_tag)
        class_val = class_match.group(1) if class_match else ""
        width_match = re.search(r'width="([^"]*)"', img_tag)
        width_val = width_match.group(1) if width_match else ""
        height_match = re.search(r'height="([^"]*)"', img_tag)
        height_val = height_match.group(1) if height_match else ""

        def patch_root_svg(root_m):
            tag = root_m.group(0)
            # Remove hardcoded width and height attributes so SVG respects CSS flex/grid max-height/max-width
            tag = re.sub(r'\s+(width|height)="[^"]*"', '', tag)
            if alt_val and 'aria-label' not in tag:
                tag = tag[:-1] + f' role="img" aria-label="{alt_val}">'
            if class_val:
                if 'class="' in tag:
                    tag = re.sub(r'class="([^"]*)"', rf'class="\1 {class_val}"', tag)
                else:
                    tag = tag[:-1] + f' class="{class_val}">'
            return tag

        svg_text = re.sub(r'<svg[^>]*>', patch_root_svg, svg_text, count=1)
        return svg_text

    content_inlined = re.sub(r'<img[^>]+>', inline_animated_svg, content)

    # 2. For remaining static images (PNGs, WebP, non-animated SVGs), convert src to data URIs
    images = re.findall(r'(?:src|srcset)="(/images/[^"]+)"', content_inlined)
    unique_images = list(set(images))

    data_uris = {}
    for img in unique_images:
        local_path = "html" + img
        if os.path.exists(local_path):
            data_uris[img] = get_base64_data_uri(local_path)
        else:
            print(f"Warning: {local_path} not found")

    content_relative = content_inlined
    for img in unique_images:
        if img in data_uris:
            content_relative = content_relative.replace(f'src="{img}"', f'src="{data_uris[img]}"')
            content_relative = content_relative.replace(f'srcset="{img}"', f'srcset="{data_uris[img]}"')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400&family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1f2937;
        }}
        /* Global animation play-state rule: ALL SVGs PAUSED by default, RUN ONLY on hover */
        svg, svg * {{
            animation-play-state: paused !important;
        }}
        .off-feature-card:hover svg, .off-feature-card:hover svg *,
        .expert-banner:hover svg, .expert-banner:hover svg *,
        .contribute-hero:hover svg, .contribute-hero:hover svg *,
        .discover-hero:hover svg, .discover-hero:hover svg *,
        .contact-hero:hover svg, .contact-hero:hover svg *,
        .contact-card:hover svg, .contact-card:hover svg *,
        .hero-media:hover svg, .hero-media:hover svg *,
        .opff-hero:hover svg, .opff-hero:hover svg *,
        .obf-hero:hover svg, .obf-hero:hover svg *,
        .opf-hero:hover svg, .opf-hero:hover svg *,
        svg:hover, svg:hover * {{
            animation-play-state: running !important;
        }}
        @media (prefers-reduced-motion: reduce) {{
            svg, svg * {{
                animation: none !important;
            }}
        }}
        /* Strictly constrain card art and prevent any SVG/image overflow */
        .off-card-art {{
            height: 160px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: hidden !important;
            position: relative !important;
            margin-bottom: 1.25rem !important;
        }}
        .off-card-art img,
        .off-card-art svg {{
            max-width: 100% !important;
            max-height: 140px !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
            display: block !important;
            margin: 0 auto !important;
            transition: transform 0.3s ease !important;
        }}
        .off-feature-card:hover .off-card-art img,
        .off-feature-card:hover .off-card-art svg {{
            transform: scale(1.05) !important;
        }}
        .expert-banner-art img,
        .expert-banner-art svg {{
            max-width: 280px !important;
            max-height: 200px !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
        }}
        .hero-media img,
        .hero-media svg {{
            max-width: 440px !important;
            max-height: 340px !important;
            width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }}
        /* Simulated Site Header */
        .site-header-preview {{
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 0.85rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .site-header-left {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }}
        .site-header-title {{
            font-weight: 700;
            font-size: 0.95rem;
            color: #334155;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .preview-badge {{
            background: #ea580c;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .site-header-right {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .nav-switch-link {{
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748b;
            text-decoration: none;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            transition: all 0.15s;
        }}
        .nav-switch-link:hover {{
            background: #f1f5f9;
            color: #0f172a;
        }}
        .nav-switch-link.active {{
            background: #e2e8f0;
            color: #0f172a;
            font-weight: 700;
        }}
        .main-container {{
            max-width: 1240px;
            margin: 0 auto;
            padding: 1.5rem 1rem 3rem;
        }}
    </style>
</head>
<body>

    <header class="site-header-preview">
        <div class="site-header-left">
            <div class="site-header-title">
                <span>🌐 {title}</span>
                <span class="preview-badge">Revamped</span>
            </div>
        </div>
        <div class="site-header-right">
            <a href="preview-discover.html" class="nav-switch-link {'active' if page_key == 'discover' else ''}">OFF Discover</a>
            <a href="preview-contribute.html" class="nav-switch-link {'active' if page_key == 'contribute' else ''}">OFF Contribute</a>
            <a href="preview-contact.html" class="nav-switch-link {'active' if page_key == 'contact' else ''}">Contact</a>
            <a href="preview-obf-discover.html" class="nav-switch-link {'active' if page_key == 'obf-discover' else ''}">OBF Discover</a>
            <a href="preview-obf-contribute.html" class="nav-switch-link {'active' if page_key == 'obf-contribute' else ''}">OBF Contribute</a>
            <a href="preview-opff-discover.html" class="nav-switch-link {'active' if page_key == 'opff-discover' else ''}">OPFF Discover</a>
            <a href="preview-opff-contribute.html" class="nav-switch-link {'active' if page_key == 'opff-contribute' else ''}">OPFF Contribute</a>
            <a href="preview-opf-discover.html" class="nav-switch-link {'active' if page_key == 'opf-discover' else ''}">OPF Discover</a>
            <a href="preview-opf-contribute.html" class="nav-switch-link {'active' if page_key == 'opf-contribute' else ''}">OPF Contribute</a>
        </div>
    </header>

    <main class="main-container">
{content_relative}
    </main>

</body>
</html>
"""
    out_file = f"preview-{page_key}.html"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {out_file} successfully ({len(html)} bytes)")
    return out_file

if __name__ == '__main__':
    for key, path, title in PAGES:
        build_preview(key, path, title)
