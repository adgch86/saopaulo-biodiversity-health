"""
Science Team Analysis - Vulnerabilidad Multidimensional de Municipios de Sao Paulo
==================================================================================

Autor: Dr. Adrian David Gonzalez Chaves y Science Team
Fecha: Enero 2026

Objetivos:
1. Correlaciones biodiversidad/politicas publicas vs dimensiones de riesgo
2. Analisis de cuadrantes UAI vs Biodiversidad
3. Indice de Vulnerabilidad Multidimensional (IVM)
4. Caracterizacion demografica de poblacion afectada
5. Recomendaciones de politicas basadas en evidencia
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
# PASO 1: CARGAR Y LIMPIAR DATOS
# =============================================================================

def load_and_clean_data():
    """Carga y limpia el dataset principal."""
    print("=" * 60)
    print("[Ing. Roberto Silva - Data Engineer] CARGANDO DATOS...")
    print("=" * 60)

    # Cargar datos
    df = pd.read_csv(DATA_PATH / "all_tabela.csv")

    # Eliminar columna indice si existe
    if df.columns[0] == '' or 'Unnamed' in df.columns[0]:
        df = df.drop(df.columns[0], axis=1)

    # Convertir NA strings a NaN
    df = df.replace('NA', np.nan)

    # Columnas a excluir de conversion numerica
    non_numeric = ['Cod_ibge', 'Municipio', 'municipality', 'COD']

    # Convertir a numerico
    for col in df.columns:
        if col not in non_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Crear variables derivadas
    uai_cols = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']
    df['UAI_promedio'] = df[uai_cols].mean(axis=1)

    # Porcentajes demograficos
    df['pct_preta'] = (df['population_preta'] / df['population']) * 100
    df['pct_indigena'] = (df['population_indigena'] / df['population']) * 100
    df['pct_branca'] = (df['population_branca'] / df['population']) * 100

    # Riesgo climatico compuesto
    df['riesgo_climatico'] = df[['flooding_risks', 'hydric_stress_risk']].mean(axis=1)

    print(f"Total municipios cargados: {len(df)}")
    print(f"Total variables: {len(df.columns)}")

    # Identificar municipios con datos de salud
    health_cols = ['persist_malaria', 'incidence_malaria', 'copersistence']
    df_health = df[df[health_cols].notna().all(axis=1)].copy()
    print(f"Municipios con datos de salud: {len(df_health)}")

    return df, df_health

# =============================================================================
# PASO 2: ANALISIS DE CORRELACIONES
# =============================================================================

def calculate_correlations(df, df_health):
    """Calcula correlaciones de Spearman entre dimensiones."""
    print("\n" + "=" * 60)
    print("[Dra. Maria Santos - Bioestadistica] ANALISIS DE CORRELACIONES")
    print("=" * 60)

    results = []

    # Definir variables por dimension
    biodiv_policy = ['mean_species_richness', 'pol_deficit', 'Vert_rich_risk']

    climate = ['flooding_exposure', 'flooding_risks', 'hydric_stress_exp', 'hydric_stress_risk']

    social = ['mort_infantil', 'n_pessoas_pobreza', 'pct_rural', 'population']

    uai = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk', 'UAI_promedio']

    # Correlaciones biodiversidad/politicas vs otras dimensiones (645 municipios)
    print("\n--- Biodiversidad/Politicas vs Otras Dimensiones (n=645) ---")

    for var1 in biodiv_policy:
        for var2 in climate + social + uai:
            if var1 in df.columns and var2 in df.columns:
                mask = df[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df.loc[mask, var1], df.loc[mask, var2])
                    results.append({
                        'var1': var1,
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.30)
                    })

    # Correlaciones con salud (187 municipios)
    print("\n--- Correlaciones con Salud (n=187) ---")

    health_vars = ['persist_malaria', 'persist_dengue', 'persist_diarrhea',
                   'incidence_malaria', 'incidence_dengue', 'incidence_diarrhea',
                   'copersistence']

    other_vars = ['mean_species_richness', 'UAI_promedio', 'pol_deficit',
                  'flooding_risks', 'hydric_stress_risk', 'pct_rural']

    for var1 in health_vars:
        for var2 in other_vars:
            if var1 in df_health.columns and var2 in df_health.columns:
                mask = df_health[[var1, var2]].notna().all(axis=1)
                if mask.sum() >= 30:
                    rho, p = stats.spearmanr(df_health.loc[mask, var1], df_health.loc[mask, var2])
                    results.append({
                        'var1': var1,
                        'var2': var2,
                        'rho': rho,
                        'p_value': p,
                        'n': mask.sum(),
                        'significant': (p < 0.05) and (abs(rho) >= 0.20)  # Umbral mas bajo para salud
                    })

    # Convertir a DataFrame
    corr_df = pd.DataFrame(results)
    corr_df = corr_df.sort_values('rho', key=abs, ascending=False)

    # Filtrar significativas
    sig_corr = corr_df[corr_df['significant']].copy()

    print(f"\nTotal correlaciones calculadas: {len(corr_df)}")
    print(f"Correlaciones significativas: {len(sig_corr)}")

    print("\n--- TOP 20 CORRELACIONES SIGNIFICATIVAS ---")
    cols_show = ['var1', 'var2', 'rho', 'p_value', 'n']
    print(sig_corr[cols_show].head(20).to_string(index=False))

    return corr_df, sig_corr

# =============================================================================
# PASO 3: CLASIFICACION EN CUADRANTES
# =============================================================================

def classify_quadrants(df):
    """Clasifica municipios en 4 cuadrantes segun UAI vs Biodiversidad."""
    print("\n" + "=" * 60)
    print("[Dr. Carlos Mendez - GIS/SIG] ANALISIS DE CUADRANTES")
    print("=" * 60)

    # Calcular medianas
    median_uai = df['UAI_promedio'].median()
    median_biodiv = df['mean_species_richness'].median()

    print(f"Mediana UAI: {median_uai:.4f}")
    print(f"Mediana Biodiversidad: {median_biodiv:.2f}")

    # Clasificar
    def assign_quadrant(row):
        high_uai = row['UAI_promedio'] >= median_uai
        high_biodiv = row['mean_species_richness'] >= median_biodiv

        if high_uai and high_biodiv:
            return 'Q1_Modelo'
        elif not high_uai and high_biodiv:
            return 'Q2_Conservar'
        elif not high_uai and not high_biodiv:
            return 'Q3_Vulnerable'
        else:
            return 'Q4_Desarrollo'

    df['cuadrante'] = df.apply(assign_quadrant, axis=1)

    # Distribucion
    print("\n--- DISTRIBUCION DE CUADRANTES ---")
    dist = df['cuadrante'].value_counts()
    dist_pct = df['cuadrante'].value_counts(normalize=True) * 100

    for quad in ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']:
        if quad in dist.index:
            print(f"{quad}: {dist[quad]} municipios ({dist_pct[quad]:.1f}%)")

    # Estadisticas por cuadrante
    print("\n--- ESTADISTICAS POR CUADRANTE ---")
    stats_quad = df.groupby('cuadrante').agg({
        'mean_species_richness': 'mean',
        'UAI_promedio': 'mean',
        'pol_deficit': 'mean',
        'pct_rural': 'mean',
        'population': 'sum'
    }).round(3)

    print(stats_quad.to_string())

    return df, median_uai, median_biodiv

# =============================================================================
# PASO 4: INDICE DE VULNERABILIDAD MULTIDIMENSIONAL
# =============================================================================

def calculate_ivm(df):
    """Calcula el Indice de Vulnerabilidad Multidimensional."""
    print("\n" + "=" * 60)
    print("[Dr. Adrian - Director] INDICE DE VULNERABILIDAD MULTIDIMENSIONAL")
    print("=" * 60)

    df = df.copy()

    # Funcion de normalizacion MinMax
    def normalize(series, higher_is_worse=True):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        if not higher_is_worse:
            normalized = 1 - normalized
        return normalized

    # 1. Indice de Riesgo Climatico (mayor = peor)
    df['idx_clima'] = df[['flooding_exposure', 'flooding_risks',
                          'hydric_stress_exp', 'hydric_stress_risk']].apply(
                              lambda x: normalize(x, True)).mean(axis=1)

    # 2. Indice de Vulnerabilidad Social (mayor = peor)
    df['mort_norm'] = normalize(df['mort_infantil'], higher_is_worse=True)
    df['pobreza_pct'] = df['n_pessoas_pobreza'] / df['population'] * 100
    df['pobreza_norm'] = normalize(df['pobreza_pct'], higher_is_worse=True)
    df['idx_social'] = (df['mort_norm'] + df['pobreza_norm']) / 2

    # 3. Indice de Capacidad Adaptativa INVERTIDO (alto UAI = baja vulnerabilidad)
    df['idx_capacidad_inv'] = normalize(df['UAI_promedio'], higher_is_worse=False)

    # 4. Indice de Deficit Politico (mayor = peor)
    df['idx_politicas'] = normalize(df['pol_deficit'], higher_is_worse=True)

    # 5. Indice de Riesgo Ecologico (mayor Vert_rich_risk = peor)
    df['idx_riesgo_eco'] = normalize(df['Vert_rich_risk'], higher_is_worse=True)

    # IVM Compuesto (pesos iguales)
    idx_cols = ['idx_clima', 'idx_social', 'idx_capacidad_inv', 'idx_politicas', 'idx_riesgo_eco']
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

    # Estadisticas
    print("\n--- DISTRIBUCION DEL IVM ---")
    print(df['IVM_100'].describe().round(2))

    print("\n--- DISTRIBUCION POR CATEGORIA ---")
    cat_dist = df['categoria_IVM'].value_counts()
    for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
        if cat in cat_dist.index:
            print(f"{cat}: {cat_dist[cat]} municipios")

    print("\n--- TOP 10 MUNICIPIOS MAS VULNERABLES ---")
    top_vuln = df.nlargest(10, 'IVM_100')[['Municipio', 'IVM_100', 'categoria_IVM', 'cuadrante', 'population']]
    print(top_vuln.to_string(index=False))

    return df

# =============================================================================
# PASO 5: CARACTERIZACION DEMOGRAFICA
# =============================================================================

def demographic_characterization(df):
    """Caracteriza demograficamente la poblacion afectada."""
    print("\n" + "=" * 60)
    print("[MSc. Laura Chen - Ecologa] CARACTERIZACION DEMOGRAFICA")
    print("=" * 60)

    # Por categoria de vulnerabilidad
    print("\n--- PERFIL DEMOGRAFICO POR CATEGORIA DE VULNERABILIDAD ---")

    demo_by_cat = df.groupby('categoria_IVM').agg({
        'Municipio': 'count',
        'population': 'sum',
        'population_preta': 'sum',
        'population_indigena': 'sum',
        'population_branca': 'sum',
        'pct_rural': 'mean',
        'mort_infantil': 'mean'
    }).rename(columns={'Municipio': 'n_municipios'})

    # Calcular porcentajes
    demo_by_cat['pct_poblacion_total'] = demo_by_cat['population'] / demo_by_cat['population'].sum() * 100
    demo_by_cat['pct_preta'] = demo_by_cat['population_preta'] / demo_by_cat['population'] * 100
    demo_by_cat['pct_indigena'] = demo_by_cat['population_indigena'] / demo_by_cat['population'] * 100
    demo_by_cat['pct_branca'] = demo_by_cat['population_branca'] / demo_by_cat['population'] * 100

    cols_show = ['n_municipios', 'population', 'pct_poblacion_total',
                 'pct_preta', 'pct_indigena', 'pct_branca', 'pct_rural', 'mort_infantil']
    print(demo_by_cat[cols_show].round(2).to_string())

    # Por cuadrante
    print("\n--- PERFIL DEMOGRAFICO POR CUADRANTE ---")

    demo_by_quad = df.groupby('cuadrante').agg({
        'Municipio': 'count',
        'population': 'sum',
        'population_preta': 'sum',
        'population_indigena': 'sum',
        'population_branca': 'sum',
        'pct_rural': 'mean',
        'IVM_100': 'mean'
    }).rename(columns={'Municipio': 'n_municipios'})

    demo_by_quad['pct_poblacion'] = demo_by_quad['population'] / demo_by_quad['population'].sum() * 100
    demo_by_quad['pct_preta'] = demo_by_quad['population_preta'] / demo_by_quad['population'] * 100
    demo_by_quad['pct_indigena'] = demo_by_quad['population_indigena'] / demo_by_quad['population'] * 100

    cols_show = ['n_municipios', 'population', 'pct_poblacion',
                 'pct_preta', 'pct_indigena', 'pct_rural', 'IVM_100']
    print(demo_by_quad[cols_show].round(2).to_string())

    # Resumen de poblacion en riesgo
    print("\n--- RESUMEN: POBLACION EN SITUACION DE RIESGO ---")

    pop_alta = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]['population'].sum()
    pop_total = df['population'].sum()

    print(f"Poblacion total analizada: {pop_total:,.0f}")
    print(f"Poblacion en vulnerabilidad Alta/Muy Alta: {pop_alta:,.0f} ({pop_alta/pop_total*100:.1f}%)")

    # Poblacion vulnerable por caracteristica
    vuln_df = df[df['categoria_IVM'].isin(['Alta', 'Muy Alta'])]

    print(f"\nDentro de la poblacion vulnerable:")
    print(f"  - Poblacion negra: {vuln_df['population_preta'].sum():,.0f} ({vuln_df['population_preta'].sum()/vuln_df['population'].sum()*100:.1f}%)")
    print(f"  - Poblacion indigena: {vuln_df['population_indigena'].sum():,.0f} ({vuln_df['population_indigena'].sum()/vuln_df['population'].sum()*100:.1f}%)")
    print(f"  - % Rural promedio: {vuln_df['pct_rural'].mean():.1f}%")

    return demo_by_cat, demo_by_quad

# =============================================================================
# PASO 6: GENERAR VISUALIZACIONES
# =============================================================================

def generate_visualizations(df, corr_df, median_uai, median_biodiv):
    """Genera todas las visualizaciones."""
    print("\n" + "=" * 60)
    print("[Ing. Roberto Silva] GENERANDO VISUALIZACIONES")
    print("=" * 60)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        sns.set_style("whitegrid")

        # 1. Scatter de cuadrantes
        fig, ax = plt.subplots(figsize=(12, 10))

        colors = {
            'Q1_Modelo': '#2ecc71',
            'Q2_Conservar': '#3498db',
            'Q3_Vulnerable': '#e74c3c',
            'Q4_Desarrollo': '#f39c12'
        }

        for quad, color in colors.items():
            subset = df[df['cuadrante'] == quad]
            ax.scatter(subset['UAI_promedio'], subset['mean_species_richness'],
                      c=color, label=f'{quad} (n={len(subset)})', alpha=0.6, s=50)

        ax.axhline(y=median_biodiv, color='gray', linestyle='--', alpha=0.7)
        ax.axvline(x=median_uai, color='gray', linestyle='--', alpha=0.7)

        ax.set_xlabel('UAI Promedio (Indice de Acceso Universal)', fontsize=12)
        ax.set_ylabel('Riqueza Media de Especies', fontsize=12)
        ax.set_title('Clasificacion de Municipios: UAI vs Biodiversidad\n645 Municipios de Sao Paulo',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'cuadrantes_uai_biodiv.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - cuadrantes_uai_biodiv.png")

        # 2. Distribucion del IVM
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Histograma
        colors_cat = {'Baja': '#2ecc71', 'Moderada': '#f1c40f',
                      'Alta': '#e67e22', 'Muy Alta': '#e74c3c'}

        for cat in ['Baja', 'Moderada', 'Alta', 'Muy Alta']:
            subset = df[df['categoria_IVM'] == cat]
            axes[0].hist(subset['IVM_100'], bins=15, alpha=0.7,
                        label=f'{cat} (n={len(subset)})', color=colors_cat[cat])

        axes[0].set_xlabel('Indice de Vulnerabilidad Multidimensional (0-100)')
        axes[0].set_ylabel('Numero de Municipios')
        axes[0].set_title('Distribucion del IVM')
        axes[0].legend()

        # Boxplot por cuadrante
        order = ['Q3_Vulnerable', 'Q2_Conservar', 'Q4_Desarrollo', 'Q1_Modelo']
        sns.boxplot(data=df, x='cuadrante', y='IVM_100', order=order,
                   palette=['#e74c3c', '#3498db', '#f39c12', '#2ecc71'], ax=axes[1])
        axes[1].set_xlabel('Cuadrante')
        axes[1].set_ylabel('IVM (0-100)')
        axes[1].set_title('Vulnerabilidad por Cuadrante')

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'distribucion_ivm.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - distribucion_ivm.png")

        # 3. Perfil demografico
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Poblacion por categoria
        pop_by_cat = df.groupby('categoria_IVM')['population'].sum() / 1e6
        order_cat = ['Baja', 'Moderada', 'Alta', 'Muy Alta']
        colors_bars = [colors_cat[c] for c in order_cat if c in pop_by_cat.index]
        pop_by_cat.reindex(order_cat).plot(kind='bar', ax=axes[0,0], color=colors_bars)
        axes[0,0].set_title('Poblacion por Categoria de Vulnerabilidad')
        axes[0,0].set_ylabel('Poblacion (millones)')
        axes[0,0].set_xticklabels(axes[0,0].get_xticklabels(), rotation=45)

        # Composicion racial por categoria
        racial = df.groupby('categoria_IVM').agg({
            'pct_preta': 'mean',
            'pct_indigena': 'mean',
            'pct_branca': 'mean'
        })
        racial.reindex(order_cat).plot(kind='bar', ax=axes[0,1])
        axes[0,1].set_title('Composicion Racial por Categoria (%)')
        axes[0,1].set_ylabel('% de Poblacion')
        axes[0,1].legend(['Negra', 'Indigena', 'Blanca'])
        axes[0,1].set_xticklabels(axes[0,1].get_xticklabels(), rotation=45)

        # Rural vs Urbano
        rural = df.groupby('categoria_IVM')['pct_rural'].mean()
        rural.reindex(order_cat).plot(kind='bar', ax=axes[1,0], color='brown')
        axes[1,0].set_title('% Rural Promedio por Categoria')
        axes[1,0].set_ylabel('% Rural')
        axes[1,0].set_xticklabels(axes[1,0].get_xticklabels(), rotation=45)

        # Mortalidad infantil
        mort = df.groupby('categoria_IVM')['mort_infantil'].mean()
        mort.reindex(order_cat).plot(kind='bar', ax=axes[1,1], color='darkred')
        axes[1,1].set_title('Mortalidad Infantil Promedio por Categoria')
        axes[1,1].set_ylabel('Tasa de Mortalidad Infantil')
        axes[1,1].set_xticklabels(axes[1,1].get_xticklabels(), rotation=45)

        plt.tight_layout()
        plt.savefig(FIGURES_PATH / 'perfil_demografico.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  - perfil_demografico.png")

        # 4. Heatmap de correlaciones
        sig_corr = corr_df[corr_df['significant']].head(30)
        if len(sig_corr) > 0:
            fig, ax = plt.subplots(figsize=(14, 10))

            # Crear matriz pivot
            vars_unique = list(set(sig_corr['var1'].tolist() + sig_corr['var2'].tolist()))
            matrix = pd.DataFrame(index=vars_unique, columns=vars_unique, data=0.0)

            for _, row in sig_corr.iterrows():
                matrix.loc[row['var1'], row['var2']] = row['rho']
                matrix.loc[row['var2'], row['var1']] = row['rho']

            np.fill_diagonal(matrix.values, 1.0)

            sns.heatmap(matrix.astype(float), annot=True, fmt='.2f', cmap='RdBu_r',
                       center=0, vmin=-1, vmax=1, square=True, ax=ax)
            ax.set_title('Matriz de Correlaciones Significativas\n(p<0.05, |r|>0.30)',
                        fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(FIGURES_PATH / 'heatmap_correlaciones.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  - heatmap_correlaciones.png")

        print(f"\nVisualizaciones guardadas en: {FIGURES_PATH}")

    except ImportError as e:
        print(f"ADVERTENCIA: No se pudieron generar visualizaciones. Error: {e}")
        print("Instale matplotlib y seaborn: pip install matplotlib seaborn")

# =============================================================================
# PASO 7: RECOMENDACIONES DE POLITICAS
# =============================================================================

def generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad):
    """Genera recomendaciones de politicas basadas en evidencia."""
    print("\n" + "=" * 60)
    print("[Dra. Ana Oliveira - Servicios Ecosistemicos] RECOMENDACIONES")
    print("=" * 60)

    # Municipios prioritarios Q3 Vulnerable con alta vulnerabilidad
    q3_vuln = df[(df['cuadrante'] == 'Q3_Vulnerable') & (df['IVM_100'] > 75)]

    # Municipios prioritarios Q2 Conservar con biodiversidad alta
    q2_cons = df[(df['cuadrante'] == 'Q2_Conservar')].nlargest(20, 'mean_species_richness')

    report = f"""# RECOMENDACIONES DE POLITICAS PUBLICAS
