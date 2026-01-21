"""
SCIENCE TEAM ANALYSIS V5 - INTEGRACION CLIMA-BIODIVERSIDAD-SALUD-VULNERABILIDAD
Dr. Adrian David Gonzalez Chaves y Equipo
Enero 2026

Pregunta central:
Los extremos climaticos estan agravando los problemas de salud,
siendo mayores en areas con menor biodiversidad y afectando a la poblacion mas vulnerable?
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuracion
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# =============================================================================
# 1. CARGAR DATOS
# =============================================================================
print("=" * 70)
print("SCIENCE TEAM - ANALISIS INTEGRADO V5")
print("Nexo: Clima - Biodiversidad - Salud - Vulnerabilidad")
print("=" * 70)

# Cargar datos consolidados (ya incluye todas las variables)
df_master = pd.read_csv(r"C:\Users\arlex\Documents\Adrian David\data\raw\2026_01_14\all_tabela.csv")

# El archivo maestro ya tiene datos de salud
df_salud = df_master.copy()

# Filtrar municipios con datos de salud validos
health_cols = ['incidence_malaria', 'incidence_dengue', 'incidence_diarrhea',
               'incidence_leptospirose', 'incidence_chagas']
df_con_salud = df_master.dropna(subset=health_cols, how='all')

print(f"\nMunicipios totales: {len(df_master)}")
print(f"Municipios con datos de salud: {len(df_con_salud)}")

# =============================================================================
# 2. PREPARAR VARIABLES
# =============================================================================

# Variables de CLIMA (riesgo climatico)
climate_vars = ['flooding_exposure', 'flooding_risks', 'hydric_stress_exp', 'hydric_stress_risk']

# Variables de BIODIVERSIDAD
biodiv_vars = ['mean_species_richness', 'forest_cover']

# Variables de SALUD (en df_salud)
health_vars = ['incidence_malaria', 'incidence_dengue', 'incidence_diarrhea',
               'incidence_leptospirose', 'incidence_chagas']

# Variables de VULNERABILIDAD SOCIAL
vuln_vars = ['mort_infantil', 'n_pessoas_pobreza', 'n_familias_rua', 'esgoto_tratado', 'IDESP_ensino_medio']

# Gobernanza
gov_vars = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']

# =============================================================================
# 3. CREAR INDICES COMPUESTOS
# =============================================================================

# Indice de Riesgo Climatico (normalizado 0-100)
for var in climate_vars:
    if var in df_master.columns:
        df_master[f'{var}_norm'] = (df_master[var] - df_master[var].min()) / (df_master[var].max() - df_master[var].min()) * 100

climate_norm_vars = [f'{v}_norm' for v in climate_vars if f'{v}_norm' in df_master.columns]
df_master['idx_clima'] = df_master[climate_norm_vars].mean(axis=1)

# Indice de Biodiversidad (normalizado 0-100)
if 'mean_species_richness' in df_master.columns:
    df_master['biodiv_norm'] = (df_master['mean_species_richness'] - df_master['mean_species_richness'].min()) / \
                               (df_master['mean_species_richness'].max() - df_master['mean_species_richness'].min()) * 100

if 'forest_cover' in df_master.columns:
    df_master['forest_norm'] = df_master['forest_cover']  # Ya esta en %

df_master['idx_biodiv'] = df_master[['biodiv_norm', 'forest_norm']].mean(axis=1)

# Indice de Vulnerabilidad Social (normalizado 0-100)
vuln_norm = []
for var in vuln_vars:
    if var in df_master.columns:
        # Invertir variables positivas (esgoto_tratado, IDESP)
        if var in ['esgoto_tratado', 'IDESP_ensino_medio']:
            df_master[f'{var}_inv'] = 100 - (df_master[var] - df_master[var].min()) / \
                                     (df_master[var].max() - df_master[var].min()) * 100
            vuln_norm.append(f'{var}_inv')
        else:
            df_master[f'{var}_norm'] = (df_master[var] - df_master[var].min()) / \
                                       (df_master[var].max() - df_master[var].min()) * 100
            vuln_norm.append(f'{var}_norm')

if vuln_norm:
    df_master['idx_vulnerabilidad'] = df_master[vuln_norm].mean(axis=1)

# Indice de Gobernanza (UAI promedio)
gov_available = [v for v in gov_vars if v in df_master.columns]
if gov_available:
    df_master['idx_gobernanza'] = df_master[gov_available].mean(axis=1)
    df_master['idx_gobernanza_100'] = df_master['idx_gobernanza'] * 100

print("\nIndices creados:")
print(f"  - idx_clima: {df_master['idx_clima'].mean():.2f} (0-100)")
print(f"  - idx_biodiv: {df_master['idx_biodiv'].mean():.2f} (0-100)")
print(f"  - idx_vulnerabilidad: {df_master['idx_vulnerabilidad'].mean():.2f} (0-100)")
print(f"  - idx_gobernanza: {df_master['idx_gobernanza'].mean():.3f} (0-1)")

# =============================================================================
# 4. PREPARAR DATASET INTEGRADO
# =============================================================================

# Usar el dataset con datos de salud validos
df_integrado = df_con_salud.copy()

# Copiar indices al dataset integrado
for col in ['idx_clima', 'idx_biodiv', 'idx_vulnerabilidad', 'idx_gobernanza', 'idx_gobernanza_100']:
    if col in df_master.columns:
        df_integrado[col] = df_master.loc[df_integrado.index, col]

print(f"\nMunicipios para analisis integrado: {len(df_integrado)}")

# Crear indice de salud (carga de enfermedad)
health_available = [h for h in health_vars if h in df_integrado.columns]
if health_available:
    for h in health_available:
        df_integrado[f'{h}_norm'] = (df_integrado[h] - df_integrado[h].min()) / \
                                    (df_integrado[h].max() - df_integrado[h].min() + 0.001) * 100
    health_norm = [f'{h}_norm' for h in health_available]
    df_integrado['idx_carga_enfermedad'] = df_integrado[health_norm].mean(axis=1)

# =============================================================================
# 5. ANALISIS DE CORRELACIONES - NEXO COMPLETO
# =============================================================================
print("\n" + "=" * 70)
print("ANALISIS DE CORRELACIONES - NEXO MULTI-DIMENSIONAL")
print("=" * 70)

# Definir variables para correlaciones
analysis_vars = ['idx_clima', 'idx_biodiv', 'idx_vulnerabilidad', 'idx_gobernanza_100']
if 'idx_carga_enfermedad' in df_integrado.columns:
    analysis_vars.append('idx_carga_enfermedad')

# Matriz de correlaciones
results = []

# A) CLIMA vs SALUD
print("\n--- A) CLIMA vs SALUD (Hipotesis: Mayor riesgo climatico = mayor enfermedad) ---")
for h in health_available:
    if h in df_integrado.columns and 'idx_clima' in df_integrado.columns:
        valid = df_integrado[[h, 'idx_clima']].dropna()
        if len(valid) > 10:
            r, p = stats.spearmanr(valid[h], valid['idx_clima'])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {h:25} vs idx_clima: r = {r:+.3f} {sig}")
            results.append({'Dimension1': 'Clima', 'Dimension2': 'Salud',
                           'Variable1': 'idx_clima', 'Variable2': h,
                           'r': r, 'p': p})

# B) BIODIVERSIDAD vs SALUD (Efecto Dilucion)
print("\n--- B) BIODIVERSIDAD vs SALUD (Efecto Dilucion: Mayor biodiv = menor enfermedad) ---")
for h in health_available:
    if h in df_integrado.columns and 'idx_biodiv' in df_integrado.columns:
        valid = df_integrado[[h, 'idx_biodiv']].dropna()
        if len(valid) > 10:
            r, p = stats.spearmanr(valid[h], valid['idx_biodiv'])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            confirma = "CONFIRMA" if r < 0 and p < 0.05 else ""
            print(f"  {h:25} vs idx_biodiv: r = {r:+.3f} {sig} {confirma}")
            results.append({'Dimension1': 'Biodiversidad', 'Dimension2': 'Salud',
                           'Variable1': 'idx_biodiv', 'Variable2': h,
                           'r': r, 'p': p})

# C) VULNERABILIDAD vs SALUD
print("\n--- C) VULNERABILIDAD vs SALUD (Mayor vulnerabilidad = mayor enfermedad?) ---")
for h in health_available:
    if h in df_integrado.columns and 'idx_vulnerabilidad' in df_integrado.columns:
        valid = df_integrado[[h, 'idx_vulnerabilidad']].dropna()
        if len(valid) > 10:
            r, p = stats.spearmanr(valid[h], valid['idx_vulnerabilidad'])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {h:25} vs idx_vuln: r = {r:+.3f} {sig}")
            results.append({'Dimension1': 'Vulnerabilidad', 'Dimension2': 'Salud',
                           'Variable1': 'idx_vulnerabilidad', 'Variable2': h,
                           'r': r, 'p': p})

# D) CLIMA vs BIODIVERSIDAD
print("\n--- D) CLIMA vs BIODIVERSIDAD (Mayor riesgo climatico = menor biodiversidad?) ---")
if 'idx_clima' in df_master.columns and 'idx_biodiv' in df_master.columns:
    valid = df_master[['idx_clima', 'idx_biodiv']].dropna()
    r, p = stats.spearmanr(valid['idx_clima'], valid['idx_biodiv'])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  idx_clima vs idx_biodiv: r = {r:+.3f} {sig} (n={len(valid)})")
    results.append({'Dimension1': 'Clima', 'Dimension2': 'Biodiversidad',
                   'Variable1': 'idx_clima', 'Variable2': 'idx_biodiv',
                   'r': r, 'p': p})

# E) CLIMA vs VULNERABILIDAD
print("\n--- E) CLIMA vs VULNERABILIDAD (Los vulnerables enfrentan mayor riesgo climatico?) ---")
if 'idx_clima' in df_master.columns and 'idx_vulnerabilidad' in df_master.columns:
    valid = df_master[['idx_clima', 'idx_vulnerabilidad']].dropna()
    r, p = stats.spearmanr(valid['idx_clima'], valid['idx_vulnerabilidad'])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    confirma = "CONFIRMA HIPOTESIS" if r > 0 and p < 0.05 else ""
    print(f"  idx_clima vs idx_vulnerabilidad: r = {r:+.3f} {sig} {confirma} (n={len(valid)})")
    results.append({'Dimension1': 'Clima', 'Dimension2': 'Vulnerabilidad',
                   'Variable1': 'idx_clima', 'Variable2': 'idx_vulnerabilidad',
                   'r': r, 'p': p})

# F) GOBERNANZA vs VULNERABILIDAD
print("\n--- F) GOBERNANZA vs VULNERABILIDAD (Los vulnerables tienen peor gobernanza?) ---")
if 'idx_gobernanza' in df_master.columns and 'idx_vulnerabilidad' in df_master.columns:
    valid = df_master[['idx_gobernanza', 'idx_vulnerabilidad']].dropna()
    r, p = stats.spearmanr(valid['idx_gobernanza'], valid['idx_vulnerabilidad'])
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    confirma = "CONFIRMA BRECHA" if r < 0 and p < 0.05 else ""
    print(f"  idx_gobernanza vs idx_vulnerabilidad: r = {r:+.3f} {sig} {confirma} (n={len(valid)})")
    results.append({'Dimension1': 'Gobernanza', 'Dimension2': 'Vulnerabilidad',
                   'Variable1': 'idx_gobernanza', 'Variable2': 'idx_vulnerabilidad',
                   'r': r, 'p': p})

# =============================================================================
# 6. ANALISIS POR TERCILES - INTERACCION CLIMA x BIODIVERSIDAD x SALUD
# =============================================================================
print("\n" + "=" * 70)
print("ANALISIS POR TERCILES: INTERACCION CLIMA x BIODIVERSIDAD x SALUD")
print("=" * 70)

# Crear terciles
df_integrado['tercil_clima'] = pd.qcut(df_integrado['idx_clima'], 3, labels=['Bajo', 'Medio', 'Alto'])
df_integrado['tercil_biodiv'] = pd.qcut(df_integrado['idx_biodiv'], 3, labels=['Baja', 'Media', 'Alta'])
df_integrado['tercil_vuln'] = pd.qcut(df_integrado['idx_vulnerabilidad'], 3, labels=['Baja', 'Media', 'Alta'])

# Analisis cruzado: Carga de enfermedad por combinacion clima-biodiversidad
print("\n--- Carga de enfermedad promedio por CLIMA x BIODIVERSIDAD ---")
if 'idx_carga_enfermedad' in df_integrado.columns:
    tabla_cruzada = df_integrado.pivot_table(
        values='idx_carga_enfermedad',
        index='tercil_clima',
        columns='tercil_biodiv',
        aggfunc='mean'
    )
    print(tabla_cruzada.round(2))

    # Guardar tabla
    tabla_cruzada.to_csv(r"C:\Users\arlex\Documents\Adrian David\outputs\tabla_clima_biodiv_salud.csv")

# Analisis: Clima x Vulnerabilidad
print("\n--- Carga de enfermedad promedio por CLIMA x VULNERABILIDAD ---")
if 'idx_carga_enfermedad' in df_integrado.columns:
    tabla_vuln = df_integrado.pivot_table(
        values='idx_carga_enfermedad',
        index='tercil_clima',
        columns='tercil_vuln',
        aggfunc='mean'
    )
    print(tabla_vuln.round(2))
    tabla_vuln.to_csv(r"C:\Users\arlex\Documents\Adrian David\outputs\tabla_clima_vuln_salud.csv")

# =============================================================================
# 7. IDENTIFICAR MUNICIPIOS TRIPLE BURDEN
# =============================================================================
print("\n" + "=" * 70)
print("MUNICIPIOS CON TRIPLE CARGA (Alto clima + Baja biodiv + Alta enfermedad)")
print("=" * 70)

# Definir umbrales (tercil superior/inferior)
if 'idx_carga_enfermedad' in df_integrado.columns:
    umbral_clima_alto = df_integrado['idx_clima'].quantile(0.67)
    umbral_biodiv_bajo = df_integrado['idx_biodiv'].quantile(0.33)
    umbral_enfermedad_alto = df_integrado['idx_carga_enfermedad'].quantile(0.67)

    triple_burden = df_integrado[
        (df_integrado['idx_clima'] >= umbral_clima_alto) &
        (df_integrado['idx_biodiv'] <= umbral_biodiv_bajo) &
        (df_integrado['idx_carga_enfermedad'] >= umbral_enfermedad_alto)
    ]

    print(f"\nMunicipios con TRIPLE CARGA: {len(triple_burden)}")
    if len(triple_burden) > 0:
        cols_mostrar = ['idx_clima', 'idx_biodiv', 'idx_carga_enfermedad', 'idx_vulnerabilidad']
        cols_disponibles = [c for c in cols_mostrar if c in triple_burden.columns]
        if 'NM_MUN' in triple_burden.columns:
            cols_disponibles = ['NM_MUN'] + cols_disponibles
        print(triple_burden[cols_disponibles].head(10))

        # Guardar
        triple_burden.to_csv(r"C:\Users\arlex\Documents\Adrian David\outputs\municipios_triple_burden.csv", index=False)

# =============================================================================
# 8. VISUALIZACIONES
# =============================================================================
print("\n" + "=" * 70)
print("GENERANDO VISUALIZACIONES")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# A) Heatmap de correlaciones entre indices
ax1 = axes[0, 0]
indices = ['idx_clima', 'idx_biodiv', 'idx_vulnerabilidad', 'idx_gobernanza_100']
indices_disponibles = [i for i in indices if i in df_master.columns]
if 'idx_carga_enfermedad' in df_integrado.columns:
    # Usar df_integrado para incluir salud
    corr_indices = df_integrado[indices_disponibles + ['idx_carga_enfermedad']].corr(method='spearman')
else:
    corr_indices = df_master[indices_disponibles].corr(method='spearman')

sns.heatmap(corr_indices, annot=True, cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, ax=ax1, fmt='.2f')
ax1.set_title('Correlaciones entre Dimensiones\n(Spearman)', fontsize=12, fontweight='bold')

# B) Scatter: Clima vs Carga de Enfermedad, coloreado por Biodiversidad
ax2 = axes[0, 1]
if 'idx_carga_enfermedad' in df_integrado.columns:
    scatter = ax2.scatter(df_integrado['idx_clima'], df_integrado['idx_carga_enfermedad'],
                         c=df_integrado['idx_biodiv'], cmap='RdYlGn', alpha=0.6, s=50)
    plt.colorbar(scatter, ax=ax2, label='Indice Biodiversidad')
    ax2.set_xlabel('Indice Riesgo Climatico')
    ax2.set_ylabel('Indice Carga de Enfermedad')
    ax2.set_title('Clima vs Salud (color = Biodiversidad)', fontsize=12, fontweight='bold')

    # Linea de tendencia
    z = np.polyfit(df_integrado['idx_clima'].dropna(),
                   df_integrado['idx_carga_enfermedad'].dropna(), 1)
    p = np.poly1d(z)
    ax2.plot(df_integrado['idx_clima'].sort_values(),
             p(df_integrado['idx_clima'].sort_values()),
             "r--", alpha=0.8, linewidth=2)

# C) Boxplot: Carga de enfermedad por tercil de biodiversidad
ax3 = axes[1, 0]
if 'idx_carga_enfermedad' in df_integrado.columns:
    df_integrado.boxplot(column='idx_carga_enfermedad', by='tercil_biodiv', ax=ax3)
    ax3.set_xlabel('Tercil de Biodiversidad')
    ax3.set_ylabel('Indice Carga de Enfermedad')
    ax3.set_title('Efecto Dilucion: Mas Biodiversidad = Menos Enfermedad?', fontsize=12, fontweight='bold')
    plt.suptitle('')  # Eliminar titulo automatico

# D) Boxplot: Carga de enfermedad por tercil de vulnerabilidad
ax4 = axes[1, 1]
if 'idx_carga_enfermedad' in df_integrado.columns:
    df_integrado.boxplot(column='idx_carga_enfermedad', by='tercil_vuln', ax=ax4)
    ax4.set_xlabel('Tercil de Vulnerabilidad Social')
    ax4.set_ylabel('Indice Carga de Enfermedad')
    ax4.set_title('Vulnerables Enfrentan Mayor Carga de Enfermedad?', fontsize=12, fontweight='bold')
    plt.suptitle('')

plt.tight_layout()
plt.savefig(r"C:\Users\arlex\Documents\Adrian David\outputs\figures\nexo_clima_biodiv_salud_v5.png",
            dpi=150, bbox_inches='tight')
print("  Guardado: nexo_clima_biodiv_salud_v5.png")

# =============================================================================
# 9. FIGURA ADICIONAL: INTERACCION TRIPLE
# =============================================================================
fig2, ax = plt.subplots(figsize=(10, 8))

if 'idx_carga_enfermedad' in df_integrado.columns:
    # Crear grupos combinados
    df_integrado['grupo_clima_biodiv'] = df_integrado['tercil_clima'].astype(str) + ' Clima / ' + \
                                          df_integrado['tercil_biodiv'].astype(str) + ' Biodiv'

    # Ordenar grupos
    orden = ['Bajo Clima / Alta Biodiv', 'Bajo Clima / Media Biodiv', 'Bajo Clima / Baja Biodiv',
             'Medio Clima / Alta Biodiv', 'Medio Clima / Media Biodiv', 'Medio Clima / Baja Biodiv',
             'Alto Clima / Alta Biodiv', 'Alto Clima / Media Biodiv', 'Alto Clima / Baja Biodiv']

    # Calcular medias por grupo
    medias = df_integrado.groupby('grupo_clima_biodiv')['idx_carga_enfermedad'].mean().sort_values()

    # Colores basados en valor
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(medias)))

    bars = ax.barh(range(len(medias)), medias.values, color=colors)
    ax.set_yticks(range(len(medias)))
    ax.set_yticklabels(medias.index)
    ax.set_xlabel('Indice Promedio de Carga de Enfermedad')
    ax.set_title('Interaccion CLIMA x BIODIVERSIDAD sobre SALUD\n(Mayor valor = Mayor carga de enfermedad)',
                 fontsize=12, fontweight='bold')

    # Agregar valores
    for i, (idx, val) in enumerate(medias.items()):
        ax.text(val + 0.5, i, f'{val:.1f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(r"C:\Users\arlex\Documents\Adrian David\outputs\figures\interaccion_clima_biodiv_salud.png",
            dpi=150, bbox_inches='tight')
print("  Guardado: interaccion_clima_biodiv_salud.png")

# =============================================================================
# 10. GUARDAR RESULTADOS
# =============================================================================

# Guardar correlaciones
df_results = pd.DataFrame(results)
df_results.to_csv(r"C:\Users\arlex\Documents\Adrian David\outputs\correlaciones_nexo_v5.csv", index=False)
print("\n  Guardado: correlaciones_nexo_v5.csv")

# Guardar dataset integrado
df_integrado.to_csv(r"C:\Users\arlex\Documents\Adrian David\outputs\municipios_integrado_v5.csv", index=False)
print("  Guardado: municipios_integrado_v5.csv")

# =============================================================================
# 11. RESUMEN EJECUTIVO
# =============================================================================
print("\n" + "=" * 70)
print("RESUMEN EJECUTIVO - HALLAZGOS CLAVE")
print("=" * 70)

print("""
PREGUNTA: Los extremos climaticos estan agravando los problemas de salud,
          siendo mayores en areas con menor biodiversidad y afectando
          a la poblacion mas vulnerable?

