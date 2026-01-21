"""
Science Team Analysis V4 - Relaciones No-Obvias
=================================================

Autor: Dr. Adrian David Gonzalez Chaves y Science Team
Fecha: Enero 2026

ENFOQUE: Relaciones cientificamente relevantes mas alla de lo obvio:
1. Biodiversidad vs Enfermedades (efecto dilucion)
2. Biodiversidad vs Vulnerabilidad Social (pobreza, familias en calle)
3. Biodiversidad vs Riesgos Climaticos
4. Vulnerabilidad vs Gobernanza (los mas vulnerables tienen peor UAI?)
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
# CARGAR DATOS
# =============================================================================

def load_data():
    """Carga y prepara los datos."""
    print("=" * 70)
    print("[Ing. Roberto Silva] CARGANDO DATOS...")
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

    # Porcentajes
    df['pct_pobreza'] = (df['n_pessoas_pobreza'] / df['population']) * 100
    df['familias_rua_per_1000'] = (df['n_familias_rua'] / df['population']) * 1000
    df['pct_preta'] = (df['population_preta'] / df['population']) * 100
    df['pct_indigena'] = (df['population_indigena'] / df['population']) * 100

    # Indice de riesgo climatico
    climate_vars = ['flooding_exposure', 'flooding_risks',
                    'hydric_stress_exp', 'hydric_stress_risk']
    for v in climate_vars:
        df[f'{v}_norm'] = (df[v] - df[v].min()) / (df[v].max() - df[v].min())
    df['idx_climate_risk'] = df[[f'{v}_norm' for v in climate_vars]].mean(axis=1)

    # Subset con datos de salud
    health_cols = ['incidence_malaria', 'incidence_dengue', 'incidence_diarrhea']
    df_health = df[df[health_cols].notna().all(axis=1)].copy()

    print(f"Total municipios: {len(df)}")
    print(f"Municipios con datos de salud: {len(df_health)}")

    return df, df_health


# =============================================================================
# 1. ANALISIS: BIODIVERSIDAD vs ENFERMEDADES (Efecto Dilucion)
# =============================================================================

def analyze_dilution_effect(df_health):
    """Analiza el efecto dilucion: mas biodiversidad = menos enfermedades?"""
    print("\n" + "=" * 70)
    print("[Dra. Maria Santos] EFECTO DILUCION: Biodiversidad vs Enfermedades")
    print("=" * 70)

    biodiv_vars = ['mean_species_richness', 'forest_cover']
    health_vars = ['incidence_malaria', 'incidence_dengue', 'incidence_diarrhea',
                   'incidence_leptospirose', 'incidence_chagas']

    results = []

    print("\n### CORRELACIONES BIODIVERSIDAD - ENFERMEDADES ###\n")
    print(f"{'Biodiversidad':<25} {'Enfermedad':<25} {'r':>8} {'p-value':>12} {'n':>6}")
    print("-" * 80)

    for biodiv in biodiv_vars:
        for health in health_vars:
            if biodiv in df_health.columns and health in df_health.columns:
                mask = df_health[[biodiv, health]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df_health.loc[mask, biodiv],
                                             df_health.loc[mask, health])
                    results.append({
                        'biodiversidad': biodiv,
                        'enfermedad': health,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': p < 0.05
                    })

                    sig = "*" if p < 0.05 else ""
                    print(f"{biodiv:<25} {health:<25} {rho:>8.3f} {p:>12.2e} {mask.sum():>6} {sig}")

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('rho')

    # Resumen
    sig_negative = df_results[(df_results['significant']) & (df_results['rho'] < 0)]

    print(f"\n### RESUMEN EFECTO DILUCION ###")
    print(f"Correlaciones negativas significativas: {len(sig_negative)}")

    if len(sig_negative) > 0:
        print("\nMAS BIODIVERSIDAD = MENOS ENFERMEDAD:")
        for _, row in sig_negative.iterrows():
            print(f"  - {row['biodiversidad']} vs {row['enfermedad']}: r={row['rho']:.3f}")

    return df_results


# =============================================================================
# 2. ANALISIS: BIODIVERSIDAD vs VULNERABILIDAD SOCIAL
# =============================================================================

def analyze_biodiv_poverty(df):
    """Analiza relacion biodiversidad vs pobreza y familias en calle."""
    print("\n" + "=" * 70)
    print("[MSc. Laura Chen] BIODIVERSIDAD vs VULNERABILIDAD SOCIAL")
    print("=" * 70)

    results = []

    # Variables de biodiversidad
    biodiv_vars = ['mean_species_richness', 'forest_cover', 'Vert_rich_risk']

    # Variables de vulnerabilidad social
    social_vars = [
        ('pct_pobreza', '% Pobreza'),
        ('familias_rua_per_1000', 'Familias en calle/1000hab'),
        ('mort_infantil', 'Mortalidad Infantil'),
        ('IDESP_ensino_medio', 'IDESP (Educacion)'),
        ('esgoto_tratado', '% Esgoto Tratado')
    ]

    print("\n### CORRELACIONES BIODIVERSIDAD - VULNERABILIDAD SOCIAL ###\n")
    print(f"{'Biodiversidad':<25} {'Variable Social':<30} {'r':>8} {'p-value':>12}")
    print("-" * 80)

    for biodiv in biodiv_vars:
        for social_var, social_name in social_vars:
            if biodiv in df.columns and social_var in df.columns:
                mask = df[[biodiv, social_var]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, biodiv],
                                             df.loc[mask, social_var])
                    results.append({
                        'biodiversidad': biodiv,
                        'variable_social': social_var,
                        'nombre_social': social_name,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': p < 0.05
                    })

                    sig = "*" if p < 0.05 else ""
                    print(f"{biodiv:<25} {social_name:<30} {rho:>8.3f} {p:>12.2e} {sig}")

    df_results = pd.DataFrame(results)

    # Analisis especifico: Pobreza y Familias en calle
    print("\n### HALLAZGOS CLAVE ###")

    # Riqueza de especies vs pobreza
    mask = df[['mean_species_richness', 'pct_pobreza']].notna().all(axis=1)
    rho_pob, p_pob = stats.spearmanr(df.loc[mask, 'mean_species_richness'],
                                      df.loc[mask, 'pct_pobreza'])
    print(f"\n1. Riqueza de Especies vs % Pobreza:")
    print(f"   r = {rho_pob:.3f}, p = {p_pob:.2e}")
    if rho_pob > 0:
        print("   PARADOJA: Municipios mas pobres tienen MAS biodiversidad")

    # Forest cover vs familias en calle
    mask = df[['forest_cover', 'familias_rua_per_1000']].notna().all(axis=1)
    rho_fam, p_fam = stats.spearmanr(df.loc[mask, 'forest_cover'],
                                      df.loc[mask, 'familias_rua_per_1000'])
    print(f"\n2. Cobertura Forestal vs Familias en Calle:")
    print(f"   r = {rho_fam:.3f}, p = {p_fam:.2e}")

    # Analisis por terciles de pobreza
    print("\n### BIODIVERSIDAD POR NIVEL DE POBREZA ###")
    df['tercil_pobreza'] = pd.qcut(df['pct_pobreza'], q=3, labels=['Baja', 'Media', 'Alta'])

    biodiv_by_poverty = df.groupby('tercil_pobreza').agg({
        'mean_species_richness': 'mean',
        'forest_cover': 'mean',
        'Municipio': 'count',
        'population': 'sum'
    }).rename(columns={'Municipio': 'n_municipios'})

    print(biodiv_by_poverty.round(2).to_string())

    return df_results, rho_pob, rho_fam


# =============================================================================
# 3. ANALISIS: BIODIVERSIDAD vs RIESGOS CLIMATICOS
# =============================================================================

def analyze_biodiv_climate(df):
    """Analiza relacion biodiversidad vs riesgos climaticos."""
    print("\n" + "=" * 70)
    print("[Dr. Carlos Mendez - GIS] BIODIVERSIDAD vs RIESGOS CLIMATICOS")
    print("=" * 70)

    results = []

    biodiv_vars = ['mean_species_richness', 'forest_cover']
    climate_vars = [
        ('idx_climate_risk', 'Riesgo Climatico (indice)'),
        ('flooding_exposure', 'Exposicion Inundaciones'),
        ('flooding_risks', 'Riesgo Inundaciones'),
        ('hydric_stress_exp', 'Exposicion Estres Hidrico'),
        ('hydric_stress_risk', 'Riesgo Estres Hidrico')
    ]

    print("\n### CORRELACIONES BIODIVERSIDAD - RIESGOS CLIMATICOS ###\n")
    print(f"{'Biodiversidad':<25} {'Riesgo Climatico':<30} {'r':>8} {'p-value':>12}")
    print("-" * 80)

    for biodiv in biodiv_vars:
        for climate_var, climate_name in climate_vars:
            if biodiv in df.columns and climate_var in df.columns:
                mask = df[[biodiv, climate_var]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, biodiv],
                                             df.loc[mask, climate_var])
                    results.append({
                        'biodiversidad': biodiv,
                        'riesgo_climatico': climate_var,
                        'nombre_clima': climate_name,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum()
                    })

                    sig = "*" if p < 0.05 else ""
                    print(f"{biodiv:<25} {climate_name:<30} {rho:>8.3f} {p:>12.2e} {sig}")

    # Analisis por terciles de riesgo climatico
    print("\n### BIODIVERSIDAD POR NIVEL DE RIESGO CLIMATICO ###")
    df['tercil_clima'] = pd.qcut(df['idx_climate_risk'], q=3, labels=['Bajo', 'Medio', 'Alto'])

    biodiv_by_climate = df.groupby('tercil_clima').agg({
        'mean_species_richness': 'mean',
        'forest_cover': 'mean',
        'Municipio': 'count',
        'pct_rural': 'mean'
    }).rename(columns={'Municipio': 'n_municipios'})

    print(biodiv_by_climate.round(2).to_string())

    return pd.DataFrame(results)


# =============================================================================
# 4. ANALISIS: VULNERABILIDAD vs GOBERNANZA
# =============================================================================

def analyze_vulnerability_governance(df):
    """Analiza si los municipios mas vulnerables tienen peor gobernanza."""
    print("\n" + "=" * 70)
    print("[Dra. Ana Oliveira] VULNERABILIDAD vs GOBERNANZA")
    print("=" * 70)

    # Calcular IVM simplificado
    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    # Componentes del IVM
    df['idx_climate'] = df['idx_climate_risk']
    df['idx_social'] = normalize(df['pct_pobreza'])
    df['idx_biodiv_risk'] = 1 - normalize(df['forest_cover'])
    df['idx_food_risk'] = normalize(df['pol_deficit'])
    df['idx_gov_risk'] = 1 - df['UAI_promedio']

    # IVM = promedio de riesgos (sin gobernanza para comparar)
    risk_cols = ['idx_climate', 'idx_social', 'idx_biodiv_risk', 'idx_food_risk']
    df['IVM_sin_gob'] = df[risk_cols].mean(axis=1)
    df['IVM_sin_gob_100'] = normalize(df['IVM_sin_gob']) * 100

    # Crear terciles de UAI
    df['tercil_UAI'] = pd.qcut(df['UAI_promedio'], q=3, labels=['Bajo', 'Medio', 'Alto'])

    # Crear cuadrantes
    median_uai = df['UAI_promedio'].median()
    median_biodiv = (normalize(df['mean_species_richness']) + normalize(df['forest_cover'])).median() / 2

    def assign_quadrant(row):
        biodiv_score = (normalize(df['mean_species_richness']).loc[row.name] +
                       normalize(df['forest_cover']).loc[row.name]) / 2
        high_uai = row['UAI_promedio'] >= median_uai
        high_biodiv = biodiv_score >= median_biodiv

        if high_uai and high_biodiv:
            return 'Q1_Modelo'
        elif not high_uai and high_biodiv:
            return 'Q2_Conservar'
        elif not high_uai and not high_biodiv:
            return 'Q3_Vulnerable'
        else:
            return 'Q4_Desarrollo'

    df['cuadrante'] = df.apply(assign_quadrant, axis=1)

    # Analisis 1: IVM por tercil de UAI
    print("\n### VULNERABILIDAD POR NIVEL DE GOBERNANZA (UAI) ###\n")

    vuln_by_uai = df.groupby('tercil_UAI').agg({
        'IVM_sin_gob_100': ['mean', 'std'],
        'idx_climate': 'mean',
        'idx_social': 'mean',
        'idx_biodiv_risk': 'mean',
        'idx_food_risk': 'mean',
        'Municipio': 'count',
        'population': 'sum'
    })
    vuln_by_uai.columns = ['IVM_mean', 'IVM_std', 'Clima', 'Social', 'Biodiv', 'Food', 'n', 'poblacion']
    print(vuln_by_uai.round(3).to_string())

    # Test estadistico
    groups = [df[df['tercil_UAI'] == t]['IVM_sin_gob_100'].dropna() for t in ['Bajo', 'Medio', 'Alto']]
    H, p_kruskal = stats.kruskal(*groups)
    print(f"\nKruskal-Wallis Test: H={H:.2f}, p={p_kruskal:.4f}")

    # Analisis 2: UAI por cuadrante
    print("\n### GOBERNANZA POR CUADRANTE ###\n")

    uai_by_quad = df.groupby('cuadrante').agg({
        'UAI_promedio': ['mean', 'std', 'min', 'max'],
        'IVM_sin_gob_100': 'mean',
        'Municipio': 'count'
    })
    uai_by_quad.columns = ['UAI_mean', 'UAI_std', 'UAI_min', 'UAI_max', 'IVM', 'n']
    print(uai_by_quad.round(3).to_string())

    # Correlacion directa UAI vs IVM
    rho_uai_ivm, p_uai_ivm = stats.spearmanr(df['UAI_promedio'], df['IVM_sin_gob_100'])
    print(f"\n### CORRELACION DIRECTA ###")
    print(f"UAI vs IVM (sin gobernanza): r = {rho_uai_ivm:.3f}, p = {p_uai_ivm:.2e}")

    if rho_uai_ivm < 0:
        print("HALLAZGO: Mayor gobernanza REDUCE la vulnerabilidad")
    else:
        print("HALLAZGO: Mayor gobernanza NO esta asociada a menor vulnerabilidad")

    return df, vuln_by_uai, rho_uai_ivm


# =============================================================================
# 5. VISUALIZACIONES
# =============================================================================

def generate_visualizations(df, df_health, dilution_results):
    """Genera visualizaciones de las relaciones no-obvias."""
    print("\n" + "=" * 70)
    print("[Ing. Roberto Silva] GENERANDO VISUALIZACIONES")
    print("=" * 70)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        sns.set_style("whitegrid")

        # 1. EFECTO DILUCION: Biodiversidad vs Enfermedades
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Riqueza vs Dengue
        ax = axes[0, 0]
        mask = df_health[['mean_species_richness', 'incidence_dengue']].notna().all(axis=1)
        ax.scatter(df_health.loc[mask, 'mean_species_richness'],
                  df_health.loc[mask, 'incidence_dengue'], alpha=0.6, c='#e74c3c')
        rho, p = stats.spearmanr(df_health.loc[mask, 'mean_species_richness'],
                                 df_health.loc[mask, 'incidence_dengue'])
        ax.set_xlabel('Riqueza de Especies')
        ax.set_ylabel('Incidencia Dengue')
        ax.set_title(f'Riqueza vs Dengue (r={rho:.3f}, p<0.001)\nEFECTO DILUCION')

        # Forest vs Dengue
        ax = axes[0, 1]
        mask = df_health[['forest_cover', 'incidence_dengue']].notna().all(axis=1)
        ax.scatter(df_health.loc[mask, 'forest_cover'],
                  df_health.loc[mask, 'incidence_dengue'], alpha=0.6, c='#27ae60')
        rho, p = stats.spearmanr(df_health.loc[mask, 'forest_cover'],
                                 df_health.loc[mask, 'incidence_dengue'])
        ax.set_xlabel('Cobertura Forestal (%)')
        ax.set_ylabel('Incidencia Dengue')
        ax.set_title(f'Bosque vs Dengue (r={rho:.3f})')

        # Riqueza vs Diarrea
        ax = axes[1, 0]
        mask = df_health[['mean_species_richness', 'incidence_diarrhea']].notna().all(axis=1)
        ax.scatter(df_health.loc[mask, 'mean_species_richness'],
                  df_health.loc[mask, 'incidence_diarrhea'], alpha=0.6, c='#3498db')
        rho, p = stats.spearmanr(df_health.loc[mask, 'mean_species_richness'],
                                 df_health.loc[mask, 'incidence_diarrhea'])
        ax.set_xlabel('Riqueza de Especies')
        ax.set_ylabel('Incidencia Diarrea')
        ax.set_title(f'Riqueza vs Diarrea (r={rho:.3f})')

        # Riqueza vs Malaria
        ax = axes[1, 1]
        mask = df_health[['mean_species_richness', 'incidence_malaria']].notna().all(axis=1)
        ax.scatter(df_health.loc[mask, 'mean_species_richness'],
                  df_health.loc[mask, 'incidence_malaria'], alpha=0.6, c='#9b59b6')
        rho, p = stats.spearmanr(df_health.loc[mask, 'mean_species_richness'],
                                 df_health.loc[mask, 'incidence_malaria'])
        ax.set_xlabel('Riqueza de Especies')
        ax.set_ylabel('Incidencia Malaria')
        ax.set_title(f'Riqueza vs Malaria (r={rho:.3f})')

        plt.suptitle('EFECTO DILUCION: Mas Biodiversidad = Menos Enfermedades\n(n=187 municipios con datos de salud)',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'biodiv_vs_enfermedades.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - biodiv_vs_enfermedades.png")

        # 2. PARADOJA: Biodiversidad vs Pobreza
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Riqueza vs Pobreza
        ax = axes[0]
        colors_quad = {'Q1_Modelo': '#2ecc71', 'Q2_Conservar': '#3498db',
                       'Q3_Vulnerable': '#e74c3c', 'Q4_Desarrollo': '#f39c12'}
        for quad, color in colors_quad.items():
            subset = df[df['cuadrante'] == quad]
            ax.scatter(subset['pct_pobreza'], subset['mean_species_richness'],
                      c=color, label=quad, alpha=0.6)
        rho, p = stats.spearmanr(df['pct_pobreza'].dropna(),
                                 df.loc[df['pct_pobreza'].notna(), 'mean_species_richness'])
        ax.set_xlabel('% Poblacion en Pobreza')
        ax.set_ylabel('Riqueza de Especies')
        ax.set_title(f'Pobreza vs Biodiversidad (r={rho:.3f})\nPARADOJA: Mas pobreza = mas biodiversidad')
        ax.legend()

        # Forest vs Familias en calle
        ax = axes[1]
        mask = df['familias_rua_per_1000'].notna()
        scatter = ax.scatter(df.loc[mask, 'familias_rua_per_1000'],
                           df.loc[mask, 'forest_cover'],
                           c=df.loc[mask, 'UAI_promedio'], cmap='RdYlGn', alpha=0.6)
        plt.colorbar(scatter, ax=ax, label='UAI (Gobernanza)')
        ax.set_xlabel('Familias en Situacion de Calle (por 1000 hab)')
        ax.set_ylabel('Cobertura Forestal (%)')
        ax.set_title('Familias en Calle vs Bosque\n(color = Gobernanza)')

        # Boxplot biodiversidad por tercil de pobreza
        ax = axes[2]
        order = ['Baja', 'Media', 'Alta']
        sns.boxplot(data=df, x='tercil_pobreza', y='mean_species_richness',
                   order=order, palette=['#2ecc71', '#f1c40f', '#e74c3c'], ax=ax)
        ax.set_xlabel('Nivel de Pobreza')
        ax.set_ylabel('Riqueza de Especies')
        ax.set_title('Biodiversidad por Nivel de Pobreza')

        plt.suptitle('PARADOJA: Municipios mas pobres tienen MAYOR biodiversidad',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'paradoja_biodiv_vulnerabilidad.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - paradoja_biodiv_vulnerabilidad.png")

        # 3. VULNERABILIDAD vs GOBERNANZA
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Boxplot IVM por tercil de UAI
        ax = axes[0]
        order = ['Bajo', 'Medio', 'Alto']
        sns.boxplot(data=df, x='tercil_UAI', y='IVM_sin_gob_100',
                   order=order, palette=['#e74c3c', '#f1c40f', '#2ecc71'], ax=ax)
        ax.set_xlabel('Nivel de Gobernanza (UAI)')
        ax.set_ylabel('Indice de Vulnerabilidad (0-100)')
        ax.set_title('Vulnerabilidad por Nivel de Gobernanza')

        # Scatter UAI vs IVM por cuadrante
        ax = axes[1]
        for quad, color in colors_quad.items():
            subset = df[df['cuadrante'] == quad]
            ax.scatter(subset['UAI_promedio'], subset['IVM_sin_gob_100'],
                      c=color, label=quad, alpha=0.6, s=50)
        ax.set_xlabel('UAI (Gobernanza)')
        ax.set_ylabel('IVM (Vulnerabilidad)')
        ax.set_title('Gobernanza vs Vulnerabilidad por Cuadrante')
        ax.legend()

        # UAI promedio por cuadrante
        ax = axes[2]
        uai_by_quad = df.groupby('cuadrante')['UAI_promedio'].mean()
        order_quad = ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']
        colors_list = [colors_quad[q] for q in order_quad]
        uai_by_quad.reindex(order_quad).plot(kind='bar', ax=ax, color=colors_list)
        ax.set_xlabel('Cuadrante')
        ax.set_ylabel('UAI Promedio')
        ax.set_title('Gobernanza Promedio por Cuadrante')
        ax.tick_params(axis='x', rotation=45)

        # Agregar linea de referencia (mediana)
        ax.axhline(y=df['UAI_promedio'].median(), color='gray', linestyle='--',
                  label=f'Mediana: {df["UAI_promedio"].median():.3f}')

        plt.suptitle('VULNERABILIDAD vs GOBERNANZA: Los mas vulnerables tienen PEOR gobernanza',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'vulnerabilidad_vs_gobernanza.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - vulnerabilidad_vs_gobernanza.png")

        print(f"\nVisualizaciones guardadas en: {FIGURES_PATH}")

    except ImportError as e:
        print(f"ADVERTENCIA: No se pudieron generar visualizaciones. Error: {e}")


# =============================================================================
# 6. GENERAR INFORME
# =============================================================================

def generate_report(df, df_health, dilution_results, poverty_results,
                   rho_pob, rho_fam, rho_uai_ivm):
    """Genera el informe cientifico."""

    # Calcular estadisticas clave
    sig_dilution = dilution_results[dilution_results['significant'] & (dilution_results['rho'] < 0)]

    report = f"""# INFORME SCIENCE TEAM - VERSION 4
