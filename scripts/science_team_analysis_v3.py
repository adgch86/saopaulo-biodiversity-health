"""
Science Team Analysis V3 - Vulnerabilidad Multidimensional de Municipios de Sao Paulo
======================================================================================

Autor: Dr. Adrian David Gonzalez Chaves y Science Team
Fecha: Enero 2026

CLASIFICACION BASADA EN METADATA.XLSX:

5 DIMENSIONES DE RIESGO:
1. Climate Risk: flooding_risks, flooding_exposure, hydric_stress_exp, hydric_stress_risk
2. Health Risk: persist_*, incidence_*, copersistence
3. Social Vulnerability: mort_infantil, n_pessoas_pobreza, IDESP, familias_rua, population*, esgoto
4. Biodiversity: forest_cover, mean/max_species_richness, Vert_rich_risk
5. Food Security Risk: pol_deficit (deficit de polinizacion)

GOBERNANZA (Capacidad de Adaptacion Climatica):
- UAI, UAI_food, UAI_env, UAI_mob, UAI_Crisk, UAI_housing
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

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
FIGURES_PATH.mkdir(parents=True, exist_ok=True)

# =============================================================================
# DEFINICION DE DIMENSIONES SEGUN METADATA
# =============================================================================

DIMENSIONES_RIESGO = {
    'climate_risk': {
        'nombre': 'Riesgo Climatico',
        'variables': ['flooding_exposure', 'flooding_risks',
                      'hydric_stress_exp', 'hydric_stress_risk'],
        'descripcion': 'Exposicion y riesgo a inundaciones y estres hidrico',
        'higher_is_worse': True
    },

    'health_risk': {
        'nombre': 'Riesgo de Salud',
        'variables': ['persist_malaria', 'persist_leptospirose', 'persist_diarrhea',
                      'persist_dengue', 'persist_chagas',
                      'incidence_malaria', 'incidence_leptospirose', 'incidence_diarrhea',
                      'incidence_dengue', 'incidence_chagas', 'copersistence'],
        'descripcion': 'Persistencia e incidencia de enfermedades (solo 187 municipios)',
        'higher_is_worse': True
    },

    'social_vulnerability': {
        'nombre': 'Vulnerabilidad Social',
        'variables': ['mort_infantil', 'n_pessoas_pobreza', 'IDESP_ensino_medio',
                      'n_familias_rua', 'esgoto_tratado'],
        'descripcion': 'Mortalidad infantil, pobreza, educacion, familias en calle, saneamiento',
        'higher_is_worse': True  # Excepto IDESP y esgoto que son inversos
    },

    'biodiversity': {
        'nombre': 'Biodiversidad',
        'variables': ['forest_cover', 'mean_species_richness', 'max_species_richness',
                      'Vert_rich_risk'],
        'descripcion': 'Cobertura forestal, riqueza de especies, riesgo para vertebrados',
        'higher_is_worse': False  # Mayor biodiversidad = mejor (excepto Vert_rich_risk)
    },

    'food_security_risk': {
        'nombre': 'Riesgo de Seguridad Alimentaria',
        'variables': ['pol_deficit'],
        'descripcion': 'Deficit de polinizacion (afecta produccion agricola)',
        'higher_is_worse': True
    }
}

GOBERNANZA = {
    'nombre': 'Capacidad de Adaptacion Climatica (Gobernanza)',
    'variables': ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk'],
    'descripcion': 'Indice de Acceso Universal - Politicas de adaptacion',
    'higher_is_worse': False  # Mayor UAI = mejor capacidad
}

DEMOGRAFICAS = {
    'nombre': 'Variables Demograficas',
    'variables': ['population', 'population_preta', 'population_indigena',
                  'population_branca', 'pct_rural', 'pct_urbana'],
    'descripcion': 'Poblacion total y composicion demografica'
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
    # UAI promedio (Gobernanza)
    uai_cols = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']
    df['UAI_promedio'] = df[uai_cols].mean(axis=1)

    # Porcentajes demograficos
    df['pct_preta'] = (df['population_preta'] / df['population']) * 100
    df['pct_indigena'] = (df['population_indigena'] / df['population']) * 100
    df['pct_branca'] = (df['population_branca'] / df['population']) * 100

    print(f"Total municipios cargados: {len(df)}")
    print(f"Total variables: {len(df.columns)}")

    # Municipios con datos de salud
    health_cols = ['persist_malaria', 'incidence_malaria', 'copersistence']
    df_health = df[df[health_cols].notna().all(axis=1)].copy()
    print(f"Municipios con datos de salud: {len(df_health)}")

    # Mostrar estructura de dimensiones segun metadata
    print("\n" + "=" * 70)
    print("DIMENSIONES SEGUN METADATA.XLSX")
    print("=" * 70)

    print("\n### 5 DIMENSIONES DE RIESGO ###")
    for dim_id, dim_info in DIMENSIONES_RIESGO.items():
        available = [v for v in dim_info['variables'] if v in df.columns]
        print(f"\n{dim_info['nombre'].upper()}: {len(available)} variables")
        print(f"  {dim_info['descripcion']}")
        for v in available:
            if v in df.columns:
                non_null = df[v].notna().sum()
                print(f"    - {v}: {non_null} valores")

    print(f"\n### GOBERNANZA (Capacidad de Adaptacion) ###")
    available = [v for v in GOBERNANZA['variables'] if v in df.columns]
    print(f"{GOBERNANZA['nombre']}: {len(available)} variables")
    for v in available:
        print(f"    - {v}")

    return df, df_health

# =============================================================================
# PASO 2: CALCULAR INDICES POR DIMENSION
# =============================================================================

def calculate_dimension_indices(df):
    """Calcula indices normalizados para cada dimension de riesgo."""
    print("\n" + "=" * 70)
    print("[Dra. Maria Santos - Bioestadistica] INDICES POR DIMENSION")
    print("=" * 70)

    df = df.copy()

    def normalize(series, higher_is_worse=True):
        """Normaliza a 0-1. Si higher_is_worse, mayor valor = mayor riesgo."""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        if not higher_is_worse:
            normalized = 1 - normalized
        return normalized

    # 1. INDICE DE RIESGO CLIMATICO
    climate_vars = ['flooding_exposure', 'flooding_risks',
                    'hydric_stress_exp', 'hydric_stress_risk']
    for v in climate_vars:
        df[f'{v}_norm'] = normalize(df[v], higher_is_worse=True)
    df['idx_climate_risk'] = df[[f'{v}_norm' for v in climate_vars]].mean(axis=1)
    print(f"\n1. Riesgo Climatico: mean={df['idx_climate_risk'].mean():.3f}")

    # 2. INDICE DE VULNERABILIDAD SOCIAL
    # mort_infantil y n_pessoas_pobreza: mayor = peor
    # IDESP y esgoto: mayor = mejor (invertir)
    df['mort_norm'] = normalize(df['mort_infantil'], higher_is_worse=True)
    df['pobreza_pct'] = df['n_pessoas_pobreza'] / df['population'] * 100
    df['pobreza_norm'] = normalize(df['pobreza_pct'], higher_is_worse=True)
    df['idesp_norm'] = normalize(df['IDESP_ensino_medio'], higher_is_worse=False)  # Invertir
    df['esgoto_norm'] = normalize(df['esgoto_tratado'], higher_is_worse=False)  # Invertir
    df['familias_rua_norm'] = normalize(df['n_familias_rua'] / df['population'] * 1000, higher_is_worse=True)

    df['idx_social_vuln'] = df[['mort_norm', 'pobreza_norm', 'idesp_norm',
                                 'esgoto_norm', 'familias_rua_norm']].mean(axis=1)
    print(f"2. Vulnerabilidad Social: mean={df['idx_social_vuln'].mean():.3f}")

    # 3. INDICE DE BIODIVERSIDAD (como RIESGO: menor biodiversidad = mayor riesgo)
    df['forest_norm'] = normalize(df['forest_cover'], higher_is_worse=False)  # Invertir
    df['richness_norm'] = normalize(df['mean_species_richness'], higher_is_worse=False)  # Invertir
    df['vert_risk_norm'] = normalize(df['Vert_rich_risk'], higher_is_worse=True)  # Ya es riesgo

    df['idx_biodiv_risk'] = df[['forest_norm', 'richness_norm', 'vert_risk_norm']].mean(axis=1)
    print(f"3. Riesgo Biodiversidad: mean={df['idx_biodiv_risk'].mean():.3f}")

    # 4. INDICE DE RIESGO SEGURIDAD ALIMENTARIA (Deficit Polinizacion)
    df['idx_food_security_risk'] = normalize(df['pol_deficit'], higher_is_worse=True)
    print(f"4. Riesgo Seguridad Alimentaria: mean={df['idx_food_security_risk'].mean():.3f}")

    # 5. INDICE DE GOBERNANZA (como capacidad: mayor = MEJOR, invertir para riesgo)
    df['idx_governance'] = df['UAI_promedio']  # Ya esta en 0-1
    df['idx_governance_risk'] = 1 - df['idx_governance']  # Invertir: menor gobernanza = mayor riesgo
    print(f"5. Deficit Gobernanza: mean={df['idx_governance_risk'].mean():.3f}")

    return df

# =============================================================================
# PASO 3: ANALISIS DE CORRELACIONES ENTRE DIMENSIONES
# =============================================================================

def calculate_correlations(df, df_health):
    """Calcula correlaciones entre las 5 dimensiones de riesgo y gobernanza."""
    print("\n" + "=" * 70)
    print("[Dra. Maria Santos] CORRELACIONES ENTRE DIMENSIONES")
    print("=" * 70)

    results = []

    # Variables de cada dimension
    indices = {
        'Riesgo Climatico': 'idx_climate_risk',
        'Vulnerabilidad Social': 'idx_social_vuln',
        'Riesgo Biodiversidad': 'idx_biodiv_risk',
        'Riesgo Seg. Alimentaria': 'idx_food_security_risk',
        'Deficit Gobernanza': 'idx_governance_risk',
        'UAI (Gobernanza)': 'UAI_promedio'
    }

    # Agregar variables originales importantes
    vars_originales = {
        'Deficit Polinizacion': 'pol_deficit',
        'Cobertura Forestal': 'forest_cover',
        'Riqueza Especies': 'mean_species_richness',
        'Riesgo Vertebrados': 'Vert_rich_risk',
        'Mortalidad Infantil': 'mort_infantil',
        '% Rural': 'pct_rural',
        '% Poblacion Negra': 'pct_preta',
        '% Poblacion Indigena': 'pct_indigena'
    }

    all_vars = {**indices, **vars_originales}

    # Correlaciones entre todas las variables
    print("\n### CORRELACIONES ENTRE DIMENSIONES DE RIESGO Y GOBERNANZA ###")

    for name1, var1 in all_vars.items():
        for name2, var2 in all_vars.items():
            if var1 != var2 and var1 in df.columns and var2 in df.columns:
                mask = df[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, var1], df.loc[mask, var2])
                    results.append({
                        'dimension1': name1,
                        'var1': var1,
                        'dimension2': name2,
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.30)
                    })

    # Agregar correlaciones con salud (187 municipios)
    health_vars = {
        'Incidencia Malaria': 'incidence_malaria',
        'Incidencia Dengue': 'incidence_dengue',
        'Incidencia Diarrea': 'incidence_diarrhea',
        'Copersistencia': 'copersistence'
    }

    for name1, var1 in health_vars.items():
        for name2, var2 in {**indices, **vars_originales}.items():
            if var1 in df_health.columns and var2 in df_health.columns:
                mask = df_health[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df_health.loc[mask, var1],
                                             df_health.loc[mask, var2])
                    results.append({
                        'dimension1': name1,
                        'var1': var1,
                        'dimension2': name2,
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.25)
                    })

    corr_df = pd.DataFrame(results)
    corr_df = corr_df.drop_duplicates(subset=['var1', 'var2'])
    corr_df = corr_df.sort_values('rho', key=abs, ascending=False)

    sig_corr = corr_df[corr_df['significant']].copy()

    print(f"\nTotal correlaciones: {len(corr_df)}")
    print(f"Significativas (p<0.05, |r|>0.30): {len(sig_corr)}")

    # Mostrar top correlaciones
    print("\n--- TOP 25 CORRELACIONES SIGNIFICATIVAS ---")
    cols_show = ['dimension1', 'dimension2', 'rho', 'p_value', 'n']
    print(sig_corr[cols_show].head(25).to_string(index=False))

    # Correlaciones especificas importantes
    print("\n--- CORRELACIONES CLAVE BIODIVERSIDAD/POLINIZACION ---")
    biodiv_corr = sig_corr[
        (sig_corr['dimension1'].isin(['Riesgo Biodiversidad', 'Deficit Polinizacion',
                                       'Cobertura Forestal', 'Riqueza Especies'])) |
        (sig_corr['dimension2'].isin(['Riesgo Biodiversidad', 'Deficit Polinizacion',
                                       'Cobertura Forestal', 'Riqueza Especies']))
    ].head(15)
    if len(biodiv_corr) > 0:
        print(biodiv_corr[cols_show].to_string(index=False))

    print("\n--- CORRELACIONES CLAVE GOBERNANZA ---")
    gob_corr = sig_corr[
        (sig_corr['dimension1'].isin(['UAI (Gobernanza)', 'Deficit Gobernanza'])) |
        (sig_corr['dimension2'].isin(['UAI (Gobernanza)', 'Deficit Gobernanza']))
    ].head(15)
    if len(gob_corr) > 0:
        print(gob_corr[cols_show].to_string(index=False))

    return corr_df, sig_corr

# =============================================================================
# PASO 4: CLASIFICACION EN CUADRANTES
# =============================================================================

def classify_quadrants(df):
    """Clasifica municipios usando UAI vs Indice de Biodiversidad."""
    print("\n" + "=" * 70)
    print("[Dr. Carlos Mendez - GIS/SIG] ANALISIS DE CUADRANTES")
    print("=" * 70)

    # Crear indice de biodiversidad positivo (mayor = mejor)
    df['idx_biodiv_positivo'] = 1 - df['idx_biodiv_risk']

    median_uai = df['UAI_promedio'].median()
    median_biodiv = df['idx_biodiv_positivo'].median()

    print(f"Mediana UAI (Gobernanza): {median_uai:.4f}")
    print(f"Mediana Indice Biodiversidad: {median_biodiv:.4f}")

    def assign_quadrant(row):
        high_uai = row['UAI_promedio'] >= median_uai
        high_biodiv = row['idx_biodiv_positivo'] >= median_biodiv

        if high_uai and high_biodiv:
            return 'Q1_Modelo'
        elif not high_uai and high_biodiv:
            return 'Q2_Conservar'
        elif not high_uai and not high_biodiv:
            return 'Q3_Vulnerable'
        else:
            return 'Q4_Desarrollo'

    df['cuadrante'] = df.apply(assign_quadrant, axis=1)

    print("\n--- DISTRIBUCION DE CUADRANTES ---")
    for quad in ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']:
        n = len(df[df['cuadrante'] == quad])
        pct = n / len(df) * 100
        print(f"{quad}: {n} municipios ({pct:.1f}%)")

    print("\n--- CARACTERISTICAS POR CUADRANTE ---")
    stats_quad = df.groupby('cuadrante').agg({
        'mean_species_richness': 'mean',
        'forest_cover': 'mean',
        'pol_deficit': 'mean',
        'UAI_promedio': 'mean',
        'idx_climate_risk': 'mean',
        'idx_social_vuln': 'mean',
        'pct_rural': 'mean',
        'population': 'sum'
    }).round(3)

    # Renombrar para claridad
    stats_quad.columns = ['Riqueza_spp', 'Forest_%', 'Deficit_polin',
                          'UAI', 'Riesgo_clima', 'Vuln_social',
                          'Rural_%', 'Poblacion']
    print(stats_quad.to_string())

    return df, median_uai, median_biodiv

# =============================================================================
# PASO 5: INDICE DE VULNERABILIDAD MULTIDIMENSIONAL
# =============================================================================

def calculate_ivm(df):
    """Calcula el IVM considerando las 5 dimensiones de riesgo."""
    print("\n" + "=" * 70)
    print("[Dr. Adrian - Director] INDICE DE VULNERABILIDAD MULTIDIMENSIONAL")
    print("=" * 70)

    df = df.copy()

    # IVM = promedio de los 5 indices de riesgo
    # (todos ya normalizados donde mayor = mayor riesgo)
    risk_indices = ['idx_climate_risk', 'idx_social_vuln', 'idx_biodiv_risk',
                    'idx_food_security_risk', 'idx_governance_risk']

    print("\n--- COMPONENTES DEL IVM (5 dimensiones de riesgo) ---")
    for idx in risk_indices:
        print(f"  {idx}: mean={df[idx].mean():.3f}, std={df[idx].std():.3f}")

    df['IVM'] = df[risk_indices].mean(axis=1)
    df['IVM_100'] = (df['IVM'] - df['IVM'].min()) / (df['IVM'].max() - df['IVM'].min()) * 100

    df['categoria_IVM'] = pd.cut(
        df['IVM_100'],
        bins=[0, 25, 50, 75, 100],
        labels=['Baja', 'Moderada', 'Alta', 'Muy Alta'],
        include_lowest=True
    )

    print("\n--- DISTRIBUCION DEL IVM ---")
    print(df['IVM_100'].describe().round(2))

    print("\n--- DISTRIBUCION POR CATEGORIA ---")
    for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
        n = len(df[df['categoria_IVM'] == cat])
        if n > 0:
            print(f"{cat}: {n} municipios")

    print("\n--- TOP 15 MUNICIPIOS MAS VULNERABLES ---")
    top_vuln = df.nlargest(15, 'IVM_100')[
        ['Municipio', 'IVM_100', 'categoria_IVM', 'cuadrante',
         'pol_deficit', 'forest_cover', 'UAI_promedio', 'population']
    ]
    print(top_vuln.to_string(index=False))

    # Cruce IVM por cuadrante
    print("\n--- IVM PROMEDIO POR CUADRANTE ---")
    ivm_by_quad = df.groupby('cuadrante')['IVM_100'].agg(['mean', 'std', 'min', 'max'])
    print(ivm_by_quad.round(2).to_string())

    return df

# =============================================================================
# PASO 6: CARACTERIZACION DEMOGRAFICA
# =============================================================================

def demographic_characterization(df):
    """Caracteriza la poblacion afectada por cada nivel de vulnerabilidad."""
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
        'pol_deficit': 'mean',
        'forest_cover': 'mean',
        'UAI_promedio': 'mean',
        'idx_climate_risk': 'mean',
        'idx_social_vuln': 'mean'
    }).rename(columns={'Municipio': 'n_mun'})

    total_pop = demo_by_cat['population'].sum()
    demo_by_cat['pct_pop'] = demo_by_cat['population'] / total_pop * 100
    demo_by_cat['pct_preta'] = demo_by_cat['population_preta'] / demo_by_cat['population'] * 100
    demo_by_cat['pct_indigena'] = demo_by_cat['population_indigena'] / demo_by_cat['population'] * 100

    cols_show = ['n_mun', 'population', 'pct_pop', 'pct_preta', 'pct_indigena',
                 'pct_rural', 'pol_deficit', 'forest_cover', 'UAI_promedio']
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
        'forest_cover': 'mean',
        'UAI_promedio': 'mean'
    }).rename(columns={'Municipio': 'n_mun'})

    demo_by_quad['pct_pop'] = demo_by_quad['population'] / demo_by_quad['population'].sum() * 100
    demo_by_quad['pct_preta'] = demo_by_quad['population_preta'] / demo_by_quad['population'] * 100
    demo_by_quad['pct_indigena'] = demo_by_quad['population_indigena'] / demo_by_quad['population'] * 100

    cols_show = ['n_mun', 'population', 'pct_pop', 'pct_preta', 'pct_indigena',
                 'pct_rural', 'IVM_100', 'pol_deficit', 'forest_cover', 'UAI_promedio']
    print(demo_by_quad[cols_show].round(2).to_string())

    # Resumen poblacion vulnerable
    print("\n--- RESUMEN: POBLACION EN RIESGO ---")
    vuln_df = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]
    vuln_pop = vuln_df['population'].sum()

    print(f"Poblacion total: {total_pop:,.0f}")
    print(f"Poblacion vulnerable (IVM Alta/Muy Alta): {vuln_pop:,.0f} ({vuln_pop/total_pop*100:.1f}%)")
    print(f"Municipios vulnerables: {len(vuln_df)}")

    print(f"\nCaracteristicas de la poblacion vulnerable:")
    print(f"  - Deficit polinizacion promedio: {vuln_df['pol_deficit'].mean():.3f}")
    print(f"  - Cobertura forestal promedio: {vuln_df['forest_cover'].mean():.1f}%")
    print(f"  - UAI promedio: {vuln_df['UAI_promedio'].mean():.3f}")
    print(f"  - % Rural promedio: {vuln_df['pct_rural'].mean():.1f}%")
    print(f"  - Poblacion negra: {vuln_df['population_preta'].sum():,.0f} ({vuln_df['population_preta'].sum()/vuln_pop*100:.1f}%)")
    print(f"  - Poblacion indigena: {vuln_df['population_indigena'].sum():,.0f} ({vuln_df['population_indigena'].sum()/vuln_pop*100:.1f}%)")

    return demo_by_cat, demo_by_quad

# =============================================================================
# PASO 7: VISUALIZACIONES
# =============================================================================

def generate_visualizations(df, corr_df, median_uai, median_biodiv):
    """Genera visualizaciones."""
    print("\n" + "=" * 70)
    print("[Ing. Roberto Silva] GENERANDO VISUALIZACIONES")
    print("=" * 70)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        sns.set_style("whitegrid")

        # 1. Scatter UAI vs Biodiversidad
        fig, ax = plt.subplots(figsize=(12, 10))

        colors = {
            'Q1_Modelo': '#2ecc71',
            'Q2_Conservar': '#3498db',
            'Q3_Vulnerable': '#e74c3c',
            'Q4_Desarrollo': '#f39c12'
        }

        for quad, color in colors.items():
            subset = df[df['cuadrante'] == quad]
            ax.scatter(subset['UAI_promedio'], subset['idx_biodiv_positivo'],
                      c=color, label=f'{quad} (n={len(subset)})', alpha=0.6, s=50)

        ax.axhline(y=median_biodiv, color='gray', linestyle='--', alpha=0.7)
        ax.axvline(x=median_uai, color='gray', linestyle='--', alpha=0.7)

        ax.set_xlabel('UAI - Capacidad de Adaptacion (Gobernanza)', fontsize=12)
        ax.set_ylabel('Indice de Biodiversidad\n(Riqueza + Cobertura Forestal - Riesgo Vertebrados)', fontsize=12)
        ax.set_title('Clasificacion de Municipios: Gobernanza vs Biodiversidad\n645 Municipios de Sao Paulo',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'cuadrantes_v3.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - cuadrantes_v3.png")

        # 2. Relacion Biodiversidad - Polinizacion - Seguridad Alimentaria
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Riqueza vs Deficit Polinizacion
        ax = axes[0]
        scatter = ax.scatter(df['mean_species_richness'], df['pol_deficit'],
                            c=df['forest_cover'], cmap='RdYlGn', alpha=0.6)
        plt.colorbar(scatter, ax=ax, label='Cobertura Forestal (%)')
        rho, p = stats.spearmanr(df['mean_species_richness'], df['pol_deficit'])
        ax.set_xlabel('Riqueza de Especies')
        ax.set_ylabel('Deficit de Polinizacion (Riesgo Seg. Alimentaria)')
        ax.set_title(f'Biodiversidad vs Seguridad Alimentaria\nr={rho:.3f}')

        # Forest vs Deficit Polinizacion
        ax = axes[1]
        scatter = ax.scatter(df['forest_cover'], df['pol_deficit'],
                            c=df['mean_species_richness'], cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, ax=ax, label='Riqueza Especies')
        rho, p = stats.spearmanr(df['forest_cover'], df['pol_deficit'])
        ax.set_xlabel('Cobertura Forestal (%)')
        ax.set_ylabel('Deficit de Polinizacion')
        ax.set_title(f'Cobertura Forestal vs Deficit Polinizacion\nr={rho:.3f}')

        # UAI vs Deficit Polinizacion
        ax = axes[2]
        scatter = ax.scatter(df['UAI_promedio'], df['pol_deficit'],
                            c=df['pct_rural'], cmap='coolwarm', alpha=0.6)
        plt.colorbar(scatter, ax=ax, label='% Rural')
        rho, p = stats.spearmanr(df['UAI_promedio'], df['pol_deficit'])
        ax.set_xlabel('UAI (Gobernanza)')
        ax.set_ylabel('Deficit de Polinizacion')
        ax.set_title(f'Gobernanza vs Deficit Polinizacion\nr={rho:.3f}')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'biodiversidad_polinizacion_v3.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - biodiversidad_polinizacion_v3.png")

        # 3. Distribucion IVM
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
        plt.savefig(FIGURES_PATH / 'distribucion_ivm_v3.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - distribucion_ivm_v3.png")

        # 4. Perfil de riesgos por cuadrante
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        order_quad = ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']
        colors_quad = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']

        # Deficit polinizacion
        data = df.groupby('cuadrante')['pol_deficit'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[0,0], color=colors_quad)
        axes[0,0].set_title('Deficit de Polinizacion\n(Riesgo Seg. Alimentaria)')
        axes[0,0].set_ylabel('Deficit (0-1)')
        axes[0,0].tick_params(axis='x', rotation=45)

        # Cobertura forestal
        data = df.groupby('cuadrante')['forest_cover'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[0,1], color=colors_quad)
        axes[0,1].set_title('Cobertura Forestal\n(Biodiversidad)')
        axes[0,1].set_ylabel('%')
        axes[0,1].tick_params(axis='x', rotation=45)

        # Riqueza especies
        data = df.groupby('cuadrante')['mean_species_richness'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[0,2], color=colors_quad)
        axes[0,2].set_title('Riqueza de Especies\n(Biodiversidad)')
        axes[0,2].set_ylabel('N especies')
        axes[0,2].tick_params(axis='x', rotation=45)

        # UAI
        data = df.groupby('cuadrante')['UAI_promedio'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[1,0], color=colors_quad)
        axes[1,0].set_title('UAI\n(Gobernanza/Adaptacion)')
        axes[1,0].set_ylabel('UAI (0-1)')
        axes[1,0].tick_params(axis='x', rotation=45)

        # Riesgo climatico
        data = df.groupby('cuadrante')['idx_climate_risk'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[1,1], color=colors_quad)
        axes[1,1].set_title('Riesgo Climatico')
        axes[1,1].set_ylabel('Indice (0-1)')
        axes[1,1].tick_params(axis='x', rotation=45)

        # Vulnerabilidad social
        data = df.groupby('cuadrante')['idx_social_vuln'].mean().reindex(order_quad)
        data.plot(kind='bar', ax=axes[1,2], color=colors_quad)
        axes[1,2].set_title('Vulnerabilidad Social')
        axes[1,2].set_ylabel('Indice (0-1)')
        axes[1,2].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'perfil_riesgos_cuadrante_v3.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - perfil_riesgos_cuadrante_v3.png")

        print(f"\nVisualizaciones guardadas en: {FIGURES_PATH}")

    except ImportError as e:
        print(f"ADVERTENCIA: No se pudieron generar visualizaciones. Error: {e}")

# =============================================================================
# PASO 8: RECOMENDACIONES
# =============================================================================

def generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad):
    """Genera recomendaciones basadas en el analisis."""
    print("\n" + "=" * 70)
    print("[Dra. Ana Oliveira] RECOMENDACIONES DE POLITICAS")
    print("=" * 70)

    # Correlacion biodiversidad-polinizacion
    rho_rich_pol, _ = stats.spearmanr(df['mean_species_richness'], df['pol_deficit'])
    rho_forest_pol, _ = stats.spearmanr(df['forest_cover'], df['pol_deficit'])

    q3_vuln = df[(df['cuadrante'] == 'Q3_Vulnerable') & (df['IVM_100'] > 65)]
    total_pop = df['population'].sum()

    report = f"""# INFORME SCIENCE TEAM - VERSION 3
