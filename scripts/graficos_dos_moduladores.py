"""
=============================================================================
Graficos de Regresion con DOS Moduladores
=============================================================================

Modulador 1: % Poblacion Negra (mejor modulador, captura vulnerabilidad urbana)
Modulador 2: Indice Compuesto (dominado por pobreza, r=0.75)

Genera graficos identicos para comparar como cada modulador afecta
la relacion entre Gobernanza/Biodiversidad y Riesgo Ambiental.

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
print("GRAFICOS DE REGRESION CON DOS MODULADORES")
print("=" * 80)

df = pd.read_csv(f"{PROJECT_ROOT}/outputs/municipios_integrado_v6.csv")
print(f"\nDatos: {len(df)} municipios")

# =============================================================================
# 2. CREAR TERCILES PARA AMBOS MODULADORES
# =============================================================================
print("\n2. Creando terciles para ambos moduladores...")

# Modulador 1: % Poblacion Negra
df['tercil_pct_preta'] = pd.qcut(
    df['pct_preta'].rank(method='first'),
    q=3,
    labels=['Bajo', 'Medio', 'Alto']
)

# Modulador 2: Indice Compuesto (vulnerabilidad)
df['tercil_idx_vuln'] = pd.qcut(
    df['idx_vulnerabilidad'].rank(method='first'),
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

print("   % Pob. Negra - Terciles:")
for t in ['Bajo', 'Medio', 'Alto']:
    n = (df['tercil_pct_preta'] == t).sum()
    media = df[df['tercil_pct_preta'] == t]['pct_preta'].mean()
    print(f"     {t}: {n} municipios (media: {media:.1f}%)")

print("\n   Indice Vulnerabilidad - Terciles:")
for t in ['Baja', 'Media', 'Alta']:
    n = (df['tercil_idx_vuln'] == t).sum()
    media = df[df['tercil_idx_vuln'] == t]['idx_vulnerabilidad'].mean()
    print(f"     {t}: {n} municipios (media: {media:.1f})")

# =============================================================================
# 3. DEFINIR COMBINACIONES DE VARIABLES
# =============================================================================

# Mejores predictores identificados
combinaciones = [
    # Fila 1: Gobernanza
    ('idx_gobernanza', 'idx_carga_enfermedad', 'UAI General', 'Carga Enfermedad'),
    ('UAI_mob', 'idx_clima', 'UAI Movilidad', 'Riesgo Climatico'),
    ('UAI_Crisk', 'pol_deficit', 'UAI Riesgo Climatico', 'Deficit Polinizacion'),
    # Fila 2: Biodiversidad
    ('idx_biodiv', 'idx_carga_enfermedad', 'Indice Biodiversidad', 'Carga Enfermedad'),
    ('max_species_richness', 'idx_clima', 'Riqueza Especies (Max)', 'Riesgo Climatico'),
    ('forest_cover', 'pol_deficit', 'Cobertura Forestal', 'Deficit Polinizacion'),
]

# Colores para terciles
colores_preta = {'Bajo': '#27ae60', 'Medio': '#f1c40f', 'Alto': '#e74c3c'}
colores_vuln = {'Baja': '#27ae60', 'Media': '#f1c40f', 'Alta': '#e74c3c'}

# =============================================================================
# 4. FUNCION PARA CREAR GRAFICOS
# =============================================================================

def crear_grafico_regresion(df, combinaciones, var_modulador, tercil_col, colores,
                            titulo_modulador, nombre_archivo):
    """
    Crea un grafico de 2x3 con regresiones estratificadas por el modulador
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 11))

    for i, (var_x, var_y, nombre_x, nombre_y) in enumerate(combinaciones):
        row = i // 3
        col = i % 3
        ax = axes[row, col]

        # Obtener terciles ordenados
        if 'preta' in tercil_col:
            terciles = ['Bajo', 'Medio', 'Alto']
            labels = [f'% Negra {t}' for t in terciles]
        else:
            terciles = ['Baja', 'Media', 'Alta']
            labels = [f'Vuln. {t}' for t in terciles]

        # Graficar cada tercil
        for tercil, label in zip(terciles, labels):
            subset = df[df[tercil_col] == tercil]
            ax.scatter(subset[var_x], subset[var_y],
                       c=colores[tercil], alpha=0.5, label=label, s=25, edgecolor='white')

            # Linea de regresion
            valid = subset[[var_x, var_y]].dropna()
            if len(valid) > 10:
                z = np.polyfit(valid[var_x], valid[var_y], 1)
                p = np.poly1d(z)
                x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
                ax.plot(x_line, p(x_line), c=colores[tercil], linewidth=2.5, linestyle='--')

        # Correlacion general
        valid_all = df[[var_x, var_y]].dropna()
        r, pval = stats.spearmanr(valid_all[var_x], valid_all[var_y])
        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""

        ax.set_xlabel(nombre_x, fontsize=10, fontweight='bold')
        ax.set_ylabel(nombre_y, fontsize=10)
        ax.set_title(f'{nombre_x} vs {nombre_y}\nr = {r:.3f} {sig}', fontsize=10)

        if i == 0:
            ax.legend(title=titulo_modulador, fontsize=8, loc='upper right')

    plt.suptitle(f'Mejores Predictores de Riesgo Ambiental\n(modulados por {titulo_modulador}, n=645)',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f"{PROJECT_ROOT}/outputs/figures/{nombre_archivo}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   Guardado: {nombre_archivo}")

