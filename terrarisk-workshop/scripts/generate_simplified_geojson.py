"""
Generate simplified GeoJSON from São Paulo municipalities shapefile
For TerraRisk Workshop - optimized for web performance
"""

import geopandas as gpd
import json
from pathlib import Path

# Paths
SHAPEFILE_PATH = Path("data/geo/ibge_sp/SP_Municipios_2022.shp")
OUTPUT_PATH = Path("terrarisk-workshop/frontend/public/geojson/sp_simplified.json")

def main():
    print("Loading shapefile...")
    gdf = gpd.read_file(SHAPEFILE_PATH)

    print(f"Loaded {len(gdf)} municipalities")
    print(f"Original CRS: {gdf.crs}")
    print(f"Columns: {list(gdf.columns)}")

    # Reproject to WGS84 if needed
    if gdf.crs != "EPSG:4326":
        print("Reprojecting to WGS84...")
        gdf = gdf.to_crs("EPSG:4326")

    # Simplify geometries (tolerance in degrees, ~1km at equator)
    print("Simplifying geometries...")
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)

    # Keep only necessary columns
    keep_cols = ['CD_MUN', 'NM_MUN', 'geometry']
    available_cols = [c for c in keep_cols if c in gdf.columns]
    gdf = gdf[available_cols]

    # Rename columns for consistency
    rename_map = {
        'CD_MUN': 'CD_MUN',
        'NM_MUN': 'NM_MUN',
    }
    gdf = gdf.rename(columns={k: v for k, v in rename_map.items() if k in gdf.columns})

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Convert to GeoJSON
    print("Converting to GeoJSON...")
    geojson_dict = json.loads(gdf.to_json())

    # Reduce precision of coordinates
    def reduce_precision(coords, precision=5):
        if isinstance(coords[0], (list, tuple)):
            return [reduce_precision(c, precision) for c in coords]
        return [round(c, precision) for c in coords]

    for feature in geojson_dict['features']:
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            geom['coordinates'] = reduce_precision(geom['coordinates'])
        elif geom['type'] == 'MultiPolygon':
            geom['coordinates'] = reduce_precision(geom['coordinates'])

    # Write output
    print(f"Writing to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(geojson_dict, f, ensure_ascii=False)

    # Report size
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Done! Output size: {size_kb:.1f} KB")

    if size_kb > 1000:
        print("Warning: File is larger than 1MB. Consider increasing simplification tolerance.")


if __name__ == "__main__":
    main()
