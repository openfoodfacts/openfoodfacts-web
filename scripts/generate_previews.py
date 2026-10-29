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

    # Find all /images/... references in src and srcset
    images = re.findall(r'(?:src|srcset)="(/images/[^"]+)"', content)
    unique_images = list(set(images))

    # Precompute data URIs dictionary
    data_uris = {}
    for img in unique_images:
        local_path = "html" + img
        if os.path.exists(local_path):
            data_uris[img] = get_base64_data_uri(local_path)
        else:
            print(f"Warning: {local_path} not found")

    content_relative = content
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
            <a href="preview-obf-discover.html" class="nav-switch-link {'active' if page_key == 'obf-discover' else ''}">OBF</a>
            <a href="preview-opff-discover.html" class="nav-switch-link {'active' if page_key == 'opff-discover' else ''}">OPFF</a>
            <a href="preview-opf-discover.html" class="nav-switch-link {'active' if page_key == 'opf-discover' else ''}">OPF</a>
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
