"""
=============================================================================
Análisis de Hipótesis: Gobernanza y Biodiversidad como Mediadores de Riesgo
=============================================================================

Marco conceptual:
  - Y (dependiente): Riesgo/vulnerabilidad ambiental (salud, clima, polinización)
  - X (independiente): Gobernanza (UAI) o Biodiversidad
  - Z (modulador): Vulnerabilidad socio-económica

Hipótesis:
  H1: Mayor gobernanza (UAI) → menor riesgo ambiental,
      especialmente en municipios con menor vulnerabilidad social
  H2: Mayor biodiversidad → menor riesgo ambiental,
      especialmente en municipios con menor vulnerabilidad social

Autor: Science Team
Fecha: 2026-01-21
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
print("=" * 70)
print("ANÁLISIS DE HIPÓTESIS: GOBERNANZA Y BIODIVERSIDAD")
print("=" * 70)

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"
df = pd.read_csv(f"{PROJECT_ROOT}/outputs/municipios_integrado_v6.csv")

print(f"\n1. Datos cargados: {len(df)} municipios, {len(df.columns)} variables")

# =============================================================================
# 2. DEFINIR GRUPOS DE VARIABLES
# =============================================================================
print("\n2. Definiendo grupos de variables...")

# GRUPO 1: Riesgo/Vulnerabilidad Ambiental (Variables dependientes Y)
vars_riesgo_salud = ['persist_dengue', 'persist_leptospirose', 'persist_malaria', 'persist_leishmaniose',
                     'incidence_mean_dengue', 'incidence_mean_leptospirose', 'incidence_mean_malaria',
                     'incidence_mean_leishmaniose', 'copresence_years', 'idx_carga_enfermedad']

vars_riesgo_clima = ['flooding_exposure', 'flooding_risks',
                     'hydric_stress_exp', 'hydric_stress_risk', 'idx_clima']

vars_riesgo_nutricion = ['pol_deficit']

# GRUPO 2: Vulnerabilidad Socio-Económica (Modulador Z)
vars_vulnerabilidad = ['pct_rural', 'n_pessoas_pobreza', 'n_familias_rua',
                       'population_preta', 'population_indigena']

# GRUPO 3: Biodiversidad (Variable independiente X1)
vars_biodiversidad = ['mean_species_richness', 'idx_biodiv']

# GRUPO 4: Gobernanza (Variable independiente X2)
vars_gobernanza = ['idx_gobernanza', 'UAI_housing', 'UAI_env',
                   'UAI_food', 'UAI_mob', 'UAI_Crisk']

# =============================================================================
# 3. CREAR ÍNDICES COMPUESTOS
# =============================================================================
print("\n3. Creando índices compuestos...")

# Función para normalizar (0-100)
def normalize_0_100(series):
    """Normaliza una serie a escala 0-100"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100

# 3.1 Índice Compuesto de Riesgo Ambiental
print("   - Índice de Riesgo Ambiental (salud + clima + nutrición)")

# Normalizar componentes
df['riesgo_salud_norm'] = normalize_0_100(df['idx_carga_enfermedad'].fillna(0))
df['riesgo_clima_norm'] = normalize_0_100(df['idx_clima'].fillna(0))
df['riesgo_nutricion_norm'] = normalize_0_100(df['pol_deficit'].fillna(0))

# Índice compuesto (promedio ponderado)
df['idx_riesgo_ambiental'] = (
    df['riesgo_salud_norm'] * 0.4 +      # 40% salud
    df['riesgo_clima_norm'] * 0.4 +       # 40% clima
    df['riesgo_nutricion_norm'] * 0.2     # 20% nutrición
)

print(f"     Riesgo ambiental: media={df['idx_riesgo_ambiental'].mean():.1f}, "
      f"std={df['idx_riesgo_ambiental'].std():.1f}")

# 3.2 Índice Compuesto de Vulnerabilidad Socio-Económica
print("   - Índice de Vulnerabilidad Socio-Económica")

