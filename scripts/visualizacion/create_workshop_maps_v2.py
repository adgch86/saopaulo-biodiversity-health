"""
Script para generar los 10 mapas de calor ADICIONALES para el Workshop SEMIL-USP
Day 2: Scenario Dynamics - Territorial Diagnosis with Data

Mapas existentes (6):
  01_riesgo_inundacion (flooding_risks)
  02_riqueza_vertebrados (mean_species_richness)
  03_vulnerabilidad_social (pct_pobreza)
  04_incidencia_dengue (incidence_mean_dengue)
  05_gobernanza_UAI (UAI_Crisk)
  06_deficit_polinizacion (pol_deficit)

Mapas nuevos (10):
  07_cobertura_forestal (forest_cover)
  08_riesgo_fuego (fire_risk_index)
  09_estres_hidrico (hydric_stress_risk)
  10_incidencia_diarrea (incidence_diarrhea_mean)
  11_mortalidad_cardiovascular (health_death_circ_mean)
  12_hospitalizacion_respiratoria (health_hosp_resp_mean)
  13_indice_gobernanza (idx_gobernanza_100)
  14_indice_vulnerabilidad (idx_vulnerabilidad)
  15_porcentaje_rural (pct_rural)
  16_mortalidad_infantil (mort_infantil)

Autor: Science Team / AP Digital
Fecha: 2026-01-26
"""

import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import LinearColormap
import os
import numpy as np

# Rutas de archivos
BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
SHAPEFILE_PATH = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
OUTPUT_DIR = r"G:\My Drive\Adrian David\Forthe_worshop\mapas_workshop"
PNG_DIR = os.path.join(OUTPUT_DIR, "png")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

# Configuración de los 10 mapas NUEVOS
MAPAS_CONFIG = {
    "07_cobertura_forestal": {
        "variable": "forest_cover",
        "titulo": "Cobertura Forestal",
        "titulo_en": "Forest Cover",
        "descripcion": "Porcentaje de cobertura forestal del municipio",
        "descripcion_en": "Percentage of forest cover per municipality",
        "invert_colors": True,  # Mayor = más bosque = verde
        "unidad": "%"
    },
    "08_riesgo_fuego": {
        "variable": "fire_risk_index",
        "titulo": "Riesgo de Incendio",
        "titulo_en": "Fire Risk Index",
        "descripcion": "Índice compuesto de riesgo de incendio (0-100)",
        "descripcion_en": "Composite fire risk index (0-100)",
        "invert_colors": False,  # Mayor = más riesgo = rojo
        "unidad": "índice"
    },
    "09_estres_hidrico": {
        "variable": "hydric_stress_risk",
        "titulo": "Riesgo de Estrés Hídrico",
        "titulo_en": "Hydric Stress Risk",
        "descripcion": "Índice de riesgo de estrés hídrico (0-1)",
        "descripcion_en": "Hydric stress risk index (0-1)",
        "invert_colors": False,
        "unidad": "índice"
    },
    "10_incidencia_diarrea": {
        "variable": "incidence_diarrhea_mean",
        "titulo": "Incidencia de Diarrea",
        "titulo_en": "Diarrhea Incidence",
        "descripcion": "Casos promedio de diarrea por 100.000 habitantes/año",
        "descripcion_en": "Average diarrhea cases per 100,000 inhabitants/year",
        "invert_colors": False,
        "unidad": "casos/100k hab"
    },
    "11_mortalidad_cardiovascular": {
        "variable": "health_death_circ_mean",
        "titulo": "Mortalidad Cardiovascular",
        "titulo_en": "Cardiovascular Mortality",
        "descripcion": "Tasa de mortalidad por enfermedades circulatorias por 100.000 hab/año",
        "descripcion_en": "Circulatory disease mortality rate per 100,000 inhabitants/year",
        "invert_colors": False,
        "unidad": "muertes/100k hab"
    },
    "12_hospitalizacion_respiratoria": {
        "variable": "health_hosp_resp_mean",
        "titulo": "Hospitalización por Enfermedades Respiratorias",
        "titulo_en": "Respiratory Hospitalization",
        "descripcion": "Tasa de hospitalización por enfermedades respiratorias por 100.000 hab/año",
        "descripcion_en": "Respiratory disease hospitalization rate per 100,000 inhabitants/year",
        "invert_colors": False,
        "unidad": "hosp./100k hab"
    },
    "13_indice_gobernanza": {
        "variable": "idx_gobernanza_100",
        "titulo": "Índice de Gobernanza Compuesto",
        "titulo_en": "Composite Governance Index",
        "descripcion": "Índice compuesto de gobernanza municipal (0-100, incluye UAI + capacidades)",
        "descripcion_en": "Composite municipal governance index (0-100, includes UAI + capacities)",
        "invert_colors": True,  # Mayor = mejor gobernanza = verde
        "unidad": "índice"
    },
    "14_indice_vulnerabilidad": {
        "variable": "idx_vulnerabilidad",
        "titulo": "Índice de Vulnerabilidad Social",
        "titulo_en": "Social Vulnerability Index",
        "descripcion": "Índice compuesto de vulnerabilidad social (0-100)",
        "descripcion_en": "Composite social vulnerability index (0-100)",
        "invert_colors": False,  # Mayor = más vulnerable = rojo
        "unidad": "índice"
    },
    "15_porcentaje_rural": {
        "variable": "pct_rural",
        "titulo": "Población Rural",
        "titulo_en": "Rural Population",
        "descripcion": "Porcentaje de población rural del municipio",
        "descripcion_en": "Percentage of rural population per municipality",
        "invert_colors": None,  # Neutral - use blue scale
        "unidad": "%"
    },
    "16_mortalidad_infantil": {
        "variable": "mort_infantil",
        "titulo": "Mortalidad Infantil",
        "titulo_en": "Infant Mortality",
        "descripcion": "Tasa de mortalidad infantil por 1.000 nacidos vivos",
        "descripcion_en": "Infant mortality rate per 1,000 live births",
        "invert_colors": False,
        "unidad": "por 1.000 NV"
    }
}


