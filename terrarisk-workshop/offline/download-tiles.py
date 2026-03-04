#!/usr/bin/env python3
"""
Download map tiles for Sao Paulo state (offline use).
Tiles from Carto CDN: light_nolabels + light_only_labels
Zoom levels 6-11 covering SP bounding box.

Run: python download-tiles.py
Output: ./tiles/ directory (~80-120MB)
"""

import os
import math
import time
import urllib.request
import sys

# Sao Paulo bounding box (with margin)
LAT_MIN = -25.5
LAT_MAX = -19.5
LON_MIN = -54.0
LON_MAX = -43.5

# Zoom range (6-11 is enough for municipality-level workshop)
ZOOM_MIN = 6
ZOOM_MAX = 11

# Tile layers to download
LAYERS = {
    "light_nolabels": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png",
    "light_only_labels": "https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png",
}

SUBDOMAINS = ["a", "b", "c", "d"]
OUTPUT_DIR = "./tiles"
DELAY = 0.05  # 50ms between requests to not hammer the CDN


def lat_lon_to_tile(lat, lon, zoom):
    """Convert lat/lon to tile x/y at given zoom."""
    lat_rad = math.radians(lat)
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def count_tiles():
    """Count total tiles to download."""
    total = 0
    for z in range(ZOOM_MIN, ZOOM_MAX + 1):
        x_min, y_min = lat_lon_to_tile(LAT_MAX, LON_MIN, z)
        x_max, y_max = lat_lon_to_tile(LAT_MIN, LON_MAX, z)
        tiles_at_zoom = (x_max - x_min + 1) * (y_max - y_min + 1)
        total += tiles_at_zoom
        print(f"  Zoom {z}: {tiles_at_zoom} tiles ({x_max - x_min + 1}x{y_max - y_min + 1})")
    return total * len(LAYERS)


def download_tiles():
    """Download all tiles for SP region."""
    print("=== TerraRisk Tile Downloader ===")
    print(f"Region: Sao Paulo ({LAT_MIN},{LON_MIN}) to ({LAT_MAX},{LON_MAX})")
    print(f"Zoom levels: {ZOOM_MIN}-{ZOOM_MAX}")
    print(f"Layers: {', '.join(LAYERS.keys())}")
    print()

    total = count_tiles()
    print(f"\nTotal tiles to download: {total}")
    print(f"Estimated size: {total * 15 // 1024} MB")
    print()

    downloaded = 0
    errors = 0
    skipped = 0

    for layer_name, url_template in LAYERS.items():
        print(f"\n--- Downloading layer: {layer_name} ---")

        for z in range(ZOOM_MIN, ZOOM_MAX + 1):
            x_min, y_min = lat_lon_to_tile(LAT_MAX, LON_MIN, z)
            x_max, y_max = lat_lon_to_tile(LAT_MIN, LON_MAX, z)

            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    tile_dir = os.path.join(OUTPUT_DIR, layer_name, str(z), str(x))
                    tile_path = os.path.join(tile_dir, f"{y}.png")

                    # Skip if already downloaded
                    if os.path.exists(tile_path) and os.path.getsize(tile_path) > 0:
                        skipped += 1
                        continue

                    os.makedirs(tile_dir, exist_ok=True)

                    # Pick subdomain round-robin
                    s = SUBDOMAINS[downloaded % len(SUBDOMAINS)]
                    url = url_template.replace("{s}", s).replace("{z}", str(z)).replace("{x}", str(x)).replace("{y}", str(y))

                    try:
                        urllib.request.urlretrieve(url, tile_path)
                        downloaded += 1

                        if downloaded % 100 == 0:
                            pct = (downloaded + skipped) * 100 // total
                            print(f"  [{pct}%] Downloaded {downloaded}, skipped {skipped}, errors {errors}")

                        time.sleep(DELAY)

                    except Exception as e:
                        errors += 1
                        if errors < 10:
                            print(f"  Error downloading {url}: {e}")

    print(f"\n=== Done! ===")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (cached): {skipped}")
    print(f"Errors: {errors}")

    # Calculate actual size
    total_size = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    print(f"Total size: {total_size // (1024*1024)} MB")


if __name__ == "__main__":
    download_tiles()
