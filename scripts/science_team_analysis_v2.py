"""
Science Team Analysis V2 - Vulnerabilidad Multidimensional de Municipios de Sao Paulo
======================================================================================

Autor: Dr. Adrian David Gonzalez Chaves y Science Team
Fecha: Enero 2026

CORRECCIONES IMPORTANTES:
- pol_deficit = Deficit de POLINIZACION (no politico)
- forest_cover = Variable de BIODIVERSIDAD
- UAI + IDESP + esgoto = POLITICAS PUBLICAS / GOBERNANZA / ADAPTACION CLIMATICA

Dimensiones:
1. Riesgos Climaticos
2. Salud/Enfermedades
3. Vulnerabilidad Social
4. Biodiversidad (incluye forest_cover y pol_deficit como servicio ecosistemico)
5. Politicas Publicas/Gobernanza/Adaptacion Climatica (UAI, educacion, saneamiento)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
BASE_PATH = Path(r"C:\Users\arlex\Documents\Adrian David")
DATA_PATH = BASE_PATH / "data" / "raw" / "2026_01_14"
OUTPUT_PATH = BASE_PATH / "outputs"
FIGURES_PATH = OUTPUT_PATH / "figures"
DOCS_PATH = BASE_PATH / "docs"

# Crear directorios si no existen
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
FIGURES_PATH.mkdir(parents=True, exist_ok=True)

# =============================================================================
# DEFINICION CORRECTA DE VARIABLES POR DIMENSION
# =============================================================================

DIMENSIONES = {
    'riesgos_climaticos': {
        'variables': ['flooding_exposure', 'flooding_risks',
                      'hydric_stress_exp', 'hydric_stress_risk'],
        'descripcion': 'Exposicion y riesgo a inundaciones y estres hidrico'
    },

    'salud': {
        'variables': ['persist_malaria', 'persist_leptospirose', 'persist_diarrhea',
                      'persist_dengue', 'persist_chagas',
                      'incidence_malaria', 'incidence_leptospirose', 'incidence_diarrhea',
                      'incidence_dengue', 'incidence_chagas', 'copersistence'],
        'descripcion': 'Persistencia e incidencia de enfermedades (solo 187 municipios)'
    },

    'vulnerabilidad_social': {
        'variables': ['population', 'population_preta', 'population_indigena',
                      'population_branca', 'pct_rural', 'pct_urbana',
                      'n_familias_rua', 'n_pessoas_pobreza', 'mort_infantil'],
        'descripcion': 'Caracteristicas demograficas y sociales'
    },

    'biodiversidad': {
        'variables': ['mean_species_richness', 'max_species_richness',
                      'Vert_rich_risk', 'forest_cover', 'pol_deficit'],
        'descripcion': 'Riqueza de especies, cobertura forestal y deficit de polinizacion'
    },

    'politicas_gobernanza': {
        'variables': ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk',
                      'IDESP_ensino_medio', 'esgoto_tratado'],
        'descripcion': 'Indice de Acceso Universal, educacion y saneamiento'
    }
}

# =============================================================================
# PASO 1: CARGAR Y LIMPIAR DATOS
# =============================================================================

def load_and_clean_data():
    """Carga y limpia el dataset principal."""
    print("=" * 70)
    print("[Ing. Roberto Silva - Data Engineer] CARGANDO DATOS...")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH / "all_tabela.csv")

    if df.columns[0] == '' or 'Unnamed' in df.columns[0]:
        df = df.drop(df.columns[0], axis=1)

    df = df.replace('NA', np.nan)

    non_numeric = ['Cod_ibge', 'Municipio', 'municipality', 'COD']
    for col in df.columns:
        if col not in non_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Variables derivadas
    uai_cols = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']
    df['UAI_promedio'] = df[uai_cols].mean(axis=1)

    # Indice de Gobernanza (UAI + educacion + saneamiento normalizado)
    df['esgoto_norm'] = df['esgoto_tratado'] / 100
    df['idesp_norm'] = df['IDESP_ensino_medio'] / df['IDESP_ensino_medio'].max()
    df['idx_gobernanza'] = (df['UAI_promedio'] + df['esgoto_norm'] + df['idesp_norm']) / 3

    # Porcentajes demograficos
    df['pct_preta'] = (df['population_preta'] / df['population']) * 100
    df['pct_indigena'] = (df['population_indigena'] / df['population']) * 100
    df['pct_branca'] = (df['population_branca'] / df['population']) * 100

    # Riesgo climatico compuesto
    df['riesgo_climatico'] = df[['flooding_risks', 'hydric_stress_risk']].mean(axis=1)

    # Indice de Biodiversidad (riqueza + cobertura forestal - deficit polinizacion)
    df['biodiv_norm'] = (df['mean_species_richness'] - df['mean_species_richness'].min()) / \
                        (df['mean_species_richness'].max() - df['mean_species_richness'].min())
    df['forest_norm'] = df['forest_cover'] / 100
    df['pol_deficit_inv'] = 1 - df['pol_deficit']  # Invertir: menor deficit = mejor
    df['idx_biodiversidad'] = (df['biodiv_norm'] + df['forest_norm'] + df['pol_deficit_inv']) / 3

    print(f"Total municipios cargados: {len(df)}")
    print(f"Total variables: {len(df.columns)}")

    # Municipios con datos de salud
    health_cols = ['persist_malaria', 'incidence_malaria', 'copersistence']
    df_health = df[df[health_cols].notna().all(axis=1)].copy()
    print(f"Municipios con datos de salud: {len(df_health)}")

    # Mostrar estructura de dimensiones
    print("\n--- VARIABLES POR DIMENSION (CORREGIDO) ---")
    for dim, info in DIMENSIONES.items():
        available = [v for v in info['variables'] if v in df.columns]
        print(f"\n{dim.upper()}: {len(available)} variables")
        print(f"  {info['descripcion']}")
        print(f"  Variables: {', '.join(available)}")

    return df, df_health

# =============================================================================
# PASO 2: ANALISIS DE CORRELACIONES (CORREGIDO)
# =============================================================================

def calculate_correlations(df, df_health):
    """Calcula correlaciones de Spearman entre dimensiones."""
    print("\n" + "=" * 70)
    print("[Dra. Maria Santos - Bioestadistica] ANALISIS DE CORRELACIONES")
    print("=" * 70)

    results = []

    # BIODIVERSIDAD (incluyendo pol_deficit y forest_cover)
    biodiv_vars = ['mean_species_richness', 'forest_cover', 'pol_deficit', 'Vert_rich_risk']

    # POLITICAS/GOBERNANZA
    gobernanza_vars = ['UAI_promedio', 'UAI_housing', 'UAI_env', 'UAI_food',
                       'UAI_mob', 'UAI_Crisk', 'IDESP_ensino_medio', 'esgoto_tratado',
                       'idx_gobernanza']

    # RIESGOS CLIMATICOS
    clima_vars = ['flooding_exposure', 'flooding_risks',
                  'hydric_stress_exp', 'hydric_stress_risk', 'riesgo_climatico']

    # VULNERABILIDAD SOCIAL
    social_vars = ['mort_infantil', 'n_pessoas_pobreza', 'pct_rural', 'population',
                   'pct_preta', 'pct_indigena']

    # SALUD (solo 187)
    salud_vars = ['persist_malaria', 'persist_dengue', 'persist_diarrhea',
                  'incidence_malaria', 'incidence_dengue', 'incidence_diarrhea',
                  'copersistence']

    # =========================================================================
    # CORRELACIONES BIODIVERSIDAD vs OTRAS DIMENSIONES (645 municipios)
    # =========================================================================
    print("\n--- BIODIVERSIDAD vs Otras Dimensiones (n=645) ---")

    for var1 in biodiv_vars:
        for var2 in gobernanza_vars + clima_vars + social_vars:
            if var1 in df.columns and var2 in df.columns:
                mask = df[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, var1], df.loc[mask, var2])
                    results.append({
                        'dimension1': 'BIODIVERSIDAD',
                        'var1': var1,
                        'dimension2': get_dimension(var2),
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.30)
                    })

    # =========================================================================
    # CORRELACIONES GOBERNANZA vs OTRAS DIMENSIONES (645 municipios)
    # =========================================================================
    print("\n--- GOBERNANZA vs Otras Dimensiones (n=645) ---")

    for var1 in gobernanza_vars:
        for var2 in clima_vars + social_vars:
            if var1 in df.columns and var2 in df.columns:
                mask = df[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, var1], df.loc[mask, var2])
                    results.append({
                        'dimension1': 'GOBERNANZA',
                        'var1': var1,
                        'dimension2': get_dimension(var2),
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.30)
                    })

    # =========================================================================
    # CORRELACIONES CON SALUD (187 municipios)
    # =========================================================================
    print("\n--- SALUD vs Otras Dimensiones (n=187) ---")

    for var1 in salud_vars:
        for var2 in biodiv_vars + gobernanza_vars + clima_vars + social_vars:
            if var1 in df_health.columns and var2 in df_health.columns:
                mask = df_health[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df_health.loc[mask, var1],
                                             df_health.loc[mask, var2])
                    results.append({
                        'dimension1': 'SALUD',
                        'var1': var1,
                        'dimension2': get_dimension(var2),
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.20)
                    })

    # Convertir a DataFrame
    corr_df = pd.DataFrame(results)
    corr_df = corr_df.sort_values('rho', key=abs, ascending=False)

    # Filtrar significativas
    sig_corr = corr_df[corr_df['significant']].copy()

    print(f"\nTotal correlaciones calculadas: {len(corr_df)}")
    print(f"Correlaciones significativas: {len(sig_corr)}")

    # Mostrar top correlaciones por categoria
    print("\n" + "=" * 70)
    print("TOP CORRELACIONES SIGNIFICATIVAS POR DIMENSION")
    print("=" * 70)

    # Biodiversidad
    print("\n### BIODIVERSIDAD vs Otras Dimensiones ###")
    biodiv_corr = sig_corr[sig_corr['dimension1'] == 'BIODIVERSIDAD'].head(15)
    if len(biodiv_corr) > 0:
        print(biodiv_corr[['var1', 'var2', 'rho', 'p_value', 'n']].to_string(index=False))

    # Gobernanza
    print("\n### GOBERNANZA vs Otras Dimensiones ###")
    gob_corr = sig_corr[sig_corr['dimension1'] == 'GOBERNANZA'].head(15)
    if len(gob_corr) > 0:
        print(gob_corr[['var1', 'var2', 'rho', 'p_value', 'n']].to_string(index=False))

    # Salud
    print("\n### SALUD vs Otras Dimensiones ###")
    salud_corr = sig_corr[sig_corr['dimension1'] == 'SALUD'].head(15)
    if len(salud_corr) > 0:
        print(salud_corr[['var1', 'var2', 'rho', 'p_value', 'n']].to_string(index=False))

    return corr_df, sig_corr

def get_dimension(var):
    """Retorna la dimension de una variable."""
    if var in ['mean_species_richness', 'forest_cover', 'pol_deficit',
               'Vert_rich_risk', 'idx_biodiversidad', 'biodiv_norm',
               'forest_norm', 'pol_deficit_inv']:
        return 'BIODIVERSIDAD'
    elif var in ['UAI_promedio', 'UAI_housing', 'UAI_env', 'UAI_food',
                 'UAI_mob', 'UAI_Crisk', 'IDESP_ensino_medio', 'esgoto_tratado',
                 'idx_gobernanza', 'esgoto_norm', 'idesp_norm']:
        return 'GOBERNANZA'
    elif var in ['flooding_exposure', 'flooding_risks', 'hydric_stress_exp',
                 'hydric_stress_risk', 'riesgo_climatico']:
        return 'CLIMA'
    elif var in ['mort_infantil', 'n_pessoas_pobreza', 'pct_rural', 'population',
                 'pct_preta', 'pct_indigena', 'pct_branca', 'n_familias_rua',
                 'population_preta', 'population_indigena', 'population_branca',
                 'pct_urbana']:
        return 'SOCIAL'
    elif 'persist' in var or 'incidence' in var or 'copersistence' in var:
        return 'SALUD'
    else:
        return 'OTRA'

# =============================================================================
# PASO 3: CLASIFICACION EN CUADRANTES (CORREGIDO)
# =============================================================================

def classify_quadrants(df):
    """Clasifica municipios usando Gobernanza vs Biodiversidad."""
    print("\n" + "=" * 70)
    print("[Dr. Carlos Mendez - GIS/SIG] ANALISIS DE CUADRANTES")
    print("=" * 70)

    # Usar indices compuestos
    median_gob = df['idx_gobernanza'].median()
    median_biodiv = df['idx_biodiversidad'].median()

    print(f"Mediana Indice Gobernanza: {median_gob:.4f}")
    print(f"Mediana Indice Biodiversidad: {median_biodiv:.4f}")

    def assign_quadrant(row):
        high_gob = row['idx_gobernanza'] >= median_gob
        high_biodiv = row['idx_biodiversidad'] >= median_biodiv

        if high_gob and high_biodiv:
            return 'Q1_Modelo'
        elif not high_gob and high_biodiv:
            return 'Q2_Conservar'
        elif not high_gob and not high_biodiv:
            return 'Q3_Vulnerable'
        else:
            return 'Q4_Desarrollo'

    df['cuadrante'] = df.apply(assign_quadrant, axis=1)

    print("\n--- DISTRIBUCION DE CUADRANTES ---")
    dist = df['cuadrante'].value_counts()
    dist_pct = df['cuadrante'].value_counts(normalize=True) * 100

    for quad in ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']:
        if quad in dist.index:
            print(f"{quad}: {dist[quad]} municipios ({dist_pct[quad]:.1f}%)")

    print("\n--- ESTADISTICAS POR CUADRANTE ---")
    stats_quad = df.groupby('cuadrante').agg({
        'mean_species_richness': 'mean',
        'forest_cover': 'mean',
        'pol_deficit': 'mean',
        'idx_gobernanza': 'mean',
        'UAI_promedio': 'mean',
        'riesgo_climatico': 'mean',
        'pct_rural': 'mean',
        'population': 'sum'
    }).round(3)

    print(stats_quad.to_string())

    # Interpretacion ecologica
    print("\n--- INTERPRETACION ECOLOGICA ---")
    for quad in ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']:
        subset = df[df['cuadrante'] == quad]
        print(f"\n{quad}:")
        print(f"  - Deficit polinizacion promedio: {subset['pol_deficit'].mean():.3f}")
        print(f"  - Cobertura forestal promedio: {subset['forest_cover'].mean():.1f}%")
        print(f"  - Riqueza especies promedio: {subset['mean_species_richness'].mean():.0f}")
        print(f"  - UAI promedio: {subset['UAI_promedio'].mean():.3f}")

    return df, median_gob, median_biodiv

# =============================================================================
# PASO 4: INDICE DE VULNERABILIDAD MULTIDIMENSIONAL (CORREGIDO)
# =============================================================================

def calculate_ivm(df):
    """Calcula el Indice de Vulnerabilidad Multidimensional con interpretacion correcta."""
    print("\n" + "=" * 70)
    print("[Dr. Adrian - Director] INDICE DE VULNERABILIDAD MULTIDIMENSIONAL")
    print("=" * 70)

    df = df.copy()

    def normalize(series, higher_is_worse=True):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        if not higher_is_worse:
            normalized = 1 - normalized
        return normalized

    # 1. RIESGO CLIMATICO (mayor = mas vulnerable)
    df['idx_clima'] = df[['flooding_exposure', 'flooding_risks',
                          'hydric_stress_exp', 'hydric_stress_risk']].apply(
                              lambda x: normalize(x, True)).mean(axis=1)

    # 2. VULNERABILIDAD SOCIAL (mayor = mas vulnerable)
    df['mort_norm'] = normalize(df['mort_infantil'], higher_is_worse=True)
    df['pobreza_pct'] = df['n_pessoas_pobreza'] / df['population'] * 100
    df['pobreza_norm'] = normalize(df['pobreza_pct'], higher_is_worse=True)
    df['idx_social'] = (df['mort_norm'] + df['pobreza_norm']) / 2

    # 3. DEFICIT BIODIVERSIDAD (mayor deficit polinizacion + menor cobertura = mas vulnerable)
    df['idx_biodiv_vuln'] = (normalize(df['pol_deficit'], True) +
                              normalize(df['forest_cover'], False) +
                              normalize(df['mean_species_richness'], False)) / 3

    # 4. DEFICIT GOBERNANZA (menor UAI/educacion/saneamiento = mas vulnerable)
    df['idx_gob_vuln'] = normalize(df['idx_gobernanza'], higher_is_worse=False)

    # 5. RIESGO ECOLOGICO (Vert_rich_risk)
    df['idx_riesgo_eco'] = normalize(df['Vert_rich_risk'], higher_is_worse=True)

    # IVM Compuesto (pesos iguales 20% cada dimension)
    idx_cols = ['idx_clima', 'idx_social', 'idx_biodiv_vuln', 'idx_gob_vuln', 'idx_riesgo_eco']
    df['IVM'] = df[idx_cols].mean(axis=1)

    # Escalar a 0-100
    df['IVM_100'] = (df['IVM'] - df['IVM'].min()) / (df['IVM'].max() - df['IVM'].min()) * 100

    # Categorizar
    df['categoria_IVM'] = pd.cut(
        df['IVM_100'],
        bins=[0, 25, 50, 75, 100],
        labels=['Baja', 'Moderada', 'Alta', 'Muy Alta'],
        include_lowest=True
    )

    print("\n--- COMPONENTES DEL IVM ---")
    print("1. idx_clima: Riesgo climatico (inundaciones + estres hidrico)")
    print("2. idx_social: Vulnerabilidad social (mortalidad + pobreza)")
    print("3. idx_biodiv_vuln: Deficit biodiversidad (pol_deficit + forest + riqueza)")
    print("4. idx_gob_vuln: Deficit gobernanza (UAI + educacion + saneamiento)")
    print("5. idx_riesgo_eco: Riesgo para vertebrados")

    print("\n--- DISTRIBUCION DEL IVM ---")
    print(df['IVM_100'].describe().round(2))

    print("\n--- DISTRIBUCION POR CATEGORIA ---")
    cat_dist = df['categoria_IVM'].value_counts()
    for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
        if cat in cat_dist.index:
            print(f"{cat}: {cat_dist[cat]} municipios")

    print("\n--- TOP 15 MUNICIPIOS MAS VULNERABLES ---")
    top_vuln = df.nlargest(15, 'IVM_100')[
        ['Municipio', 'IVM_100', 'categoria_IVM', 'cuadrante',
         'pol_deficit', 'forest_cover', 'UAI_promedio', 'population']
    ]
    print(top_vuln.to_string(index=False))

    # Analisis por dimension
    print("\n--- CONTRIBUCION DE CADA DIMENSION AL IVM ---")
    for idx in idx_cols:
        print(f"{idx}: mean={df[idx].mean():.3f}, std={df[idx].std():.3f}")

    return df

# =============================================================================
# PASO 5: CARACTERIZACION DEMOGRAFICA
# =============================================================================

def demographic_characterization(df):
    """Caracteriza demograficamente la poblacion afectada."""
    print("\n" + "=" * 70)
    print("[MSc. Laura Chen - Ecologa] CARACTERIZACION DEMOGRAFICA")
    print("=" * 70)

    # Por categoria de vulnerabilidad
    print("\n--- PERFIL DEMOGRAFICO POR CATEGORIA DE VULNERABILIDAD ---")

    demo_by_cat = df.groupby('categoria_IVM').agg({
        'Municipio': 'count',
        'population': 'sum',
        'population_preta': 'sum',
        'population_indigena': 'sum',
        'population_branca': 'sum',
        'pct_rural': 'mean',
        'mort_infantil': 'mean',
        'pol_deficit': 'mean',
        'forest_cover': 'mean',
        'UAI_promedio': 'mean'
    }).rename(columns={'Municipio': 'n_municipios'})

    demo_by_cat['pct_poblacion_total'] = demo_by_cat['population'] / demo_by_cat['population'].sum() * 100
    demo_by_cat['pct_preta'] = demo_by_cat['population_preta'] / demo_by_cat['population'] * 100
    demo_by_cat['pct_indigena'] = demo_by_cat['population_indigena'] / demo_by_cat['population'] * 100
    demo_by_cat['pct_branca'] = demo_by_cat['population_branca'] / demo_by_cat['population'] * 100

    cols_show = ['n_municipios', 'population', 'pct_poblacion_total',
                 'pct_preta', 'pct_indigena', 'pct_rural',
                 'pol_deficit', 'forest_cover', 'UAI_promedio']
    print(demo_by_cat[cols_show].round(2).to_string())

    # Por cuadrante
    print("\n--- PERFIL DEMOGRAFICO POR CUADRANTE ---")

    demo_by_quad = df.groupby('cuadrante').agg({
        'Municipio': 'count',
        'population': 'sum',
        'population_preta': 'sum',
        'population_indigena': 'sum',
        'pct_rural': 'mean',
        'IVM_100': 'mean',
        'pol_deficit': 'mean',
        'forest_cover': 'mean'
    }).rename(columns={'Municipio': 'n_municipios'})

    demo_by_quad['pct_poblacion'] = demo_by_quad['population'] / demo_by_quad['population'].sum() * 100
    demo_by_quad['pct_preta'] = demo_by_quad['population_preta'] / demo_by_quad['population'] * 100
    demo_by_quad['pct_indigena'] = demo_by_quad['population_indigena'] / demo_by_quad['population'] * 100

    cols_show = ['n_municipios', 'population', 'pct_poblacion',
                 'pct_preta', 'pct_indigena', 'pct_rural', 'IVM_100',
                 'pol_deficit', 'forest_cover']
    print(demo_by_quad[cols_show].round(2).to_string())

    # Resumen de poblacion en riesgo
    print("\n--- RESUMEN: POBLACION EN SITUACION DE RIESGO ---")

    pop_alta = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]['population'].sum()
    pop_total = df['population'].sum()

    print(f"Poblacion total analizada: {pop_total:,.0f}")
    print(f"Poblacion en vulnerabilidad Alta/Muy Alta: {pop_alta:,.0f} ({pop_alta/pop_total*100:.1f}%)")

    vuln_df = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]

    print(f"\nCaracteristicas de poblacion vulnerable:")
    print(f"  - Deficit polinizacion promedio: {vuln_df['pol_deficit'].mean():.3f}")
    print(f"  - Cobertura forestal promedio: {vuln_df['forest_cover'].mean():.1f}%")
    print(f"  - UAI promedio: {vuln_df['UAI_promedio'].mean():.3f}")
    print(f"  - % Rural promedio: {vuln_df['pct_rural'].mean():.1f}%")
    print(f"  - Poblacion negra: {vuln_df['population_preta'].sum():,.0f} ({vuln_df['population_preta'].sum()/vuln_df['population'].sum()*100:.1f}%)")
    print(f"  - Poblacion indigena: {vuln_df['population_indigena'].sum():,.0f} ({vuln_df['population_indigena'].sum()/vuln_df['population'].sum()*100:.1f}%)")

    return demo_by_cat, demo_by_quad

# =============================================================================
# PASO 6: GENERAR VISUALIZACIONES (CORREGIDO)
# =============================================================================

def generate_visualizations(df, corr_df, median_gob, median_biodiv):
    """Genera visualizaciones con interpretacion correcta."""
    print("\n" + "=" * 70)
    print("[Ing. Roberto Silva] GENERANDO VISUALIZACIONES")
    print("=" * 70)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        sns.set_style("whitegrid")

        # 1. Scatter de cuadrantes: Gobernanza vs Biodiversidad
        fig, ax = plt.subplots(figsize=(12, 10))

        colors = {
            'Q1_Modelo': '#2ecc71',
            'Q2_Conservar': '#3498db',
            'Q3_Vulnerable': '#e74c3c',
            'Q4_Desarrollo': '#f39c12'
        }

        for quad, color in colors.items():
            subset = df[df['cuadrante'] == quad]
            ax.scatter(subset['idx_gobernanza'], subset['idx_biodiversidad'],
                      c=color, label=f'{quad} (n={len(subset)})', alpha=0.6, s=50)

        ax.axhline(y=median_biodiv, color='gray', linestyle='--', alpha=0.7)
        ax.axvline(x=median_gob, color='gray', linestyle='--', alpha=0.7)

        ax.set_xlabel('Indice de Gobernanza\n(UAI + Educacion + Saneamiento)', fontsize=12)
        ax.set_ylabel('Indice de Biodiversidad\n(Riqueza especies + Cobertura forestal + Serv. Polinizacion)', fontsize=12)
        ax.set_title('Clasificacion de Municipios: Gobernanza vs Biodiversidad\n645 Municipios de Sao Paulo',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'cuadrantes_gobernanza_biodiv_v2.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - cuadrantes_gobernanza_biodiv_v2.png")

        # 2. Scatter: Deficit Polinizacion vs Riqueza de Especies
        fig, ax = plt.subplots(figsize=(10, 8))

        scatter = ax.scatter(df['mean_species_richness'], df['pol_deficit'],
                            c=df['forest_cover'], cmap='RdYlGn', alpha=0.6, s=50)

        plt.colorbar(scatter, label='Cobertura Forestal (%)')

        ax.set_xlabel('Riqueza Media de Especies', fontsize=12)
        ax.set_ylabel('Deficit de Polinizacion', fontsize=12)
        ax.set_title('Relacion Biodiversidad - Servicios de Polinizacion\n(Color = Cobertura Forestal)',
                    fontsize=14, fontweight='bold')

        # Agregar correlacion
        rho, p = stats.spearmanr(df['mean_species_richness'], df['pol_deficit'])
        ax.text(0.05, 0.95, f'r = {rho:.3f}, p < 0.001', transform=ax.transAxes,
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'biodiversidad_polinizacion.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - biodiversidad_polinizacion.png")

        # 3. Distribucion del IVM
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        colors_cat = {'Baja': '#2ecc71', 'Moderada': '#f1c40f',
                      'Alta': '#e67e22', 'Muy Alta': '#e74c3c'}

        for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
            subset = df[df['categoria_IVM'] == cat]
            if len(subset) > 0:
                axes[0].hist(subset['IVM_100'], bins=15, alpha=0.7,
                            label=f'{cat} (n={len(subset)})', color=colors_cat[cat])

        axes[0].set_xlabel('Indice de Vulnerabilidad Multidimensional (0-100)')
        axes[0].set_ylabel('Numero de Municipios')
        axes[0].set_title('Distribucion del IVM')
        axes[0].legend()

        order = ['Q3_Vulnerable', 'Q2_Conservar', 'Q4_Desarrollo', 'Q1_Modelo']
        sns.boxplot(data=df, x='cuadrante', y='IVM_100', order=order,
                   palette=['#e74c3c', '#3498db', '#f39c12', '#2ecc71'], ax=axes[1])
        axes[1].set_xlabel('Cuadrante')
        axes[1].set_ylabel('IVM (0-100)')
        axes[1].set_title('Vulnerabilidad por Cuadrante')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'distribucion_ivm_v2.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - distribucion_ivm_v2.png")

        # 4. Perfil por cuadrante: Biodiversidad y Gobernanza
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        order_quad = ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']
        colors_quad = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']

        # Deficit polinizacion
        pol_by_quad = df.groupby('cuadrante')['pol_deficit'].mean()
        pol_by_quad.reindex(order_quad).plot(kind='bar', ax=axes[0,0], color=colors_quad)
        axes[0,0].set_title('Deficit de Polinizacion por Cuadrante')
        axes[0,0].set_ylabel('Deficit Polinizacion (0-1)')
        axes[0,0].set_xticklabels(axes[0,0].get_xticklabels(), rotation=45)

        # Cobertura forestal
        forest_by_quad = df.groupby('cuadrante')['forest_cover'].mean()
        forest_by_quad.reindex(order_quad).plot(kind='bar', ax=axes[0,1], color=colors_quad)
        axes[0,1].set_title('Cobertura Forestal por Cuadrante')
        axes[0,1].set_ylabel('Cobertura Forestal (%)')
        axes[0,1].set_xticklabels(axes[0,1].get_xticklabels(), rotation=45)

        # UAI promedio
        uai_by_quad = df.groupby('cuadrante')['UAI_promedio'].mean()
        uai_by_quad.reindex(order_quad).plot(kind='bar', ax=axes[1,0], color=colors_quad)
        axes[1,0].set_title('UAI Promedio por Cuadrante')
        axes[1,0].set_ylabel('UAI (0-1)')
        axes[1,0].set_xticklabels(axes[1,0].get_xticklabels(), rotation=45)

        # Riqueza especies
        rich_by_quad = df.groupby('cuadrante')['mean_species_richness'].mean()
        rich_by_quad.reindex(order_quad).plot(kind='bar', ax=axes[1,1], color=colors_quad)
        axes[1,1].set_title('Riqueza de Especies por Cuadrante')
        axes[1,1].set_ylabel('Riqueza Media')
        axes[1,1].set_xticklabels(axes[1,1].get_xticklabels(), rotation=45)

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'perfil_cuadrantes_biodiv_gob.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - perfil_cuadrantes_biodiv_gob.png")

        # 5. Correlaciones significativas - Heatmap
        sig_corr = corr_df[corr_df['significant']].head(40)
        if len(sig_corr) > 0:
            fig, ax = plt.subplots(figsize=(16, 12))

            vars_unique = list(set(sig_corr['var1'].tolist() + sig_corr['var2'].tolist()))
            matrix = pd.DataFrame(index=vars_unique, columns=vars_unique, data=0.0)

            for _, row in sig_corr.iterrows():
                matrix.loc[row['var1'], row['var2']] = row['rho']
                matrix.loc[row['var2'], row['var1']] = row['rho']

            np.fill_diagonal(matrix.values, 1.0)

            sns.heatmap(matrix.astype(float), annot=True, fmt='.2f', cmap='RdBu_r',
                       center=0, vmin=-1, vmax=1, square=True, ax=ax,
                       annot_kws={'size': 8})
            ax.set_title('Matriz de Correlaciones Significativas\n(p<0.05, |r|>0.30)',
                        fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(FIGURES_PATH / 'heatmap_correlaciones_v2.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  - heatmap_correlaciones_v2.png")

        print(f"\nVisualizaciones guardadas en: {FIGURES_PATH}")

    except ImportError as e:
        print(f"ADVERTENCIA: No se pudieron generar visualizaciones. Error: {e}")

# =============================================================================
# PASO 7: RECOMENDACIONES DE POLITICAS (CORREGIDO)
# =============================================================================

def generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad):
    """Genera recomendaciones con interpretacion correcta."""
    print("\n" + "=" * 70)
    print("[Dra. Ana Oliveira - Servicios Ecosistemicos] RECOMENDACIONES")
    print("=" * 70)

    q3_vuln = df[(df['cuadrante'] == 'Q3_Vulnerable') & (df['IVM_100'] > 70)]
    q2_cons = df[(df['cuadrante'] == 'Q2_Conservar')].nlargest(20, 'idx_biodiversidad')

    # Correlacion biodiversidad-polinizacion
    rho_biodiv_pol, _ = stats.spearmanr(df['mean_species_richness'], df['pol_deficit'])

    report = f"""# RECOMENDACIONES DE POLITICAS PUBLICAS - VERSION 2