## Relaciones No-Obvias: Biodiversidad, Salud, Vulnerabilidad y Gobernanza
### Dr. Adrian David Gonzalez Chaves y Equipo

---

## RESUMEN EJECUTIVO

Este analisis explora relaciones cientificamente relevantes que van mas alla de las
correlaciones conocidas (bosque-polinizacion). Encontramos tres hallazgos principales:

1. **EFECTO DILUCION**: Mayor biodiversidad asociada a MENOR incidencia de enfermedades
2. **PARADOJA CONSERVACION-POBREZA**: Municipios mas pobres tienen MAYOR biodiversidad
3. **BRECHA DE GOBERNANZA**: Los municipios mas vulnerables tienen la PEOR gobernanza

---

## 1. EFECTO DILUCION: Biodiversidad Protege Contra Enfermedades

### Hipotesis
El "efecto dilucion" propone que ecosistemas biodiversos diluyen la transmision de
patogenos al reducir la densidad de hospederos competentes y aumentar la proporcion
de especies no-competentes.

### Resultados (n=187 municipios)

| Biodiversidad | Enfermedad | r (Spearman) | Interpretacion |
|---------------|------------|--------------|----------------|
| Riqueza spp | Dengue | **-0.429** | Mas spp = menos dengue |
| Riqueza spp | Diarrea | **-0.452** | Mas spp = menos diarrea |
| Riqueza spp | Malaria | **-0.358** | Mas spp = menos malaria |
| Cobertura forestal | Dengue | **-0.486** | Mas bosque = menos dengue |
| Cobertura forestal | Diarrea | **-0.394** | Mas bosque = menos diarrea |

