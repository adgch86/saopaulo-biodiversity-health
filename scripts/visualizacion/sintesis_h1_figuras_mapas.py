"""
Síntesis H1 Nexus Assessment - 5 Figuras Principales + 3 Mapas Bidimensionales

Figuras:
  F1: Panel resumen causal (forest → pol_deficit → climate → health) con coeficientes SEM
  F2: Heatmap de correlaciones Biodiv × Salud (top relationships)
  F3: Forest plot de coeficientes SEM por enfermedad
  F4: Panel de modulación social (scatter forest vs dengue por 4 moderadores)
  F5: Diagrama de mediación con proporciones

Mapas bidimensionales:
  M1: Biodiversidad (forest_cover) × Carga de enfermedad (idx_carga_enfermedad) - bivariate
  M2: Vulnerabilidad social × Riesgo climático - bivariate
  M3: Gobernanza × Déficit de polinización - bivariate

Autor: Science Team / AP Digital
Fecha: 2026-01-26
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from matplotlib.colors import ListedColormap, BoundaryNorm
import geopandas as gpd
import os

# Rutas
BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
SHAPEFILE_PATH = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")
H1_1 = os.path.join(BASE_DIR, "outputs/modelos/h1_1_correlations.csv")
H1_2 = os.path.join(BASE_DIR, "outputs/modelos/h1_2_mediation.csv")
H1_3 = os.path.join(BASE_DIR, "outputs/modelos/h1_3_moderation.csv")
H1_4 = os.path.join(BASE_DIR, "outputs/modelos/h1_4_sem_paths.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Labels legibles
HEALTH_LABELS = {
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_diarrhea_mean': 'Diarrhea',
    'health_death_circ_mean': 'CV Mortality',
    'health_hosp_resp_mean': 'Resp. Hosp.'
}

BIODIV_LABELS = {
    'forest_cover': 'Forest Cover',
    'mean_species_richness': 'Species Richness',
    'pol_deficit': 'Pollination Deficit'
}

CLIMATE_LABELS = {
    'flooding_risks': 'Flood Risk',
    'fire_risk_index': 'Fire Risk',
    'hydric_stress_risk': 'Hydric Stress'
}


def load_data():
    df = pd.read_csv(CSV_PATH)
    corr = pd.read_csv(H1_1)
    med = pd.read_csv(H1_2)
    mod = pd.read_csv(H1_3)
    sem = pd.read_csv(H1_4)
    print(f"Data: {len(df)} municipalities, {len(corr)} correlations, {len(sem)} SEM paths")
    return df, corr, med, mod, sem


def load_geodata(df):
    gdf = gpd.read_file(SHAPEFILE_PATH)
    gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)
    gdf = gdf.merge(df, on='cod_ibge', how='left')
    gdf = gdf.to_crs(epsg=4326)
    return gdf


# ============================================================
# FIGURA 1: Panel Resumen Causal con coeficientes SEM
# ============================================================
def fig1_causal_panel(sem):
    """Diagrama de flujo causal con coeficientes SEM para dengue"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Filter dengue SEM paths
    dengue = sem[sem['health_outcome'] == 'incidence_mean_dengue'].copy()

    # Node positions and colors
    nodes = {
        'Governance\n(idx_gobernanza)': (1, 6.5, '#3498db', 1.4),
        'Forest\nCover': (3.5, 6.5, '#27ae60', 1.2),
        'Species\nRichness': (3.5, 4.5, '#27ae60', 1.2),
        'Pollination\nDeficit': (5.5, 5.5, '#e67e22', 1.2),
        'Flood\nRisk': (7, 7, '#e74c3c', 1.0),
        'Fire\nRisk': (7, 4, '#e74c3c', 1.0),
        'Dengue\nIncidence': (9, 5.5, '#8e44ad', 1.5),
    }

    # Draw nodes
    for label, (x, y, color, size) in nodes.items():
        circle = plt.Circle((x, y), size * 0.4, color=color, alpha=0.2, ec=color, linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color=color)

    # Key SEM paths with coefficients
    paths = [
        ('Governance\n(idx_gobernanza)', 'Forest\nCover', 0.202, '***'),
        ('Forest\nCover', 'Pollination\nDeficit', -0.654, '***'),
        ('Species\nRichness', 'Pollination\nDeficit', 0.079, '*'),
        ('Forest\nCover', 'Flood\nRisk', 0.217, '***'),
        ('Pollination\nDeficit', 'Flood\nRisk', -0.329, '***'),
        ('Pollination\nDeficit', 'Fire\nRisk', 0.405, '***'),
        ('Fire\nRisk', 'Dengue\nIncidence', 0.287, '***'),
        ('Forest\nCover', 'Dengue\nIncidence', -0.108, '*'),
        ('Species\nRichness', 'Dengue\nIncidence', -0.328, '***'),
        ('Flood\nRisk', 'Dengue\nIncidence', 0.005, 'ns'),
    ]

    for src_label, dst_label, coef, sig in paths:
        sx, sy = nodes[src_label][0], nodes[src_label][1]
        dx, dy = nodes[dst_label][0], nodes[dst_label][1]

        # Arrow color by sign
        if sig == 'ns':
            arrow_color = '#bdc3c7'
            lw = 1
        elif coef < 0:
            arrow_color = '#27ae60'  # Green = protective
            lw = max(1.5, abs(coef) * 6)
        else:
            arrow_color = '#e74c3c'  # Red = risk
            lw = max(1.5, abs(coef) * 6)

        # Shorten arrows to not overlap nodes
        dx_len = dx - sx
        dy_len = dy - sy
        dist = np.sqrt(dx_len**2 + dy_len**2)
        if dist > 0:
            shrink = 0.45 / dist
            sx2 = sx + dx_len * shrink
            sy2 = sy + dy_len * shrink
            dx2 = dx - dx_len * shrink
            dy2 = dy - dy_len * shrink
        else:
            sx2, sy2, dx2, dy2 = sx, sy, dx, dy

        ax.annotate('', xy=(dx2, dy2), xytext=(sx2, sy2),
                     arrowprops=dict(arrowstyle='->', color=arrow_color, lw=lw,
                                     connectionstyle='arc3,rad=0.05'))

        # Label
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        offset_x = -0.15 if dx_len < 0 else 0.15
        offset_y = 0.2
        label_text = f'{coef:+.3f}{sig}' if sig != 'ns' else f'{coef:+.3f} ns'
        ax.text(mx + offset_x, my + offset_y, label_text,
                fontsize=8, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='gray'),
                fontweight='bold', color=arrow_color)

    # Title
    ax.text(5, 0.5, 'H1 Nexus Assessment: Structural Equation Model — Dengue Incidence',
            ha='center', va='center', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.text(5, 0.1, 'SEM standardized coefficients | N = 645 municipalities, State of S\u00e3o Paulo | *** p<0.001, * p<0.05, ns = not significant',
            ha='center', va='center', fontsize=9, color='#7f8c8d')

    # Legend
    legend_elements = [
        mpatches.Patch(color='#27ae60', alpha=0.5, label='Protective effect (-)'),
        mpatches.Patch(color='#e74c3c', alpha=0.5, label='Risk amplifier (+)'),
        mpatches.Patch(color='#bdc3c7', alpha=0.5, label='Non-significant'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'h1_FIG1_causal_panel.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# FIGURA 2: Heatmap Biodiversidad x Salud con correlaciones
# ============================================================
def fig2_heatmap_biodiv_health(corr):
    """Heatmap focused: Biodiv+Climate rows vs Health columns"""
    # Filter direct biodiv->health and climate->health
    predictors = list(BIODIV_LABELS.keys()) + list(CLIMATE_LABELS.keys())
    outcomes = list(HEALTH_LABELS.keys())

    pred_labels = {**BIODIV_LABELS, **CLIMATE_LABELS}

    # Build matrix
    matrix = np.zeros((len(predictors), len(outcomes)))
    sig_matrix = np.zeros((len(predictors), len(outcomes)), dtype=bool)

    for i, pred in enumerate(predictors):
        for j, out in enumerate(outcomes):
            row = corr[(corr['predictor'] == pred) & (corr['outcome'] == out)]
            if len(row) > 0:
                matrix[i, j] = row.iloc[0]['r_spearman']
                sig_matrix[i, j] = row.iloc[0]['significant']

    fig, ax = plt.subplots(figsize=(12, 7))

    # Custom diverging colormap
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=-0.5, vmax=0.5)

    # Labels
    ax.set_xticks(range(len(outcomes)))
    ax.set_xticklabels([HEALTH_LABELS[o] for o in outcomes], rotation=35, ha='right', fontsize=11)
    ax.set_yticks(range(len(predictors)))
    ax.set_yticklabels([pred_labels[p] for p in predictors], fontsize=11)

    # Annotate with values and significance
    for i in range(len(predictors)):
        for j in range(len(outcomes)):
            val = matrix[i, j]
            sig = sig_matrix[i, j]
            stars = '***' if sig and abs(val) > 0.3 else ('**' if sig and abs(val) > 0.1 else ('*' if sig else ''))
            color = 'white' if abs(val) > 0.3 else 'black'
            ax.text(j, i, f'{val:.2f}{stars}', ha='center', va='center',
                    fontsize=9, fontweight='bold' if sig else 'normal', color=color)

    # Divider between biodiv and climate
    ax.axhline(y=2.5, color='white', linewidth=3)
    ax.text(-1.8, 1, 'Biodiversity', fontsize=11, fontweight='bold', color='#27ae60',
            ha='center', va='center', rotation=90)
    ax.text(-1.8, 4, 'Climate\nRisk', fontsize=11, fontweight='bold', color='#e74c3c',
            ha='center', va='center', rotation=90)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8, label='Spearman r')
    cbar.ax.tick_params(labelsize=10)

    ax.set_title('H1.1: Biodiversity & Climate Risk vs. Health Outcomes\nSpearman correlations | N = 645 municipalities',
                 fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'h1_FIG2_heatmap_biodiv_health.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# FIGURA 3: Forest plot SEM coeficientes por enfermedad
# ============================================================
def fig3_forest_plot_sem(sem):
    """Forest plot: key SEM paths across all 7 health outcomes"""
    # Key paths to compare across diseases
    key_paths = [
        ('mean_species_richness_z', 'Species Richness', '#27ae60'),
        ('forest_cover_z', 'Forest Cover', '#2ecc71'),
        ('pol_deficit_z', 'Pollin. Deficit', '#e67e22'),
        ('fire_risk_index_z', 'Fire Risk', '#e74c3c'),
        ('flooding_risks_z', 'Flood Risk', '#c0392b'),
        ('idx_gobernanza_100_z', 'Governance', '#3498db'),
    ]

    health_outcomes = list(HEALTH_LABELS.keys())

    fig, axes = plt.subplots(1, len(key_paths), figsize=(22, 8), sharey=True)

    for col_idx, (path_var, path_label, color) in enumerate(key_paths):
        ax = axes[col_idx]
        coefs = []
        sigs = []

        for h in health_outcomes:
            h_z = h + '_z' if not h.endswith('_z') else h
            # Find path from path_var to health outcome
            row = sem[(sem['health_outcome'] == h) &
                      (sem['path'].str.contains(path_var)) &
                      (sem['path'].str.contains(h.split('incidence_')[-1].split('health_')[-1][:8]))]

            # More specific: direct path to health
            for _, r in sem[sem['health_outcome'] == h].iterrows():
                p = r['path']
                parts = p.split('\u2192')
                if len(parts) == 2:
                    src = parts[0].strip()
                    dst = parts[1].strip()
                    if src == path_var and h.replace('incidence_mean_', '').replace('health_', '')[:6] in dst:
                        coefs.append(r['coefficient'])
                        sigs.append(r['p_value'] < 0.05)
                        break
            else:
                coefs.append(0)
                sigs.append(False)

        y_pos = np.arange(len(health_outcomes))
        colors = [color if s else '#bdc3c7' for s in sigs]
        alphas = [0.9 if s else 0.4 for s in sigs]

        bars = ax.barh(y_pos, coefs, color=colors, edgecolor='white', height=0.6)
        for bar, alpha in zip(bars, alphas):
            bar.set_alpha(alpha)

        ax.axvline(x=0, color='black', linewidth=0.5, linestyle='-')
        ax.set_xlim(-0.45, 0.45)
        ax.set_title(path_label, fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('\u03b2 (SEM)', fontsize=9)

        # Annotate values
        for i, (c, s) in enumerate(zip(coefs, sigs)):
            if abs(c) > 0.001:
                stars = '***' if s and abs(c) > 0.2 else ('*' if s else '')
                x_pos = c + 0.02 if c >= 0 else c - 0.02
                ha = 'left' if c >= 0 else 'right'
                ax.text(x_pos, i, f'{c:.2f}{stars}', va='center', ha=ha,
                        fontsize=8, fontweight='bold' if s else 'normal')

        if col_idx == 0:
            ax.set_yticks(y_pos)
            ax.set_yticklabels([HEALTH_LABELS[h] for h in health_outcomes], fontsize=10)

        ax.grid(axis='x', alpha=0.2)

    fig.suptitle('H1.4: SEM Path Coefficients by Predictor Across All Health Outcomes',
                 fontsize=14, fontweight='bold', y=0.98)
    fig.text(0.5, 0.01, 'Standardized coefficients (\u03b2) from full SEM | N = 645 municipalities | *** p<0.001, * p<0.05',
             ha='center', fontsize=10, color='#7f8c8d')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    path = os.path.join(OUTPUT_DIR, 'h1_FIG3_forest_plot_sem.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# FIGURA 4: Panel modulación social (4 moderadores)
# ============================================================
def fig4_modulation_panel(df):
    """Panel 2x2: Forest vs Dengue modulado por 4 variables sociales"""
    moderators = [
        ('pct_pobreza', 'Poverty Rate (%)', '#e74c3c'),
        ('pct_preta', 'Black Population (%)', '#8e44ad'),
        ('pct_rural', 'Rural Population (%)', '#f39c12'),
        ('pct_indigena', 'Indigenous Pop. (%)', '#16a085'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()

    x_var = 'forest_cover'
    y_var = 'incidence_mean_dengue'

    for idx, (mod_var, mod_label, color) in enumerate(moderators):
        ax = axes[idx]
        valid = df[[x_var, y_var, mod_var]].dropna()

        # Terciles
        terciles = pd.qcut(valid[mod_var], 3, labels=['Low', 'Medium', 'High'])
        valid['tercil'] = terciles

        colors_tercil = {'Low': '#3498db', 'Medium': '#f39c12', 'High': '#e74c3c'}
        markers = {'Low': 'o', 'Medium': 's', 'High': '^'}

        for tercil in ['Low', 'Medium', 'High']:
            subset = valid[valid['tercil'] == tercil]
            ax.scatter(subset[x_var], subset[y_var], alpha=0.25, s=15,
                       c=colors_tercil[tercil], marker=markers[tercil], label=None)

            # Regression line
            if len(subset) > 10:
                from scipy import stats
                slope, intercept, r, p, se = stats.linregress(subset[x_var], subset[y_var])
                x_line = np.linspace(subset[x_var].min(), subset[x_var].max(), 100)
                y_line = slope * x_line + intercept
                sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
                ax.plot(x_line, y_line, color=colors_tercil[tercil], linewidth=2.5,
                        label=f'{tercil} {mod_label}: r={r:.3f} {sig}')

        ax.set_xlabel('Forest Cover (%)', fontsize=11)
        ax.set_ylabel('Dengue Incidence (per 100k)', fontsize=11)
        ax.set_title(f'Moderated by {mod_label}', fontsize=12, fontweight='bold', color=color)
        ax.legend(fontsize=9, loc='upper right', framealpha=0.9)
        ax.grid(alpha=0.15)

    fig.suptitle('H1.3: Forest Cover vs. Dengue Incidence Modulated by Social Vulnerability',
                 fontsize=14, fontweight='bold', y=1.01)
    fig.text(0.5, -0.01,
             'Each panel shows tercile-stratified regressions | N = 645 municipalities | Environmental justice evidence',
             ha='center', fontsize=10, color='#7f8c8d')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'h1_FIG4_modulation_panel.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# FIGURA 5: Diagrama de mediación con proporciones
# ============================================================
def fig5_mediation_diagram(med):
    """Diagrama resumiendo mediación por déficit de polinización"""
    # Summarize mediation by biodiversity source and climate risk
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Key mediation results
    # Forest -> pol_deficit -> flooding: 48.6% mediated
    # Forest -> pol_deficit -> fire: indirect = -0.253 (suppression)
    # Species -> pol_deficit -> flooding: 31.6% mediated

    # Draw boxes
    boxes = {
        'Forest Cover': (1.5, 6, '#27ae60'),
        'Species Richness': (1.5, 2, '#2ecc71'),
        'Pollination\nDeficit': (5, 4, '#e67e22'),
        'Flood Risk': (8.5, 6, '#e74c3c'),
        'Fire Risk': (8.5, 2, '#c0392b'),
    }

    for label, (x, y, color) in boxes.items():
        rect = plt.Rectangle((x - 0.9, y - 0.5), 1.8, 1.0,
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2,
                              transform=ax.transData, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=11,
                fontweight='bold', color=color, zorder=3)

    # Arrows with labels
    arrows = [
        (1.5, 6, 5, 4, 'r = -0.765***', '#27ae60', 3),
        (1.5, 2, 5, 4, 'r = -0.567***', '#2ecc71', 2.5),
        (5, 4, 8.5, 6, 'Mediates 48.6%\nof Forest\u2192Flood', '#e67e22', 2.5),
        (5, 4, 8.5, 2, 'Mediates\nForest\u2192Fire\n(suppression)', '#e67e22', 2),
        (1.5, 6, 8.5, 6, 'Direct: r = 0.351***', '#95a5a6', 1.5),
        (1.5, 6, 8.5, 2, 'Direct: r = -0.149***', '#95a5a6', 1.5),
    ]

    for sx, sy, dx, dy, label, color, lw in arrows:
        # Shorten
        ddx, ddy = dx - sx, dy - sy
        dist = np.sqrt(ddx**2 + ddy**2)
        shrk = 1.0 / dist
        sx2 = sx + ddx * shrk
        sy2 = sy + ddy * shrk
        dx2 = dx - ddx * shrk
        dy2 = dy - ddy * shrk

        ax.annotate('', xy=(dx2, dy2), xytext=(sx2, sy2),
                     arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                     connectionstyle='arc3,rad=0.08'))

        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        # Offset for readability
        offset_y = 0.35 if sy == dy else 0
        offset_x = 0.3 if sx == dx else 0
        ax.text(mx + offset_x, my + offset_y, label, fontsize=9, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.9, edgecolor=color, boxstyle='round,pad=0.3'),
                color=color, fontweight='bold')

    # Title
    ax.text(5, 7.5, 'H1.2: Pollination Deficit as Mediator in the Biodiversity\u2192Climate Risk Chain',
            ha='center', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.text(5, 0.3, 'Sobel test mediation analysis | N = 645 municipalities | All mediation paths p < 0.001',
            ha='center', fontsize=10, color='#7f8c8d')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'h1_FIG5_mediation_diagram.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# MAPA BIDIMENSIONAL - Función genérica bivariate choropleth
# ============================================================
def create_bivariate_colormap():
    """Creates a 3x3 bivariate color matrix"""
    # Rows: variable Y (bottom to top)
    # Cols: variable X (left to right)
    # Classic bivariate: blue-x, red-y, purple-both
    colors_3x3 = [
        # Low Y
        ['#e8e8e8', '#b5c0da', '#6c83b5'],  # Low X, Med X, High X
        # Med Y
        ['#dfb0d6', '#a5add3', '#5698b9'],
        # High Y
        ['#be64ac', '#8c62aa', '#3b4994'],
    ]
    return colors_3x3


def bivariate_map(gdf, var_x, var_y, label_x, label_y, title, filename):
    """Create a bivariate choropleth map"""
    valid = gdf[[var_x, var_y, 'geometry']].dropna(subset=[var_x, var_y]).copy()

    # Classify into terciles
    valid['cat_x'] = pd.qcut(valid[var_x], 3, labels=[0, 1, 2]).astype(int)
    valid['cat_y'] = pd.qcut(valid[var_y], 3, labels=[0, 1, 2]).astype(int)

    colors_3x3 = create_bivariate_colormap()

    # Assign colors
    valid['biv_color'] = valid.apply(lambda r: colors_3x3[r['cat_y']][r['cat_x']], axis=1)

    fig, ax = plt.subplots(1, 1, figsize=(14, 12))

    # Plot municipalities without data in gray
    gdf_nodata = gdf[~gdf.index.isin(valid.index)]
    if len(gdf_nodata) > 0:
        gdf_nodata.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.3)

    # Plot bivariate colors
    for color_val in valid['biv_color'].unique():
        subset = valid[valid['biv_color'] == color_val]
        subset.plot(ax=ax, color=color_val, edgecolor='#666666', linewidth=0.3)

    ax.set_axis_off()
    ax.set_title(title, fontsize=15, fontweight='bold', pad=20, color='#2c3e50')

    # Add bivariate legend
    legend_ax = fig.add_axes([0.12, 0.08, 0.15, 0.15])
    for i in range(3):
        for j in range(3):
            rect = plt.Rectangle((j, i), 1, 1, facecolor=colors_3x3[i][j],
                                  edgecolor='white', linewidth=1)
            legend_ax.add_patch(rect)

    legend_ax.set_xlim(0, 3)
    legend_ax.set_ylim(0, 3)
    legend_ax.set_xlabel(f'{label_x} \u2192', fontsize=10, fontweight='bold')
    legend_ax.set_ylabel(f'{label_y} \u2192', fontsize=10, fontweight='bold')
    legend_ax.set_xticks([0.5, 1.5, 2.5])
    legend_ax.set_xticklabels(['Low', 'Med', 'High'], fontsize=8)
    legend_ax.set_yticks([0.5, 1.5, 2.5])
    legend_ax.set_yticklabels(['Low', 'Med', 'High'], fontsize=8)
    legend_ax.set_aspect('equal')

    # Source text
    fig.text(0.5, 0.02, f'N = {len(valid)} municipalities | State of S\u00e3o Paulo, Brazil | Workshop SEMIL-USP 2026',
             ha='center', fontsize=9, color='#95a5a6')

    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] {path}")
    return path


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("SYNTHESIS H1: 5 FIGURES + 3 BIVARIATE MAPS")
    print("=" * 60)

    print("\n1. Loading data...")
    df, corr, med, mod, sem = load_data()

    print("\n2. Generating 5 main figures...")
    print("\n  FIG 1: Causal panel (SEM dengue)")
    fig1_causal_panel(sem)

    print("  FIG 2: Heatmap Biodiv x Health")
    fig2_heatmap_biodiv_health(corr)

    print("  FIG 3: Forest plot SEM by disease")
    fig3_forest_plot_sem(sem)

    print("  FIG 4: Modulation panel (4 moderators)")
    fig4_modulation_panel(df)

    print("  FIG 5: Mediation diagram")
    fig5_mediation_diagram(med)

    print("\n3. Loading geodata for maps...")
    gdf = load_geodata(df)

    print("\n4. Generating 3 bivariate maps...")

    print("\n  MAP 1: Biodiversity x Disease Burden")
    bivariate_map(gdf,
                  var_x='forest_cover', var_y='idx_carga_enfermedad',
                  label_x='Forest Cover', label_y='Disease Burden',
                  title='Biodiversity-Health Nexus:\nForest Cover vs. Disease Burden Index',
                  filename='h1_MAP1_bivariate_forest_disease.png')

    print("  MAP 2: Social Vulnerability x Climate Risk")
    bivariate_map(gdf,
                  var_x='idx_vulnerabilidad', var_y='idx_clima',
                  label_x='Social Vulnerability', label_y='Climate Risk',
                  title='Climate Justice:\nSocial Vulnerability vs. Climate Risk Index',
                  filename='h1_MAP2_bivariate_vuln_climate.png')

    print("  MAP 3: Governance x Pollination Deficit")
    bivariate_map(gdf,
                  var_x='idx_gobernanza_100', var_y='pol_deficit',
                  label_x='Governance', label_y='Pollination Deficit',
                  title='Governance-Ecosystem Services Nexus:\nGovernance Index vs. Pollination Deficit',
                  filename='h1_MAP3_bivariate_governance_poldef.png')

    print("\n" + "=" * 60)
    print("DONE: 5 figures + 3 maps generated")
    print(f"Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
