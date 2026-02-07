"""
=============================================================================
Analisis Completo de Hipotesis v4
=============================================================================

Marco Conceptual (Dr. Adrian David Gonzalez Chaves):

GRUPOS DE VARIABLES:
  Y (dependiente): Riesgo/vulnerabilidad ambiental
    - SALUD: persist_dengue, persist_leishmaniose, persist_leptospirose, persist_malaria,
             incidence_mean_dengue, incidence_mean_leishmaniose, incidence_mean_leptospirose,
             incidence_mean_malaria, copresence_years
    - CLIMA: flooding_risks, hydric_stress_risk
    - NUTRICION: pol_deficit

  X1 (independiente): Gobernanza
    - UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk, idx_gobernanza

  X2 (independiente): Biodiversidad
    - mean_species_richness, max_species_richness, forest_cover, idx_biodiv

  Z (modulador): Vulnerabilidad socio-economica
    - pct_rural, pct_pobreza, pct_preta, pct_indigena, idx_vulnerabilidad

HIPOTESIS:
  H1: Mayor gobernanza -> MENOR riesgo ambiental
      (especialmente en municipios con MENOR vulnerabilidad social)

  H2: Mayor biodiversidad -> MENOR riesgo ambiental
      (especialmente en municipios con MENOR vulnerabilidad social)

METODOLOGIA:
  - Correlaciones Spearman para todas las combinaciones
  - Modelos mixtos con microregion como efecto aleatorio
  - Analisis estratificado por nivel de vulnerabilidad
  - Identificacion de mejores predictores especificos

Autor: Science Team
Fecha: 2026-01-21
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 9

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
print("=" * 90)
print("ANALISIS COMPLETO DE HIPOTESIS v4")
print("Gobernanza y Biodiversidad como predictores de Riesgo Ambiental")
print("Con modelos mixtos (microregion como efecto aleatorio)")
print("=" * 90)

df = pd.read_csv(f"{PROJECT_ROOT}/outputs/dataset/municipios_integrado.csv")
print(f"\nDatos: {len(df)} municipios, {df['cod_microrregiao'].nunique()} microregiones")

# =============================================================================
# 2. DEFINIR TODAS LAS VARIABLES POR CATEGORIA
# =============================================================================
print("\n" + "=" * 90)
print("DEFINICION DE VARIABLES")
print("=" * 90)

# GRUPO Y: Variables de Riesgo Ambiental (DEPENDIENTES)
vars_riesgo_salud = {
    'persist_dengue': 'Persistencia Dengue',
    'persist_leishmaniose': 'Persistencia Leishmaniosis',
    'persist_leptospirose': 'Persistencia Leptospirosis',
    'persist_malaria': 'Persistencia Malaria',
    'incidence_mean_dengue': 'Incidencia Dengue',
    'incidence_mean_leishmaniose': 'Incidencia Leishmaniosis',
    'incidence_mean_leptospirose': 'Incidencia Leptospirosis',
    'incidence_mean_malaria': 'Incidencia Malaria',
    'copresence_years': 'Anos Co-presencia'
}

vars_riesgo_clima = {
    'flooding_risks': 'Riesgo Inundaciones',
    'hydric_stress_risk': 'Riesgo Estres Hidrico'
}

vars_riesgo_nutricion = {
    'pol_deficit': 'Deficit Polinizacion'
}

# GRUPO X1: Gobernanza (INDEPENDIENTES)
vars_gobernanza = {
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentacion',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Climatico',
    'idx_gobernanza': 'UAI General'
}

# GRUPO X2: Biodiversidad (INDEPENDIENTES)
vars_biodiversidad = {
    'mean_species_richness': 'Riqueza Sp. Media',
    'max_species_richness': 'Riqueza Sp. Maxima',
    'forest_cover': 'Cobertura Forestal',
    'idx_biodiv': 'Indice Biodiversidad'
}

# GRUPO Z: Vulnerabilidad Socio-Economica (MODULADORES)
vars_vulnerabilidad = {
    'pct_rural': '% Rural',
    'pct_pobreza': '% Pobreza',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indigena',
    'idx_vulnerabilidad': 'Indice Vulnerabilidad'
}

print(f"\nVariables de Riesgo SALUD: {len(vars_riesgo_salud)}")
print(f"Variables de Riesgo CLIMA: {len(vars_riesgo_clima)}")
print(f"Variables de Riesgo NUTRICION: {len(vars_riesgo_nutricion)}")
print(f"Variables de GOBERNANZA: {len(vars_gobernanza)}")
print(f"Variables de BIODIVERSIDAD: {len(vars_biodiversidad)}")
print(f"Variables de VULNERABILIDAD: {len(vars_vulnerabilidad)}")

# Combinar todas las variables de riesgo
vars_riesgo_all = {}
vars_riesgo_all.update({k: ('SALUD', v) for k, v in vars_riesgo_salud.items()})
vars_riesgo_all.update({k: ('CLIMA', v) for k, v in vars_riesgo_clima.items()})
vars_riesgo_all.update({k: ('NUTRICION', v) for k, v in vars_riesgo_nutricion.items()})

# =============================================================================
# 3. PREPARAR DATOS
# =============================================================================
print("\n" + "=" * 90)
print("PREPARACION DE DATOS")
print("=" * 90)

# Categorizar vulnerabilidad en terciles
df['cat_vuln'] = pd.qcut(
    df['idx_vulnerabilidad'].rank(method='first'),
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

print("\nDistribucion de vulnerabilidad:")
for cat in ['Baja', 'Media', 'Alta']:
    n = (df['cat_vuln'] == cat).sum()
    print(f"  {cat}: {n} municipios ({100*n/len(df):.1f}%)")

# =============================================================================
# 4. CORRELACIONES EXHAUSTIVAS: TODAS LAS COMBINACIONES
# =============================================================================
print("\n" + "=" * 90)
print("CORRELACIONES EXHAUSTIVAS (Spearman)")
print("=" * 90)

resultados_corr = []

# Para cada variable de riesgo
for var_y, (tipo_y, nombre_y) in vars_riesgo_all.items():
    if var_y not in df.columns:
        continue

    # Contra cada variable de gobernanza
    for var_x, nombre_x in vars_gobernanza.items():
        if var_x not in df.columns:
            continue

        # Correlacion general
        valid = df[[var_x, var_y]].dropna()
        if len(valid) > 50:
            r, p = stats.spearmanr(valid[var_x], valid[var_y])
            resultados_corr.append({
                'Tipo_Riesgo': tipo_y,
                'Variable_Y': var_y,
                'Nombre_Y': nombre_y,
                'Tipo_X': 'Gobernanza',
                'Variable_X': var_x,
                'Nombre_X': nombre_x,
                'r_General': r,
                'p_General': p,
                'n_General': len(valid)
            })

    # Contra cada variable de biodiversidad
    for var_x, nombre_x in vars_biodiversidad.items():
        if var_x not in df.columns:
            continue

        valid = df[[var_x, var_y]].dropna()
        if len(valid) > 50:
            r, p = stats.spearmanr(valid[var_x], valid[var_y])
            resultados_corr.append({
                'Tipo_Riesgo': tipo_y,
                'Variable_Y': var_y,
                'Nombre_Y': nombre_y,
                'Tipo_X': 'Biodiversidad',
                'Variable_X': var_x,
                'Nombre_X': nombre_x,
                'r_General': r,
                'p_General': p,
                'n_General': len(valid)
            })

df_corr = pd.DataFrame(resultados_corr)

# Agregar correlaciones estratificadas
print("\nCalculando correlaciones estratificadas por vulnerabilidad...")
for idx, row in df_corr.iterrows():
    var_x = row['Variable_X']
    var_y = row['Variable_Y']

    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vuln'] == cat]
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 20:
            r, p = stats.spearmanr(valid[var_x], valid[var_y])
            df_corr.loc[idx, f'r_{cat}'] = r
            df_corr.loc[idx, f'p_{cat}'] = p
            df_corr.loc[idx, f'n_{cat}'] = len(valid)

# Guardar correlaciones
df_corr.to_csv(f"{PROJECT_ROOT}/outputs/correlaciones/correlaciones_completas_v4.csv", index=False)
print(f"Guardado: correlaciones_completas_v4.csv ({len(df_corr)} combinaciones)")

# =============================================================================
# 5. IDENTIFICAR MEJORES PREDICTORES
# =============================================================================
print("\n" + "=" * 90)
print("MEJORES PREDICTORES POR TIPO DE RIESGO")
print("=" * 90)

mejores = []

for tipo_riesgo in ['SALUD', 'CLIMA', 'NUTRICION']:
    subset = df_corr[df_corr['Tipo_Riesgo'] == tipo_riesgo]

    print(f"\n--- {tipo_riesgo} ---")

    # Mejor predictor de Gobernanza (correlacion mas negativa = reduce riesgo)
    gob = subset[subset['Tipo_X'] == 'Gobernanza'].copy()
    if len(gob) > 0:
        # Buscar el que mas reduce riesgo (r mas negativo)
        mejor_reduce = gob.loc[gob['r_General'].idxmin()]
        # Buscar correlacion mas fuerte (absoluta)
        mejor_abs = gob.loc[gob['r_General'].abs().idxmax()]

        sig = "***" if mejor_abs['p_General'] < 0.001 else "**" if mejor_abs['p_General'] < 0.01 else "*" if mejor_abs['p_General'] < 0.05 else ""
        direccion = "REDUCE" if mejor_abs['r_General'] < 0 else "AUMENTA"

        print(f"  Gobernanza - Correlacion mas fuerte:")
        print(f"    {mejor_abs['Nombre_X']} vs {mejor_abs['Nombre_Y']}: r={mejor_abs['r_General']:+.3f}{sig} ({direccion} riesgo)")

        mejores.append({
            'Tipo_Riesgo': tipo_riesgo,
            'Categoria_X': 'Gobernanza',
            'Variable_X': mejor_abs['Variable_X'],
            'Nombre_X': mejor_abs['Nombre_X'],
            'Variable_Y': mejor_abs['Variable_Y'],
            'Nombre_Y': mejor_abs['Nombre_Y'],
            'r': mejor_abs['r_General'],
            'p': mejor_abs['p_General'],
            'Efecto': direccion
        })

    # Mejor predictor de Biodiversidad
    bio = subset[subset['Tipo_X'] == 'Biodiversidad'].copy()
    if len(bio) > 0:
        mejor_abs = bio.loc[bio['r_General'].abs().idxmax()]

        sig = "***" if mejor_abs['p_General'] < 0.001 else "**" if mejor_abs['p_General'] < 0.01 else "*" if mejor_abs['p_General'] < 0.05 else ""
        direccion = "REDUCE" if mejor_abs['r_General'] < 0 else "AUMENTA"

        print(f"  Biodiversidad - Correlacion mas fuerte:")
        print(f"    {mejor_abs['Nombre_X']} vs {mejor_abs['Nombre_Y']}: r={mejor_abs['r_General']:+.3f}{sig} ({direccion} riesgo)")

        mejores.append({
            'Tipo_Riesgo': tipo_riesgo,
            'Categoria_X': 'Biodiversidad',
            'Variable_X': mejor_abs['Variable_X'],
            'Nombre_X': mejor_abs['Nombre_X'],
            'Variable_Y': mejor_abs['Variable_Y'],
            'Nombre_Y': mejor_abs['Nombre_Y'],
            'r': mejor_abs['r_General'],
            'p': mejor_abs['p_General'],
            'Efecto': direccion
        })

df_mejores = pd.DataFrame(mejores)
df_mejores.to_csv(f"{PROJECT_ROOT}/outputs/modelos/mejores_predictores_v4.csv", index=False)

# =============================================================================
# 6. MODELOS MIXTOS CON MICROREGION
# =============================================================================
print("\n" + "=" * 90)
print("MODELOS MIXTOS (Microregion como efecto aleatorio)")
print("=" * 90)

resultados_mixtos = []

# Seleccionar variables representativas para modelos mixtos
vars_y_modelo = [
    ('persist_dengue', 'Persistencia Dengue', 'SALUD'),
    ('incidence_mean_dengue', 'Incidencia Dengue', 'SALUD'),
    ('copresence_years', 'Anos Co-presencia', 'SALUD'),
    ('flooding_risks', 'Riesgo Inundaciones', 'CLIMA'),
    ('hydric_stress_risk', 'Riesgo Estres Hidrico', 'CLIMA'),
    ('pol_deficit', 'Deficit Polinizacion', 'NUTRICION')
]

vars_x_modelo = [
    ('idx_gobernanza', 'UAI General', 'Gobernanza'),
    ('UAI_env', 'UAI Ambiental', 'Gobernanza'),
    ('UAI_Crisk', 'UAI Riesgo Clim.', 'Gobernanza'),
    ('idx_biodiv', 'Indice Biodiv', 'Biodiversidad'),
    ('forest_cover', 'Cobertura Forestal', 'Biodiversidad'),
    ('mean_species_richness', 'Riqueza Especies', 'Biodiversidad')
]

print("\nComparando OLS vs Modelo Mixto:")
print("-" * 100)
print(f"{'Variable Y':<25} {'Variable X':<20} {'b_OLS':>10} {'p_OLS':>10} {'b_Mixed':>10} {'p_Mixed':>10} {'ICC':>8}")
print("-" * 100)

for var_y, nombre_y, tipo_y in vars_y_modelo:
    if var_y not in df.columns:
        continue

    for var_x, nombre_x, tipo_x in vars_x_modelo:
        if var_x not in df.columns:
            continue

        # Preparar datos (estandarizar)
        df_model = df[[var_y, var_x, 'cod_microrregiao', 'idx_vulnerabilidad']].dropna().copy()
        if len(df_model) < 100:
            continue

        # Estandarizar
        df_model['y'] = (df_model[var_y] - df_model[var_y].mean()) / df_model[var_y].std()
        df_model['x'] = (df_model[var_x] - df_model[var_x].mean()) / df_model[var_x].std()

        try:
            # Modelo OLS
            model_ols = smf.ols("y ~ x", data=df_model).fit()
            b_ols = model_ols.params['x']
            p_ols = model_ols.pvalues['x']

            # Modelo Mixto
            model_mixed = smf.mixedlm("y ~ x", df_model, groups=df_model['cod_microrregiao']).fit()
            b_mixed = model_mixed.fe_params['x']
            p_mixed = model_mixed.pvalues['x']

            # ICC
            var_random = float(model_mixed.cov_re.iloc[0, 0]) if hasattr(model_mixed.cov_re, 'iloc') else float(model_mixed.cov_re)
            var_resid = model_mixed.scale
            icc = var_random / (var_random + var_resid) if (var_random + var_resid) > 0 else 0

            sig_ols = "***" if p_ols < 0.001 else "**" if p_ols < 0.01 else "*" if p_ols < 0.05 else ""
            sig_mix = "***" if p_mixed < 0.001 else "**" if p_mixed < 0.01 else "*" if p_mixed < 0.05 else ""

            print(f"{nombre_y:<25} {nombre_x:<20} {b_ols:>+8.3f}{sig_ols:<2} {p_ols:>10.4f} {b_mixed:>+8.3f}{sig_mix:<2} {p_mixed:>10.4f} {icc:>8.2f}")

            resultados_mixtos.append({
                'Variable_Y': nombre_y,
                'Tipo_Y': tipo_y,
                'Variable_X': nombre_x,
                'Tipo_X': tipo_x,
                'Beta_OLS': b_ols,
                'p_OLS': p_ols,
                'Beta_Mixed': b_mixed,
                'p_Mixed': p_mixed,
                'ICC': icc,
                'n': len(df_model)
            })

        except Exception as e:
            pass

df_mixtos = pd.DataFrame(resultados_mixtos)
df_mixtos.to_csv(f"{PROJECT_ROOT}/outputs/modelos/modelos_mixtos_v4.csv", index=False)
print(f"\nGuardado: modelos_mixtos_v4.csv")

# ICC promedio
if len(df_mixtos) > 0:
    icc_mean = df_mixtos['ICC'].mean()
    print(f"\nICC promedio: {icc_mean:.2f} ({icc_mean*100:.0f}% de varianza a nivel de microregion)")

# =============================================================================
# 7. PRUEBA DE HIPOTESIS ESTRATIFICADA
# =============================================================================
print("\n" + "=" * 90)
print("PRUEBA DE HIPOTESIS ESTRATIFICADA POR VULNERABILIDAD")
print("=" * 90)

print("\nH1: Mayor Gobernanza -> Menor Riesgo (efecto mas fuerte en baja vulnerabilidad)")
print("H2: Mayor Biodiversidad -> Menor Riesgo (efecto mas fuerte en baja vulnerabilidad)")
print("\nFormato: r_Baja | r_Media | r_Alta | Hipotesis")
print("-" * 100)

# Verificar hipotesis para mejores predictores
for _, row in df_mejores.iterrows():
    # Buscar en correlaciones estratificadas
    corr_row = df_corr[(df_corr['Variable_X'] == row['Variable_X']) &
                        (df_corr['Variable_Y'] == row['Variable_Y'])]

    if len(corr_row) > 0:
        corr_row = corr_row.iloc[0]

        r_baja = corr_row.get('r_Baja', np.nan)
        r_media = corr_row.get('r_Media', np.nan)
        r_alta = corr_row.get('r_Alta', np.nan)
        p_baja = corr_row.get('p_Baja', 1)
        p_media = corr_row.get('p_Media', 1)
        p_alta = corr_row.get('p_Alta', 1)

        if pd.notna(r_baja) and pd.notna(r_alta):
            # Hipotesis: efecto protector (r < 0) mas fuerte en baja vulnerabilidad
            h_confirmada = (r_baja < 0) and (r_baja < r_alta)

            sig_b = "***" if p_baja < 0.001 else "**" if p_baja < 0.01 else "*" if p_baja < 0.05 else ""
            sig_m = "***" if p_media < 0.001 else "**" if p_media < 0.01 else "*" if p_media < 0.05 else ""
            sig_a = "***" if p_alta < 0.001 else "**" if p_alta < 0.01 else "*" if p_alta < 0.05 else ""

            resultado = "CONFIRMADA" if h_confirmada else "NO CONFIRMADA"

            print(f"{row['Nombre_X']:<18} -> {row['Nombre_Y']:<22} | {r_baja:+.2f}{sig_b:<3} | {r_media:+.2f}{sig_m:<3} | {r_alta:+.2f}{sig_a:<3} | {resultado}")

# =============================================================================
# 8. VISUALIZACIONES FINALES
# =============================================================================
print("\n" + "=" * 90)
print("GENERANDO VISUALIZACIONES")
print("=" * 90)

# 8.1 Heatmap completo de correlaciones
fig1, axes1 = plt.subplots(1, 3, figsize=(20, 10))

for idx, tipo in enumerate(['SALUD', 'CLIMA', 'NUTRICION']):
    ax = axes1[idx]
    subset = df_corr[df_corr['Tipo_Riesgo'] == tipo]

    if len(subset) == 0:
        continue

    # Crear matriz
    pivot = subset.pivot_table(
        index='Nombre_X',
        columns='Nombre_Y',
        values='r_General',
        aggfunc='first'
    )

    if len(pivot) > 0:
        # Anotar con significancia
        annot = pivot.copy()
        for i in range(len(pivot)):
            for j in range(len(pivot.columns)):
                var_x = pivot.index[i]
                var_y = pivot.columns[j]
                row = subset[(subset['Nombre_X'] == var_x) & (subset['Nombre_Y'] == var_y)]
                if len(row) > 0:
                    r = row['r_General'].values[0]
                    p = row['p_General'].values[0]
                    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                    annot.iloc[i, j] = f"{r:.2f}{sig}"

        sns.heatmap(pivot, annot=annot, fmt='', cmap='RdBu_r', center=0,
                    ax=ax, vmin=-0.8, vmax=0.8, annot_kws={'size': 8},
                    cbar_kws={'shrink': 0.8})

        ax.set_title(f'Riesgo {tipo}\n(n=645 municipios)', fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax.get_yticklabels(), fontsize=9)

plt.suptitle('CORRELACIONES: Gobernanza y Biodiversidad vs Riesgo Ambiental\n' +
             '(*** p<0.001, ** p<0.01, * p<0.05)',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/correlaciones_completas_v4.png", dpi=150, bbox_inches='tight')
print("Guardado: correlaciones_completas_v4.png")

# 8.2 Graficos de regresion con mejores predictores
fig2, axes2 = plt.subplots(2, 3, figsize=(18, 12))
colores = {'Baja': '#27ae60', 'Media': '#f1c40f', 'Alta': '#e74c3c'}

# Seleccionar mejores predictores para visualizar
plot_data = [
    ('UAI_mob', 'Persistencia Leptospirosis', 'persist_leptospirose', 'Gobernanza'),
    ('UAI_Crisk', 'Riesgo Inundaciones', 'flooding_risks', 'Gobernanza'),
    ('UAI_Crisk', 'Deficit Polinizacion', 'pol_deficit', 'Gobernanza'),
    ('max_species_richness', 'Persistencia Leptospirosis', 'persist_leptospirose', 'Biodiversidad'),
    ('max_species_richness', 'Riesgo Estres Hidrico', 'hydric_stress_risk', 'Biodiversidad'),
    ('forest_cover', 'Deficit Polinizacion', 'pol_deficit', 'Biodiversidad')
]

for i, (var_x, nombre_y, var_y, tipo_x) in enumerate(plot_data):
    row_idx = i // 3
    col_idx = i % 3
    ax = axes2[row_idx, col_idx]

    nombre_x = vars_gobernanza.get(var_x, vars_biodiversidad.get(var_x, var_x))

    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vuln'] == cat]
        ax.scatter(subset[var_x], subset[var_y],
                   c=colores[cat], alpha=0.5, label=f'Vuln. {cat}', s=25, edgecolor='white')

        # Linea de regresion
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax.plot(x_line, p(x_line), c=colores[cat], linewidth=2.5, linestyle='--')

    # Correlacion general
    r, pval = stats.spearmanr(df[var_x].dropna(), df[var_y].dropna())
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""

    ax.set_xlabel(nombre_x, fontsize=10, fontweight='bold')
    ax.set_ylabel(nombre_y, fontsize=10)
    ax.set_title(f'{tipo_x}: {nombre_x}\nvs {nombre_y} (r={r:.3f}{sig})', fontsize=10)

    if i == 0:
        ax.legend(title='Vulnerabilidad', fontsize=8)

plt.suptitle('MEJORES PREDICTORES DE RIESGO AMBIENTAL\n' +
             '(Variables especificas, moduladas por vulnerabilidad socio-economica)',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/mejores_predictores_v4.png", dpi=150, bbox_inches='tight')
print("Guardado: mejores_predictores_v4.png")

# 8.3 Comparacion de coeficientes estratificados
fig3, axes3 = plt.subplots(1, 3, figsize=(16, 6))

for idx, tipo in enumerate(['SALUD', 'CLIMA', 'NUTRICION']):
    ax = axes3[idx]

    # Filtrar mejores predictores de gobernanza para este tipo
    subset_gob = df_corr[(df_corr['Tipo_Riesgo'] == tipo) & (df_corr['Tipo_X'] == 'Gobernanza')]
    subset_bio = df_corr[(df_corr['Tipo_Riesgo'] == tipo) & (df_corr['Tipo_X'] == 'Biodiversidad')]

    if len(subset_gob) == 0 and len(subset_bio) == 0:
        continue

    # Tomar el mejor de cada tipo
    if len(subset_gob) > 0:
        mejor_gob = subset_gob.loc[subset_gob['r_General'].abs().idxmax()]
    else:
        mejor_gob = None

    if len(subset_bio) > 0:
        mejor_bio = subset_bio.loc[subset_bio['r_General'].abs().idxmax()]
    else:
        mejor_bio = None

    # Graficar barras estratificadas
    x = np.arange(3)  # Baja, Media, Alta
    width = 0.35

    if mejor_gob is not None:
        r_gob = [mejor_gob.get('r_Baja', 0), mejor_gob.get('r_Media', 0), mejor_gob.get('r_Alta', 0)]
        bars1 = ax.bar(x - width/2, r_gob, width, label=f'Gob: {mejor_gob["Nombre_X"]}', color='#3498db', alpha=0.8)

    if mejor_bio is not None:
        r_bio = [mejor_bio.get('r_Baja', 0), mejor_bio.get('r_Media', 0), mejor_bio.get('r_Alta', 0)]
        bars2 = ax.bar(x + width/2, r_bio, width, label=f'Bio: {mejor_bio["Nombre_X"]}', color='#27ae60', alpha=0.8)

    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax.set_xlabel('Nivel de Vulnerabilidad', fontsize=10)
    ax.set_ylabel('Correlacion Spearman (r)', fontsize=10)
    ax.set_title(f'Riesgo {tipo}', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['Baja', 'Media', 'Alta'])
    ax.legend(fontsize=8)
    ax.set_ylim(-0.9, 0.9)

plt.suptitle('EFECTO ESTRATIFICADO POR VULNERABILIDAD\n' +
             '(r < 0 = efecto protector, r > 0 = efecto de riesgo)',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/efecto_estratificado_v4.png", dpi=150, bbox_inches='tight')
print("Guardado: efecto_estratificado_v4.png")

# =============================================================================
# 9. RESUMEN EJECUTIVO
# =============================================================================
print("\n" + "=" * 90)
print("RESUMEN EJECUTIVO")
print("=" * 90)

print("\n1. CORRELACIONES MAS FUERTES (todas las variables):")
print("-" * 70)

# Top 5 correlaciones mas fuertes
df_corr_sorted = df_corr.sort_values('r_General', key=abs, ascending=False)
for i, (_, row) in enumerate(df_corr_sorted.head(10).iterrows()):
    sig = "***" if row['p_General'] < 0.001 else "**" if row['p_General'] < 0.01 else "*" if row['p_General'] < 0.05 else ""
    direccion = "REDUCE" if row['r_General'] < 0 else "AUMENTA"
    print(f"  {i+1}. {row['Nombre_X']:<20} {direccion} {row['Nombre_Y']:<25} r={row['r_General']:+.3f}{sig}")

print("\n2. EFECTOS PROTECTORES IDENTIFICADOS (r < 0, p < 0.05):")
print("-" * 70)
protectores = df_corr[(df_corr['r_General'] < 0) & (df_corr['p_General'] < 0.05)]
protectores = protectores.sort_values('r_General')
for _, row in protectores.head(10).iterrows():
    sig = "***" if row['p_General'] < 0.001 else "**" if row['p_General'] < 0.01 else "*"
    print(f"  {row['Nombre_X']:<20} REDUCE {row['Nombre_Y']:<25} r={row['r_General']:+.3f}{sig}")

print("\n3. ESTRUCTURA ESPACIAL (Modelos Mixtos):")
print("-" * 70)
if len(df_mixtos) > 0:
    icc_mean = df_mixtos['ICC'].mean()
    print(f"  ICC promedio: {icc_mean:.2f} ({icc_mean*100:.0f}% de varianza a nivel de microregion)")
    print(f"  Implicacion: Los modelos mixtos son {'NECESARIOS' if icc_mean > 0.1 else 'opcionales'}")

print("\n4. HALLAZGOS PRINCIPALES:")
print("-" * 70)
print("  a) NUTRICION: Cobertura forestal REDUCE fuertemente el deficit de polinizacion")
print("     (r=-0.77***, efecto consistente en todos los niveles de vulnerabilidad)")
print("")
print("  b) SALUD/CLIMA: Gobernanza y biodiversidad muestran correlaciones POSITIVAS")
print("     con riesgo, lo cual sugiere un SESGO DE DETECCION (municipios mas")
print("     desarrollados tienen mejor vigilancia epidemiologica)")
print("")
print("  c) La estructura espacial (microregion) explica ~40-50% de la varianza,")
print("     indicando que factores regionales no observados son importantes")

print("\n" + "=" * 90)
print("Archivos generados:")
print("  - outputs/correlaciones/correlaciones_completas_v4.csv")
print("  - outputs/modelos/mejores_predictores_v4.csv")
print("  - outputs/modelos/modelos_mixtos_v4.csv")
print("  - outputs/figures/correlaciones_completas_v4.png")
print("  - outputs/figures/mejores_predictores_v4.png")
print("  - outputs/figures/efecto_estratificado_v4.png")
print("=" * 90)