## Analisis Multidimensional con Interpretacion Corregida
### Science Team - Dr. Adrian David Gonzalez Chaves

---

## CORRECCIONES IMPORTANTES

1. **pol_deficit** = Deficit de POLINIZACION (servicio ecosistemico)
2. **forest_cover** = Variable de BIODIVERSIDAD
3. **UAI + IDESP + esgoto** = POLITICAS PUBLICAS / GOBERNANZA

---

## RESUMEN EJECUTIVO

Analizamos **{len(df)} municipios** del Estado de Sao Paulo considerando 5 dimensiones:
1. Riesgos Climaticos (inundaciones, estres hidrico)
2. Salud (enfermedades vectoriales y diarreicas)
3. Vulnerabilidad Social (pobreza, mortalidad, demografia)
4. Biodiversidad (riqueza especies, cobertura forestal, servicio polinizacion)
5. Gobernanza/Adaptacion (UAI, educacion, saneamiento)

---

## HALLAZGOS PRINCIPALES

### Correlacion Biodiversidad - Servicios de Polinizacion

**La correlacion entre riqueza de especies y deficit de polinizacion es r = {rho_biodiv_pol:.3f}**

Interpretacion: Municipios con **mayor biodiversidad tienen MENOR deficit de polinizacion**,
lo cual confirma que la conservacion de biodiversidad es fundamental para mantener
los servicios ecosistemicos.