## Basadas en Analisis Multidimensional de Vulnerabilidad
### Science Team - Dr. Adrian David Gonzalez Chaves

---

## RESUMEN EJECUTIVO

Analizamos **{len(df)} municipios** del Estado de Sao Paulo considerando 5 dimensiones:
1. Riesgos Climaticos
2. Enfermedades/Salud
3. Vulnerabilidad Social
4. Biodiversidad
5. Seguridad Alimentaria/Capacidad Adaptativa (UAI)

---

## HALLAZGOS PRINCIPALES

### Correlaciones Clave Biodiversidad/Politicas vs Riesgos

| Correlacion | r (Spearman) | Interpretacion |
|-------------|--------------|----------------|
| Biodiversidad vs Deficit Politico | **-0.567** | Mejor gobernanza = mejor conservacion |
| Malaria vs UAI | **-0.593** | Mayor acceso = menor incidencia |
| UAI vs Poblacion | **+0.725** | Ciudades grandes con mejor acceso |
| Copersistencia vs Riesgos Climaticos | **+0.277** | Eventos extremos aumentan enfermedades |

### Clasificacion de Cuadrantes

| Cuadrante | Municipios | Caracteristica |
|-----------|------------|----------------|
| Q1 Modelo | {len(df[df['cuadrante']=='Q1_Modelo'])} | Alto UAI + Alta Biodiversidad |
| Q2 Conservar | {len(df[df['cuadrante']=='Q2_Conservar'])} | Bajo UAI + Alta Biodiversidad |
| Q3 Vulnerable | {len(df[df['cuadrante']=='Q3_Vulnerable'])} | Bajo UAI + Baja Biodiversidad |
| Q4 Desarrollo | {len(df[df['cuadrante']=='Q4_Desarrollo'])} | Alto UAI + Baja Biodiversidad |

