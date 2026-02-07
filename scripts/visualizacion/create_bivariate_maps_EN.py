"""
Mapas Bivariados en Inglés - Workshop
=====================================
1) Governance vs Vulnerability (Governance on Y axis)
2) Climate Risk vs Vulnerability (Vulnerability on Y axis)

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
print("Loading data...")
df = pd.read_csv(CSV_PATH)
gdf = gpd.read_file(SHP_PATH)
gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)

print(f"Dataset: {len(df)} municipalities")

# Colores para cuadrantes
COLORS = {
    'Q1_Optimal': '#2ecc71',    # Verde
    'Q2_Risk': '#f1c40f',       # Amarillo
    'Q3_Critical': '#e74c3c',   # Rojo
    'Q4_Potential': '#e67e22',  # Naranja
}

# Definición de los 2 análisis
ANALYSES = [
    {
        'name': 'Governance_vs_Vulnerability',
        'var_x': 'idx_vulnerabilidad',
        'var_y': 'idx_gobernanza_100',
        'label_x': 'Vulnerability',
        'label_y': 'Governance',
        'high_x_good': False,  # Low vulnerability is good
        'high_y_good': True,   # High governance is good
    },
    {
        'name': 'ClimateRisk_vs_Vulnerability',
        'var_x': 'idx_clima',
        'var_y': 'idx_vulnerabilidad',
        'label_x': 'Climate Risk',
        'label_y': 'Vulnerability',
        'high_x_good': False,  # Low climate risk is good
        'high_y_good': False,  # Low vulnerability is good
    },
]

def assign_quadrant(row, var_x, var_y, median_x, median_y, high_x_good, high_y_good):
    """Assign quadrant based on median splits"""
    x_high = row[var_x] >= median_x
    y_high = row[var_y] >= median_y

    # Determine if current position is "good" for each axis
    x_good = not x_high if not high_x_good else x_high
    y_good = y_high if high_y_good else not y_high

    if x_good and y_good:
        return 'Q1_Optimal'
    elif not x_good and y_good:
        return 'Q2_Risk'
    elif not x_good and not y_good:
        return 'Q3_Critical'
    else:  # x_good and not y_good
        return 'Q4_Potential'

# Generar los 2 mapas
for config in ANALYSES:
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {config['label_x']} vs {config['label_y']}")
    print(f"{'='*60}")

    var_x = config['var_x']
    var_y = config['var_y']

    # Calcular medianas
    median_x = df[var_x].median()
    median_y = df[var_y].median()

    print(f"Median {config['label_x']}: {median_x:.2f}")
    print(f"Median {config['label_y']}: {median_y:.2f}")

    # Asignar cuadrantes
    col_name = f"quadrant_{config['name']}"
    df[col_name] = df.apply(
        lambda row: assign_quadrant(
            row, var_x, var_y, median_x, median_y,
            config['high_x_good'], config['high_y_good']
        ),
        axis=1
    )

    # Estadísticas por cuadrante
    stats = df.groupby(col_name).agg({
        'cod_ibge': 'count',
        'population': 'sum',
        var_x: 'mean',
        var_y: 'mean'
    }).rename(columns={'cod_ibge': 'n_mun', 'population': 'total_pop'})

    stats['pct_mun'] = (stats['n_mun'] / stats['n_mun'].sum() * 100).round(1)
    stats['pct_pop'] = (stats['total_pop'] / stats['total_pop'].sum() * 100).round(1)

    # Reordenar
    order = ['Q1_Optimal', 'Q2_Risk', 'Q3_Critical', 'Q4_Potential']
    stats = stats.reindex([q for q in order if q in stats.index])

    print(f"\n{'Quadrant':<15} {'N Mun':>8} {'%Mun':>7} {'Population':>15} {'%Pop':>7}")
    print('-'*60)
    for q in order:
        if q in stats.index:
            row = stats.loc[q]
            print(f"{q:<15} {row['n_mun']:>8.0f} {row['pct_mun']:>6.1f}% {row['total_pop']:>15,.0f} {row['pct_pop']:>6.1f}%")

    # Merge con geometrías
    merged = gdf.merge(df[['cod_ibge', col_name]], on='cod_ibge', how='left')

    # Crear figura
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # === MAPA ===
    ax1 = axes[0]
    for q, color in COLORS.items():
        subset = merged[merged[col_name] == q]
        if len(subset) > 0:
            subset.plot(ax=ax1, color=color, edgecolor='white', linewidth=0.2)

    ax1.axis('off')
    ax1.set_title(f"{config['label_x']} vs {config['label_y']}\nQuadrants (n=645 municipalities)",
                  fontsize=12, fontweight='bold')

    # Leyenda con estadísticas
    legend_elements = []
    for q in order:
        if q in stats.index:
            n = stats.loc[q, 'n_mun']
            pct_pop = stats.loc[q, 'pct_pop']
            label = q.replace('_', ' ')
            legend_elements.append(
                Patch(facecolor=COLORS[q],
                      label=f"{label} ({n:.0f} mun, {pct_pop:.1f}% pop)")
            )
    ax1.legend(handles=legend_elements, loc='lower left', fontsize=9)

    # === SCATTER PLOT ===
    ax2 = axes[1]
    for q, color in COLORS.items():
        subset = df[df[col_name] == q]
        if len(subset) > 0:
            ax2.scatter(subset[var_x], subset[var_y], c=color, alpha=0.6, s=20,
                       label=q.replace('_', ' '))

    # Líneas de medianas
    ax2.axvline(median_x, color='black', linestyle='--', linewidth=1, alpha=0.7)
    ax2.axhline(median_y, color='black', linestyle='--', linewidth=1, alpha=0.7)

    ax2.set_xlabel(config['label_x'], fontsize=11)
    ax2.set_ylabel(config['label_y'], fontsize=11)
    ax2.set_title(f"Distribution of Municipalities\nLines = medians", fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=8)

    plt.tight_layout()

    # Guardar
    filename = f"bivariate_{config['name']}_EN.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"\n[SAVED] {filename}")

print("\n" + "="*60)
print("COMPLETED - 2 bivariate maps saved")
print("="*60)