HALLAZGOS:
""")

# Calcular estadisticas clave
if 'idx_carga_enfermedad' in df_integrado.columns:
    # 1. Efecto del clima en salud
    r_clima_salud, p_clima_salud = stats.spearmanr(
        df_integrado['idx_clima'].dropna(),
        df_integrado['idx_carga_enfermedad'].dropna()
    )
    print(f"1. CLIMA -> SALUD:")
    print(f"   Correlacion riesgo climatico vs carga enfermedad: r = {r_clima_salud:+.3f}")
    if r_clima_salud > 0 and p_clima_salud < 0.05:
        print(f"   CONFIRMADO: Mayor riesgo climatico asociado a mayor enfermedad")
    else:
        print(f"   NO CONFIRMADO: Relacion no significativa (p={p_clima_salud:.3f})")

    # 2. Efecto de biodiversidad en salud
    r_biodiv_salud, p_biodiv_salud = stats.spearmanr(
        df_integrado['idx_biodiv'].dropna(),
        df_integrado['idx_carga_enfermedad'].dropna()
    )
    print(f"\n2. BIODIVERSIDAD -> SALUD (Efecto Dilucion):")
    print(f"   Correlacion biodiversidad vs carga enfermedad: r = {r_biodiv_salud:+.3f}")
    if r_biodiv_salud < 0 and p_biodiv_salud < 0.05:
        print(f"   CONFIRMADO: Mayor biodiversidad asociada a MENOR enfermedad")
    else:
        print(f"   NO CONFIRMADO: Relacion no significativa (p={p_biodiv_salud:.3f})")

    # 3. Vulnerables con mayor enfermedad?
    r_vuln_salud, p_vuln_salud = stats.spearmanr(
        df_integrado['idx_vulnerabilidad'].dropna(),
        df_integrado['idx_carga_enfermedad'].dropna()
    )
    print(f"\n3. VULNERABILIDAD -> SALUD:")
    print(f"   Correlacion vulnerabilidad vs carga enfermedad: r = {r_vuln_salud:+.3f}")
    if r_vuln_salud > 0 and p_vuln_salud < 0.05:
        print(f"   CONFIRMADO: Poblacion vulnerable tiene mayor carga de enfermedad")
    else:
        print(f"   NO CONFIRMADO: Relacion no significativa (p={p_vuln_salud:.3f})")

# 4. Interaccion clima-biodiversidad
print(f"\n4. INTERACCION CLIMA x BIODIVERSIDAD:")
if 'idx_carga_enfermedad' in df_integrado.columns:
    # Comparar extremos
    alto_clima_baja_biodiv = df_integrado[
        (df_integrado['tercil_clima'] == 'Alto') &
        (df_integrado['tercil_biodiv'] == 'Baja')
    ]['idx_carga_enfermedad'].mean()

    bajo_clima_alta_biodiv = df_integrado[
        (df_integrado['tercil_clima'] == 'Bajo') &
        (df_integrado['tercil_biodiv'] == 'Alta')
    ]['idx_carga_enfermedad'].mean()

    diferencia = alto_clima_baja_biodiv - bajo_clima_alta_biodiv
    print(f"   Carga enfermedad en Alto Clima + Baja Biodiv: {alto_clima_baja_biodiv:.1f}")
    print(f"   Carga enfermedad en Bajo Clima + Alta Biodiv: {bajo_clima_alta_biodiv:.1f}")
    print(f"   Diferencia: {diferencia:+.1f} puntos")
    if diferencia > 5:
        print(f"   CONFIRMADO: La combinacion de alto riesgo climatico + baja biodiversidad")
        print(f"               genera MAYOR carga de enfermedad")

print("\n" + "=" * 70)
print("ANALISIS COMPLETADO")
print("=" * 70)

plt.show()