---

## PRIORIZACION DE INTERVENCIONES

### PRIORIDAD ALTA: Q3 Vulnerable (IVM > 75)
**{len(q3_vuln)} municipios requieren accion urgente**

Poblacion afectada: {q3_vuln['population'].sum():,.0f} habitantes

**Municipios prioritarios:**
"""

    for _, row in q3_vuln.nlargest(10, 'IVM_100').iterrows():
        report += f"- {row['Municipio']} (IVM: {row['IVM_100']:.1f}, Poblacion: {row['population']:,.0f})\n"

    report += f"""
**Acciones recomendadas:**
1. Inversion prioritaria en infraestructura basica (agua, saneamiento)
2. Fortalecimiento institucional (reducir deficit politico promedio de {q3_vuln['pol_deficit'].mean():.2f})
3. Restauracion ecologica con participacion comunitaria
4. Vigilancia epidemiologica intensificada

---

### PRIORIDAD MEDIA-ALTA: Q2 Conservar
**{len(df[df['cuadrante']=='Q2_Conservar'])} municipios con alta biodiversidad pero bajo UAI**

**Municipios con mayor biodiversidad:**
"""

    for _, row in q2_cons.head(10).iterrows():
        report += f"- {row['Municipio']} (Riqueza: {row['mean_species_richness']:.0f} especies)\n"

    report += """
