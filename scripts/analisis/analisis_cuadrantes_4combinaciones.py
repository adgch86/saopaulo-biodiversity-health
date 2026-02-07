"""
Análisis de Cuadrantes - 4 Combinaciones
=========================================
1) Gobernanza vs Biodiversidad
2) Gobernanza vs Salud (Carga de Enfermedad)
3) Gobernanza vs Riesgo Climático
4) Biodiversidad vs Vulnerabilidad

Para cada cuadrante: número de municipios y población total.

Autor: Science Team / AP Digital
Fecha: 2026-02-03
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
FIG_DIR = os.path.join(BASE_DIR, "outputs/figures")
SHP_PATH = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")

# Load data
df = pd.read_csv(CSV_PATH)
gdf = gpd.read_file(SHP_PATH)
gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)

print(f"Dataset: {len(df)} municipios")
print(f"Poblacion total SP: {df['population'].sum():,.0f}")

# Definir las 4 combinaciones de analisis
analisis = [
    {
        'name': 'Gobernanza_vs_Biodiversidad',
        'var_x': 'idx_gobernanza_100',
        'var_y': 'idx_biodiv',
        'label_x': 'Gobernanza',
        'label_y': 'Biodiversidad',
        'high_x_good': True,
        'high_y_good': True,
    },
    {
        'name': 'Gobernanza_vs_Salud',
        'var_x': 'idx_gobernanza_100',
        'var_y': 'idx_carga_enfermedad',
        'label_x': 'Gobernanza',
        'label_y': 'Carga Enfermedad',
        'high_x_good': True,
        'high_y_good': False,
    },
    {
        'name': 'Gobernanza_vs_Clima',
        'var_x': 'idx_gobernanza_100',
        'var_y': 'idx_clima',
        'label_x': 'Gobernanza',
        'label_y': 'Riesgo Climatico',
        'high_x_good': True,
        'high_y_good': False,
    },
    {
        'name': 'Biodiversidad_vs_Vulnerabilidad',
        'var_x': 'idx_biodiv',
        'var_y': 'idx_vulnerabilidad',
        'label_x': 'Biodiversidad',
        'label_y': 'Vulnerabilidad',
        'high_x_good': True,
        'high_y_good': False,
    },
]

# Colores para cuadrantes
cuadrante_colors = {
    'Q1_Optimo': '#2ecc71',
    'Q2_Riesgo': '#f1c40f',
    'Q3_Critico': '#e74c3c',
    'Q4_Potencial': '#e67e22',
}

all_results = []

for config in analisis:
    print(f"\n{'='*60}")
    print(f"ANALISIS: {config['label_x']} vs {config['label_y']}")
    print(f"{'='*60}")

    var_x = config['var_x']
    var_y = config['var_y']

    # Calcular medianas
    median_x = df[var_x].median()
    median_y = df[var_y].median()

    print(f"Mediana {config['label_x']}: {median_x:.2f}")
    print(f"Mediana {config['label_y']}: {median_y:.2f}")

    # Crear cuadrantes
    def assign_quadrant(row):
        x_high = row[var_x] >= median_x
        y_high = row[var_y] >= median_y

        x_good = x_high if config['high_x_good'] else not x_high
        y_good = not y_high if not config['high_y_good'] else y_high

        if x_good and y_good:
            return 'Q1_Optimo'
        elif x_good and not y_good:
            return 'Q2_Riesgo'
        elif not x_good and not y_good:
            return 'Q3_Critico'
        else:
            return 'Q4_Potencial'

    col_name = f"cuadrante_{config['name']}"
    df[col_name] = df.apply(assign_quadrant, axis=1)

    # Calcular estadisticas por cuadrante
    stats = df.groupby(col_name).agg({
        'cod_ibge': 'count',
        'population': 'sum',
        var_x: 'mean',
        var_y: 'mean'
    }).rename(columns={'cod_ibge': 'n_municipios', 'population': 'poblacion_total'})

    stats['pct_municipios'] = (stats['n_municipios'] / stats['n_municipios'].sum() * 100).round(1)
    stats['pct_poblacion'] = (stats['poblacion_total'] / stats['poblacion_total'].sum() * 100).round(1)

    # Reordenar
    order = ['Q1_Optimo', 'Q2_Riesgo', 'Q3_Critico', 'Q4_Potencial']
    stats = stats.reindex([q for q in order if q in stats.index])

    print(f"\n{'Cuadrante':<15} {'N Mun':>8} {'%Mun':>7} {'Poblacion':>15} {'%Pob':>7} {config['label_x'][:10]:>12} {config['label_y'][:10]:>12}")
    print('-'*80)

    for q in order:
        if q in stats.index:
            row = stats.loc[q]
            print(f"{q:<15} {row['n_municipios']:>8.0f} {row['pct_municipios']:>6.1f}% {row['poblacion_total']:>15,.0f} {row['pct_poblacion']:>6.1f}% {row[var_x]:>12.1f} {row[var_y]:>12.1f}")

    # Guardar para CSV
    stats_export = stats.reset_index()
    stats_export.columns = ['cuadrante', 'n_municipios', 'poblacion_total', f'mean_{var_x}', f'mean_{var_y}', 'pct_municipios', 'pct_poblacion']
    stats_export['analisis'] = config['name']
    stats_export['var_x'] = config['label_x']
    stats_export['var_y'] = config['label_y']
    all_results.append(stats_export)

    # Crear mapa
    merged = gdf.merge(df[['cod_ibge', col_name]], on='cod_ibge', how='left')

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Mapa de cuadrantes
    ax1 = axes[0]
    for q, color in cuadrante_colors.items():
        subset = merged[merged[col_name] == q]
        if len(subset) > 0:
            subset.plot(ax=ax1, color=color, edgecolor='white', linewidth=0.2)

    ax1.axis('off')
    ax1.set_title(f"{config['label_x']} vs {config['label_y']}\nCuadrantes (n=645 municipios)",
                  fontsize=12, fontweight='bold')

    # Legend con stats
    legend_elements = []
    for q in order:
        if q in stats.index:
            n = stats.loc[q, 'n_municipios']
            pct_pob = stats.loc[q, 'pct_poblacion']
            legend_elements.append(
                Patch(facecolor=cuadrante_colors[q],
                      label=f"{q.replace('_', ' ')} ({n:.0f} mun, {pct_pob:.1f}% pob)")
            )
    ax1.legend(handles=legend_elements, loc='lower left', fontsize=9)

    # Scatter plot con cuadrantes
    ax2 = axes[1]
    for q, color in cuadrante_colors.items():
        subset = df[df[col_name] == q]
        if len(subset) > 0:
            ax2.scatter(subset[var_x], subset[var_y], c=color, alpha=0.6, s=20, label=q.replace('_', ' '))

    ax2.axvline(median_x, color='black', linestyle='--', linewidth=1, alpha=0.7)
    ax2.axhline(median_y, color='black', linestyle='--', linewidth=1, alpha=0.7)
    ax2.set_xlabel(config['label_x'], fontsize=11)
    ax2.set_ylabel(config['label_y'], fontsize=11)
    ax2.set_title(f"Distribucion de Municipios\nLineas = medianas", fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, f"cuadrantes_{config['name']}.png"), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n[SAVED] cuadrantes_{config['name']}.png")

# Guardar resultados consolidados
results_df = pd.concat(all_results, ignore_index=True)
results_df.to_csv(os.path.join(BASE_DIR, 'outputs/clasificacion/analisis_cuadrantes_4combinaciones.csv'), index=False)
print(f"\n[SAVED] analisis_cuadrantes_4combinaciones.csv")

# Resumen final
print(f"\n{'='*60}")
print('RESUMEN: CUADRANTES CRITICOS (Q3) POR ANALISIS')
print(f"{'='*60}")
for config in analisis:
    col_name = f"cuadrante_{config['name']}"
    q3 = df[df[col_name] == 'Q3_Critico']
    pob_total = df['population'].sum()
    print(f"\n{config['label_x']} vs {config['label_y']}:")
    print(f"  Q3 Critico: {len(q3)} municipios ({len(q3)/len(df)*100:.1f}%), {q3['population'].sum():,.0f} habitantes ({q3['population'].sum()/pob_total*100:.1f}%)")

print("\n" + "="*60)
print("ANALISIS COMPLETADO")
print("="*60)
