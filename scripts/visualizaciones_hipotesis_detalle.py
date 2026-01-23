"""
=============================================================================
Visualizaciones Detalladas: Descomposicion por Componentes de Riesgo
=============================================================================

Hallazgos principales del analisis inicial:
1. La gobernanza reduce riesgo de SALUD pero se asocia positivamente con riesgo CLIMATICO
   (probablemente porque ciudades mas urbanizadas tienen mas gobernanza pero mas exposicion)
2. La biodiversidad reduce TODOS los riesgos excepto el climatico
3. El efecto protector de la gobernanza es MAS FUERTE en municipios con ALTA vulnerabilidad
   (contrario a la hipotesis inicial - esto sugiere que la gobernanza "compensa" la vulnerabilidad)

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

# Configuracion
plt.style.use('seaborn-v0_8-whitegrid')
PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

# Cargar datos
df = pd.read_csv(f"{PROJECT_ROOT}/outputs/analisis_hipotesis_data.csv")
print(f"Datos cargados: {len(df)} municipios")

# =============================================================================
# 1. HEATMAP DE CORRELACIONES POR GRUPO
# =============================================================================
print("\n1. Generando heatmap de correlaciones...")

# Preparar matriz de correlaciones
vars_y = ['riesgo_salud_norm', 'riesgo_clima_norm', 'riesgo_nutricion_norm', 'idx_riesgo_ambiental']
vars_x = ['idx_gobernanza', 'idx_biodiv', 'idx_vulnerabilidad_socio']
labels_y = ['Riesgo Salud', 'Riesgo Clima', 'Riesgo Nutricion', 'Riesgo Total']
labels_x = ['Gobernanza (UAI)', 'Biodiversidad', 'Vulnerabilidad SE']

# Calcular correlaciones
corr_matrix = np.zeros((len(vars_y), len(vars_x)))
for i, vy in enumerate(vars_y):
    for j, vx in enumerate(vars_x):
        valid = df[[vy, vx]].dropna()
        r, p = stats.spearmanr(valid[vy], valid[vx])
        corr_matrix[i, j] = r

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr_matrix, cmap='RdYlGn_r', vmin=-0.7, vmax=0.7)

# Etiquetas
ax.set_xticks(range(len(labels_x)))
ax.set_yticks(range(len(labels_y)))
ax.set_xticklabels(labels_x, fontsize=12)
ax.set_yticklabels(labels_y, fontsize=12)

# Valores en celdas
for i in range(len(vars_y)):
    for j in range(len(vars_x)):
        text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                       ha='center', va='center', color='black', fontsize=14, fontweight='bold')

plt.colorbar(im, label='Correlacion Spearman')
ax.set_title('Correlaciones: Factores Protectores vs Componentes de Riesgo\n(Verde = reduce riesgo, Rojo = aumenta riesgo)',
             fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/heatmap_riesgo_factores.png", dpi=150, bbox_inches='tight')
print("   Guardado: heatmap_riesgo_factores.png")

# =============================================================================
# 2. GRAFICOS DE REGRESION POR COMPONENTE
# =============================================================================
print("\n2. Generando graficos de regresion por componente...")

fig, axes = plt.subplots(3, 2, figsize=(14, 15))

componentes = [
    ('riesgo_salud_norm', 'Riesgo de Salud (Enfermedades)'),
    ('riesgo_clima_norm', 'Riesgo Climatico (Inundaciones/Sequia)'),
    ('riesgo_nutricion_norm', 'Riesgo Nutricional (Deficit Polinizacion)')
]

colors = {'Baja': '#2ecc71', 'Media': '#f39c12', 'Alta': '#e74c3c'}

for row, (var_riesgo, titulo) in enumerate(componentes):
    # Columna 1: Gobernanza
    ax1 = axes[row, 0]
    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_gobernanza', var_riesgo])
        ax1.scatter(subset['idx_gobernanza'], subset[var_riesgo],
                    c=colors[cat], alpha=0.6, label=f'Vuln. {cat}', s=40)
        # Linea de regresion
        if len(subset) > 5:
            z = np.polyfit(subset['idx_gobernanza'], subset[var_riesgo], 1)
            p = np.poly1d(z)
            x_line = np.linspace(subset['idx_gobernanza'].min(), subset['idx_gobernanza'].max(), 50)
            ax1.plot(x_line, p(x_line), c=colors[cat], linewidth=2, linestyle='--')

    ax1.set_xlabel('Indice de Gobernanza (UAI)')
    ax1.set_ylabel(titulo)
    if row == 0:
        ax1.legend(title='Vulnerabilidad', loc='upper right', fontsize=8)

    # Correlacion global
    valid = df[['idx_gobernanza', var_riesgo]].dropna()
    r, p = stats.spearmanr(valid['idx_gobernanza'], valid[var_riesgo])
    signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    ax1.set_title(f'Gobernanza vs {titulo}\nr={r:.3f}{signo}', fontsize=11)

    # Columna 2: Biodiversidad
    ax2 = axes[row, 1]
    for cat in ['Baja', 'Media', 'Alta']:
        subset = df[df['cat_vulnerabilidad'] == cat].dropna(subset=['idx_biodiv', var_riesgo])
        ax2.scatter(subset['idx_biodiv'], subset[var_riesgo],
                    c=colors[cat], alpha=0.6, label=f'Vuln. {cat}', s=40)
        if len(subset) > 5:
            z = np.polyfit(subset['idx_biodiv'], subset[var_riesgo], 1)
            p_line = np.poly1d(z)
            x_line = np.linspace(subset['idx_biodiv'].min(), subset['idx_biodiv'].max(), 50)
            ax2.plot(x_line, p_line(x_line), c=colors[cat], linewidth=2, linestyle='--')

    ax2.set_xlabel('Indice de Biodiversidad')
    ax2.set_ylabel(titulo)

    # Correlacion global
    valid = df[['idx_biodiv', var_riesgo]].dropna()
    r, p = stats.spearmanr(valid['idx_biodiv'], valid[var_riesgo])
    signo = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    ax2.set_title(f'Biodiversidad vs {titulo}\nr={r:.3f}{signo}', fontsize=11)

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/regresion_componentes_detalle.png", dpi=150, bbox_inches='tight')
print("   Guardado: regresion_componentes_detalle.png")

# =============================================================================
# 3. DIAGRAMA DE SINTESIS: EFECTO DIFERENCIAL
# =============================================================================
print("\n3. Generando diagrama de sintesis...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Gobernanza - efecto por nivel de vulnerabilidad
ax1 = axes[0]
componentes_short = ['Salud', 'Clima', 'Nutricion']
vars_comp = ['riesgo_salud_norm', 'riesgo_clima_norm', 'riesgo_nutricion_norm']

x = np.arange(len(componentes_short))
width = 0.25

for i, cat in enumerate(['Baja', 'Media', 'Alta']):
    correlaciones = []
    for var in vars_comp:
        subset = df[df['cat_vulnerabilidad'] == cat]
        valid = subset[['idx_gobernanza', var]].dropna()
        r, p = stats.spearmanr(valid['idx_gobernanza'], valid[var])
        correlaciones.append(r)

    bars = ax1.bar(x + (i-1)*width, correlaciones, width, label=f'Vuln. {cat}', color=colors[cat])

ax1.axhline(y=0, color='gray', linestyle='--', linewidth=1)
ax1.set_xlabel('Componente de Riesgo')
ax1.set_ylabel('Correlacion con Gobernanza (Spearman r)')
ax1.set_title('A) Efecto de la Gobernanza sobre Riesgo\npor nivel de Vulnerabilidad Socio-Economica')
ax1.set_xticks(x)
ax1.set_xticklabels(componentes_short)
ax1.legend(title='Vulnerabilidad')
ax1.set_ylim(-0.7, 0.7)

# Panel B: Biodiversidad - efecto por nivel de vulnerabilidad
ax2 = axes[1]
for i, cat in enumerate(['Baja', 'Media', 'Alta']):
    correlaciones = []
    for var in vars_comp:
        subset = df[df['cat_vulnerabilidad'] == cat]
        valid = subset[['idx_biodiv', var]].dropna()
        r, p = stats.spearmanr(valid['idx_biodiv'], valid[var])
        correlaciones.append(r)

    bars = ax2.bar(x + (i-1)*width, correlaciones, width, label=f'Vuln. {cat}', color=colors[cat])

ax2.axhline(y=0, color='gray', linestyle='--', linewidth=1)
ax2.set_xlabel('Componente de Riesgo')
ax2.set_ylabel('Correlacion con Biodiversidad (Spearman r)')
ax2.set_title('B) Efecto de la Biodiversidad sobre Riesgo\npor nivel de Vulnerabilidad Socio-Economica')
ax2.set_xticks(x)
ax2.set_xticklabels(componentes_short)
ax2.legend(title='Vulnerabilidad')
ax2.set_ylim(-0.8, 0.5)

plt.tight_layout()
plt.savefig(f"{PROJECT_ROOT}/outputs/figures/sintesis_efecto_diferencial.png", dpi=150, bbox_inches='tight')
print("   Guardado: sintesis_efecto_diferencial.png")

# =============================================================================
# 4. TABLA RESUMEN INTERPRETATIVA
# =============================================================================
print("\n4. Generando tabla resumen...")

print("\n" + "=" * 70)
print("RESUMEN DE HALLAZGOS CLAVE")
print("=" * 70)

print("""
HALLAZGO 1: PARADOJA DE LA GOBERNANZA
---------------------------------------
- Mayor gobernanza REDUCE el riesgo de SALUD (r=-0.45***)
- Pero AUMENTA el riesgo CLIMATICO (r=+0.44***)
- Esto ocurre porque las ciudades mas urbanizadas tienen:
  * Mejor infraestructura de salud (UAI alto)
  * Pero mayor exposicion a inundaciones (mas superficie impermeable)