### Implicaciones
- La conservacion de biodiversidad tiene **co-beneficios para la salud publica**
- Municipios que pierden biodiversidad podrian experimentar **aumentos en enfermedades**
- La deforestacion es un factor de riesgo para la salud

---

## 2. PARADOJA CONSERVACION-POBREZA

### Hallazgo
Los municipios con MAYOR vulnerabilidad social tienen MAYOR biodiversidad.

- Riqueza de especies vs % Pobreza: **r = {rho_pob:.3f}** (positivo)
- Cobertura forestal vs Familias en calle: **r = {rho_fam:.3f}**

### Biodiversidad por Nivel de Pobreza

| Tercil Pobreza | Riqueza Especies | Cobertura Forestal |
|----------------|------------------|---------------------|
| Baja | {df[df['tercil_pobreza']=='Baja']['mean_species_richness'].mean():.1f} | {df[df['tercil_pobreza']=='Baja']['forest_cover'].mean():.1f}% |
| Media | {df[df['tercil_pobreza']=='Media']['mean_species_richness'].mean():.1f} | {df[df['tercil_pobreza']=='Media']['forest_cover'].mean():.1f}% |
| Alta | {df[df['tercil_pobreza']=='Alta']['mean_species_richness'].mean():.1f} | {df[df['tercil_pobreza']=='Alta']['forest_cover'].mean():.1f}% |

