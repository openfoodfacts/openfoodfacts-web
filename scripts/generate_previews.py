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

def build_preview(page_type):
    src_file = f"lang/en/texts/{page_type}.html"
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

    title = "Contribute" if page_type == "contribute" else "Discover"

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
    <title>Open Food Facts — {title} Page Redesign Preview</title>
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
        /* Preview Banner Navigation */
        .preview-topbar {{
            background: #231206;
            color: #ffffff;
            padding: 0.75rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 99999;
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
            font-family: "Plus Jakarta Sans", sans-serif;
        }}
        .preview-topbar-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .preview-logo {{
            font-weight: 900;
            font-size: 1.15rem;
            color: #ffffff;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .preview-badge {{
            background: #ed8857;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .preview-tabs {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .preview-tab {{
            padding: 0.45rem 0.95rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 700;
            transition: all 0.2s ease;
        }}
        .preview-tab.active {{
            background: #ffffff;
            color: #231206;
        }}
        .preview-tab:not(.active) {{
            background: rgba(255,255,255,0.12);
            color: #ffd8c2;
        }}
        .preview-tab:not(.active):hover {{
            background: rgba(255,255,255,0.25);
            color: #ffffff;
        }}
        .preview-container {{
            max-width: 1280px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        /* Mock Site Header */
        .mock-site-nav {{
            max-width: 1200px;
            margin: 0 auto 1.5rem auto;
            padding: 0.75rem 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e5e7eb;
            font-size: 0.9rem;
            color: #6b7280;
        }}
        .mock-nav-links {{
            display: flex;
            gap: 1.5rem;
        }}
        .mock-nav-link {{
            color: #374151;
            text-decoration: none;
            font-weight: 600;
        }}
        .mock-nav-link:hover {{
            color: #ea580c;
        }}
    </style>
</head>
<body>

    <!-- Preview Switcher Bar -->
    <header class="preview-topbar">
        <div class="preview-topbar-left">
            <span class="preview-logo">🥗 Open Food Facts</span>
            <span class="preview-badge">PR #97 Design Preview</span>
        </div>
        <nav class="preview-tabs" aria-label="Preview switcher">
            <a href="preview-contribute.html" class="preview-tab {'active' if page_type == 'contribute' else ''}">
                🤝 Contribute Page
            </a>
            <a href="preview-discover.html" class="preview-tab {'active' if page_type == 'discover' else ''}">
                🔍 Discover Page
            </a>
        </nav>
    </header>

    <div class="mock-site-nav">
        <div>🌍 <strong>world.openfoodfacts.org</strong> / {page_type}</div>
        <div class="mock-nav-links">
            <a href="preview-discover.html" class="mock-nav-link">Discover</a>
            <a href="preview-contribute.html" class="mock-nav-link">Contribute</a>
            <a href="https://world.openfoodfacts.org/data" class="mock-nav-link">Data</a>
            <a href="https://world.openfoodfacts.org/donors" class="mock-nav-link">Donate</a>
        </div>
    </div>

    <!-- Main Content -->
    <main class="preview-container">
        {content_relative}
    </main>

</body>
</html>
"""
    output_filename = f"preview-{page_type}.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {output_filename} successfully ({len(html)} bytes)")

if __name__ == "__main__":
    build_preview("contribute")
    build_preview("discover")