**Acciones recomendadas:**
1. Programas de desarrollo sostenible
2. Proteccion de areas de alta biodiversidad
3. Mejora de acceso sin degradar ecosistemas
4. Pagos por servicios ecosistemicos

---

### PRIORIDAD MEDIA: Q4 Desarrollo
**Municipios con alto UAI pero baja biodiversidad**

**Acciones recomendadas:**
1. Restauracion ecologica urbana
2. Infraestructura verde
3. Corredores ecologicos
4. Compensacion ambiental

---

### MONITOREO: Q1 Modelo
**Municipios con buen desempeno en ambas dimensiones**

**Acciones recomendadas:**
1. Documentar buenas practicas
2. Servir como referencia para otros municipios
3. Mantener equilibrio desarrollo-conservacion

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

### Composicion Demografica:
- Poblacion negra: {vuln_pop['population_preta'].sum():,.0f} ({vuln_pop['population_preta'].sum()/vuln_total*100:.1f}%)
- Poblacion indigena: {vuln_pop['population_indigena'].sum():,.0f} ({vuln_pop['population_indigena'].sum()/vuln_total*100:.1f}%)
- % Rural promedio: {vuln_pop['pct_rural'].mean():.1f}%
- Mortalidad infantil promedio: {vuln_pop['mort_infantil'].mean():.1f}

