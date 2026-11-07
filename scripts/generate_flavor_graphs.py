import os
import random

def generate_svg_scatter(flavor, title, img_svg_snippet, metric1_label, metric1_val, metric2_label, metric2_val, unit_header, pointer_x, pointer_y, dot_colors, border_color):
    # Fixed seed for consistent dots
    random.seed(42 if flavor == 'obf' else (43 if flavor == 'opff' else 44))
    
    dots_svg = []
    # Generate background scatter points
    for _ in range(85):
        cx = random.randint(15, 310)
        cy = random.randint(10, 225)
        # Avoid clustering directly inside the tooltip box (approx 35 to 195, 10 to 180)
        if 35 < cx < 195 and 15 < cy < 170:
            if random.random() > 0.15:
                continue
        r = random.choice([4, 4.5, 5, 5.5, 6])
        col = random.choice(dot_colors)
        alpha = random.choice([0.65, 0.75, 0.85, 0.95])
        dots_svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" fill-opacity="{alpha}" />')

    # Selected dot
    selected_dot = f'''
    <circle cx="{pointer_x}" cy="{pointer_y}" r="8" fill="{border_color}" fill-opacity="0.3" />
    <circle cx="{pointer_x}" cy="{pointer_y}" r="5" fill="{border_color}" stroke="#ffffff" stroke-width="1.5" />
    '''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240">
  <defs>
    <filter id="shadow-{flavor}" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.18" flood-color="#000000" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="320" height="240" fill="#ffffff" rx="12" />

  <!-- Grid lines -->
  <line x1="25" y1="50" x2="310" y2="50" stroke="#f1f5f9" stroke-width="1" />
  <line x1="25" y1="105" x2="310" y2="105" stroke="#f1f5f9" stroke-width="1" />
  <line x1="25" y1="160" x2="310" y2="160" stroke="#f1f5f9" stroke-width="1" />
  <line x1="25" y1="215" x2="310" y2="215" stroke="#cbd5e1" stroke-width="1.5" />
  <line x1="25" y1="20" x2="25" y2="215" stroke="#cbd5e1" stroke-width="1.5" />

  <!-- Axis labels -->
  <text x="18" y="218" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">0</text>
  <text x="18" y="163" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">10</text>
  <text x="18" y="108" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">20</text>
  <text x="18" y="53" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">30</text>

  <text x="25" y="228" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">0</text>
  <text x="110" y="228" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">10</text>
  <text x="200" y="228" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">20</text>
  <text x="290" y="228" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9" fill="#94a3b8" text-anchor="middle">30</text>

  <!-- Scatter points -->
  <g id="scatter-dots">
    {''.join(dots_svg)}
    {selected_dot}
  </g>

  <!-- Tooltip Box -->
  <g filter="url(#shadow-{flavor})">
    <!-- Bubble path with callout arrow pointing to ({pointer_x}, {pointer_y}) -->
    <path d="M 40,15 
             H 185 
             A 6,6 0 0 1 191,21 
             V 165 
             A 6,6 0 0 1 185,171 
             H {pointer_x + 8} 
             L {pointer_x},{pointer_y - 3} 
             L {pointer_x - 8},171 
             H 46 
             A 6,6 0 0 1 40,165 
             Z" 
          fill="#ffffff" stroke="{border_color}" stroke-width="1.75" />

    <!-- Product Title -->
    <text x="49" y="32" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="700" fill="#1e293b">{title}</text>

    <!-- Product Thumbnail Frame -->
    <rect x="49" y="40" width="133" height="74" fill="#f8fafc" stroke="#e2e8f0" rx="4" />
    
    <!-- Embedded Illustration / Icon -->
    <g transform="translate(49, 40)">
      {img_svg_snippet}
    </g>

    <!-- Metrics -->
    <text x="49" y="128" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="9.5" font-weight="600" fill="#64748b">{unit_header}</text>
    
    <text x="49" y="145" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10.5" font-weight="700" fill="#334155">{metric1_label} : <tspan fill="{border_color}">{metric1_val}</tspan></text>
    
    <text x="49" y="161" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10.5" font-weight="700" fill="#334155">{metric2_label} : <tspan fill="{border_color}">{metric2_val}</tspan></text>
  </g>
</svg>'''
    return svg

# 1. Open Beauty Facts (OBF)
obf_thumb = '''
<rect width="133" height="74" fill="#fdf2f8" rx="4" />
<!-- Cream pot & beauty bottle icon -->
<g transform="translate(48, 12) scale(0.7)">
  <!-- Bottle body -->
  <rect x="10" y="20" width="32" height="48" rx="6" fill="#ec4899" />
  <rect x="18" y="10" width="16" height="12" rx="2" fill="#db2777" />
  <rect x="22" y="4" width="8" height="7" rx="1" fill="#be185d" />
  <!-- White label on bottle -->
  <rect x="14" y="30" width="24" height="28" rx="3" fill="#ffffff" />
  <line x1="18" y1="38" x2="34" y2="38" stroke="#ec4899" stroke-width="2" stroke-linecap="round" />
  <line x1="20" y1="44" x2="32" y2="44" stroke="#f472b6" stroke-width="1.5" stroke-linecap="round" />
  <line x1="22" y1="50" x2="30" y2="50" stroke="#f472b6" stroke-width="1.5" stroke-linecap="round" />