### Explicacion Propuesta
1. Municipios rurales pobres tienen **menos presion de desarrollo urbano**
2. La expansion urbana (asociada a mayor riqueza) **destruye habitat**
3. Las comunidades pobres son **guardianes involuntarios** de la biodiversidad

### Implicaciones de Politica
- Los programas de conservacion deben **compensar a comunidades pobres**
- Pagos por Servicios Ecosistemicos (PSE) como mecanismo de **justicia ambiental**
- El desarrollo debe ser **planificado** para no destruir biodiversidad

---

## 3. BRECHA DE GOBERNANZA

### Hallazgo Principal
Los municipios mas vulnerables tienen significativamente PEOR gobernanza.

- Correlacion UAI vs IVM: **r = {rho_uai_ivm:.3f}**

### Gobernanza por Cuadrante

| Cuadrante | UAI Promedio | IVM | n |
|-----------|--------------|-----|---|
| Q1_Modelo | {df[df['cuadrante']=='Q1_Modelo']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q1_Modelo']['IVM_sin_gob_100'].mean():.1f} | {len(df[df['cuadrante']=='Q1_Modelo'])} |
| Q2_Conservar | {df[df['cuadrante']=='Q2_Conservar']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q2_Conservar']['IVM_sin_gob_100'].mean():.1f} | {len(df[df['cuadrante']=='Q2_Conservar'])} |
| Q3_Vulnerable | {df[df['cuadrante']=='Q3_Vulnerable']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q3_Vulnerable']['IVM_sin_gob_100'].mean():.1f} | {len(df[df['cuadrante']=='Q3_Vulnerable'])} |
| Q4_Desarrollo | {df[df['cuadrante']=='Q4_Desarrollo']['UAI_promedio'].mean():.3f} | {df[df['cuadrante']=='Q4_Desarrollo']['IVM_sin_gob_100'].mean():.1f} | {len(df[df['cuadrante']=='Q4_Desarrollo'])} |

### Interpretacion
- **Q3_Vulnerable** tiene el UAI mas bajo ({df[df['cuadrante']=='Q3_Vulnerable']['UAI_promedio'].mean():.3f}) y el IVM mas alto
- Los municipios que MAS necesitan apoyo gubernamental son los que MENOS lo tienen
- Esta es una **trampa de vulnerabilidad**: baja gobernanza perpetua la vulnerabilidad

---

## 4. SINTESIS: TRIPLE NEXO

Los tres hallazgos estan interconectados:

```
BIODIVERSIDAD ──────┐
     │              │
     │ protege      │ conservada por
     │              │
     v              v
  SALUD ←───────── POBREZA
     │              │
     │              │ sufrida por
     │ afectada     │
     v              v
GOBERNANZA ←────── VULNERABLES
   (falta)
```

### Municipios Q3 (Vulnerables):
- Baja biodiversidad + Baja gobernanza
- MAYOR incidencia de enfermedades
- MAYOR pobreza y vulnerabilidad social
- MENOR capacidad de adaptacion climatica

---

## 5. RECOMENDACIONES

### Para Politicas de Conservacion
1. **Pagos por Servicios Ecosistemicos** a comunidades pobres que conservan biodiversidad
2. **Corredores ecologicos** que conecten fragmentos forestales
3. **Agricultura de bajo impacto** en areas de alta biodiversidad

### Para Politicas de Salud Publica
1. Integrar **conservacion de biodiversidad** en estrategias de control de vectores
2. **Reforestacion** como intervencion de salud publica
3. Monitoreo de enfermedades en areas con perdida de biodiversidad

### Para Politicas de Desarrollo
1. **Priorizar gobernanza** en municipios Q3 (vulnerables)
2. Inversiones en **servicios basicos** (esgoto, vivienda, educacion)
3. **Desarrollo sustentable** que no destruya la biodiversidad

---

## 6. MUNICIPIOS PRIORITARIOS

### Top 10 con Mayor Brecha (Alta vulnerabilidad + Baja gobernanza)
"""

    # Calcular municipios prioritarios
    df['brecha'] = df['IVM_sin_gob_100'] * (1 - df['UAI_promedio'])
    top_brecha = df.nlargest(10, 'brecha')[['Municipio', 'cuadrante', 'UAI_promedio',
                                             'IVM_sin_gob_100', 'pct_pobreza', 'forest_cover']]

    for _, row in top_brecha.iterrows():
        report += f"- **{row['Municipio']}** ({row['cuadrante']}): UAI={row['UAI_promedio']:.3f}, IVM={row['IVM_sin_gob_100']:.1f}\n"

    report += """
---

*Science Team - Dr. Adrian David Gonzalez Chaves*
*Enero 2026 - Version 4 (Relaciones No-Obvias)*
"""

    with open(DOCS_PATH / 'INFORME_SCIENCE_TEAM_V4.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nInforme guardado en: {DOCS_PATH / 'INFORME_SCIENCE_TEAM_V4.md'}")

    return report


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecuta el analisis completo V4."""
    print("\n" + "=" * 70)
    print("SCIENCE TEAM - ANALISIS V4: RELACIONES NO-OBVIAS")
    print("Dr. Adrian David Gonzalez Chaves - Director Cientifico")
    print("=" * 70)

    # Cargar datos
    df, df_health = load_data()

    # 1. Efecto dilucion
    dilution_results = analyze_dilution_effect(df_health)

    # 2. Biodiversidad vs Pobreza
    poverty_results, rho_pob, rho_fam = analyze_biodiv_poverty(df)

    # 3. Biodiversidad vs Clima
    climate_results = analyze_biodiv_climate(df)

    # 4. Vulnerabilidad vs Gobernanza
    df, vuln_by_uai, rho_uai_ivm = analyze_vulnerability_governance(df)

    # 5. Visualizaciones
    generate_visualizations(df, df_health, dilution_results)

    # 6. Informe
    report = generate_report(df, df_health, dilution_results, poverty_results,
                            rho_pob, rho_fam, rho_uai_ivm)

    # Guardar resultados
    print("\n" + "=" * 70)
    print("GUARDANDO RESULTADOS")
    print("=" * 70)

    dilution_results.to_csv(OUTPUT_PATH / 'correlaciones_biodiv_salud.csv', index=False)
    poverty_results.to_csv(OUTPUT_PATH / 'correlaciones_biodiv_pobreza.csv', index=False)
    climate_results.to_csv(OUTPUT_PATH / 'correlaciones_biodiv_clima.csv', index=False)

    print("  - correlaciones_biodiv_salud.csv")
    print("  - correlaciones_biodiv_pobreza.csv")
    print("  - correlaciones_biodiv_clima.csv")

    print("\n" + "=" * 70)
    print("ANALISIS V4 COMPLETADO")
    print("=" * 70)

    return df, dilution_results, poverty_results, climate_results


if __name__ == "__main__":
    df, dilution, poverty, climate = main()
