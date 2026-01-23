"""
=============================================================================
Analisis de Hipotesis v2: Gobernanza y Biodiversidad como Mediadores de Riesgo
=============================================================================

Mejoras respecto a v1:
  - Analisis granular: todas las variables por dimension (no solo indices)
  - Modelos mixtos: micro/mesoregion como efectos aleatorios
  - Identificacion de mejores predictores especificos

Marco conceptual:
  Y (dependiente): Riesgo ambiental (salud, clima, nutricion)
  X1 (independiente): Gobernanza (UAI y sus 5 componentes)
  X2 (independiente): Biodiversidad (riqueza especies, cobertura forestal)
  Z (modulador): Vulnerabilidad socio-economica

Autor: Science Team - Dr. Adrian David Gonzalez Chaves
Fecha: 2026-01-21
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.regression.mixed_linear_model import MixedLM
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

# =============================================================================
# 1. CARGAR Y PREPARAR DATOS
# =============================================================================
print("=" * 80)
print("ANALISIS DE HIPOTESIS v2: GOBERNANZA Y BIODIVERSIDAD")
print("Con modelos mixtos y analisis granular por componentes")
print("=" * 80)

df = pd.read_csv(f"{PROJECT_ROOT}/outputs/municipios_integrado_v6.csv")
print(f"\n1. Datos cargados: {len(df)} municipios, {len(df.columns)} variables")

# =============================================================================
# 2. DEFINIR GRUPOS DE VARIABLES (GRANULAR)
# =============================================================================
print("\n2. Definiendo grupos de variables (analisis granular)...")

# GRUPO Y: Variables de Riesgo/Vulnerabilidad Ambiental (DEPENDIENTES)
vars_riesgo = {
    'SALUD': {
        'persist_dengue': 'Persistencia Dengue',
        'persist_leishmaniose': 'Persistencia Leishmaniosis',
        'persist_leptospirose': 'Persistencia Leptospirosis',
        'persist_malaria': 'Persistencia Malaria',
        'incidence_mean_dengue': 'Incidencia Media Dengue',
        'incidence_mean_leishmaniose': 'Incidencia Media Leishmaniosis',
        'incidence_mean_leptospirose': 'Incidencia Media Leptospirosis',
        'incidence_mean_malaria': 'Incidencia Media Malaria',
        'copresence_years': 'Anos Co-presencia Enfermedades',
        'idx_carga_enfermedad': 'Indice Carga Enfermedad'
    },
    'CLIMA': {
        'flooding_exposure': 'Exposicion Inundaciones',
        'flooding_risks': 'Riesgo Inundaciones',
        'hydric_stress_exp': 'Exposicion Estres Hidrico',
        'hydric_stress_risk': 'Riesgo Estres Hidrico',
        'idx_clima': 'Indice Riesgo Climatico'
    },
    'NUTRICION': {
        'pol_deficit': 'Deficit de Polinizacion'
    }
}

# GRUPO X1: Gobernanza (INDEPENDIENTES)
vars_gobernanza = {
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentacion',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Climatico',
    'idx_gobernanza': 'UAI General (Indice)'
}

# GRUPO X2: Biodiversidad (INDEPENDIENTES)
vars_biodiversidad = {
    'mean_species_richness': 'Riqueza Especies (Media)',
    'max_species_richness': 'Riqueza Especies (Max)',
    'forest_cover': 'Cobertura Forestal',
    'idx_biodiv': 'Indice Biodiversidad'
}

# GRUPO Z: Vulnerabilidad Socio-Economica (MODULADORES)
vars_vulnerabilidad = {
    'pct_rural': '% Poblacion Rural',
    'pct_pobreza': '% Pobreza',
    'pct_preta': '% Poblacion Negra',
    'pct_indigena': '% Poblacion Indigena',
    'idx_vulnerabilidad': 'Indice Vulnerabilidad'
}

print(f"   - Riesgo Salud: {len(vars_riesgo['SALUD'])} variables")
print(f"   - Riesgo Clima: {len(vars_riesgo['CLIMA'])} variables")
print(f"   - Riesgo Nutricion: {len(vars_riesgo['NUTRICION'])} variables")
print(f"   - Gobernanza: {len(vars_gobernanza)} variables")
print(f"   - Biodiversidad: {len(vars_biodiversidad)} variables")
print(f"   - Vulnerabilidad: {len(vars_vulnerabilidad)} variables")

# =============================================================================
# 3. PREPARAR DATOS PARA MODELOS MIXTOS
# =============================================================================
print("\n3. Preparando datos para modelos mixtos...")

# Verificar estructura jerarquica
print(f"   - Microregiones: {df['cod_microrregiao'].nunique()}")
print(f"   - Mesoregiones: {df['cod_mesorregiao'].nunique()}")

# Estandarizar variables para comparabilidad
from sklearn.preprocessing import StandardScaler

def standardize(series):
    """Estandariza una serie (z-score)"""
    valid = series.dropna()
    if len(valid) == 0 or valid.std() == 0:
        return series
    return (series - series.mean()) / series.std()

# Crear version estandarizada de variables clave
vars_to_std = (list(vars_gobernanza.keys()) +
               list(vars_biodiversidad.keys()) +
               list(vars_vulnerabilidad.keys()))

for var in vars_to_std:
    if var in df.columns:
        df[f'{var}_std'] = standardize(df[var])

# Categorizar vulnerabilidad en terciles
df['cat_vulnerabilidad'] = pd.qcut(
    df['idx_vulnerabilidad'].rank(method='first'),
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

print(f"   Distribucion vulnerabilidad:")
for cat in ['Baja', 'Media', 'Alta']:
    n = (df['cat_vulnerabilidad'] == cat).sum()
    print(f"     - {cat}: {n} municipios ({100*n/len(df):.1f}%)")

# =============================================================================
# 4. ANALISIS DE CORRELACIONES EXHAUSTIVO
# =============================================================================
print("\n4. Analisis de correlaciones exhaustivo...")

resultados_corr = []

# Para cada tipo de riesgo
for tipo_riesgo, vars_y in vars_riesgo.items():
    for var_y, nombre_y in vars_y.items():
        if var_y not in df.columns:
            continue

        # Correlaciones con Gobernanza
        for var_x, nombre_x in vars_gobernanza.items():
            if var_x not in df.columns:
                continue
            valid = df[[var_x, var_y]].dropna()
            if len(valid) > 30:
                r, p = stats.spearmanr(valid[var_x], valid[var_y])
                resultados_corr.append({
                    'Tipo_Riesgo': tipo_riesgo,
                    'Variable_Y': var_y,
                    'Nombre_Y': nombre_y,
                    'Predictor_Tipo': 'Gobernanza',
                    'Variable_X': var_x,
                    'Nombre_X': nombre_x,
                    'Spearman_r': r,
                    'p_value': p,
                    'n': len(valid),
                    'Significativo': '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
                })

        # Correlaciones con Biodiversidad
        for var_x, nombre_x in vars_biodiversidad.items():
            if var_x not in df.columns:
                continue
            valid = df[[var_x, var_y]].dropna()
            if len(valid) > 30:
                r, p = stats.spearmanr(valid[var_x], valid[var_y])
                resultados_corr.append({
                    'Tipo_Riesgo': tipo_riesgo,
                    'Variable_Y': var_y,
                    'Nombre_Y': nombre_y,
                    'Predictor_Tipo': 'Biodiversidad',
                    'Variable_X': var_x,
                    'Nombre_X': nombre_x,
                    'Spearman_r': r,
                    'p_value': p,
                    'n': len(valid),
                    'Significativo': '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
                })

df_corr = pd.DataFrame(resultados_corr)
df_corr.to_csv(f"{PROJECT_ROOT}/outputs/correlaciones_exhaustivas_v2.csv", index=False)
print(f"   Guardado: correlaciones_exhaustivas_v2.csv ({len(df_corr)} combinaciones)")

# =============================================================================
# 5. IDENTIFICAR MEJORES PREDICTORES POR TIPO DE RIESGO
# =============================================================================
print("\n5. Mejores predictores por tipo de riesgo...")

mejores_predictores = []

for tipo_riesgo in ['SALUD', 'CLIMA', 'NUTRICION']:
    subset = df_corr[df_corr['Tipo_Riesgo'] == tipo_riesgo]

    # Mejor predictor de Gobernanza
    gob_subset = subset[subset['Predictor_Tipo'] == 'Gobernanza']
    if len(gob_subset) > 0:
        mejor_gob = gob_subset.loc[gob_subset['Spearman_r'].abs().idxmax()]
        mejores_predictores.append({
            'Tipo_Riesgo': tipo_riesgo,
            'Categoria': 'Gobernanza',
            'Mejor_Predictor': mejor_gob['Nombre_X'],
            'Variable': mejor_gob['Variable_X'],
            'Para_Variable': mejor_gob['Nombre_Y'],
            'r': mejor_gob['Spearman_r'],
            'p': mejor_gob['p_value']
        })

    # Mejor predictor de Biodiversidad
    bio_subset = subset[subset['Predictor_Tipo'] == 'Biodiversidad']
    if len(bio_subset) > 0:
        mejor_bio = bio_subset.loc[bio_subset['Spearman_r'].abs().idxmax()]
        mejores_predictores.append({
            'Tipo_Riesgo': tipo_riesgo,
            'Categoria': 'Biodiversidad',
            'Mejor_Predictor': mejor_bio['Nombre_X'],
            'Variable': mejor_bio['Variable_X'],
            'Para_Variable': mejor_bio['Nombre_Y'],
            'r': mejor_bio['Spearman_r'],
            'p': mejor_bio['p_value']
        })

df_mejores = pd.DataFrame(mejores_predictores)
print("\n   MEJORES PREDICTORES:")
print("-" * 80)
for _, row in df_mejores.iterrows():
    signo = "***" if row['p'] < 0.001 else "**" if row['p'] < 0.01 else "*" if row['p'] < 0.05 else ""
    direccion = "reduce" if row['r'] < 0 else "aumenta"
    print(f"   {row['Tipo_Riesgo']:10} | {row['Categoria']:12} | {row['Mejor_Predictor']:25} {direccion} {row['Para_Variable']}")
    print(f"            |              | r = {row['r']:+.3f} {signo}")

# =============================================================================
# 6. MODELOS MIXTOS JERARQUICOS
# =============================================================================
print("\n6. Modelos mixtos jerarquicos (microregion como efecto aleatorio)...")

resultados_mixtos = []

# Seleccionar variables Y principales para modelos mixtos
vars_y_principales = [
    ('idx_carga_enfermedad', 'Carga Enfermedad', 'SALUD'),
    ('idx_clima', 'Riesgo Climatico', 'CLIMA'),
    ('pol_deficit', 'Deficit Polinizacion', 'NUTRICION')
]

# Seleccionar variables X principales
vars_x_principales = [
    ('idx_gobernanza_std', 'UAI General', 'Gobernanza'),
    ('UAI_env_std', 'UAI Ambiental', 'Gobernanza'),
    ('UAI_Crisk_std', 'UAI Riesgo Clim.', 'Gobernanza'),
    ('idx_biodiv_std', 'Indice Biodiv', 'Biodiversidad'),
    ('forest_cover_std', 'Cobertura Forestal', 'Biodiversidad')
]

print("\n   Comparando modelos OLS vs Mixtos (microregion):")
print("-" * 80)

for var_y, nombre_y, tipo_y in vars_y_principales:
    if var_y not in df.columns:
        continue

    print(f"\n   Variable dependiente: {nombre_y}")

    for var_x, nombre_x, tipo_x in vars_x_principales:
        if var_x not in df.columns:
            continue

        # Preparar datos
        df_model = df[[var_y, var_x, 'cod_microrregiao', 'idx_vulnerabilidad_std']].dropna()
        if len(df_model) < 100:
            continue

        try:
            # Modelo OLS simple
            formula_ols = f"{var_y} ~ {var_x}"
            model_ols = smf.ols(formula_ols, data=df_model).fit()

            # Modelo Mixto con microregion como efecto aleatorio
            formula_mixed = f"{var_y} ~ {var_x}"
            model_mixed = smf.mixedlm(formula_mixed, df_model, groups=df_model['cod_microrregiao']).fit()

            # Extraer resultados
            beta_ols = model_ols.params[var_x]
            pval_ols = model_ols.pvalues[var_x]
            r2_ols = model_ols.rsquared

            beta_mixed = model_mixed.fe_params[var_x]
            pval_mixed = model_mixed.pvalues[var_x]

            # Calcular ICC (Intraclass Correlation Coefficient)
            var_random = model_mixed.cov_re.iloc[0, 0] if hasattr(model_mixed.cov_re, 'iloc') else float(model_mixed.cov_re)
            var_resid = model_mixed.scale
            icc = var_random / (var_random + var_resid) if (var_random + var_resid) > 0 else 0

            resultados_mixtos.append({
                'Variable_Y': nombre_y,
                'Tipo_Y': tipo_y,
                'Variable_X': nombre_x,
                'Tipo_X': tipo_x,
                'Beta_OLS': beta_ols,
                'p_OLS': pval_ols,
                'R2_OLS': r2_ols,
                'Beta_Mixed': beta_mixed,
                'p_Mixed': pval_mixed,
                'ICC': icc,
                'n': len(df_model)
            })

            sig_ols = "***" if pval_ols < 0.001 else "**" if pval_ols < 0.01 else "*" if pval_ols < 0.05 else ""
            sig_mix = "***" if pval_mixed < 0.001 else "**" if pval_mixed < 0.01 else "*" if pval_mixed < 0.05 else ""

            print(f"     {nombre_x:20} | OLS: b={beta_ols:+.3f}{sig_ols} | Mixed: b={beta_mixed:+.3f}{sig_mix} | ICC={icc:.2f}")

        except Exception as e:
            print(f"     {nombre_x:20} | Error: {str(e)[:40]}")

df_mixtos = pd.DataFrame(resultados_mixtos)
if len(df_mixtos) > 0:
    df_mixtos.to_csv(f"{PROJECT_ROOT}/outputs/modelos_mixtos_v2.csv", index=False)
    print(f"\n   Guardado: modelos_mixtos_v2.csv")

# =============================================================================
# 7. ANALISIS ESTRATIFICADO POR VULNERABILIDAD
# =============================================================================
print("\n7. Analisis estratificado por nivel de vulnerabilidad...")

resultados_estrat = []

for cat_vuln in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat_vuln]

    for var_y, nombre_y, tipo_y in vars_y_principales:
        if var_y not in subset.columns:
            continue

        for var_x, nombre_x, tipo_x in vars_x_principales[:3]:  # Solo gobernanza para brevedad
            if var_x.replace('_std', '') not in subset.columns and var_x not in subset.columns:
                continue

            var_x_use = var_x.replace('_std', '') if var_x.replace('_std', '') in subset.columns else var_x
            valid = subset[[var_x_use, var_y]].dropna()

            if len(valid) > 20:
                r, p = stats.spearmanr(valid[var_x_use], valid[var_y])
                resultados_estrat.append({
                    'Vulnerabilidad': cat_vuln,
                    'Variable_Y': nombre_y,
                    'Variable_X': nombre_x,
                    'Tipo_X': tipo_x,
                    'r': r,
                    'p': p,
                    'n': len(valid)
                })

df_estrat = pd.DataFrame(resultados_estrat)
if len(df_estrat) > 0:
    df_estrat.to_csv(f"{PROJECT_ROOT}/outputs/correlaciones_estratificadas_v2.csv", index=False)

# Mostrar resultados
print("\n   CORRELACIONES ESTRATIFICADAS POR VULNERABILIDAD:")
print("-" * 80)
for var_y in df_estrat['Variable_Y'].unique():
    print(f"\n   {var_y}:")
    for var_x in df_estrat[df_estrat['Variable_Y'] == var_y]['Variable_X'].unique():
        vals = df_estrat[(df_estrat['Variable_Y'] == var_y) & (df_estrat['Variable_X'] == var_x)]
        line = f"     {var_x:20} |"
        for cat in ['Baja', 'Media', 'Alta']:
            row = vals[vals['Vulnerabilidad'] == cat]
            if len(row) > 0:
                r = row['r'].values[0]
                p = row['p'].values[0]
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                line += f" {cat}: {r:+.2f}{sig:3} |"
        print(line)

# =============================================================================
# 8. VISUALIZACIONES PRINCIPALES
# =============================================================================
print("\n8. Generando visualizaciones...")

# 8.1 Heatmap de correlaciones exhaustivas
fig, axes = plt.subplots(1, 3, figsize=(18, 8))

for idx, tipo_riesgo in enumerate(['SALUD', 'CLIMA', 'NUTRICION']):
    ax = axes[idx]
    subset = df_corr[df_corr['Tipo_Riesgo'] == tipo_riesgo]

    if len(subset) == 0:
        continue

    # Crear matriz de correlaciones
    pivot = subset.pivot_table(
        index='Nombre_X',
        columns='Nombre_Y',
        values='Spearman_r',
        aggfunc='first'
    )

    if len(pivot) > 0:
        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                    ax=ax, vmin=-0.5, vmax=0.5, annot_kws={'size': 8})
        ax.set_title(f'Riesgo {tipo_riesgo}', fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        plt.setp(ax.get_yticklabels(), fontsize=8)

plt.suptitle('Correlaciones: Gobernanza y Biodiversidad vs Riesgo Ambiental\n(645 municipios de Sao Paulo)',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/heatmap_correlaciones_v2.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: heatmap_correlaciones_v2.png")

# 8.2 Graficos de regresion con mejores predictores
fig2, axes2 = plt.subplots(2, 3, figsize=(16, 11))

colores_vuln = {'Baja': '#27ae60', 'Media': '#f39c12', 'Alta': '#c0392b'}

# Fila 1: Gobernanza (mejores predictores)
mejores_gob = {
    'SALUD': ('UAI_env', 'UAI Ambiental'),
    'CLIMA': ('UAI_Crisk', 'UAI Riesgo Clim.'),
    'NUTRICION': ('UAI_food', 'UAI Alimentacion')
}

vars_y_plot = [
    ('idx_carga_enfermedad', 'Carga Enfermedad'),
    ('idx_clima', 'Riesgo Climatico'),
    ('pol_deficit', 'Deficit Polinizacion')
]

# Determinar mejores predictores dinamicamente
for i, (var_y, nombre_y) in enumerate(vars_y_plot):
    ax = axes2[0, i]
    tipo = ['SALUD', 'CLIMA', 'NUTRICION'][i]

    # Buscar mejor predictor de gobernanza para esta variable
    subset_corr = df_corr[(df_corr['Variable_Y'] == var_y) & (df_corr['Predictor_Tipo'] == 'Gobernanza')]
    if len(subset_corr) > 0:
        mejor = subset_corr.loc[subset_corr['Spearman_r'].abs().idxmax()]
        var_x = mejor['Variable_X']
        nombre_x = mejor['Nombre_X']
        r_val = mejor['Spearman_r']
        p_val = mejor['p_value']
    else:
        var_x = 'idx_gobernanza'
        nombre_x = 'UAI General'
        r_val, p_val = 0, 1

    # Graficar por categoria de vulnerabilidad
    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset[var_x], subset[var_y],
                   c=colores_vuln[cat], alpha=0.5, label=f'Vuln. {cat}', s=25, edgecolor='white')

        # Linea de regresion
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax.plot(x_line, p(x_line), c=colores_vuln[cat], linewidth=2, linestyle='--', alpha=0.8)

    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    ax.set_xlabel(nombre_x, fontsize=10)
    ax.set_ylabel(nombre_y, fontsize=10)
    ax.set_title(f'{nombre_x} vs {nombre_y}\nr = {r_val:.3f} {sig}', fontsize=11)
    if i == 0:
        ax.legend(title='Vulnerabilidad', fontsize=8)

# Fila 2: Biodiversidad (mejores predictores)
for i, (var_y, nombre_y) in enumerate(vars_y_plot):
    ax = axes2[1, i]

    # Buscar mejor predictor de biodiversidad para esta variable
    subset_corr = df_corr[(df_corr['Variable_Y'] == var_y) & (df_corr['Predictor_Tipo'] == 'Biodiversidad')]
    if len(subset_corr) > 0:
        mejor = subset_corr.loc[subset_corr['Spearman_r'].abs().idxmax()]
        var_x = mejor['Variable_X']
        nombre_x = mejor['Nombre_X']
        r_val = mejor['Spearman_r']
        p_val = mejor['p_value']
    else:
        var_x = 'idx_biodiv'
        nombre_x = 'Indice Biodiv'
        r_val, p_val = 0, 1

    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset[var_x], subset[var_y],
                   c=colores_vuln[cat], alpha=0.5, label=f'Vuln. {cat}', s=25, edgecolor='white')

        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax.plot(x_line, p(x_line), c=colores_vuln[cat], linewidth=2, linestyle='--', alpha=0.8)

    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
    ax.set_xlabel(nombre_x, fontsize=10)
    ax.set_ylabel(nombre_y, fontsize=10)
    ax.set_title(f'{nombre_x} vs {nombre_y}\nr = {r_val:.3f} {sig}', fontsize=11)

plt.suptitle('Mejores Predictores de Riesgo Ambiental\n(modulados por vulnerabilidad socio-economica, n=645)',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/regresion_mejores_predictores_v2.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: regresion_mejores_predictores_v2.png")

# 8.3 Comparacion OLS vs Modelos Mixtos
if len(df_mixtos) > 0:
    fig3, ax3 = plt.subplots(figsize=(12, 6))

    # Preparar datos
    df_plot = df_mixtos.copy()
    df_plot['Variable'] = df_plot['Variable_X'] + '\n-> ' + df_plot['Variable_Y']

    x = np.arange(len(df_plot))
    width = 0.35

    bars1 = ax3.bar(x - width/2, df_plot['Beta_OLS'], width, label='OLS', color='#3498db', alpha=0.8)
    bars2 = ax3.bar(x + width/2, df_plot['Beta_Mixed'], width, label='Modelo Mixto', color='#e74c3c', alpha=0.8)

    ax3.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax3.set_xlabel('Relacion', fontsize=11)
    ax3.set_ylabel('Coeficiente (Beta estandarizado)', fontsize=11)
    ax3.set_title('Comparacion: OLS vs Modelo Mixto (Microregion como efecto aleatorio)\n' +
                  'ICC indica % de varianza explicada por la estructura jerarquica', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(df_plot['Variable'], fontsize=8, rotation=45, ha='right')
    ax3.legend()

    # Agregar ICC como texto
    for i, (_, row) in enumerate(df_plot.iterrows()):
        ax3.text(i, max(row['Beta_OLS'], row['Beta_Mixed']) + 0.02,
                 f'ICC={row["ICC"]:.2f}', ha='center', fontsize=8, color='gray')

    plt.tight_layout()
    plt.savefig(f"{PROJECT_ROOT}/outputs/figures/ols_vs_mixto_v2.png", dpi=150, bbox_inches='tight')
    print(f"   Guardado: ols_vs_mixto_v2.png")

# =============================================================================
# 9. RESUMEN DE HALLAZGOS
# =============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE HALLAZGOS PRINCIPALES")
print("=" * 80)

print("\n9.1 MEJORES PREDICTORES POR TIPO DE RIESGO:")
print("-" * 60)

for tipo in ['SALUD', 'CLIMA', 'NUTRICION']:
    print(f"\n   Riesgo {tipo}:")

    # Gobernanza
    gob = df_corr[(df_corr['Tipo_Riesgo'] == tipo) & (df_corr['Predictor_Tipo'] == 'Gobernanza')]
    if len(gob) > 0:
        mejor = gob.loc[gob['Spearman_r'].abs().idxmax()]
        direccion = "PROTECTOR (reduce riesgo)" if mejor['Spearman_r'] < 0 else "RIESGO (aumenta)"
        sig = "***" if mejor['p_value'] < 0.001 else "**" if mejor['p_value'] < 0.01 else "*"
        print(f"     Gobernanza: {mejor['Nombre_X']:25} r={mejor['Spearman_r']:+.3f}{sig} -> {direccion}")

    # Biodiversidad
    bio = df_corr[(df_corr['Tipo_Riesgo'] == tipo) & (df_corr['Predictor_Tipo'] == 'Biodiversidad')]
    if len(bio) > 0:
        mejor = bio.loc[bio['Spearman_r'].abs().idxmax()]
        direccion = "PROTECTOR (reduce riesgo)" if mejor['Spearman_r'] < 0 else "RIESGO (aumenta)"
        sig = "***" if mejor['p_value'] < 0.001 else "**" if mejor['p_value'] < 0.01 else "*"
        print(f"     Biodiversidad: {mejor['Nombre_X']:23} r={mejor['Spearman_r']:+.3f}{sig} -> {direccion}")

print("\n9.2 EFECTO DE LA ESTRUCTURA JERARQUICA (ICC):")
print("-" * 60)
if len(df_mixtos) > 0:
    icc_medio = df_mixtos['ICC'].mean()
    print(f"   ICC promedio: {icc_medio:.2f} ({icc_medio*100:.0f}% de varianza a nivel de microregion)")
    if icc_medio > 0.1:
        print("   -> Los modelos mixtos son importantes: existe estructura espacial significativa")
    else:
        print("   -> La estructura espacial es debil; OLS puede ser suficiente")

print("\n9.3 EFECTO MODULADOR DE LA VULNERABILIDAD:")
print("-" * 60)
if len(df_estrat) > 0:
    # Analizar si el efecto cambia por vulnerabilidad
    for var_y in df_estrat['Variable_Y'].unique():
        for var_x in df_estrat[df_estrat['Variable_Y'] == var_y]['Variable_X'].unique():
            vals = df_estrat[(df_estrat['Variable_Y'] == var_y) & (df_estrat['Variable_X'] == var_x)]
            if len(vals) == 3:
                r_baja = vals[vals['Vulnerabilidad'] == 'Baja']['r'].values[0]
                r_alta = vals[vals['Vulnerabilidad'] == 'Alta']['r'].values[0]

                if abs(r_alta) > abs(r_baja) * 1.5:
                    print(f"   {var_x} -> {var_y}: Efecto MAS FUERTE en alta vulnerabilidad")
                elif abs(r_baja) > abs(r_alta) * 1.5:
                    print(f"   {var_x} -> {var_y}: Efecto MAS FUERTE en baja vulnerabilidad")

print("\n" + "=" * 80)
print("Analisis completado. Archivos generados:")
print("  - outputs/correlaciones_exhaustivas_v2.csv")
print("  - outputs/modelos_mixtos_v2.csv")
print("  - outputs/correlaciones_estratificadas_v2.csv")
print("  - outputs/figures/heatmap_correlaciones_v2.png")
print("  - outputs/figures/regresion_mejores_predictores_v2.png")
print("  - outputs/figures/ols_vs_mixto_v2.png")
print("=" * 80)
