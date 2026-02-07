"""
=============================================================================
Comparacion de Variables de Vulnerabilidad Social
=============================================================================

Objetivo: Determinar cual variable de vulnerabilidad es mejor modulador
de la relacion Gobernanza/Biodiversidad -> Riesgo Ambiental

Variables a comparar:
  - idx_vulnerabilidad (indice compuesto)
  - pct_rural (% poblacion rural)
  - pct_pobreza (% personas en pobreza extrema)
  - pct_preta (% poblacion negra)
  - pct_indigena (% poblacion indigena)

Autor: Science Team
Fecha: 2026-01-21
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
print("=" * 80)
print("COMPARACION DE VARIABLES DE VULNERABILIDAD SOCIAL")
print("=" * 80)

df = pd.read_csv(f"{PROJECT_ROOT}/outputs/dataset/municipios_integrado.csv")
print(f"\nDatos: {len(df)} municipios")

# =============================================================================
# 2. DEFINIR VARIABLES
# =============================================================================

# Variables de vulnerabilidad a comparar
vars_vulnerabilidad = {
    'idx_vulnerabilidad': 'Indice Compuesto',
    'pct_rural': '% Rural',
    'pct_pobreza': '% Pobreza',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indigena'
}

# Variables de riesgo (Y)
vars_riesgo = {
    'persist_dengue': 'Persist. Dengue',
    'persist_leptospirose': 'Persist. Leptospirosis',
    'incidence_mean_dengue': 'Incid. Dengue',
    'flooding_risks': 'Riesgo Inundaciones',
    'hydric_stress_risk': 'Riesgo Estres Hidrico',
    'pol_deficit': 'Deficit Polinizacion'
}

# Variables predictoras (X)
vars_predictores = {
    'idx_gobernanza': 'UAI General',
    'idx_biodiv': 'Indice Biodiversidad',
    'forest_cover': 'Cobertura Forestal'
}

# =============================================================================
# 3. CORRELACIONES ENTRE VARIABLES DE VULNERABILIDAD
# =============================================================================
print("\n" + "=" * 80)
print("1. CORRELACIONES ENTRE VARIABLES DE VULNERABILIDAD")
print("=" * 80)

# Matriz de correlacion
vars_vuln_list = list(vars_vulnerabilidad.keys())
corr_matrix = df[vars_vuln_list].corr(method='spearman')

print("\nMatriz de correlacion Spearman:")
print("-" * 60)
print(corr_matrix.round(3).to_string())

# Correlacion de cada componente con el indice
print("\n\nCorrelacion de cada componente con el INDICE COMPUESTO:")
print("-" * 60)
for var, nombre in vars_vulnerabilidad.items():
    if var != 'idx_vulnerabilidad':
        r = corr_matrix.loc[var, 'idx_vulnerabilidad']
        print(f"  {nombre:<20}: r = {r:+.3f}")

# =============================================================================
# 4. EVALUAR CADA VARIABLE COMO MODULADOR
# =============================================================================
print("\n" + "=" * 80)
print("2. EVALUACION DE CADA VARIABLE COMO MODULADOR")
print("   (Diferencia de correlacion entre tercil Alto vs Bajo)")
print("=" * 80)

resultados_modulacion = []

for var_vuln, nombre_vuln in vars_vulnerabilidad.items():
    # Crear terciles para esta variable
    try:
        df[f'tercil_{var_vuln}'] = pd.qcut(
            df[var_vuln].rank(method='first'),
            q=3,
            labels=['Bajo', 'Medio', 'Alto']
        )
    except:
        continue

    for var_x, nombre_x in vars_predictores.items():
        for var_y, nombre_y in vars_riesgo.items():
            if var_x not in df.columns or var_y not in df.columns:
                continue

            # Correlacion en tercil Bajo
            bajo = df[df[f'tercil_{var_vuln}'] == 'Bajo']
            valid_bajo = bajo[[var_x, var_y]].dropna()

            # Correlacion en tercil Alto
            alto = df[df[f'tercil_{var_vuln}'] == 'Alto']
            valid_alto = alto[[var_x, var_y]].dropna()

            if len(valid_bajo) > 30 and len(valid_alto) > 30:
                r_bajo, p_bajo = stats.spearmanr(valid_bajo[var_x], valid_bajo[var_y])
                r_alto, p_alto = stats.spearmanr(valid_alto[var_x], valid_alto[var_y])

                # Diferencia de correlacion (magnitud del efecto modulador)
                diff = abs(r_bajo - r_alto)

                resultados_modulacion.append({
                    'Variable_Vuln': var_vuln,
                    'Nombre_Vuln': nombre_vuln,
                    'Variable_X': var_x,
                    'Nombre_X': nombre_x,
                    'Variable_Y': var_y,
                    'Nombre_Y': nombre_y,
                    'r_Bajo': r_bajo,
                    'r_Alto': r_alto,
                    'Diferencia': diff,
                    'Direccion': 'Bajo > Alto' if abs(r_bajo) > abs(r_alto) else 'Alto > Bajo'
                })

df_modulacion = pd.DataFrame(resultados_modulacion)

# Calcular poder de modulacion promedio por variable de vulnerabilidad
print("\nPoder de modulacion promedio (diferencia |r_bajo - r_alto|):")
print("-" * 60)

poder_modulacion = df_modulacion.groupby('Nombre_Vuln')['Diferencia'].mean().sort_values(ascending=False)
for nombre, diff in poder_modulacion.items():
    print(f"  {nombre:<20}: {diff:.3f}")

mejor_modulador = poder_modulacion.idxmax()
print(f"\n  MEJOR MODULADOR: {mejor_modulador}")

# =============================================================================
# 5. ANALISIS DETALLADO DEL MEJOR MODULADOR
# =============================================================================
print("\n" + "=" * 80)
print(f"3. ANALISIS DETALLADO: {mejor_modulador}")
print("=" * 80)

# Obtener variable correspondiente
var_mejor = [k for k, v in vars_vulnerabilidad.items() if v == mejor_modulador][0]

print(f"\nCorrelaciones estratificadas por {mejor_modulador}:")
print("-" * 80)
print(f"{'Predictor':<20} {'Riesgo':<22} {'Bajo':<10} {'Medio':<10} {'Alto':<10} {'Diff':<8}")
print("-" * 80)

subset_mejor = df_modulacion[df_modulacion['Nombre_Vuln'] == mejor_modulador]
subset_mejor = subset_mejor.sort_values('Diferencia', ascending=False)

for _, row in subset_mejor.iterrows():
    # Obtener correlacion media tambien
    medio = df[df[f'tercil_{var_mejor}'] == 'Medio']
    valid_medio = medio[[row['Variable_X'], row['Variable_Y']]].dropna()
    r_medio, _ = stats.spearmanr(valid_medio[row['Variable_X']], valid_medio[row['Variable_Y']]) if len(valid_medio) > 30 else (np.nan, np.nan)

    print(f"{row['Nombre_X']:<20} {row['Nombre_Y']:<22} {row['r_Bajo']:+.2f}     {r_medio:+.2f}     {row['r_Alto']:+.2f}     {row['Diferencia']:.2f}")

# =============================================================================
# 6. COMPARACION VISUAL
# =============================================================================
print("\n" + "=" * 80)
print("4. GENERANDO VISUALIZACIONES")
print("=" * 80)

# 6.1 Heatmap de correlaciones entre variables de vulnerabilidad
fig1, ax1 = plt.subplots(figsize=(8, 6))

# Renombrar para visualizacion
corr_renamed = corr_matrix.copy()
corr_renamed.index = [vars_vulnerabilidad[v] for v in corr_renamed.index]
corr_renamed.columns = [vars_vulnerabilidad[v] for v in corr_renamed.columns]

sns.heatmap(corr_renamed, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0,
            ax=ax1, vmin=-1, vmax=1, square=True,
            annot_kws={'size': 11, 'fontweight': 'bold'})
ax1.set_title('Correlaciones entre Variables de Vulnerabilidad Social\n(Spearman, n=645)',
              fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/correlaciones_vulnerabilidad.png", dpi=150, bbox_inches='tight')
print("Guardado: correlaciones_vulnerabilidad.png")

# 6.2 Comparacion de poder de modulacion
fig2, ax2 = plt.subplots(figsize=(10, 6))

colores = ['#e74c3c' if n == mejor_modulador else '#3498db' for n in poder_modulacion.index]
bars = ax2.barh(poder_modulacion.index, poder_modulacion.values, color=colores, edgecolor='black')

ax2.set_xlabel('Poder de Modulacion Promedio\n(|r_bajo - r_alto|)', fontsize=11)
ax2.set_title('Comparacion de Variables de Vulnerabilidad como Moduladores\n(Mayor diferencia = mejor modulador)',
              fontsize=12, fontweight='bold')
ax2.axvline(x=poder_modulacion.mean(), color='gray', linestyle='--', label=f'Media: {poder_modulacion.mean():.3f}')

# Agregar valores
for bar, val in zip(bars, poder_modulacion.values):
    ax2.text(val + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}',
             va='center', fontsize=10)

ax2.legend()
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/comparacion_moduladores.png", dpi=150, bbox_inches='tight')
print("Guardado: comparacion_moduladores.png")

# 6.3 Efecto estratificado para las 3 mejores combinaciones
fig3, axes3 = plt.subplots(1, 3, figsize=(15, 5))

# Seleccionar las 3 combinaciones con mayor diferencia
top3 = subset_mejor.head(3)
colores_tercil = {'Bajo': '#27ae60', 'Medio': '#f1c40f', 'Alto': '#e74c3c'}

for i, (_, row) in enumerate(top3.iterrows()):
    ax = axes3[i]
    var_x = row['Variable_X']
    var_y = row['Variable_Y']

    for tercil in ['Bajo', 'Medio', 'Alto']:
        subset = df[df[f'tercil_{var_mejor}'] == tercil]
        ax.scatter(subset[var_x], subset[var_y],
                   c=colores_tercil[tercil], alpha=0.5, label=f'{mejor_modulador} {tercil}', s=25)

        # Linea de regresion
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax.plot(x_line, p(x_line), c=colores_tercil[tercil], linewidth=2.5, linestyle='--')

    ax.set_xlabel(row['Nombre_X'], fontsize=10, fontweight='bold')
    ax.set_ylabel(row['Nombre_Y'], fontsize=10)
    ax.set_title(f"{row['Nombre_X']} vs {row['Nombre_Y']}\n(Diff: {row['Diferencia']:.2f})", fontsize=10)
    if i == 0:
        ax.legend(fontsize=8)

plt.suptitle(f'Efecto Modulador de {mejor_modulador}\n(Top 3 combinaciones con mayor diferencia)',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/mejor_modulador_detalle.png", dpi=150, bbox_inches='tight')
print("Guardado: mejor_modulador_detalle.png")

# =============================================================================
# 7. RESUMEN
# =============================================================================
print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)

print(f"\n1. CORRELACIONES CON EL INDICE COMPUESTO:")
print("-" * 50)
for var, nombre in vars_vulnerabilidad.items():
    if var != 'idx_vulnerabilidad':
        r = corr_matrix.loc[var, 'idx_vulnerabilidad']
        contrib = "ALTA" if abs(r) > 0.7 else "MEDIA" if abs(r) > 0.4 else "BAJA"
        print(f"   {nombre:<20}: r = {r:+.3f} (contribucion {contrib})")

print(f"\n2. RANKING DE MODULADORES:")
print("-" * 50)
for i, (nombre, diff) in enumerate(poder_modulacion.items(), 1):
    marca = " <-- MEJOR" if nombre == mejor_modulador else ""
    print(f"   {i}. {nombre:<20}: {diff:.3f}{marca}")

print(f"\n3. CONCLUSION:")
print("-" * 50)
if mejor_modulador == 'Indice Compuesto':
    print("   El INDICE COMPUESTO es el mejor modulador.")
    print("   Esto indica que la combinacion ponderada de variables")
    print("   captura mejor la vulnerabilidad que cualquier variable individual.")
else:
    print(f"   '{mejor_modulador}' es MEJOR modulador que el indice compuesto.")
    print(f"   Considerar usar esta variable directamente en los analisis.")

# Guardar resultados
df_modulacion.to_csv(f"{PROJECT_ROOT}/outputs/modelos/comparacion_moduladores_vuln.csv", index=False)
print(f"\nGuardado: comparacion_moduladores_vuln.csv")

print("\n" + "=" * 80)