# =============================================================================
# 5. CREAR GRAFICOS CON % POB. NEGRA
# =============================================================================
print("\n3. Generando graficos con modulador: % Pob. Negra...")

crear_grafico_regresion(
    df, combinaciones,
    var_modulador='pct_preta',
    tercil_col='tercil_pct_preta',
    colores=colores_preta,
    titulo_modulador='% Pob. Negra',
    nombre_archivo='regresion_modulador_pct_negra.png'
)

# =============================================================================
# 6. CREAR GRAFICOS CON INDICE VULNERABILIDAD
# =============================================================================
print("\n4. Generando graficos con modulador: Indice Vulnerabilidad (Pobreza)...")

crear_grafico_regresion(
    df, combinaciones,
    var_modulador='idx_vulnerabilidad',
    tercil_col='tercil_idx_vuln',
    colores=colores_vuln,
    titulo_modulador='Vulnerabilidad (Pobreza)',
    nombre_archivo='regresion_modulador_idx_vuln.png'
)

# =============================================================================
# 7. TABLA COMPARATIVA DE CORRELACIONES
# =============================================================================
print("\n5. Calculando correlaciones estratificadas...")

resultados = []

for var_x, var_y, nombre_x, nombre_y in combinaciones:
    # Con % Pob. Negra
    for tercil in ['Bajo', 'Medio', 'Alto']:
        subset = df[df['tercil_pct_preta'] == tercil]
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 20:
            r, p = stats.spearmanr(valid[var_x], valid[var_y])
            resultados.append({
                'Variable_X': nombre_x,
                'Variable_Y': nombre_y,
                'Modulador': '% Pob. Negra',
                'Tercil': tercil,
                'r': r,
                'p': p
            })

    # Con Indice Vulnerabilidad
    for tercil in ['Baja', 'Media', 'Alta']:
        subset = df[df['tercil_idx_vuln'] == tercil]
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 20:
            r, p = stats.spearmanr(valid[var_x], valid[var_y])
            resultados.append({
                'Variable_X': nombre_x,
                'Variable_Y': nombre_y,
                'Modulador': 'Idx Vulnerabilidad',
                'Tercil': tercil,
                'r': r,
                'p': p
            })

df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(f"{PROJECT_ROOT}/outputs/correlaciones_dos_moduladores.csv", index=False)

# =============================================================================
# 8. MOSTRAR COMPARACION
# =============================================================================
print("\n" + "=" * 90)
print("COMPARACION DE CORRELACIONES POR MODULADOR")
print("=" * 90)

print("\n{:<25} {:<20} | {:^30} | {:^30}".format(
    'Relacion', '', '% Pob. Negra', 'Idx Vulnerabilidad'))
print("{:<25} {:<20} | {:^10} {:^10} {:^10} | {:^10} {:^10} {:^10}".format(
    '', '', 'Bajo', 'Medio', 'Alto', 'Baja', 'Media', 'Alta'))
print("-" * 110)

for var_x, var_y, nombre_x, nombre_y in combinaciones:
    # Obtener correlaciones para % Pob. Negra
    r_preta = {}
    for tercil in ['Bajo', 'Medio', 'Alto']:
        row = df_resultados[(df_resultados['Variable_X'] == nombre_x) &
                            (df_resultados['Variable_Y'] == nombre_y) &
                            (df_resultados['Modulador'] == '% Pob. Negra') &
                            (df_resultados['Tercil'] == tercil)]
        if len(row) > 0:
            r = row['r'].values[0]
            p = row['p'].values[0]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            r_preta[tercil] = f"{r:+.2f}{sig}"
        else:
            r_preta[tercil] = "N/A"

    # Obtener correlaciones para Idx Vulnerabilidad
    r_vuln = {}
    for tercil in ['Baja', 'Media', 'Alta']:
        row = df_resultados[(df_resultados['Variable_X'] == nombre_x) &
                            (df_resultados['Variable_Y'] == nombre_y) &
                            (df_resultados['Modulador'] == 'Idx Vulnerabilidad') &
                            (df_resultados['Tercil'] == tercil)]
        if len(row) > 0:
            r = row['r'].values[0]
            p = row['p'].values[0]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            r_vuln[tercil] = f"{r:+.2f}{sig}"
        else:
            r_vuln[tercil] = "N/A"

    print("{:<25} {:<20} | {:^10} {:^10} {:^10} | {:^10} {:^10} {:^10}".format(
        nombre_x[:23], nombre_y[:18],
        r_preta.get('Bajo', 'N/A'), r_preta.get('Medio', 'N/A'), r_preta.get('Alto', 'N/A'),
        r_vuln.get('Baja', 'N/A'), r_vuln.get('Media', 'N/A'), r_vuln.get('Alta', 'N/A')
    ))

