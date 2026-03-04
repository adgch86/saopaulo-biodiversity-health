#!/usr/bin/env python3
"""Patch MapViewer.tsx to support offline tiles via NEXT_PUBLIC_TILE_URL."""

filepath = '/opt/terrarisk-workshop/terrarisk-workshop/frontend/src/components/map/MapViewer.tsx'

with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Replace base tile layer block
    if '// Base tile layer' in line and 'offline' not in line:
        # Replace the comment + tileLayer + attribution + addTo block
        new_lines.append('      // Base tile layer - supports offline mode via NEXT_PUBLIC_TILE_URL\n')
        new_lines.append("      const tileBase = process.env.NEXT_PUBLIC_TILE_URL || 'https://{s}.basemaps.cartocdn.com';\n")
        new_lines.append("      const isOffline = tileBase.includes('localhost') || tileBase.includes('127.0.0.1');\n")
        new_lines.append('      L.tileLayer(isOffline\n')
        new_lines.append("        ? `${tileBase}/tiles/light_nolabels/{z}/{x}/{y}.png`\n")
        new_lines.append("        : `${tileBase}/light_nolabels/{z}/{x}/{y}{r}.png`, {\n")
        new_lines.append("        attribution: '&copy; <a href=\"https://carto.com/\">CARTO</a>',\n")
        new_lines.append('      }).addTo(map);\n')
        # Skip old lines (comment + tileLayer + attribution + addTo)
        i += 1  # skip old tileLayer line
        i += 1  # skip old attribution line
        i += 1  # skip old }).addTo(map) line
        i += 1  # move past
        continue

    # Replace labels tile layer line
    if "light_only_labels" in line and "basemaps.cartocdn.com" in line and "isOffline" not in line:
        new_lines.append('      L.tileLayer(isOffline\n')
        new_lines.append("        ? `${tileBase}/tiles/light_only_labels/{z}/{x}/{y}.png`\n")
        new_lines.append("        : 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {\n")
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print('MapViewer.tsx patched successfully')