# Calcular porcentajes de población vulnerable
df['pct_pobreza'] = (df['n_pessoas_pobreza'] / df['population'] * 100).fillna(0)
df['pct_preta'] = (df['population_preta'] / df['population'] * 100).fillna(0)
df['pct_indigena'] = (df['population_indigena'] / df['population'] * 100).fillna(0)

# Normalizar componentes
df['vuln_rural_norm'] = normalize_0_100(df['pct_rural'].fillna(0))
df['vuln_pobreza_norm'] = normalize_0_100(df['pct_pobreza'])
df['vuln_preta_norm'] = normalize_0_100(df['pct_preta'])
df['vuln_indigena_norm'] = normalize_0_100(df['pct_indigena'])

# Índice compuesto de vulnerabilidad
df['idx_vulnerabilidad_socio'] = (
    df['vuln_rural_norm'] * 0.25 +
    df['vuln_pobreza_norm'] * 0.35 +
    df['vuln_preta_norm'] * 0.25 +
    df['vuln_indigena_norm'] * 0.15
)

print(f"     Vulnerabilidad: media={df['idx_vulnerabilidad_socio'].mean():.1f}, "
      f"std={df['idx_vulnerabilidad_socio'].std():.1f}")

# 3.3 Categorizar vulnerabilidad en terciles
df['cat_vulnerabilidad'] = pd.qcut(
    df['idx_vulnerabilidad_socio'],
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

print(f"     Distribución por categoría:")
for cat in ['Baja', 'Media', 'Alta']:
    n = (df['cat_vulnerabilidad'] == cat).sum()
    print(f"       - {cat}: {n} municipios ({100*n/len(df):.1f}%)")

# =============================================================================
# 4. ANÁLISIS DE CORRELACIONES POR GRUPO
# =============================================================================
print("\n4. Análisis de correlaciones por grupo de variables...")

# Correlaciones Gobernanza vs Riesgo
print("\n   4.1 GOBERNANZA vs RIESGO AMBIENTAL:")
corr_gob = {}
for var_gob in ['idx_gobernanza']:
    for var_riesgo in ['idx_riesgo_ambiental', 'riesgo_salud_norm',
                       'riesgo_clima_norm', 'riesgo_nutricion_norm']:
        valid = df[[var_gob, var_riesgo]].dropna()
        r, p = stats.spearmanr(valid[var_gob], valid[var_riesgo])
        corr_gob[f"{var_gob} vs {var_riesgo}"] = {'r': r, 'p': p}
        signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"       {var_riesgo}: r={r:+.3f} {signo}")

# Correlaciones Biodiversidad vs Riesgo
print("\n   4.2 BIODIVERSIDAD vs RIESGO AMBIENTAL:")
for var_biodiv in ['idx_biodiv']:
    for var_riesgo in ['idx_riesgo_ambiental', 'riesgo_salud_norm',
                       'riesgo_clima_norm', 'riesgo_nutricion_norm']:
        valid = df[[var_biodiv, var_riesgo]].dropna()
        r, p = stats.spearmanr(valid[var_biodiv], valid[var_riesgo])
        signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"       {var_riesgo}: r={r:+.3f} {signo}")

# =============================================================================
# 5. ANÁLISIS ESTRATIFICADO POR VULNERABILIDAD
# =============================================================================
print("\n5. Análisis estratificado por nivel de vulnerabilidad...")

# 5.1 H1: Gobernanza → Riesgo (estratificado por vulnerabilidad)
print("\n   5.1 H1: GOBERNANZA -> RIESGO AMBIENTAL")
print("       (¿La relación cambia según el nivel de vulnerabilidad?)")

results_h1 = {}
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat]
    valid = subset[['idx_gobernanza', 'idx_riesgo_ambiental']].dropna()
    if len(valid) > 10:
        r, p = stats.spearmanr(valid['idx_gobernanza'], valid['idx_riesgo_ambiental'])
        results_h1[cat] = {'r': r, 'p': p, 'n': len(valid)}
        signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"       Vulnerabilidad {cat}: r={r:+.3f} {signo} (n={len(valid)})")

# 5.2 H2: Biodiversidad → Riesgo (estratificado por vulnerabilidad)
print("\n   5.2 H2: BIODIVERSIDAD -> RIESGO AMBIENTAL")
print("       (¿La relación cambia según el nivel de vulnerabilidad?)")