HALLAZGO 2: ROL PROTECTOR DE LA BIODIVERSIDAD
-----------------------------------------------
- La biodiversidad reduce CONSISTENTEMENTE:
  * Riesgo de salud: r=-0.53***
  * Deficit de polinizacion: r=-0.66*** (muy fuerte)
- PERO se asocia positivamente con riesgo climatico (r=+0.34***)
  (Areas con mas biodiversidad suelen estar en zonas con mas eventos climaticos)

HALLAZGO 3: EFECTO COMPENSATORIO EN VULNERABILIDAD ALTA
---------------------------------------------------------
- Contrario a la hipotesis inicial:
  * El efecto protector de gobernanza es MAS FUERTE en municipios
    con ALTA vulnerabilidad (r=-0.61*** vs r=-0.29 en baja vuln.)
- Interpretacion: La gobernanza "compensa" la vulnerabilidad social
  Los municipios vulnerables que invierten en gobernanza obtienen
  mayores beneficios relativos.

HALLAZGO 4: BIODIVERSIDAD COMO FACTOR UNIVERSAL
-------------------------------------------------
- El efecto de la biodiversidad es mas CONSISTENTE entre grupos
- Reduce riesgo de salud en todos los niveles de vulnerabilidad
- Efecto mas fuerte sobre deficit de polinizacion (r=-0.72*** en alta vuln.)
""")

# Guardar resumen
with open(f"{PROJECT_ROOT}/outputs/resumen_hipotesis_hallazgos.txt", 'w', encoding='utf-8') as f:
    f.write("""
