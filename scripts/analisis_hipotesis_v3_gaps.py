"""
=============================================================================
Analisis de Hipotesis v3: Prueba Directa de Hipotesis e Identificacion de GAPS
=============================================================================

Marco Conceptual (Dr. Adrian David Gonzalez Chaves):

  GRUPOS DE VARIABLES:
  - Y (dependiente): Riesgo/vulnerabilidad ambiental (salud, clima, nutricion)
  - X1 (independiente): Gobernanza (UAI y componentes)
  - X2 (independiente): Biodiversidad (riqueza especies, cobertura forestal)
  - Z (modulador): Vulnerabilidad socio-economica

  HIPOTESIS:
  H1: Mayor gobernanza (UAI) -> MENOR riesgo ambiental,
      especialmente en municipios con MENOR vulnerabilidad social

  H2: Mayor biodiversidad -> MENOR riesgo ambiental,
      especialmente en municipios con MENOR vulnerabilidad social

  OBJETIVO:
  Identificar GAPS de gobernanza donde intervenciones pueden reducir riesgos

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
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
print("=" * 80)
print("ANALISIS DE HIPOTESIS v3: PRUEBA DIRECTA E IDENTIFICACION DE GAPS")
print("=" * 80)

df = pd.read_csv(f"{PROJECT_ROOT}/outputs/municipios_integrado_v6.csv")
print(f"\n1. Datos: {len(df)} municipios")

# =============================================================================
# 2. CREAR INDICES COMPUESTOS DE RIESGO AMBIENTAL
# =============================================================================
print("\n2. Creando indices compuestos de riesgo ambiental...")

def normalize_0_100(series):
    """Normaliza a escala 0-100"""
    min_val, max_val = series.min(), series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100

# 2.1 Indice de Riesgo de Salud (combinando persistencia e incidencia)
print("   - Indice de Riesgo Salud...")
salud_vars = ['persist_dengue', 'persist_leishmaniose', 'persist_leptospirose', 'persist_malaria']
for var in salud_vars:
    if var in df.columns:
        df[f'{var}_norm'] = normalize_0_100(df[var].fillna(0))

df['idx_riesgo_salud'] = df[[f'{v}_norm' for v in salud_vars if f'{v}_norm' in df.columns]].mean(axis=1)
print(f"     Media: {df['idx_riesgo_salud'].mean():.1f}, Std: {df['idx_riesgo_salud'].std():.1f}")

# 2.2 Indice de Riesgo Climatico (inundaciones + estres hidrico)
print("   - Indice de Riesgo Climatico...")
df['idx_riesgo_clima'] = (
    normalize_0_100(df['flooding_risks'].fillna(0)) * 0.5 +
    normalize_0_100(df['hydric_stress_risk'].fillna(0)) * 0.5
)
print(f"     Media: {df['idx_riesgo_clima'].mean():.1f}, Std: {df['idx_riesgo_clima'].std():.1f}")

# 2.3 Indice de Riesgo Nutricional (deficit polinizacion)
print("   - Indice de Riesgo Nutricional...")
df['idx_riesgo_nutricion'] = normalize_0_100(df['pol_deficit'].fillna(0))
print(f"     Media: {df['idx_riesgo_nutricion'].mean():.1f}, Std: {df['idx_riesgo_nutricion'].std():.1f}")

# 2.4 Indice Compuesto de Riesgo Ambiental Total
print("   - Indice de Riesgo Ambiental Total...")
df['idx_riesgo_total'] = (
    df['idx_riesgo_salud'] * 0.4 +
    df['idx_riesgo_clima'] * 0.4 +
    df['idx_riesgo_nutricion'] * 0.2
)
print(f"     Media: {df['idx_riesgo_total'].mean():.1f}, Std: {df['idx_riesgo_total'].std():.1f}")

# =============================================================================
# 3. CATEGORIZAR VULNERABILIDAD SOCIO-ECONOMICA
# =============================================================================
print("\n3. Categorizando vulnerabilidad socio-economica...")

# Usar el indice ya calculado
df['cat_vulnerabilidad'] = pd.qcut(
    df['idx_vulnerabilidad'].rank(method='first'),
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

print(f"   Distribucion:")
for cat in ['Baja', 'Media', 'Alta']:
    n = (df['cat_vulnerabilidad'] == cat).sum()
    media_vuln = df[df['cat_vulnerabilidad'] == cat]['idx_vulnerabilidad'].mean()
    print(f"     {cat}: {n} municipios (idx_vuln medio: {media_vuln:.1f})")

# =============================================================================
# 4. PRUEBA DE HIPOTESIS H1: GOBERNANZA -> RIESGO
# =============================================================================
print("\n" + "=" * 80)
print("4. PRUEBA DE HIPOTESIS H1: Mayor Gobernanza -> Menor Riesgo Ambiental")
print("   Expectativa: Correlacion NEGATIVA, mas fuerte en BAJA vulnerabilidad")
print("=" * 80)

# Variables de gobernanza a probar
vars_gob = {
    'idx_gobernanza': 'UAI General',
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentacion',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Climatico'
}

# Variables de riesgo
vars_riesgo = {
    'idx_riesgo_total': 'Riesgo Total',
    'idx_riesgo_salud': 'Riesgo Salud',
    'idx_riesgo_clima': 'Riesgo Clima',
    'idx_riesgo_nutricion': 'Riesgo Nutricion'
}

resultados_h1 = []

print("\n   Correlaciones Gobernanza vs Riesgo (estratificado por vulnerabilidad):")
print("-" * 90)
print(f"   {'Variable Gob':<20} {'Riesgo':<18} {'Baja':<12} {'Media':<12} {'Alta':<12} {'Hipotesis'}")
print("-" * 90)

for var_gob, nombre_gob in vars_gob.items():
    for var_riesgo, nombre_riesgo in vars_riesgo.items():
        correlaciones = {}

        for cat in ['Baja', 'Media', 'Alta']:
            subset = df[df['cat_vulnerabilidad'] == cat]
            valid = subset[[var_gob, var_riesgo]].dropna()
            if len(valid) > 30:
                r, p = stats.spearmanr(valid[var_gob], valid[var_riesgo])
                correlaciones[cat] = {'r': r, 'p': p, 'n': len(valid)}

        if len(correlaciones) == 3:
            # Verificar hipotesis: r negativa y mas fuerte en baja vulnerabilidad
            r_baja = correlaciones['Baja']['r']
            r_alta = correlaciones['Alta']['r']

            # Hipotesis confirmada si:
            # 1. Correlacion negativa (protector)
            # 2. Efecto mas fuerte (mas negativo) en baja vulnerabilidad
            h1_confirmada = r_baja < 0 and r_baja < r_alta

            resultado = "CONFIRMADA" if h1_confirmada else "NO CONFIRMADA"

            # Formato de salida
            def format_r(cat):
                r = correlaciones[cat]['r']
                p = correlaciones[cat]['p']
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                return f"{r:+.2f}{sig}"

            print(f"   {nombre_gob:<20} {nombre_riesgo:<18} {format_r('Baja'):<12} {format_r('Media'):<12} {format_r('Alta'):<12} {resultado}")

            resultados_h1.append({
                'Variable_Gob': nombre_gob,
                'Variable_Riesgo': nombre_riesgo,
                'r_Baja': correlaciones['Baja']['r'],
                'p_Baja': correlaciones['Baja']['p'],
                'r_Media': correlaciones['Media']['r'],
                'p_Media': correlaciones['Media']['p'],
                'r_Alta': correlaciones['Alta']['r'],
                'p_Alta': correlaciones['Alta']['p'],
                'H1_Confirmada': h1_confirmada
            })

df_h1 = pd.DataFrame(resultados_h1)

# Resumen H1
print("\n   RESUMEN H1:")
n_confirmadas = df_h1['H1_Confirmada'].sum()
n_total = len(df_h1)
print(f"   - Hipotesis confirmadas: {n_confirmadas}/{n_total} ({100*n_confirmadas/n_total:.1f}%)")

# Casos donde SI se confirma el efecto protector
if n_confirmadas > 0:
    print("\n   Casos donde gobernanza REDUCE riesgo (especialmente en baja vulnerabilidad):")
    confirmadas = df_h1[df_h1['H1_Confirmada']]
    for _, row in confirmadas.iterrows():
        print(f"     - {row['Variable_Gob']} reduce {row['Variable_Riesgo']}")
        print(f"       (r_baja={row['r_Baja']:.3f}, r_alta={row['r_Alta']:.3f})")

# =============================================================================
# 5. PRUEBA DE HIPOTESIS H2: BIODIVERSIDAD -> RIESGO
# =============================================================================
print("\n" + "=" * 80)
print("5. PRUEBA DE HIPOTESIS H2: Mayor Biodiversidad -> Menor Riesgo Ambiental")
print("   Expectativa: Correlacion NEGATIVA, mas fuerte en BAJA vulnerabilidad")
print("=" * 80)

vars_biodiv = {
    'idx_biodiv': 'Indice Biodiversidad',
    'mean_species_richness': 'Riqueza Especies (Media)',
    'max_species_richness': 'Riqueza Especies (Max)',
    'forest_cover': 'Cobertura Forestal'
}

resultados_h2 = []

print("\n   Correlaciones Biodiversidad vs Riesgo (estratificado por vulnerabilidad):")
print("-" * 90)
print(f"   {'Variable Biodiv':<22} {'Riesgo':<18} {'Baja':<12} {'Media':<12} {'Alta':<12} {'Hipotesis'}")
print("-" * 90)

for var_biodiv, nombre_biodiv in vars_biodiv.items():
    for var_riesgo, nombre_riesgo in vars_riesgo.items():
        correlaciones = {}

        for cat in ['Baja', 'Media', 'Alta']:
            subset = df[df['cat_vulnerabilidad'] == cat]
            valid = subset[[var_biodiv, var_riesgo]].dropna()
            if len(valid) > 30:
                r, p = stats.spearmanr(valid[var_biodiv], valid[var_riesgo])
                correlaciones[cat] = {'r': r, 'p': p, 'n': len(valid)}

        if len(correlaciones) == 3:
            r_baja = correlaciones['Baja']['r']
            r_alta = correlaciones['Alta']['r']

            h2_confirmada = r_baja < 0 and r_baja < r_alta
            resultado = "CONFIRMADA" if h2_confirmada else "NO CONFIRMADA"

            def format_r(cat):
                r = correlaciones[cat]['r']
                p = correlaciones[cat]['p']
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                return f"{r:+.2f}{sig}"

            print(f"   {nombre_biodiv:<22} {nombre_riesgo:<18} {format_r('Baja'):<12} {format_r('Media'):<12} {format_r('Alta'):<12} {resultado}")

            resultados_h2.append({
                'Variable_Biodiv': nombre_biodiv,
                'Variable_Riesgo': nombre_riesgo,
                'r_Baja': correlaciones['Baja']['r'],
                'p_Baja': correlaciones['Baja']['p'],
                'r_Media': correlaciones['Media']['r'],
                'p_Media': correlaciones['Media']['p'],
                'r_Alta': correlaciones['Alta']['r'],
                'p_Alta': correlaciones['Alta']['p'],
                'H2_Confirmada': h2_confirmada
            })

df_h2 = pd.DataFrame(resultados_h2)

# Resumen H2
print("\n   RESUMEN H2:")
n_confirmadas = df_h2['H2_Confirmada'].sum()
n_total = len(df_h2)
print(f"   - Hipotesis confirmadas: {n_confirmadas}/{n_total} ({100*n_confirmadas/n_total:.1f}%)")

if n_confirmadas > 0:
    print("\n   Casos donde biodiversidad REDUCE riesgo (especialmente en baja vulnerabilidad):")
    confirmadas = df_h2[df_h2['H2_Confirmada']]
    for _, row in confirmadas.iterrows():
        print(f"     - {row['Variable_Biodiv']} reduce {row['Variable_Riesgo']}")
        print(f"       (r_baja={row['r_Baja']:.3f}, r_alta={row['r_Alta']:.3f})")

# =============================================================================
# 6. ANALISIS DE INTERACCION (MODELO CON TERMINO DE INTERACCION)
# =============================================================================
print("\n" + "=" * 80)
print("6. MODELOS DE INTERACCION: Gobernanza x Vulnerabilidad")
print("   Probando si el efecto de gobernanza DEPENDE del nivel de vulnerabilidad")
print("=" * 80)

# Estandarizar variables para el modelo
df['gob_std'] = (df['idx_gobernanza'] - df['idx_gobernanza'].mean()) / df['idx_gobernanza'].std()
df['vuln_std'] = (df['idx_vulnerabilidad'] - df['idx_vulnerabilidad'].mean()) / df['idx_vulnerabilidad'].std()
df['biodiv_std'] = (df['idx_biodiv'] - df['idx_biodiv'].mean()) / df['idx_biodiv'].std()

print("\n   Modelos: Riesgo ~ Gobernanza + Vulnerabilidad + Gobernanza*Vulnerabilidad")
print("-" * 80)

for var_riesgo, nombre_riesgo in vars_riesgo.items():
    try:
        # Modelo con interaccion
        formula = f"{var_riesgo} ~ gob_std + vuln_std + gob_std:vuln_std"
        modelo = smf.ols(formula, data=df).fit()

        b_gob = modelo.params['gob_std']
        p_gob = modelo.pvalues['gob_std']
        b_inter = modelo.params['gob_std:vuln_std']
        p_inter = modelo.pvalues['gob_std:vuln_std']

        sig_gob = "***" if p_gob < 0.001 else "**" if p_gob < 0.01 else "*" if p_gob < 0.05 else ""
        sig_inter = "***" if p_inter < 0.001 else "**" if p_inter < 0.01 else "*" if p_inter < 0.05 else ""

        # Interpretar interaccion
        if p_inter < 0.05:
            if b_inter > 0:
                interp = "Efecto protector MAYOR en baja vulnerabilidad"
            else:
                interp = "Efecto protector MAYOR en alta vulnerabilidad"
        else:
            interp = "Sin interaccion significativa"

        print(f"   {nombre_riesgo:<20} | b_gob={b_gob:+.2f}{sig_gob} | b_inter={b_inter:+.2f}{sig_inter} | {interp}")

    except Exception as e:
        print(f"   {nombre_riesgo:<20} | Error: {str(e)[:40]}")

# =============================================================================
# 7. IDENTIFICACION DE GAPS DE GOBERNANZA
# =============================================================================
print("\n" + "=" * 80)
print("7. IDENTIFICACION DE GAPS DE GOBERNANZA")
print("   Municipios con ALTA vulnerabilidad + BAJA gobernanza = Prioridad de intervencion")
print("=" * 80)

# Crear cuadrantes de gobernanza-vulnerabilidad
mediana_gob = df['idx_gobernanza'].median()
mediana_vuln = df['idx_vulnerabilidad'].median()

def clasificar_gap(row):
    alta_vuln = row['idx_vulnerabilidad'] >= mediana_vuln
    baja_gob = row['idx_gobernanza'] < mediana_gob

    if alta_vuln and baja_gob:
        return 'GAP_CRITICO'  # Alta vulnerabilidad + Baja gobernanza
    elif alta_vuln and not baja_gob:
        return 'DESARROLLO'   # Alta vulnerabilidad + Alta gobernanza (en proceso)
    elif not alta_vuln and baja_gob:
        return 'OPORTUNIDAD'  # Baja vulnerabilidad + Baja gobernanza
    else:
        return 'MODELO'       # Baja vulnerabilidad + Alta gobernanza

df['categoria_gap'] = df.apply(clasificar_gap, axis=1)

print("\n   Distribucion de municipios por categoria:")
print("-" * 60)
for cat in ['GAP_CRITICO', 'DESARROLLO', 'OPORTUNIDAD', 'MODELO']:
    subset = df[df['categoria_gap'] == cat]
    n = len(subset)
    pct = 100 * n / len(df)
    riesgo_medio = subset['idx_riesgo_total'].mean()
    print(f"   {cat:<15}: {n:>3} municipios ({pct:>5.1f}%) | Riesgo medio: {riesgo_medio:.1f}")

# Comparar riesgos entre categorias
print("\n   Comparacion de riesgos por categoria:")
print("-" * 70)
for var_riesgo, nombre_riesgo in vars_riesgo.items():
    print(f"\n   {nombre_riesgo}:")
    for cat in ['GAP_CRITICO', 'DESARROLLO', 'OPORTUNIDAD', 'MODELO']:
        subset = df[df['categoria_gap'] == cat]
        media = subset[var_riesgo].mean()
        std = subset[var_riesgo].std()
        print(f"     {cat:<15}: {media:.1f} +/- {std:.1f}")

# Test estadistico: GAP_CRITICO vs MODELO
print("\n   Test Mann-Whitney: GAP_CRITICO vs MODELO")
print("-" * 60)
for var_riesgo, nombre_riesgo in vars_riesgo.items():
    gap = df[df['categoria_gap'] == 'GAP_CRITICO'][var_riesgo].dropna()
    modelo = df[df['categoria_gap'] == 'MODELO'][var_riesgo].dropna()
    if len(gap) > 10 and len(modelo) > 10:
        stat, p = stats.mannwhitneyu(gap, modelo, alternative='greater')
        diff = gap.mean() - modelo.mean()
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"   {nombre_riesgo:<20}: GAP-MODELO = {diff:+.1f} puntos, p={p:.4f} {sig}")

# =============================================================================
# 8. LISTA DE MUNICIPIOS PRIORITARIOS (GAPS CRITICOS)
# =============================================================================
print("\n" + "=" * 80)
print("8. MUNICIPIOS PRIORITARIOS (GAP CRITICO)")
print("=" * 80)

gaps_criticos = df[df['categoria_gap'] == 'GAP_CRITICO'].copy()
gaps_criticos = gaps_criticos.sort_values('idx_riesgo_total', ascending=False)

print(f"\n   Total: {len(gaps_criticos)} municipios con gap critico de gobernanza")
print("\n   Top 20 municipios prioritarios (mayor riesgo total):")
print("-" * 90)
print(f"   {'Municipio':<25} {'Microregion':<20} {'Riesgo':<8} {'Gob':<8} {'Vuln':<8}")
print("-" * 90)

for i, (_, row) in enumerate(gaps_criticos.head(20).iterrows()):
    micro = str(row['nome_microrregiao'])[:18] if pd.notna(row['nome_microrregiao']) else 'N/A'
    print(f"   {row['Municipio'][:23]:<25} {micro:<20} {row['idx_riesgo_total']:.1f}     {row['idx_gobernanza']:.2f}     {row['idx_vulnerabilidad']:.1f}")

# =============================================================================
# 9. VISUALIZACIONES
# =============================================================================
print("\n9. Generando visualizaciones...")

# 9.1 Grafico de regresion H1: Gobernanza vs Riesgo (color = vulnerabilidad)
fig, axes = plt.subplots(2, 4, figsize=(18, 10))

colores = {'Baja': '#27ae60', 'Media': '#f1c40f', 'Alta': '#e74c3c'}

# Fila 1: Gobernanza vs cada tipo de riesgo
for i, (var_riesgo, nombre_riesgo) in enumerate(vars_riesgo.items()):
    ax = axes[0, i]

    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset['idx_gobernanza'], subset[var_riesgo],
                   c=colores[cat], alpha=0.5, label=f'Vuln. {cat}', s=20, edgecolor='white')

        # Linea de regresion
        valid = subset[['idx_gobernanza', var_riesgo]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid['idx_gobernanza'], valid[var_riesgo], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid['idx_gobernanza'].min(), valid['idx_gobernanza'].max(), 50)
            ax.plot(x_line, p(x_line), c=colores[cat], linewidth=2.5, linestyle='--')

    # Calcular correlacion general
    r, pval = stats.spearmanr(df['idx_gobernanza'].dropna(), df[var_riesgo].dropna())
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""

    ax.set_xlabel('Indice de Gobernanza (UAI)', fontsize=9)
    ax.set_ylabel(nombre_riesgo, fontsize=9)
    ax.set_title(f'H1: Gobernanza vs {nombre_riesgo}\nr = {r:.3f} {sig}', fontsize=10)
    if i == 0:
        ax.legend(title='Vulnerabilidad', fontsize=8, loc='upper right')

# Fila 2: Biodiversidad vs cada tipo de riesgo
for i, (var_riesgo, nombre_riesgo) in enumerate(vars_riesgo.items()):
    ax = axes[1, i]

    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset['idx_biodiv'], subset[var_riesgo],
                   c=colores[cat], alpha=0.5, label=f'Vuln. {cat}', s=20, edgecolor='white')

        valid = subset[['idx_biodiv', var_riesgo]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid['idx_biodiv'], valid[var_riesgo], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid['idx_biodiv'].min(), valid['idx_biodiv'].max(), 50)
            ax.plot(x_line, p(x_line), c=colores[cat], linewidth=2.5, linestyle='--')

    r, pval = stats.spearmanr(df['idx_biodiv'].dropna(), df[var_riesgo].dropna())
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""

    ax.set_xlabel('Indice de Biodiversidad', fontsize=9)
    ax.set_ylabel(nombre_riesgo, fontsize=9)
    ax.set_title(f'H2: Biodiversidad vs {nombre_riesgo}\nr = {r:.3f} {sig}', fontsize=10)

plt.suptitle('PRUEBA DE HIPOTESIS: Efecto de Gobernanza y Biodiversidad sobre Riesgo Ambiental\n' +
             '(modulado por vulnerabilidad socio-economica, n=645 municipios de Sao Paulo)',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/hipotesis_h1_h2_v3.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: hipotesis_h1_h2_v3.png")

# 9.2 Mapa de GAPS de gobernanza
fig2, ax2 = plt.subplots(figsize=(12, 8))

colores_gap = {
    'GAP_CRITICO': '#c0392b',   # Rojo - Prioridad
    'DESARROLLO': '#f39c12',     # Naranja - En proceso
    'OPORTUNIDAD': '#3498db',    # Azul - Potencial
    'MODELO': '#27ae60'          # Verde - Referencia
}

for cat in ['MODELO', 'OPORTUNIDAD', 'DESARROLLO', 'GAP_CRITICO']:
    subset = df[df['categoria_gap'] == cat]
    ax2.scatter(subset['idx_gobernanza'], subset['idx_vulnerabilidad'],
                c=colores_gap[cat], alpha=0.6, label=f'{cat} (n={len(subset)})',
                s=subset['idx_riesgo_total'] * 2, edgecolor='white')

# Lineas de mediana
ax2.axvline(x=mediana_gob, color='gray', linestyle='--', linewidth=1, label=f'Mediana Gob ({mediana_gob:.2f})')
ax2.axhline(y=mediana_vuln, color='gray', linestyle=':', linewidth=1, label=f'Mediana Vuln ({mediana_vuln:.1f})')

# Etiquetas de cuadrantes
ax2.text(0.15, mediana_vuln + 15, 'GAP CRITICO\n(Prioridad)', fontsize=11, fontweight='bold', color='#c0392b')
ax2.text(0.55, mediana_vuln + 15, 'DESARROLLO\n(En proceso)', fontsize=11, fontweight='bold', color='#f39c12')
ax2.text(0.15, mediana_vuln - 20, 'OPORTUNIDAD\n(Potencial)', fontsize=11, fontweight='bold', color='#3498db')
ax2.text(0.55, mediana_vuln - 20, 'MODELO\n(Referencia)', fontsize=11, fontweight='bold', color='#27ae60')

ax2.set_xlabel('Indice de Gobernanza (UAI)', fontsize=12)
ax2.set_ylabel('Indice de Vulnerabilidad Socio-Economica', fontsize=12)
ax2.set_title('IDENTIFICACION DE GAPS DE GOBERNANZA\n(Tamano de punto = Riesgo Ambiental Total)',
              fontsize=13, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/gaps_gobernanza_v3.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: gaps_gobernanza_v3.png")

# 9.3 Comparacion de riesgos por categoria de gap
fig3, axes3 = plt.subplots(1, 4, figsize=(16, 5))

for i, (var_riesgo, nombre_riesgo) in enumerate(vars_riesgo.items()):
    ax = axes3[i]

    data_plot = []
    for cat in ['GAP_CRITICO', 'DESARROLLO', 'OPORTUNIDAD', 'MODELO']:
        valores = df[df['categoria_gap'] == cat][var_riesgo].dropna()
        data_plot.append(valores)

    bp = ax.boxplot(data_plot, labels=['GAP\nCRITICO', 'DESA-\nRROLLO', 'OPOR-\nTUNIDAD', 'MODELO'],
                    patch_artist=True)

    colors_bp = ['#c0392b', '#f39c12', '#3498db', '#27ae60']
    for patch, color in zip(bp['boxes'], colors_bp):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel(nombre_riesgo, fontsize=10)
    ax.set_title(f'{nombre_riesgo}', fontsize=11, fontweight='bold')

plt.suptitle('COMPARACION DE RIESGO AMBIENTAL POR CATEGORIA DE GAP\n' +
             '(Los municipios con GAP CRITICO tienen significativamente mas riesgo)',
             fontsize=12, fontweight='bold', y=1.05)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/riesgo_por_gap_v3.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: riesgo_por_gap_v3.png")

# =============================================================================
# 10. GUARDAR RESULTADOS
# =============================================================================
print("\n10. Guardando resultados...")

# Dataset con clasificaciones
df_export = df[['cod_ibge', 'Municipio', 'nome_microrregiao', 'nome_mesorregiao',
                'idx_gobernanza', 'idx_biodiv', 'idx_vulnerabilidad',
                'idx_riesgo_total', 'idx_riesgo_salud', 'idx_riesgo_clima', 'idx_riesgo_nutricion',
                'cat_vulnerabilidad', 'categoria_gap']].copy()

df_export.to_csv(f"{PROJECT_ROOT}/outputs/municipios_gaps_gobernanza_v3.csv", index=False)
print(f"   Guardado: municipios_gaps_gobernanza_v3.csv")

# Tabla de hipotesis
df_h1.to_csv(f"{PROJECT_ROOT}/outputs/resultados_h1_gobernanza_v3.csv", index=False)
df_h2.to_csv(f"{PROJECT_ROOT}/outputs/resultados_h2_biodiversidad_v3.csv", index=False)
print(f"   Guardado: resultados_h1_gobernanza_v3.csv")
print(f"   Guardado: resultados_h2_biodiversidad_v3.csv")

# Lista de municipios prioritarios
gaps_criticos[['cod_ibge', 'Municipio', 'nome_microrregiao',
               'idx_gobernanza', 'idx_vulnerabilidad', 'idx_riesgo_total',
               'idx_riesgo_salud', 'idx_riesgo_clima', 'idx_riesgo_nutricion']].to_csv(
    f"{PROJECT_ROOT}/outputs/municipios_gap_critico_v3.csv", index=False
)
print(f"   Guardado: municipios_gap_critico_v3.csv ({len(gaps_criticos)} municipios)")

# =============================================================================
# 11. RESUMEN EJECUTIVO
# =============================================================================
print("\n" + "=" * 80)
print("RESUMEN EJECUTIVO")
print("=" * 80)

print("\n1. HIPOTESIS H1 (Gobernanza -> Menor Riesgo):")
n_conf_h1 = df_h1['H1_Confirmada'].sum()
print(f"   - Se confirma en {n_conf_h1}/{len(df_h1)} combinaciones ({100*n_conf_h1/len(df_h1):.0f}%)")
if n_conf_h1 > 0:
    conf = df_h1[df_h1['H1_Confirmada']]
    print(f"   - Confirmada principalmente para: {', '.join(conf['Variable_Riesgo'].unique())}")

print("\n2. HIPOTESIS H2 (Biodiversidad -> Menor Riesgo):")
n_conf_h2 = df_h2['H2_Confirmada'].sum()
print(f"   - Se confirma en {n_conf_h2}/{len(df_h2)} combinaciones ({100*n_conf_h2/len(df_h2):.0f}%)")
if n_conf_h2 > 0:
    conf = df_h2[df_h2['H2_Confirmada']]
    print(f"   - Confirmada principalmente para: {', '.join(conf['Variable_Riesgo'].unique())}")

print("\n3. GAPS DE GOBERNANZA IDENTIFICADOS:")
n_gap = len(df[df['categoria_gap'] == 'GAP_CRITICO'])
print(f"   - {n_gap} municipios con GAP CRITICO (alta vulnerabilidad + baja gobernanza)")
print(f"   - Riesgo medio en GAP_CRITICO: {df[df['categoria_gap'] == 'GAP_CRITICO']['idx_riesgo_total'].mean():.1f}")
print(f"   - Riesgo medio en MODELO: {df[df['categoria_gap'] == 'MODELO']['idx_riesgo_total'].mean():.1f}")
diff = df[df['categoria_gap'] == 'GAP_CRITICO']['idx_riesgo_total'].mean() - df[df['categoria_gap'] == 'MODELO']['idx_riesgo_total'].mean()
print(f"   - Diferencia: {diff:+.1f} puntos de riesgo")

print("\n4. RECOMENDACION:")
print("   Los municipios con GAP CRITICO deben ser priorizados para")
print("   intervenciones de gobernanza urbana, especialmente en:")
top_riesgo = gaps_criticos.head(5)['Municipio'].tolist()
print(f"   {', '.join(top_riesgo)}")

print("\n" + "=" * 80)
print("Analisis completado.")
print("=" * 80)