</g>
'''
obf_colors = ['#ec4899', '#f43f5e', '#8b5cf6', '#a855f7', '#06b6d4', '#10b981', '#fbbf24', '#f97316']
obf_svg = generate_svg_scatter(
    flavor='obf',
    title='Gentle Shampoo Bio',
    img_svg_snippet=obf_thumb,
    metric1_label='Allergens',
    metric1_val='0',
    metric2_label='INCI count',
    metric2_val='11',
    unit_header='for 100 ml :',
    pointer_x=115,
    pointer_y=202,
    dot_colors=obf_colors,
    border_color='#db2777'
)

# 2. Open Pet Food Facts (OPFF)
opff_thumb = '''
<rect width="133" height="74" fill="#fff7ed" rx="4" />
<!-- Pet food bag / bowl icon -->
<g transform="translate(46, 10) scale(0.72)">
  <!-- Pouch / bag -->
  <path d="M 12,14 L 18,65 L 42,65 L 48,14 Z" fill="#ea580c" />
  <path d="M 12,14 L 30,22 L 48,14 Z" fill="#c2410c" />
  <!-- White paw badge -->
  <circle cx="30" cy="40" r="12" fill="#ffffff" />
  <circle cx="30" cy="42" r="4.5" fill="#ea580c" />
  <circle cx="24" cy="33" r="2.2" fill="#ea580c" />
  <circle cx="29" cy="30" r="2.2" fill="#ea580c" />
  <circle cx="35" cy="33" r="2.2" fill="#ea580c" />
</g>
'''
opff_colors = ['#ea580c', '#f97316', '#fb923c', '#16a34a', '#22c55e', '#eab308', '#dc2626']
opff_svg = generate_svg_scatter(
    flavor='opff',
    title='Salmon &amp; Rice Cat Food',
    img_svg_snippet=opff_thumb,
    metric1_label='Protein',
    metric1_val='34 %',
    metric2_label='Fat',
    metric2_val='14 %',
    unit_header='for 100 g :',
    pointer_x=120,
    pointer_y=198,
    dot_colors=opff_colors,
    border_color='#ea580c'
)

# 3. Open Products Facts (OPF)
opf_thumb = '''
<rect width="133" height="74" fill="#eef2ff" rx="4" />
<!-- Appliance / Washing machine icon -->
<g transform="translate(48, 10) scale(0.72)">
  <rect x="10" y="8" width="42" height="56" rx="4" fill="#ffffff" stroke="#4338ca" stroke-width="2.5" />
  <line x1="10" y1="20" x2="52" y2="20" stroke="#c7d2fe" stroke-width="1.5" />
  <circle cx="18" cy="14" r="2" fill="#4338ca" />
  <circle cx="25" cy="14" r="2" fill="#4338ca" />
  <rect x="36" y="12" width="10" height="4" rx="1" fill="#6366f1" />
  <!-- Drum -->
  <circle cx="31" cy="40" r="14" fill="#e0e7ff" stroke="#4338ca" stroke-width="2" />
  <circle cx="31" cy="40" r="9" fill="#c7d2fe" />
</g>
'''
opf_colors = ['#4338ca', '#6366f1', '#059669', '#10b981', '#0ea5e9', '#f59e0b', '#ef4444']
opf_svg = generate_svg_scatter(
    flavor='opf',
    title='EcoClean 8kg Washer',
    img_svg_snippet=opf_thumb,
    metric1_label='Repair Score',
    metric1_val='8.6 / 10',
    metric2_label='Energy class',
    metric2_val='A',
    unit_header='Specifications :',
    pointer_x=110,
    pointer_y=195,
    dot_colors=opf_colors,
    border_color='#4338ca'
)

# Save SVGs in html/images/svg/ and openfoodfacts-design/images/
os.makedirs('html/images/svg', exist_ok=True)
with open('html/images/svg/compare-graph-obf.svg', 'w') as f:
    f.write(obf_svg)
with open('html/images/svg/compare-graph-opff.svg', 'w') as f:
    f.write(opff_svg)
with open('html/images/svg/compare-graph-opf.svg', 'w') as f:
    f.write(opf_svg)

print('Successfully generated compare-graph-obf.svg, compare-graph-opff.svg, compare-graph-opf.svg')