results_h2 = {}
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat]
    valid = subset[['idx_biodiv', 'idx_riesgo_ambiental']].dropna()
    if len(valid) > 10:
        r, p = stats.spearmanr(valid['idx_biodiv'], valid['idx_riesgo_ambiental'])
        results_h2[cat] = {'r': r, 'p': p, 'n': len(valid)}
        signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"       Vulnerabilidad {cat}: r={r:+.3f} {signo} (n={len(valid)})")

# =============================================================================
# 6. VISUALIZACIONES DE REGRESIÓN CON MODULADOR
# =============================================================================
print("\n6. Generando visualizaciones...")

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 6.1 H1: Gobernanza vs Riesgo (color = vulnerabilidad)
ax1 = axes[0, 0]
colors = {'Baja': '#2ecc71', 'Media': '#f39c12', 'Alta': '#e74c3c'}
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat]
    ax1.scatter(subset['idx_gobernanza'], subset['idx_riesgo_ambiental'],
                c=colors[cat], alpha=0.6, label=f'Vuln. {cat}', s=40, edgecolor='white')

# Líneas de regresión por grupo
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_gobernanza', 'idx_riesgo_ambiental'])
    if len(subset) > 5:
        z = np.polyfit(subset['idx_gobernanza'], subset['idx_riesgo_ambiental'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(subset['idx_gobernanza'].min(), subset['idx_gobernanza'].max(), 100)
        ax1.plot(x_line, p(x_line), c=colors[cat], linewidth=2, linestyle='--')

ax1.set_xlabel('Índice de Gobernanza (UAI)')
ax1.set_ylabel('Índice de Riesgo Ambiental')
ax1.set_title('H1: Gobernanza → Riesgo Ambiental\n(modulado por vulnerabilidad socio-económica)')
ax1.legend(title='Vulnerabilidad', loc='upper right')

# 6.2 H2: Biodiversidad vs Riesgo (color = vulnerabilidad)
ax2 = axes[0, 1]
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat]
    ax2.scatter(subset['idx_biodiv'], subset['idx_riesgo_ambiental'],
                c=colors[cat], alpha=0.6, label=f'Vuln. {cat}', s=40, edgecolor='white')

for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_biodiv', 'idx_riesgo_ambiental'])
    if len(subset) > 5:
        z = np.polyfit(subset['idx_biodiv'], subset['idx_riesgo_ambiental'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(subset['idx_biodiv'].min(), subset['idx_biodiv'].max(), 100)
        ax2.plot(x_line, p(x_line), c=colors[cat], linewidth=2, linestyle='--')

ax2.set_xlabel('Índice de Biodiversidad')
ax2.set_ylabel('Índice de Riesgo Ambiental')
ax2.set_title('H2: Biodiversidad → Riesgo Ambiental\n(modulado por vulnerabilidad socio-económica)')
ax2.legend(title='Vulnerabilidad', loc='upper right')

# 6.3 Comparación de pendientes H1
ax3 = axes[1, 0]
slopes_h1 = []
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_gobernanza', 'idx_riesgo_ambiental'])
    if len(subset) > 5:
        slope, intercept, r, p, se = stats.linregress(subset['idx_gobernanza'], subset['idx_riesgo_ambiental'])
        slopes_h1.append({'Vulnerabilidad': cat, 'Pendiente': slope, 'R²': r**2, 'SE': se})

df_slopes_h1 = pd.DataFrame(slopes_h1)
bars = ax3.bar(df_slopes_h1['Vulnerabilidad'], df_slopes_h1['Pendiente'],
               color=[colors[c] for c in df_slopes_h1['Vulnerabilidad']], edgecolor='black')
ax3.axhline(y=0, color='gray', linestyle='--', linewidth=1)
ax3.set_xlabel('Nivel de Vulnerabilidad Socio-Económica')
ax3.set_ylabel('Pendiente (β)')
ax3.set_title('H1: Efecto de Gobernanza sobre Riesgo\npor nivel de vulnerabilidad')

# Añadir valores
for bar, row in zip(bars, df_slopes_h1.itertuples()):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'β={row.Pendiente:.3f}', ha='center', va='bottom' if row.Pendiente > 0 else 'top')

# 6.4 Comparación de pendientes H2
ax4 = axes[1, 1]
slopes_h2 = []
for cat in ['Baja', 'Media', 'Alta']:
    subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_biodiv', 'idx_riesgo_ambiental'])
    if len(subset) > 5:
        slope, intercept, r, p, se = stats.linregress(subset['idx_biodiv'], subset['idx_riesgo_ambiental'])
        slopes_h2.append({'Vulnerabilidad': cat, 'Pendiente': slope, 'R²': r**2, 'SE': se})

df_slopes_h2 = pd.DataFrame(slopes_h2)
bars = ax4.bar(df_slopes_h2['Vulnerabilidad'], df_slopes_h2['Pendiente'],
               color=[colors[c] for c in df_slopes_h2['Vulnerabilidad']], edgecolor='black')
ax4.axhline(y=0, color='gray', linestyle='--', linewidth=1)
ax4.set_xlabel('Nivel de Vulnerabilidad Socio-Económica')
ax4.set_ylabel('Pendiente (β)')
ax4.set_title('H2: Efecto de Biodiversidad sobre Riesgo\npor nivel de vulnerabilidad')

for bar, row in zip(bars, df_slopes_h2.itertuples()):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'β={row.Pendiente:.3f}', ha='center', va='bottom' if row.Pendiente > 0 else 'top')

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/hipotesis_gobernanza_biodiv.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: outputs/figures/hipotesis_gobernanza_biodiv.png")

# =============================================================================
# 7. ANÁLISIS DETALLADO POR COMPONENTES
# =============================================================================
print("\n7. Análisis detallado por componentes de riesgo...")

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 10))