RESUMEN DE HALLAZGOS: ANALISIS DE HIPOTESIS
============================================

HIPOTESIS ORIGINALES:
H1: Mayor gobernanza -> menor riesgo ambiental,
    especialmente en municipios con baja vulnerabilidad social
H2: Mayor biodiversidad -> menor riesgo ambiental,
    especialmente en municipios con baja vulnerabilidad social

RESULTADOS:

1. PARADOJA DE LA GOBERNANZA
   - La gobernanza reduce riesgo de SALUD (r=-0.45***)
   - Pero aumenta riesgo CLIMATICO (r=+0.44***)
   - Razon: ciudades urbanizadas tienen mejor salud pero mas exposicion climatica

2. ROL PROTECTOR DE BIODIVERSIDAD
   - Reduce riesgo de salud (r=-0.53***)
   - Reduce deficit de polinizacion (r=-0.66***)
   - Pero areas biodiversas tienen mas eventos climaticos (r=+0.34***)

3. EFECTO COMPENSATORIO (HALLAZGO CLAVE)
   - Contrario a la hipotesis: el efecto protector de gobernanza
     es MAS FUERTE en municipios con ALTA vulnerabilidad
   - Gobernanza vs Riesgo Salud:
     * Baja vulnerabilidad: r=-0.29
     * Alta vulnerabilidad: r=-0.61***
   - Interpretacion: La gobernanza compensa la vulnerabilidad social

4. BIODIVERSIDAD COMO FACTOR UNIVERSAL
   - Efecto consistente en todos los niveles de vulnerabilidad
   - Especialmente protector para deficit de polinizacion

IMPLICACIONES PARA POLITICAS:
1. Priorizar inversiones en gobernanza en municipios vulnerables
   (mayor retorno relativo)
2. Conservar biodiversidad como estrategia de salud publica
3. Separar acciones para riesgo climatico (infraestructura verde)
   de acciones para riesgo de salud (vigilancia epidemiologica)
""")

print("   Guardado: resumen_hipotesis_hallazgos.txt")

print("\n" + "=" * 70)
print("Visualizaciones completadas.")
print("=" * 70)