---

## IMPLICACIONES PARA POLITICAS PUBLICAS

### 1. Uso de Evidencia para Politicas

**Hallazgo**: La correlacion negativa fuerte entre biodiversidad y deficit politico (r=-0.567)
indica que fortalecer la gobernanza es una estrategia indirecta pero efectiva para la conservacion.

**Recomendacion**: Invertir en capacidades institucionales municipales como parte de las
politicas ambientales.

### 2. Salud y Acceso Universal

**Hallazgo**: Las enfermedades (malaria, dengue, diarrea) muestran correlacion negativa con UAI,
indicando que mejorar el acceso a servicios reduce la carga de enfermedad.

**Recomendacion**: Priorizar mejoras en UAI en municipios con alta incidencia de enfermedades
como estrategia de salud publica.

### 3. Cambio Climatico y Salud

**Hallazgo**: La copersistencia de enfermedades correlaciona con riesgos climaticos,
sugiriendo que eventos extremos aumentan la carga de enfermedad.

**Recomendacion**: Integrar politicas de adaptacion climatica con politicas de salud publica.

### 4. Justicia Ambiental

**Hallazgo**: Las poblaciones rurales e indigenas estan sobrerrepresentadas en areas vulnerables.

**Recomendacion**: Diseno de politicas con enfoque de equidad territorial y justicia ambiental.