componentes_riesgo = [
    ('riesgo_salud_norm', 'Riesgo Salud'),
    ('riesgo_clima_norm', 'Riesgo Clima'),
    ('riesgo_nutricion_norm', 'Riesgo Nutrición')
]

# Fila 1: Gobernanza vs cada componente
for i, (var, titulo) in enumerate(componentes_riesgo):
    ax = axes2[0, i]
    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset['idx_gobernanza'], subset[var],
                   c=colors[cat], alpha=0.5, label=f'Vuln. {cat}', s=30)
    ax.set_xlabel('Gobernanza (UAI)')
    ax.set_ylabel(titulo)
    ax.set_title(f'Gobernanza vs {titulo}')
    if i == 0:
        ax.legend(title='Vulnerabilidad', fontsize=8)

# Fila 2: Biodiversidad vs cada componente
for i, (var, titulo) in enumerate(componentes_riesgo):
    ax = axes2[1, i]
    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat]
        ax.scatter(subset['idx_biodiv'], subset[var],
                   c=colors[cat], alpha=0.5, label=f'Vuln. {cat}', s=30)
    ax.set_xlabel('Biodiversidad')
    ax.set_ylabel(titulo)
    ax.set_title(f'Biodiversidad vs {titulo}')

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/componentes_riesgo_detalle.png", dpi=150, bbox_inches='tight')
print(f"   Guardado: outputs/figures/componentes_riesgo_detalle.png")

# =============================================================================
# 8. TABLA RESUMEN DE CORRELACIONES ESTRATIFICADAS
# =============================================================================
print("\n8. Tabla resumen de correlaciones estratificadas...")

resultados = []

for var_x, nombre_x in [('idx_gobernanza', 'Gobernanza'), ('idx_biodiv', 'Biodiversidad')]:
    for var_y, nombre_y in [('idx_riesgo_ambiental', 'Riesgo Total'),
                            ('riesgo_salud_norm', 'Riesgo Salud'),
                            ('riesgo_clima_norm', 'Riesgo Clima'),
                            ('riesgo_nutricion_norm', 'Riesgo Nutrición')]:
        for cat in ['Baja', 'Media', 'Alta']:
            subset = df[df['cat_vulnerabilidad'] == cat]
            valid = subset[[var_x, var_y]].dropna()
            if len(valid) > 10:
                r, p = stats.spearmanr(valid[var_x], valid[var_y])
                resultados.append({
                    'Variable_X': nombre_x,
                    'Variable_Y': nombre_y,
                    'Vulnerabilidad': cat,
                    'Spearman_r': r,
                    'p_value': p,
                    'Significativo': '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns',
                    'n': len(valid)
                })

