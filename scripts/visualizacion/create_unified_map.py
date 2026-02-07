"""
Mapa unificado con selector de capas para Workshop SEMIL-USP
Todas las 6 variables en un solo mapa con control de capas

Autor: Adrian David / AP Digital
Fecha: 2026-01-23
"""

import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import LinearColormap
from branca.element import Element
import os

# Rutas
BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
SHAPEFILE_PATH = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
OUTPUT_DIR = r"G:\My Drive\Adrian David\Forthe_worshop\mapas_workshop"

# Configuracion de las 6 capas
CAPAS_CONFIG = [
    {
        "id": "riesgo_inundacion",
        "variable": "flooding_risks",
        "nombre": "Riesgo de Inundacion",
        "descripcion": "Indice de riesgo (0-1)",
        "invert": False,
        "show": True  # Capa visible por defecto
    },
    {
        "id": "riqueza_vertebrados",
        "variable": "mean_species_richness",
        "nombre": "Riqueza de Vertebrados",
        "descripcion": "Numero medio de especies",
        "invert": True,
        "show": False
    },
    {
        "id": "vulnerabilidad_social",
        "variable": "pct_pobreza",
        "nombre": "Vulnerabilidad Social",
        "descripcion": "% poblacion en pobreza",
        "invert": False,
        "show": False
    },
    {
        "id": "incidencia_dengue",
        "variable": "incidence_mean_dengue",
        "nombre": "Incidencia Dengue",
        "descripcion": "Casos/100k hab/ano",
        "invert": False,
        "show": False
    },
    {
        "id": "gobernanza_uai",
        "variable": "UAI_Crisk",
        "nombre": "Gobernanza UAI",
        "descripcion": "Capacidad gestion riesgo (0-1)",
        "invert": True,
        "show": False
    },
    {
        "id": "deficit_polinizacion",
        "variable": "pol_deficit",
        "nombre": "Deficit Polinizacion",
        "descripcion": "Perdida servicio ecosistemico (%)",
        "invert": False,
        "show": False
    }
]


def cargar_datos():
    """Carga y hace merge de shapefile con datos municipales"""
    print("Cargando datos...")

    gdf = gpd.read_file(SHAPEFILE_PATH)
    df = pd.read_csv(CSV_PATH)

    # Ajustar codigos IBGE
    gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)

    # Merge
    gdf_merged = gdf.merge(df, on='cod_ibge', how='left')

    # Convertir a WGS84
    gdf_merged = gdf_merged.to_crs(epsg=4326)

    print(f"  {len(gdf_merged)} municipios cargados")
    return gdf_merged


def crear_colormap(values, invert=False):
    """Crea colormap verde-amarillo-rojo o invertido"""
    vmin = values.min()
    vmax = values.max()

    if invert:
        colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
    else:
        colors = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']

    return LinearColormap(colors=colors, vmin=vmin, vmax=vmax)


def crear_mapa_unificado(gdf):
    """Crea mapa con todas las capas y selector"""

    # Centro de Sao Paulo
    center = [-22.5, -48.5]

    # Crear mapa base
    m = folium.Map(
        location=center,
        zoom_start=7,
        tiles='cartodbpositron'
    )

    # Crear cada capa
    colormaps = {}

    for config in CAPAS_CONFIG:
        variable = config['variable']
        nombre = config['nombre']
        invert = config['invert']
        show = config['show']

        print(f"  Creando capa: {nombre}")

        # Filtrar datos validos
        gdf_valid = gdf[gdf[variable].notna()].copy()

        # Crear colormap
        colormap = crear_colormap(gdf_valid[variable], invert=invert)
        colormaps[variable] = colormap

        # Funcion de estilo
        def style_function(feature, var=variable, cm=colormap):
            value = feature['properties'].get(var)
            if value is None or pd.isna(value):
                return {
                    'fillColor': '#cccccc',
                    'color': '#999999',
                    'weight': 0.5,
                    'fillOpacity': 0.3
                }
            return {
                'fillColor': cm(value),
                'color': '#333333',
                'weight': 0.5,
                'fillOpacity': 0.7
            }

        # Preparar GeoJSON
        cols = ['NM_MUN', 'cod_ibge', variable, 'geometry']
        cols_exist = [c for c in cols if c in gdf.columns]
        gdf_layer = gdf[cols_exist].copy()

        # Crear FeatureGroup para la capa
        fg = folium.FeatureGroup(name=nombre, show=show)

        # Agregar GeoJson a la capa
        folium.GeoJson(
            gdf_layer.__geo_interface__,
            style_function=lambda x, var=variable, cm=colormap: {
                'fillColor': cm(x['properties'].get(var)) if x['properties'].get(var) is not None else '#cccccc',
                'color': '#333333',
                'weight': 0.5,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_MUN', variable],
                aliases=['Municipio:', f'{nombre}:'],
                localize=True
            )
        ).add_to(fg)

        fg.add_to(m)

    # Agregar control de capas
    folium.LayerControl(collapsed=False).add_to(m)

    # Agregar titulo
    title_html = '''
    <div style="position: fixed;
                top: 10px; left: 60px;
                background-color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                z-index: 1000;
                font-family: Arial, sans-serif;
                max-width: 300px;">
        <h3 style="margin: 0 0 10px 0; color: #333;">Workshop SEMIL-USP</h3>
        <p style="margin: 0; font-size: 12px; color: #666;">
            Seleccione una capa en el panel derecho para visualizar diferentes indicadores de los 645 municipios de Sao Paulo.
        </p>
        <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
        <p style="margin: 0; font-size: 10px; color: #999;">
            <b>Escala de colores:</b><br>
            Verde = Favorable / Bajo riesgo<br>
            Rojo = Desfavorable / Alto riesgo
        </p>
    </div>
    '''
    m.get_root().html.add_child(Element(title_html))

    # Agregar leyendas para cada variable (mostrar solo la activa via CSS/JS)
    legend_html = '''
    <div id="legend-container" style="position: fixed;
                bottom: 30px; left: 60px;
                background-color: white;
                padding: 10px 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                z-index: 1000;
                font-family: Arial, sans-serif;
                font-size: 11px;">
        <b>Leyenda de colores</b><br>
        <div style="display: flex; align-items: center; margin-top: 5px;">
            <div style="width: 120px; height: 15px; background: linear-gradient(to right, #1a9850, #91cf60, #d9ef8b, #fee08b, #fc8d59, #d73027);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; width: 120px;">
            <span>Bajo</span>
            <span>Alto</span>
        </div>
        <p style="margin: 5px 0 0 0; font-size: 9px; color: #666;">
            * Para Biodiversidad y Gobernanza:<br>
            Verde = Alto (favorable)
        </p>
    </div>
    '''
    m.get_root().html.add_child(Element(legend_html))

    return m


def main():
    print("=" * 60)
    print("MAPA UNIFICADO CON SELECTOR DE CAPAS")
    print("=" * 60)

    # Cargar datos
    gdf = cargar_datos()

    # Crear mapa
    print("\nCreando mapa unificado...")
    m = crear_mapa_unificado(gdf)

    # Guardar
    output_path = os.path.join(OUTPUT_DIR, "mapa_unificado_capas.html")
    m.save(output_path)

    print(f"\n[OK] Mapa guardado: {output_path}")
    print("\nInstrucciones:")
    print("  1. Abre el archivo HTML en un navegador")
    print("  2. Usa el panel de capas (esquina superior derecha)")
    print("  3. Activa/desactiva capas para comparar variables")


if __name__ == "__main__":
    main()