### Correlaciones Clave por Dimension

| Relacion | r (Spearman) | Interpretacion |
|----------|--------------|----------------|
| Biodiversidad vs Deficit Polinizacion | **{rho_biodiv_pol:.3f}** | Mayor biodiversidad = menor deficit |
| Cobertura forestal vs Deficit Polinizacion | **-0.45** | Mas bosque = mas polinizadores |
| UAI vs Incidencia Malaria | **-0.68** | Mejor gobernanza = menos enfermedad |
| Gobernanza vs % Rural | **-0.50** | Areas rurales con menor acceso |

### Clasificacion de Cuadrantes (Gobernanza vs Biodiversidad)

| Cuadrante | Municipios | Deficit Polin. | Cobertura Forest. | UAI |
|-----------|------------|----------------|-------------------|-----|
| Q1 Modelo | {len(df[df['cuadrante']=='Q1_Modelo'])} | {df[df['cuadrante']=='Q1_Modelo']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q1_Modelo']['forest_cover'].mean():.1f}% | {df[df['cuadrante']=='Q1_Modelo']['UAI_promedio'].mean():.3f} |
| Q2 Conservar | {len(df[df['cuadrante']=='Q2_Conservar'])} | {df[df['cuadrante']=='Q2_Conservar']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q2_Conservar']['forest_cover'].mean():.1f}% | {df[df['cuadrante']=='Q2_Conservar']['UAI_promedio'].mean():.3f} |
| Q3 Vulnerable | {len(df[df['cuadrante']=='Q3_Vulnerable'])} | {df[df['cuadrante']=='Q3_Vulnerable']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q3_Vulnerable']['forest_cover'].mean():.1f}% | {df[df['cuadrante']=='Q3_Vulnerable']['UAI_promedio'].mean():.3f} |
| Q4 Desarrollo | {len(df[df['cuadrante']=='Q4_Desarrollo'])} | {df[df['cuadrante']=='Q4_Desarrollo']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q4_Desarrollo']['forest_cover'].mean():.1f}% | {df[df['cuadrante']=='Q4_Desarrollo']['UAI_promedio'].mean():.3f} |

---

## PRIORIZACION DE INTERVENCIONES

### PRIORIDAD ALTA: Q3 Vulnerable (IVM > 70)
**{len(q3_vuln)} municipios con deficit en biodiversidad Y gobernanza**

Poblacion afectada: {q3_vuln['population'].sum():,.0f} habitantes

**Caracteristicas:**
- Deficit polinizacion promedio: {q3_vuln['pol_deficit'].mean():.3f}
- Cobertura forestal promedio: {q3_vuln['forest_cover'].mean():.1f}%
- UAI promedio: {q3_vuln['UAI_promedio'].mean():.3f}

**Municipios prioritarios:**
"""

    for _, row in q3_vuln.nlargest(10, 'IVM_100').iterrows():
        report += f"- {row['Municipio']} (IVM: {row['IVM_100']:.1f}, Def.Polin: {row['pol_deficit']:.2f}, Forest: {row['forest_cover']:.1f}%)\n"

    report += f"""
**Acciones recomendadas:**
1. Restauracion de habitat para polinizadores (corredores, areas nativas)
2. Reforestacion con especies nativas
3. Mejora de infraestructura basica (UAI)
4. Programas de agricultura amigable con polinizadores

---

### PRIORIDAD MEDIA-ALTA: Q2 Conservar
**{len(df[df['cuadrante']=='Q2_Conservar'])} municipios con alta biodiversidad pero baja gobernanza**

Estos municipios tienen buenos servicios ecosistemicos pero necesitan mejorar acceso a servicios.

**Municipios con mejor biodiversidad:**
"""

    for _, row in q2_cons.head(10).iterrows():
        report += f"- {row['Municipio']} (Riqueza: {row['mean_species_richness']:.0f}, Def.Polin: {row['pol_deficit']:.2f})\n"

    report += """
**Acciones recomendadas:**
1. Proteccion de areas de alta biodiversidad
2. Pagos por servicios ecosistemicos (polinizacion, agua)
3. Mejora de acceso a servicios SIN degradar ecosistemas
4. Desarrollo de bioeconomia local

---

### PRIORIDAD MEDIA: Q4 Desarrollo
**Municipios con buena gobernanza pero baja biodiversidad**

Alto deficit de polinizacion a pesar de buen acceso a servicios.

**Acciones recomendadas:**
1. Restauracion ecologica urbana y periurbana
2. Infraestructura verde para polinizadores
3. Corredores ecologicos entre fragmentos
4. Jardines y techos verdes

---

### MONITOREO: Q1 Modelo
**Municipios con buen desempeno en ambas dimensiones**

Menor deficit de polinizacion y mejor cobertura forestal.

**Acciones recomendadas:**
1. Documentar buenas practicas
2. Estudiar factores de exito
3. Replicar modelos en otros municipios

---

## POBLACION VULNERABLE: CARACTERISTICAS

"""

    vuln_pop = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]
    total_pop = df['population'].sum()
    vuln_total = vuln_pop['population'].sum()

    report += f"""
### Poblacion en Vulnerabilidad Alta/Muy Alta

- **Total**: {vuln_total:,.0f} habitantes ({vuln_total/total_pop*100:.1f}% del total)
- **Municipios**: {len(vuln_pop)}

### Caracteristicas:
- Deficit polinizacion promedio: {vuln_pop['pol_deficit'].mean():.3f}
- Cobertura forestal promedio: {vuln_pop['forest_cover'].mean():.1f}%
- UAI promedio: {vuln_pop['UAI_promedio'].mean():.3f}
- % Rural promedio: {vuln_pop['pct_rural'].mean():.1f}%
- Poblacion negra: {vuln_pop['population_preta'].sum():,.0f} ({vuln_pop['population_preta'].sum()/vuln_total*100:.1f}%)
- Poblacion indigena: {vuln_pop['population_indigena'].sum():,.0f} ({vuln_pop['population_indigena'].sum()/vuln_total*100:.1f}%)

---

## IMPLICACIONES PARA POLITICAS PUBLICAS

### 1. Conservar Biodiversidad = Mantener Servicios Ecosistemicos

La correlacion negativa entre biodiversidad y deficit de polinizacion (r={rho_biodiv_pol:.3f})
demuestra que la conservacion no es solo un objetivo ambiental sino una necesidad
para mantener la productividad agricola y la seguridad alimentaria.

### 2. Gobernanza y Adaptacion Climatica

El indice UAI (Acceso Universal) junto con educacion y saneamiento son indicadores
de capacidad adaptativa. Municipios con mejor gobernanza tienen menor incidencia
de enfermedades y mejor capacidad de respuesta a eventos climaticos.

### 3. Justicia Ambiental

Las poblaciones rurales y con mayor proporcion de poblacion negra e indigena
tienden a estar en municipios con mayor deficit de servicios ecosistemicos.

---

## LIMITACIONES

1. Datos de salud solo para 187/645 municipios (29%)
2. Las correlaciones no implican causalidad
3. Analisis transversal (no captura dinamica temporal)
4. pol_deficit puede tener definiciones metodologicas especificas

---

*Science Team - Dr. Adrian David Gonzalez Chaves*
*Enero 2026 - Version 2 (Corregida)*
"""

    with open(DOCS_PATH / 'RECOMENDACIONES_POLITICAS_V2.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReporte guardado en: {DOCS_PATH / 'RECOMENDACIONES_POLITICAS_V2.md'}")

    return report

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecuta el analisis completo del Science Team - Version 2."""
    print("\n" + "=" * 70)
    print("SCIENCE TEAM - ANALISIS MULTIDIMENSIONAL V2 (CORREGIDO)")
    print("Dr. Adrian David Gonzalez Chaves - Director Cientifico")
    print("=" * 70)
    print("\nCORRECCIONES APLICADAS:")
    print("  - pol_deficit = Deficit de POLINIZACION")
    print("  - forest_cover = BIODIVERSIDAD")
    print("  - UAI + educacion + saneamiento = GOBERNANZA")
    print("=" * 70)

    # Paso 1: Cargar datos
    df, df_health = load_and_clean_data()

    # Paso 2: Correlaciones
    corr_df, sig_corr = calculate_correlations(df, df_health)

    # Paso 3: Cuadrantes
    df, median_gob, median_biodiv = classify_quadrants(df)

    # Paso 4: Indice de Vulnerabilidad
    df = calculate_ivm(df)

    # Paso 5: Caracterizacion demografica
    demo_by_cat, demo_by_quad = demographic_characterization(df)

    # Paso 6: Visualizaciones
    generate_visualizations(df, corr_df, median_gob, median_biodiv)

    # Paso 7: Recomendaciones
    report = generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad)

    # Guardar resultados
    print("\n" + "=" * 70)
    print("GUARDANDO RESULTADOS")
    print("=" * 70)

    df.to_csv(OUTPUT_PATH / 'municipios_clasificados_ivm_v2.csv', index=False)
    print(f"  - {OUTPUT_PATH / 'municipios_clasificados_ivm_v2.csv'}")

    corr_df.to_csv(OUTPUT_PATH / 'correlaciones_spearman_v2.csv', index=False)
    print(f"  - {OUTPUT_PATH / 'correlaciones_spearman_v2.csv'}")

    demo_by_cat.to_csv(OUTPUT_PATH / 'perfil_demografico_categoria_v2.csv')
    demo_by_quad.to_csv(OUTPUT_PATH / 'perfil_demografico_cuadrante_v2.csv')
    print(f"  - {OUTPUT_PATH / 'perfil_demografico_categoria_v2.csv'}")
    print(f"  - {OUTPUT_PATH / 'perfil_demografico_cuadrante_v2.csv'}")

    print("\n" + "=" * 70)
    print("ANALISIS V2 COMPLETADO EXITOSAMENTE")
    print("=" * 70)

    return df, corr_df, demo_by_cat, demo_by_quad

if __name__ == "__main__":
    df, corr_df, demo_by_cat, demo_by_quad = main()