def cargar_datos():
    """Carga y hace merge de shapefile con datos municipales"""
    print("Cargando shapefile...")
    gdf = gpd.read_file(SHAPEFILE_PATH)

    print("Cargando datos municipales (v8)...")
    df = pd.read_csv(CSV_PATH)

    # Ajustar códigos IBGE
    gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)

    print(f"Shapefile: {len(gdf)} municipios")
    print(f"Datos: {len(df)} municipios")

    # Merge
    gdf_merged = gdf.merge(df, on='cod_ibge', how='left')
    municipios_con_datos = gdf_merged.dropna(subset=['Municipio']).shape[0]
    print(f"Municipios con datos: {municipios_con_datos}")

    # Convertir a WGS84 para folium
    gdf_merged = gdf_merged.to_crs(epsg=4326)

    return gdf_merged


def crear_colormap(values, invert=None):
    """
    Crea colormap rojo-amarillo-verde (o invertido, o azul para neutral)
    """
    vmin = values.min()
    vmax = values.max()

    if invert is None:
        # Neutral: escala azul
        colors = ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b']
    elif invert:
        # Mayor valor = verde (protección/capacidad)
        colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
    else:
        # Mayor valor = rojo (riesgo)
        colors = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']

    return LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax
    )


def crear_mapa(gdf, config, nombre_archivo):
    """Crea un mapa choropleth interactivo con folium"""
    variable = config['variable']
    titulo = config['titulo']
    titulo_en = config['titulo_en']
    descripcion = config['descripcion']
    invert = config['invert_colors']
    unidad = config['unidad']

    gdf_valid = gdf[gdf[variable].notna()].copy()

    if len(gdf_valid) == 0:
        print(f"  [WARN] No hay datos válidos para {variable}")
        return None

    print(f"  {len(gdf_valid)} municipios con datos válidos")

    # Centro del mapa (São Paulo state)
    centroid = gdf_valid.geometry.centroid.unary_union.centroid
    center = [centroid.y, centroid.x]

    # Crear mapa base
    m = folium.Map(
        location=center,
        zoom_start=7,
        tiles='cartodbpositron'
    )

    # Crear colormap
    colormap = crear_colormap(gdf_valid[variable], invert=invert)

    # Estilizar polígonos
    def style_function(feature):
        value = feature['properties'].get(variable)
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return {
                'fillColor': '#cccccc',
                'color': '#666666',
                'weight': 0.5,
                'fillOpacity': 0.3
            }
        return {
            'fillColor': colormap(value),
            'color': '#333333',
            'weight': 0.5,
            'fillOpacity': 0.7
        }

    def highlight_function(feature):
        return {
            'fillColor': '#ffffff',
            'color': '#000000',
            'weight': 2,
            'fillOpacity': 0.9
        }

    # Tooltip
    tooltip = folium.GeoJsonTooltip(
        fields=['NM_MUN', variable],
        aliases=['Municipality:', f'{titulo_en}:'],
        localize=True,
        sticky=True,
        style="""
            background-color: white;
            border: 2px solid #333;
            border-radius: 5px;
            padding: 10px;
            font-family: Arial;
            font-size: 12px;
        """
    )

    # Preparar GeoJSON
    cols_to_keep = ['NM_MUN', 'Municipio', variable, 'geometry']
    cols_available = [c for c in cols_to_keep if c in gdf.columns]
    gdf_json = gdf[cols_available].copy()

    # Agregar capa GeoJSON
    geojson_layer = folium.GeoJson(
        gdf_json.__geo_interface__,
        name=titulo_en,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    )
    geojson_layer.add_to(m)

    # Colormap al mapa
    colormap.caption = f'{titulo_en} ({unidad})'
    colormap.add_to(m)

    # Título
    title_html = f'''
    <div style="position: fixed;
                top: 10px; left: 50px;
                background-color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                z-index: 1000;
                font-family: Arial, sans-serif;">
        <h3 style="margin: 0 0 5px 0; color: #333;">{titulo_en}</h3>
        <p style="margin: 0; font-size: 11px; color: #666;">{descripcion}</p>
        <p style="margin: 5px 0 0 0; font-size: 10px; color: #999;">
            Workshop SEMIL-USP | Data: {len(gdf_valid)} municipalities
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    folium.LayerControl().add_to(m)

    # Guardar HTML
    output_path = os.path.join(OUTPUT_DIR, f"{nombre_archivo}.html")
    m.save(output_path)
    print(f"  [OK] Saved: {output_path}")

    return output_path


def main():
    print("=" * 60)
    print("WORKSHOP MAPS v2 - 10 ADDITIONAL HEAT-MAPS")
    print("=" * 60)

    print("\n1. Loading data...")
    gdf = cargar_datos()

    print("\n2. Generating maps...")
    mapas_generados = []

    for nombre, config in MAPAS_CONFIG.items():
        print(f"\n  Processing: {config['titulo_en']} ({config['variable']})")
        output = crear_mapa(gdf, config, nombre)
        if output:
            mapas_generados.append({
                'nombre': nombre,
                'archivo': output,
                'variable': config['variable'],
                'titulo': config['titulo_en']
            })

    # Resumen
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Maps generated: {len(mapas_generados)}/10")
    print(f"Location: {OUTPUT_DIR}")
    print("\nFiles created:")
    for m in mapas_generados:
        print(f"  - {m['nombre']}.html ({m['variable']})")

    print(f"\nTotal maps in workshop folder: 6 (existing) + {len(mapas_generados)} (new) = {6 + len(mapas_generados)}")
    print("\nDone!")


if __name__ == "__main__":
    main()