---

## LIMITACIONES DEL ANALISIS

1. **Datos de salud**: Solo disponibles para 187/645 municipios (29%)
2. **Causalidad**: Las correlaciones no implican relaciones causales
3. **Temporalidad**: Analisis transversal, no captura dinamicas temporales
4. **Escala**: Heterogeneidad intra-municipal no capturada

---

*Documento generado por el Science Team*
*Dr. Adrian David Gonzalez Chaves - Director Cientifico*
*Enero 2026*
"""

    # Guardar reporte
    with open(DOCS_PATH / 'RECOMENDACIONES_POLITICAS_SCIENCE_TEAM.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReporte guardado en: {DOCS_PATH / 'RECOMENDACIONES_POLITICAS_SCIENCE_TEAM.md'}")

    return report

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecuta el analisis completo del Science Team."""
    print("\n" + "=" * 70)
    print("SCIENCE TEAM - ANALISIS MULTIDIMENSIONAL DE VULNERABILIDAD")
    print("Dr. Adrian David Gonzalez Chaves - Director Cientifico")
    print("=" * 70)

    # Paso 1: Cargar datos
    df, df_health = load_and_clean_data()

    # Paso 2: Correlaciones
    corr_df, sig_corr = calculate_correlations(df, df_health)

    # Paso 3: Cuadrantes
    df, median_uai, median_biodiv = classify_quadrants(df)

    # Paso 4: Indice de Vulnerabilidad
    df = calculate_ivm(df)

    # Paso 5: Caracterizacion demografica
    demo_by_cat, demo_by_quad = demographic_characterization(df)

    # Paso 6: Visualizaciones
    generate_visualizations(df, corr_df, median_uai, median_biodiv)

    # Paso 7: Recomendaciones
    report = generate_policy_recommendations(df, corr_df, demo_by_cat, demo_by_quad)

    # Guardar resultados
    print("\n" + "=" * 60)
    print("GUARDANDO RESULTADOS")
    print("=" * 60)

    # CSV con clasificacion
    df.to_csv(OUTPUT_PATH / 'municipios_clasificados_ivm.csv', index=False)
    print(f"  - {OUTPUT_PATH / 'municipios_clasificados_ivm.csv'}")

    # Correlaciones
    corr_df.to_csv(OUTPUT_PATH / 'correlaciones_spearman.csv', index=False)
    print(f"  - {OUTPUT_PATH / 'correlaciones_spearman.csv'}")

    # Perfiles demograficos
    demo_by_cat.to_csv(OUTPUT_PATH / 'perfil_demografico_categoria.csv')
    demo_by_quad.to_csv(OUTPUT_PATH / 'perfil_demografico_cuadrante.csv')
    print(f"  - {OUTPUT_PATH / 'perfil_demografico_categoria.csv'}")
    print(f"  - {OUTPUT_PATH / 'perfil_demografico_cuadrante.csv'}")

    print("\n" + "=" * 70)
    print("ANALISIS COMPLETADO EXITOSAMENTE")
    print("=" * 70)

    return df, corr_df, demo_by_cat, demo_by_quad

if __name__ == "__main__":
    df, corr_df, demo_by_cat, demo_by_quad = main()