df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(f"{PROJECT_ROOT}/outputs/correlaciones_estratificadas.csv", index=False)
print(f"   Guardado: outputs/correlaciones_estratificadas.csv")

# Mostrar tabla pivotada
print("\n   Correlaciones Spearman (*** p<0.001, ** p<0.01, * p<0.05):")
pivot = df_resultados.pivot_table(
    index=['Variable_X', 'Variable_Y'],
    columns='Vulnerabilidad',
    values='Spearman_r',
    aggfunc='first'
)[['Baja', 'Media', 'Alta']]
print(pivot.round(3).to_string())

# =============================================================================
# 9. INTERPRETACIÓN DE RESULTADOS
# =============================================================================
print("\n" + "=" * 70)
print("INTERPRETACIÓN DE RESULTADOS")
print("=" * 70)

print("\n9.1 HIPOTESIS 1: Gobernanza -> Riesgo Ambiental")
print("    Expectativa: Mayor UAI -> menor riesgo, especialmente en baja vulnerabilidad")

# Verificar si la pendiente cambia con vulnerabilidad
if len(df_slopes_h1) == 3:
    pendientes_h1 = df_slopes_h1.set_index('Vulnerabilidad')['Pendiente']
    if pendientes_h1.loc['Baja'] < pendientes_h1.loc['Alta']:
        print("    [OK] CONFIRMADA: El efecto protector de la gobernanza es mas fuerte")
        print("         en municipios con baja vulnerabilidad socio-economica")
    else:
        print("    [X] NO CONFIRMADA: El patron no sigue lo esperado")
    print(f"      Pendientes: Baja={pendientes_h1.loc['Baja']:.4f}, "
          f"Media={pendientes_h1.loc['Media']:.4f}, Alta={pendientes_h1.loc['Alta']:.4f}")

print("\n9.2 HIPOTESIS 2: Biodiversidad -> Riesgo Ambiental")
print("    Expectativa: Mayor biodiversidad -> menor riesgo, especialmente en baja vulnerabilidad")

if len(df_slopes_h2) == 3:
    pendientes_h2 = df_slopes_h2.set_index('Vulnerabilidad')['Pendiente']
    if pendientes_h2.loc['Baja'] < pendientes_h2.loc['Alta']:
        print("    [OK] CONFIRMADA: El efecto protector de la biodiversidad es mas fuerte")
        print("         en municipios con baja vulnerabilidad socio-economica")
    else:
        print("    [X] NO CONFIRMADA: El patron no sigue lo esperado")
    print(f"      Pendientes: Baja={pendientes_h2.loc['Baja']:.4f}, "
          f"Media={pendientes_h2.loc['Media']:.4f}, Alta={pendientes_h2.loc['Alta']:.4f}")

# =============================================================================
# 10. GUARDAR DATASET ENRIQUECIDO
# =============================================================================
print("\n10. Guardando dataset enriquecido...")

# Seleccionar columnas principales para exportar
cols_export = [
    'Cod_ibge', 'Municipio',
    # Índices compuestos
    'idx_riesgo_ambiental', 'riesgo_salud_norm', 'riesgo_clima_norm', 'riesgo_nutricion_norm',
    'idx_vulnerabilidad_socio', 'cat_vulnerabilidad',
    'idx_gobernanza', 'idx_biodiv',
    # Variables originales
    'pct_rural', 'pct_pobreza', 'pct_preta', 'pct_indigena',
    'population', 'mean_species_richness',
    'UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk'
]

df_export = df[[c for c in cols_export if c in df.columns]]
df_export.to_csv(f"{PROJECT_ROOT}/outputs/analisis_hipotesis_data.csv", index=False)
print(f"   Guardado: outputs/analisis_hipotesis_data.csv")

print("\n" + "=" * 70)
print("Análisis completado.")
print("=" * 70)