# =============================================================================
# 9. GRAFICO COMPARATIVO LADO A LADO
# =============================================================================
print("\n6. Generando grafico comparativo lado a lado...")

fig, axes = plt.subplots(2, 6, figsize=(24, 10))

# Columnas 0-2: Modulador % Pob. Negra
# Columnas 3-5: Modulador Idx Vulnerabilidad

for i, (var_x, var_y, nombre_x, nombre_y) in enumerate(combinaciones):
    row = i // 3
    col_preta = i % 3
    col_vuln = (i % 3) + 3

    # Grafico con % Pob. Negra
    ax1 = axes[row, col_preta]
    for tercil in ['Bajo', 'Medio', 'Alto']:
        subset = df[df['tercil_pct_preta'] == tercil]
        ax1.scatter(subset[var_x], subset[var_y],
                    c=colores_preta[tercil], alpha=0.5, s=20, edgecolor='white')
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax1.plot(x_line, p(x_line), c=colores_preta[tercil], linewidth=2, linestyle='--')

    r, pval = stats.spearmanr(df[var_x].dropna(), df[var_y].dropna())
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
    ax1.set_xlabel(nombre_x, fontsize=9)
    ax1.set_ylabel(nombre_y, fontsize=9)
    ax1.set_title(f'{nombre_x[:20]}\nvs {nombre_y[:15]} (r={r:.2f}{sig})', fontsize=9)

    # Grafico con Idx Vulnerabilidad
    ax2 = axes[row, col_vuln]
    for tercil in ['Baja', 'Media', 'Alta']:
        subset = df[df['tercil_idx_vuln'] == tercil]
        ax2.scatter(subset[var_x], subset[var_y],
                    c=colores_vuln[tercil], alpha=0.5, s=20, edgecolor='white')
        valid = subset[[var_x, var_y]].dropna()
        if len(valid) > 10:
            z = np.polyfit(valid[var_x], valid[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(valid[var_x].min(), valid[var_x].max(), 50)
            ax2.plot(x_line, p(x_line), c=colores_vuln[tercil], linewidth=2, linestyle='--')

    ax2.set_xlabel(nombre_x, fontsize=9)
    ax2.set_ylabel(nombre_y, fontsize=9)
    ax2.set_title(f'{nombre_x[:20]}\nvs {nombre_y[:15]} (r={r:.2f}{sig})', fontsize=9)

# Agregar leyendas
from matplotlib.patches import Patch
legend_preta = [Patch(facecolor=colores_preta[t], label=f'% Negra {t}') for t in ['Bajo', 'Medio', 'Alto']]
legend_vuln = [Patch(facecolor=colores_vuln[t], label=f'Vuln. {t}') for t in ['Baja', 'Media', 'Alta']]

axes[0, 0].legend(handles=legend_preta, loc='upper right', fontsize=7)
axes[0, 3].legend(handles=legend_vuln, loc='upper right', fontsize=7)

# Titulos de columnas
fig.text(0.25, 0.98, 'MODULADOR: % POBLACION NEGRA', ha='center', fontsize=12, fontweight='bold')
fig.text(0.75, 0.98, 'MODULADOR: INDICE VULNERABILIDAD (Pobreza)', ha='center', fontsize=12, fontweight='bold')

plt.suptitle('COMPARACION DE MODULADORES: Gobernanza y Biodiversidad vs Riesgo Ambiental\n(n=645 municipios de Sao Paulo)',
             fontsize=14, fontweight='bold', y=1.04)
plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/comparacion_dos_moduladores.png", dpi=150, bbox_inches='tight')
plt.close()
print("   Guardado: comparacion_dos_moduladores.png")

# =============================================================================
# 10. RESUMEN
# =============================================================================
print("\n" + "=" * 80)
print("ARCHIVOS GENERADOS")
print("=" * 80)
print("  - regresion_modulador_pct_negra.png")
print("  - regresion_modulador_idx_vuln.png")
print("  - comparacion_dos_moduladores.png")
print("  - correlaciones_dos_moduladores.csv")
print("=" * 80)