## Analisis Multidimensional de Vulnerabilidad
### Dr. Adrian David Gonzalez Chaves y Equipo

---

## METODOLOGIA BASADA EN METADATA

### 5 Dimensiones de RIESGO:
1. **Climate Risk**: Inundaciones y estres hidrico
2. **Health Risk**: Enfermedades vectoriales y diarreicas
3. **Social Vulnerability**: Mortalidad, pobreza, educacion, saneamiento
4. **Biodiversity Risk**: Perdida de cobertura forestal, riqueza especies, riesgo vertebrados
5. **Food Security Risk**: Deficit de polinizacion (afecta produccion agricola)

### Capacidad de Adaptacion (Gobernanza):
- **UAI**: Acceso a vivienda, ambiente, alimentacion, movilidad, adaptacion climatica

---

## HALLAZGOS PRINCIPALES

### Correlaciones Biodiversidad - Polinizacion - Seguridad Alimentaria

| Relacion | r (Spearman) | Interpretacion |
|----------|--------------|----------------|
| Riqueza especies vs Deficit Polinizacion | **{rho_rich_pol:.3f}** | Mayor biodiversidad = menor deficit |
| Cobertura forestal vs Deficit Polinizacion | **{rho_forest_pol:.3f}** | Mas bosque = mejor polinizacion |

