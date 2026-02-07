"""
Workshop Layers - 16 mapas con 3 niveles (Bajo, Medio, Alto)
============================================================
Genera mapas para cada variable del pool del workshop.

Autor: Science Team
Fecha: 2026-02-03
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

# Configuración
BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
SHP_PATH = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/figures/workshop_layers")

# Cargar datos
print("Cargando datos...")
df = pd.read_csv(CSV_PATH)
gdf = gpd.read_file(SHP_PATH)
gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)

print(f"Dataset: {len(df)} municipios")
print(f"Shapefile: {len(gdf)} geometrias")

# Definición de las 16 variables del workshop
VARIABLES = [
    {
        "id": 1,
        "name": "Governance_UAI_Climatic_Risk",
        "column": "UAI_Crisk",
        "title_en": "Governance - UAI Climatic Risk",
        "title_es": "Gobernanza - UAI Riesgo Climatico",
        "source": "Neder et al. 2021",
        "high_is_good": True,
    },
    {
        "id": 2,
        "name": "Governance_UAI_General",
        "column": "idx_gobernanza_100",
        "title_en": "Governance - UAI General",
        "title_es": "Gobernanza - UAI General",
        "source": "Neder et al. 2021",
        "high_is_good": True,
    },
    {
        "id": 3,
        "name": "Biodiversity_Species_Richness",
        "column": "mean_species_richness",
        "title_en": "Biodiversity - Vertebrate Species Richness",
        "title_es": "Biodiversidad - Riqueza de Especies",
        "source": "LIFE global database",
        "high_is_good": True,
    },
    {
        "id": 4,
        "name": "Natural_Habitat_Vegetation",
        "column": "forest_cover",
        "title_en": "Natural Habitat - Vegetation Cover (%)",
        "title_es": "Habitat Natural - Cobertura Vegetal (%)",
        "source": "MapBiomas",
        "high_is_good": True,
    },
    {
        "id": 5,
        "name": "Pollination_Deficit",
        "column": "pol_deficit",
        "title_en": "Pollination Deficit",
        "title_es": "Deficit de Polinizacion",
        "source": "Biota Synthesis",
        "high_is_good": False,
    },
    {
        "id": 6,
        "name": "Flooding_Risk",
        "column": "flooding_risks",
        "title_en": "Flooding Risk",
        "title_es": "Riesgo de Inundacion",
        "source": "Climate Risk Assessment",
        "high_is_good": False,
    },
    {
        "id": 7,
        "name": "Fire_Risk_Index",
        "column": "fire_risk_index",
        "title_en": "Fire Risk Index",
        "title_es": "Indice de Riesgo de Fuego",
        "source": "INPE/FIRMS",
        "high_is_good": False,
    },
    {
        "id": 8,
        "name": "Hydric_Stress_Risk",
        "column": "hydric_stress_risk",
        "title_en": "Hydric Stress Risk",
        "title_es": "Riesgo de Estres Hidrico",
        "source": "Climate Risk Assessment",
        "high_is_good": False,
    },
    {
        "id": 9,
        "name": "Zoonotic_Dengue_Incidence",
        "column": "incidence_mean_dengue",
        "title_en": "Zoonotic Disease - Dengue Incidence (per 100k)",
        "title_es": "Enfermedad Zoonotica - Incidencia Dengue (por 100k)",
        "source": "DATASUS",
        "high_is_good": False,
    },
    {
        "id": 10,
        "name": "Water_Pollution_Diarrhea",
        "column": "incidence_diarrhea_mean",
        "title_en": "Water Pollution - Diarrhea Incidence (per 100k)",
        "title_es": "Contaminacion Agua - Incidencia Diarrea (por 100k)",
        "source": "DATASUS",
        "high_is_good": False,
    },
    {
        "id": 11,
        "name": "Heat_Fire_CV_Mortality",
        "column": "health_death_circ_mean",
        "title_en": "Heat/Fire Health - CV Mortality (per 100k)",
        "title_es": "Salud Calor/Fuego - Mortalidad CV (por 100k)",
        "source": "DATASUS",
        "high_is_good": False,
    },
    {
        "id": 12,
        "name": "Heat_Fire_Resp_Hospitalization",
        "column": "health_hosp_resp_mean",
        "title_en": "Heat/Fire Health - Respiratory Hosp. (per 100k)",
        "title_es": "Salud Calor/Fuego - Hosp. Respiratoria (por 100k)",
        "source": "DATASUS",
        "high_is_good": False,
    },
    {
        "id": 13,
        "name": "Poverty_Percentage",
        "column": "pct_pobreza",
        "title_en": "Socioeconomic - Poverty (%)",
        "title_es": "Socioeconomico - Pobreza (%)",
        "source": "IBGE Census",
        "high_is_good": False,
    },
    {
        "id": 14,
        "name": "Vulnerability_Index",
        "column": "idx_vulnerabilidad",
        "title_en": "Socioeconomic - Vulnerability Index",
        "title_es": "Socioeconomico - Indice de Vulnerabilidad",
        "source": "Composite Index",
        "high_is_good": False,
    },
    {
        "id": 15,
        "name": "Rural_Population",
        "column": "pct_rural",
        "title_en": "Rural Population (%)",
        "title_es": "Poblacion Rural (%)",
        "source": "IBGE Census",
        "high_is_good": None,  # Neutral
    },
    {
        "id": 16,
        "name": "Zoonotic_Leishmaniasis_Incidence",
        "column": "incidence_mean_leishmaniose",
        "title_en": "Zoonotic Disease - Leishmaniasis Incidence (per 100k)",
        "title_es": "Enfermedad Zoonotica - Incidencia Leishmaniasis (por 100k)",
        "source": "DATASUS",
        "high_is_good": False,
    },
]

# Colores para los 3 niveles
def get_colors(high_is_good):
    if high_is_good is True:
        # Alto = bueno (verde), Bajo = malo (rojo)
        return {
            'Low': '#e74c3c',    # Rojo
            'Medium': '#f1c40f', # Amarillo
            'High': '#27ae60',   # Verde
        }
    elif high_is_good is False:
        # Alto = malo (rojo), Bajo = bueno (verde)
        return {
            'Low': '#27ae60',    # Verde
            'Medium': '#f1c40f', # Amarillo
            'High': '#e74c3c',   # Rojo
        }
    else:
        # Neutral (azul scale)
        return {
            'Low': '#3498db',    # Azul claro
            'Medium': '#2980b9', # Azul medio
            'High': '#1a5276',   # Azul oscuro
        }

def classify_terciles(series):
    """Clasifica en terciles: Low, Medium, High"""
    q33 = series.quantile(0.333)
    q66 = series.quantile(0.666)

    def classify(val):
        if pd.isna(val):
            return None
        elif val <= q33:
            return 'Low'
        elif val <= q66:
            return 'Medium'
        else:
            return 'High'

    return series.apply(classify), q33, q66

# Generar mapas
print(f"\nGenerando {len(VARIABLES)} mapas...")
print("=" * 60)

for var in VARIABLES:
    col = var['column']

    # Verificar que la columna existe
    if col not in df.columns:
        print(f"[SKIP] {var['id']:02d}. {var['name']} - columna '{col}' no encontrada")
        continue

    # Clasificar en terciles
    df[f'{col}_level'], q33, q66 = classify_terciles(df[col])

    # Merge con geometrías
    merged = gdf.merge(
        df[['cod_ibge', col, f'{col}_level']],
        on='cod_ibge',
        how='left'
    )

    # Colores
    colors = get_colors(var['high_is_good'])

    # Crear figura
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Dibujar mapa por nivel
    for level in ['Low', 'Medium', 'High']:
        subset = merged[merged[f'{col}_level'] == level]
        if len(subset) > 0:
            subset.plot(ax=ax, color=colors[level], edgecolor='white', linewidth=0.3)

    # Municipios sin datos (gris)
    no_data = merged[merged[f'{col}_level'].isna()]
    if len(no_data) > 0:
        no_data.plot(ax=ax, color='#bdc3c7', edgecolor='white', linewidth=0.3)

    ax.axis('off')

    # Título
    ax.set_title(f"{var['id']:02d}. {var['title_en']}\n{var['title_es']}",
                 fontsize=14, fontweight='bold', pad=20)

    # Estadísticas
    counts = df[f'{col}_level'].value_counts()
    low_n = counts.get('Low', 0)
    med_n = counts.get('Medium', 0)
    high_n = counts.get('High', 0)

    # Leyenda
    legend_elements = [
        Patch(facecolor=colors['Low'], label=f"Low (n={low_n}) ≤ {q33:.2f}"),
        Patch(facecolor=colors['Medium'], label=f"Medium (n={med_n}) {q33:.2f} - {q66:.2f}"),
        Patch(facecolor=colors['High'], label=f"High (n={high_n}) > {q66:.2f}"),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10,
              title="Level (Terciles)", title_fontsize=11)

    # Fuente
    ax.text(0.99, 0.01, f"Source: {var['source']}", transform=ax.transAxes,
            fontsize=8, ha='right', va='bottom', style='italic', color='gray')

    # Guardar
    filename = f"{var['id']:02d}_{var['name']}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"[OK] {var['id']:02d}. {var['name']}")
    print(f"     Low: {low_n} | Medium: {med_n} | High: {high_n}")

print("=" * 60)
print(f"\n[COMPLETADO] {len(VARIABLES)} mapas guardados en:")
print(f"  {OUTPUT_DIR}")