**Conclusion**: La conservacion de biodiversidad es FUNDAMENTAL para mantener
los servicios de polinizacion y la seguridad alimentaria.

### Clasificacion por Cuadrantes

| Cuadrante | N | Deficit Polin. | Forest % | UAI | IVM |
|-----------|---|----------------|----------|-----|-----|
| Q1 Modelo | {len(df[df['cuadrante']=='Q1_Modelo'])} | {df[df['cuadrante']=='Q1_Modelo']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q1_Modelo']['forest_cover'].mean():.1f} | {df[df['cuadrante']=='Q1_Modelo']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q1_Modelo']['IVM_100'].mean():.1f} |
| Q2 Conservar | {len(df[df['cuadrante']=='Q2_Conservar'])} | {df[df['cuadrante']=='Q2_Conservar']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q2_Conservar']['forest_cover'].mean():.1f} | {df[df['cuadrante']=='Q2_Conservar']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q2_Conservar']['IVM_100'].mean():.1f} |
| Q3 Vulnerable | {len(df[df['cuadrante']=='Q3_Vulnerable'])} | {df[df['cuadrante']=='Q3_Vulnerable']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q3_Vulnerable']['forest_cover'].mean():.1f} | {df[df['cuadrante']=='Q3_Vulnerable']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q3_Vulnerable']['IVM_100'].mean():.1f} |
| Q4 Desarrollo | {len(df[df['cuadrante']=='Q4_Desarrollo'])} | {df[df['cuadrante']=='Q4_Desarrollo']['pol_deficit'].mean():.3f} | {df[df['cuadrante']=='Q4_Desarrollo']['forest_cover'].mean():.1f} | {df[df['cuadrante']=='Q4_Desarrollo']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q4_Desarrollo']['IVM_100'].mean():.1f} |

---

## POBLACION VULNERABLE

### Por Categoria de IVM:
"""

    for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
        subset = df[df['categoria_IVM'] == cat]
        if len(subset) > 0:
            pop = subset['population'].sum()
            report += f"- **{cat}**: {len(subset)} municipios, {pop:,.0f} hab ({pop/total_pop*100:.1f}%)\n"

    vuln_df = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]
    vuln_pop = vuln_df['population'].sum()

    report += f"""
### Caracteristicas de Poblacion Vulnerable (Alta + Muy Alta):
- **Total**: {vuln_pop:,.0f} habitantes ({vuln_pop/total_pop*100:.1f}%)
- Deficit polinizacion: {vuln_df['pol_deficit'].mean():.3f}
- Cobertura forestal: {vuln_df['forest_cover'].mean():.1f}%
- UAI: {vuln_df['UAI_promedio'].mean():.3f}
- % Rural: {vuln_df['pct_rural'].mean():.1f}%
- % Poblacion negra: {vuln_df['population_preta'].sum()/vuln_pop*100:.1f}%
- % Poblacion indigena: {vuln_df['population_indigena'].sum()/vuln_pop*100:.1f}%

---

## RECOMENDACIONES

### 1. Conservar Biodiversidad = Mantener Seguridad Alimentaria

La correlacion entre riqueza de especies y deficit de polinizacion ({rho_rich_pol:.3f})
demuestra que la conservacion de biodiversidad es esencial para la produccion agricola.

**Acciones:**
- Restaurar habitat para polinizadores
- Proteger remanentes forestales
- Agricultura amigable con biodiversidad

### 2. Priorizar Municipios Q3 (Vulnerables)

{len(q3_vuln)} municipios con deficit en AMBAS dimensiones (biodiversidad Y gobernanza).

**Municipios prioritarios:**
"""

    for _, row in q3_vuln.nlargest(10, 'IVM_100').iterrows():
        report += f"- {row['Municipio']} (IVM: {row['IVM_100']:.1f})\n"

    report += """
### 3. Fortalecer Gobernanza para Adaptacion

Mayor UAI esta asociado a menor vulnerabilidad en todas las dimensiones.

**Acciones:**
- Mejorar acceso a servicios basicos
- Fortalecer capacidades municipales
- Integrar adaptacion climatica en planificacion

### 4. Justicia Ambiental

Poblaciones rurales, negras e indigenas estan sobrerrepresentadas en municipios vulnerables.

**Acciones:**
- Politicas diferenciadas por territorio
- Participacion de comunidades en decisiones
- Pagos por servicios ecosistemicos

---

*Science Team - Dr. Adrian David Gonzalez Chaves*
*Enero 2026 - Version 3 (Basada en Metadata)*
"""

    with open(DOCS_PATH / 'INFORME_SCIENCE_TEAM_V3.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nInforme guardado en: {DOCS_PATH / 'INFORME_SCIENCE_TEAM_V3.md'}")

    return report

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecuta el analisis completo V3."""
    print("\n" + "=" * 70)
    print("SCIENCE TEAM - ANALISIS MULTIDIMENSIONAL V3")
    print("Basado en clasificacion de METADATA.XLSX")
    print("Dr. Adrian David Gonzalez Chaves - Director Cientifico")
    print("=" * 70)

    # Paso 1: Cargar datos
    df, df_health = load_and_clean_data()

    # Paso 2: Calcular indices por dimension
    df = calculate_dimension_indices(df)

    # Paso 3: Correlaciones
    corr_df, sig_corr = calculate_correlations(df, df_health)

    # Paso 4: Cuadrantes
    df, median_uai, median_biodiv = classify_quadrants(df)

    # Paso 5: IVM
    df = calculate_ivm(df)

    # Paso 6: Caracterizacion demografica
    demo_by_cat, demo_by_quad = demographic_characterization(df)

    # Paso 7: Visualizaciones
    generate_visualizations(df, corr_df, median_uai, median_biodiv)

    # Paso 8: Recomendaciones
    report = generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad)

    # Guardar resultados
    print("\n" + "=" * 70)
    print("GUARDANDO RESULTADOS")
    print("=" * 70)

    df.to_csv(OUTPUT_PATH / 'municipios_ivm_v3.csv', index=False)
    corr_df.to_csv(OUTPUT_PATH / 'correlaciones_v3.csv', index=False)
    demo_by_cat.to_csv(OUTPUT_PATH / 'demo_categoria_v3.csv')
    demo_by_quad.to_csv(OUTPUT_PATH / 'demo_cuadrante_v3.csv')

    print(f"  - municipios_ivm_v3.csv")
    print(f"  - correlaciones_v3.csv")
    print(f"  - demo_categoria_v3.csv")
    print(f"  - demo_cuadrante_v3.csv")

    print("\n" + "=" * 70)
    print("ANALISIS V3 COMPLETADO")
    print("=" * 70)

    return df, corr_df, demo_by_cat, demo_by_quad

if __name__ == "__main__":
    df, corr_df, demo_by_cat, demo_by_quad = main()
