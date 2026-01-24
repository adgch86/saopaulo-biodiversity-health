# =============================================================================
# Análisis del Nexus Gobernanza - Biodiversidad - Bienestar Humano
# Versión 1.0 - Análisis completo con modelos mixtos
# =============================================================================
#
# Hipótesis principales:
# H1: Mayor gobernanza (UAI) -> Menores riesgos ambientales
#     (especialmente en municipios con menor vulnerabilidad social)
# H2: Mayor biodiversidad -> Menores riesgos ambientales
#     (especialmente en municipios con menor vulnerabilidad social)
#
# Autor: Science Team
# Fecha: 2026-01-23
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Estadísticas
from scipy import stats
from scipy.stats import spearmanr, pearsonr
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Visualización
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
OUTPUTS = PROJECT_ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
FIGURES.mkdir(exist_ok=True)

# Configuración de matplotlib
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# =============================================================================
# DEFINICIÓN DE CATEGORÍAS DE VARIABLES
# =============================================================================

VARS_GOBERNANZA = {
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentación',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Climático',
    'idx_gobernanza': 'Indice Gobernanza (UAI promedio)'
}

VARS_BIODIVERSIDAD = {
    'mean_species_richness': 'Riqueza spp media',
    'max_species_richness': 'Riqueza spp máxima',
    'forest_cover': 'Cobertura forestal (%)',
    'pol_deficit': 'Déficit polinizacion',
    'idx_biodiv': 'Indice Biodiversidad'
}

VARS_RIESGO_CLIMA = {
    'flooding_exposure': 'Exposición inundaciones',
    'flooding_risks': 'Riesgo inundaciones',
    'hydric_stress_exp': 'Exposición estrés hídrico',
    'hydric_stress_risk': 'Riesgo estrés hídrico',
    'fire_risk_index': 'Indice riesgo fuego',
    'fire_incidence_mean': 'Incidencia fuego media',
    'idx_clima': 'Indice Riesgo Climático'
}

VARS_RIESGO_SALUD = {
    'incidence_mean_dengue': 'Incidencia dengue',
    'incidence_mean_leishmaniose': 'Incidencia leishmaniasis',
    'incidence_mean_leptospirose': 'Incidencia leptospirosis',
    'incidence_mean_malaria': 'Incidencia malaria',
    'incidence_diarrhea_mean': 'Incidencia diarrea',
    'persist_dengue': 'Persistencia dengue',
    'persist_leptospirose': 'Persistencia leptospirosis',
    'persist_diarrhea': 'Persistencia diarrea',
    'copresence_years': 'Co-presencia enfermedades',
    'idx_carga_enfermedad': 'Indice carga enfermedad',
    'health_hosp_heat_mean': 'Hospitalización calor',
    'health_death_heat_mean': 'Mortalidad calor'
}

VARS_RIESGO_NUTRICION = {
    'pol_deficit': 'Déficit polinizacion'
}

VARS_VULN_SOCIOECONOMICA = {
    'pct_rural': '% Poblacion rural',
    'pct_preta': '% Poblacion negra',
    'pct_indigena': '% Poblacion indígena',
    'pct_pobreza': '% Pobreza',
    'n_pessoas_pobreza': 'N personas pobreza',
    'mort_infantil': 'Mortalidad infantil',
    'idx_vulnerabilidad': 'Indice Vulnerabilidad'
}

# Variables compuestas de riesgo ambiental
VARS_RIESGO_AMBIENTAL = {
    **VARS_RIESGO_CLIMA,
    **VARS_RIESGO_SALUD
}


def load_data():
    """Carga el dataset integrado v8."""
    df = pd.read_csv(OUTPUTS / "municipios_integrado_v8.csv")
    df['cod_ibge'] = df['cod_ibge'].astype(str)

    # Crear indice compuesto de vulnerabilidad socioeconómica
    vuln_cols = ['pct_rural', 'pct_preta', 'pct_indigena', 'pct_pobreza', 'mort_infantil']
    for col in vuln_cols:
        if col in df.columns:
            df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    norm_cols = [f'{col}_norm' for col in vuln_cols if f'{col}_norm' in df.columns]
    if norm_cols:
        df['idx_vuln_socioeconomica'] = df[norm_cols].mean(axis=1)

    print(f"Dataset cargado: {len(df)} municipios, {len(df.columns)} variables")
    return df


def calcular_correlaciones_completas(df):
    """Calcula matriz de correlaciones entre todas las categorias."""
    print("\n" + "=" * 70)
    print("1. MATRIZ DE CORRELACIONES COMPLETA")
    print("=" * 70)

    # Seleccionar variables para correlación
    all_vars = {}
    all_vars.update(VARS_GOBERNANZA)
    all_vars.update(VARS_BIODIVERSIDAD)
    all_vars.update(VARS_RIESGO_CLIMA)
    all_vars.update(VARS_RIESGO_SALUD)
    all_vars.update(VARS_VULN_SOCIOECONOMICA)

    # Filtrar solo variables que existen
    existing_vars = [v for v in all_vars.keys() if v in df.columns]

    # Calcular correlaciones
    corr_matrix = df[existing_vars].corr(method='spearman')

    # Guardar matriz completa
    corr_matrix.to_csv(OUTPUTS / "correlaciones_nexus_completas.csv")

    # Visualizar heatmap
    fig, ax = plt.subplots(figsize=(20, 16))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                square=True, linewidths=0.5, ax=ax,
                annot_kws={'size': 6})
    plt.title('Correlaciones Spearman - Nexus Gobernanza-Biodiversidad-Riesgos', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES / "heatmap_correlaciones_nexus.png", dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Matriz de correlaciones guardada: {len(existing_vars)} variables")

    return corr_matrix


def tabla_seleccion_predictores(df):
    """Genera tabla de selección de mejores predictores por categoria."""
    print("\n" + "=" * 70)
    print("2. SELECCIÓN DE MEJORES PREDICTORES POR CATEGORÍA")
    print("=" * 70)

    results = []

    # Para cada variable de riesgo, encontrar mejor predictor de gobernanza y biodiversidad
    risk_vars = list(VARS_RIESGO_CLIMA.keys()) + list(VARS_RIESGO_SALUD.keys())
    risk_vars = [v for v in risk_vars if v in df.columns]

    for risk_var in risk_vars:
        row = {'variable_riesgo': risk_var}

        # Mejor predictor de gobernanza
        best_gob_r = 0
        best_gob_var = None
        for gob_var in VARS_GOBERNANZA.keys():
            if gob_var in df.columns:
                valid = df[[risk_var, gob_var]].dropna()
                if len(valid) > 10:
                    r, p = spearmanr(valid[risk_var], valid[gob_var])
                    if abs(r) > abs(best_gob_r):
                        best_gob_r = r
                        best_gob_var = gob_var
        row['mejor_gobernanza'] = best_gob_var
        row['r_gobernanza'] = best_gob_r

        # Mejor predictor de biodiversidad
        best_bio_r = 0
        best_bio_var = None
        for bio_var in VARS_BIODIVERSIDAD.keys():
            if bio_var in df.columns:
                valid = df[[risk_var, bio_var]].dropna()
                if len(valid) > 10:
                    r, p = spearmanr(valid[risk_var], valid[bio_var])
                    if abs(r) > abs(best_bio_r):
                        best_bio_r = r
                        best_bio_var = bio_var
        row['mejor_biodiversidad'] = best_bio_var
        row['r_biodiversidad'] = best_bio_r

        # Mejor modulador socioeconómico
        best_mod_r = 0
        best_mod_var = None
        for mod_var in VARS_VULN_SOCIOECONOMICA.keys():
            if mod_var in df.columns:
                valid = df[[risk_var, mod_var]].dropna()
                if len(valid) > 10:
                    r, p = spearmanr(valid[risk_var], valid[mod_var])
                    if abs(r) > abs(best_mod_r):
                        best_mod_r = r
                        best_mod_var = mod_var
        row['mejor_modulador'] = best_mod_var
        row['r_modulador'] = best_mod_r

        results.append(row)

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUTS / "seleccion_predictores_nexus.csv", index=False)

    # Imprimir resumen
    print("\nMejores predictores para cada variable de riesgo:")
    print("-" * 100)
    print(f"{'Variable Riesgo':<35} {'Mejor Gob':<15} {'r':<8} {'Mejor Biodiv':<20} {'r':<8} {'Mejor Mod':<15} {'r':<8}")
    print("-" * 100)
    for _, row in results_df.iterrows():
        print(f"{row['variable_riesgo']:<35} {str(row['mejor_gobernanza']):<15} {row['r_gobernanza']:>7.3f} "
              f"{str(row['mejor_biodiversidad']):<20} {row['r_biodiversidad']:>7.3f} "
              f"{str(row['mejor_modulador']):<15} {row['r_modulador']:>7.3f}")

    return results_df


def analisis_modelos_mixtos(df):
    """Implementa modelos mixtos con mesorregion como efecto aleatorio."""
    print("\n" + "=" * 70)
    print("3. MODELOS MIXTOS JERÁRQUICOS")
    print("=" * 70)
    print("(Efecto aleatorio: mesorregion)")

    results = []

    # Variables dependientes principales (riesgos)
    y_vars = ['idx_carga_enfermedad', 'idx_clima', 'incidence_mean_dengue',
              'incidence_diarrhea_mean', 'fire_risk_index']

    # Variables independientes
    x_gob = ['idx_gobernanza', 'UAI_env', 'UAI_Crisk']
    x_bio = ['idx_biodiv', 'forest_cover', 'mean_species_richness']

    for y_var in y_vars:
        if y_var not in df.columns:
            continue

        for x_var in x_gob + x_bio:
            if x_var not in df.columns:
                continue

            # Preparar datos
            model_df = df[['cod_mesorregiao', y_var, x_var, 'idx_vulnerabilidad']].dropna()
            if len(model_df) < 50:
                continue

            # Estandarizar variables
            for col in [y_var, x_var, 'idx_vulnerabilidad']:
                model_df[f'{col}_z'] = (model_df[col] - model_df[col].mean()) / model_df[col].std()

            try:
                # Modelo mixto
                formula = f"{y_var}_z ~ {x_var}_z + idx_vulnerabilidad_z + {x_var}_z:idx_vulnerabilidad_z"
                model = smf.mixedlm(formula, model_df, groups=model_df['cod_mesorregiao'])
                result = model.fit(method='powell', maxiter=500)

                # Extraer coeficientes
                row = {
                    'y_variable': y_var,
                    'x_variable': x_var,
                    'tipo_x': 'gobernanza' if x_var in x_gob else 'biodiversidad',
                    'n_obs': len(model_df),
                    'n_grupos': model_df['cod_mesorregiao'].nunique(),
                    'coef_x': result.params.get(f'{x_var}_z', np.nan),
                    'pvalue_x': result.pvalues.get(f'{x_var}_z', np.nan),
                    'coef_vuln': result.params.get('idx_vulnerabilidad_z', np.nan),
                    'pvalue_vuln': result.pvalues.get('idx_vulnerabilidad_z', np.nan),
                    'coef_interaccion': result.params.get(f'{x_var}_z:idx_vulnerabilidad_z', np.nan),
                    'pvalue_interaccion': result.pvalues.get(f'{x_var}_z:idx_vulnerabilidad_z', np.nan),
                    'var_grupo': result.cov_re.iloc[0,0] if hasattr(result, 'cov_re') else np.nan,
                    'aic': result.aic if hasattr(result, 'aic') else np.nan
                }
                results.append(row)

            except Exception as e:
                print(f"  Error en modelo {y_var} ~ {x_var}: {str(e)[:50]}")
                continue

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUTS / "modelos_mixtos_nexus.csv", index=False)

    # Resumen de modelos significativos
    print("\n--- Modelos con efectos significativos (p < 0.05) ---")
    sig = results_df[results_df['pvalue_x'] < 0.05].sort_values('pvalue_x')

    if len(sig) > 0:
        print(f"\n{'Y Variable':<25} {'X Variable':<20} {'Tipo':<12} {'Coef':<8} {'p-value':<10} {'Interacción p':<12}")
        print("-" * 95)
        for _, row in sig.head(20).iterrows():
            interp = f"{row['pvalue_interaccion']:.4f}" if not pd.isna(row['pvalue_interaccion']) else "N/A"
            print(f"{row['y_variable']:<25} {row['x_variable']:<20} {row['tipo_x']:<12} "
                  f"{row['coef_x']:>7.3f} {row['pvalue_x']:>9.4f} {interp:>12}")

    return results_df


def analisis_moduladores(df):
    """Analiza el efecto modulador de cada variable socioeconómica."""
    print("\n" + "=" * 70)
    print("4. ANÁLISIS DE EFECTOS MODULADORES")
    print("=" * 70)

    results = []

    # Relaciones principales a analizar
    relaciones = [
        ('idx_carga_enfermedad', 'idx_biodiv', 'Biodiv->Enfermedades'),
        ('idx_carga_enfermedad', 'idx_gobernanza', 'Gobernanza->Enfermedades'),
        ('idx_clima', 'forest_cover', 'Cobertura forestal->Clima'),
        ('idx_clima', 'idx_gobernanza', 'Gobernanza->Clima'),
        ('fire_risk_index', 'idx_biodiv', 'Biodiv->Fuego'),
        ('incidence_diarrhea_mean', 'flooding_risks', 'Inundacion->Diarrea'),
    ]

    for y_var, x_var, relacion in relaciones:
        if y_var not in df.columns or x_var not in df.columns:
            continue

        print(f"\n--- {relacion} ---")

        for mod_var, mod_name in VARS_VULN_SOCIOECONOMICA.items():
            if mod_var not in df.columns:
                continue

            # Dividir por terciles del modulador
            df['mod_tercil'] = pd.qcut(df[mod_var].rank(method='first'), 3,
                                       labels=['Bajo', 'Medio', 'Alto'])

            corrs = {}
            for tercil in ['Bajo', 'Medio', 'Alto']:
                subset = df[df['mod_tercil'] == tercil][[y_var, x_var]].dropna()
                if len(subset) > 20:
                    r, p = spearmanr(subset[y_var], subset[x_var])
                    corrs[tercil] = {'r': r, 'p': p, 'n': len(subset)}

            if len(corrs) == 3:
                # Calcular diferencia entre bajo y alto
                diff_r = corrs['Alto']['r'] - corrs['Bajo']['r']

                results.append({
                    'relacion': relacion,
                    'y_var': y_var,
                    'x_var': x_var,
                    'modulador': mod_var,
                    'modulador_nombre': mod_name,
                    'r_bajo': corrs['Bajo']['r'],
                    'r_medio': corrs['Medio']['r'],
                    'r_alto': corrs['Alto']['r'],
                    'diff_alto_bajo': diff_r,
                    'efecto_modulador': 'Amplifica' if diff_r > 0.1 else ('Atenúa' if diff_r < -0.1 else 'Neutro')
                })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUTS / "efectos_moduladores_nexus.csv", index=False)

    # Resumen
    print("\nEfectos moduladores más fuertes:")
    print("-" * 100)
    top_mod = results_df.reindex(results_df['diff_alto_bajo'].abs().sort_values(ascending=False).index).head(15)
    print(f"{'Relación':<30} {'Modulador':<20} {'r(Bajo)':<10} {'r(Alto)':<10} {'Diff':<10} {'Efecto':<12}")
    print("-" * 100)
    for _, row in top_mod.iterrows():
        print(f"{row['relacion']:<30} {row['modulador_nombre']:<20} {row['r_bajo']:>9.3f} "
              f"{row['r_alto']:>9.3f} {row['diff_alto_bajo']:>9.3f} {row['efecto_modulador']:<12}")

    return results_df


def graficar_hipotesis(df, predictores_df):
    """Genera gráficos de regresión para H1 y H2."""
    print("\n" + "=" * 70)
    print("5. VISUALIZACIÓN DE HIPÓTESIS H1 Y H2")
    print("=" * 70)

    # H1: Gobernanza -> Riesgos (modulado por vulnerabilidad)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Crear terciles de vulnerabilidad para colorear
    df['vuln_tercil'] = pd.qcut(df['idx_vulnerabilidad'].rank(method='first'), 3,
                                labels=['Baja vuln', 'Media vuln', 'Alta vuln'])
    colors = {'Baja vuln': '#2ecc71', 'Media vuln': '#f39c12', 'Alta vuln': '#e74c3c'}

    # H1: Gobernanza vs diferentes riesgos
    h1_plots = [
        ('idx_gobernanza', 'idx_carga_enfermedad', 'Gobernanza vs Carga Enfermedad'),
        ('idx_gobernanza', 'idx_clima', 'Gobernanza vs Riesgo Climático'),
        ('idx_gobernanza', 'fire_risk_index', 'Gobernanza vs Riesgo Fuego'),
    ]

    for i, (x, y, title) in enumerate(h1_plots):
        ax = axes[0, i]
        for tercil, color in colors.items():
            subset = df[df['vuln_tercil'] == tercil]
            ax.scatter(subset[x], subset[y], c=color, alpha=0.5, label=tercil, s=20)
            # Línea de tendencia
            valid = subset[[x, y]].dropna()
            if len(valid) > 10:
                z = np.polyfit(valid[x], valid[y], 1)
                p = np.poly1d(z)
                x_line = np.linspace(valid[x].min(), valid[x].max(), 100)
                ax.plot(x_line, p(x_line), c=color, linestyle='--', alpha=0.8)
        ax.set_xlabel('Indice Gobernanza (UAI)')
        ax.set_ylabel(y.replace('_', ' ').title())
        ax.set_title(f'H1: {title}')
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)

    # H2: Biodiversidad vs diferentes riesgos
    h2_plots = [
        ('idx_biodiv', 'idx_carga_enfermedad', 'Biodiversidad vs Carga Enfermedad'),
        ('forest_cover', 'idx_clima', 'Cobertura Forestal vs Riesgo Climático'),
        ('mean_species_richness', 'fire_risk_index', 'Riqueza Especies vs Riesgo Fuego'),
    ]

    for i, (x, y, title) in enumerate(h2_plots):
        ax = axes[1, i]
        for tercil, color in colors.items():
            subset = df[df['vuln_tercil'] == tercil]
            ax.scatter(subset[x], subset[y], c=color, alpha=0.5, label=tercil, s=20)
            valid = subset[[x, y]].dropna()
            if len(valid) > 10:
                z = np.polyfit(valid[x], valid[y], 1)
                p = np.poly1d(z)
                x_line = np.linspace(valid[x].min(), valid[x].max(), 100)
                ax.plot(x_line, p(x_line), c=color, linestyle='--', alpha=0.8)
        ax.set_xlabel(x.replace('_', ' ').title())
        ax.set_ylabel(y.replace('_', ' ').title())
        ax.set_title(f'H2: {title}')

    plt.suptitle('Hipótesis: Efecto de Gobernanza (H1) y Biodiversidad (H2) sobre Riesgos\n'
                 'Modulado por Vulnerabilidad Socioeconómica', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES / "hipotesis_h1_h2_nexus.png", dpi=150, bbox_inches='tight')
    plt.close()

    print("Gráficos de hipótesis guardados.")


def ranking_municipios_riesgo(df):
    """Genera ranking de municipios por riesgo y vulnerabilidad."""
    print("\n" + "=" * 70)
    print("6. RANKING DE MUNICIPIOS POR RIESGO Y VULNERABILIDAD")
    print("=" * 70)

    # Crear indice compuesto de riesgo ambiental
    risk_cols = ['idx_clima', 'idx_carga_enfermedad', 'fire_risk_index']
    risk_cols = [c for c in risk_cols if c in df.columns]

    for col in risk_cols:
        df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    norm_cols = [f'{col}_norm' for col in risk_cols]
    df['idx_riesgo_total'] = df[norm_cols].mean(axis=1)

    # Ranking por riesgo total
    df['rank_riesgo'] = df['idx_riesgo_total'].rank(ascending=False)
    df['rank_vulnerabilidad'] = df['idx_vulnerabilidad'].rank(ascending=False)

    # Combinar: municipios con alto riesgo Y alta vulnerabilidad
    df['prioridad_intervencion'] = (df['rank_riesgo'] + df['rank_vulnerabilidad']) / 2
    df['rank_prioridad'] = df['prioridad_intervencion'].rank(ascending=True)

    # Top 50 municipios prioritarios
    ranking = df.nsmallest(50, 'rank_prioridad')[
        ['cod_ibge', 'Municipio', 'nome_mesorregiao', 'cuadrante',
         'idx_riesgo_total', 'idx_vulnerabilidad', 'idx_gobernanza',
         'idx_biodiv', 'rank_riesgo', 'rank_vulnerabilidad', 'rank_prioridad']
    ].copy()

    ranking.to_csv(OUTPUTS / "ranking_municipios_prioritarios.csv", index=False)

    print("\nTop 20 Municipios Prioritarios (Mayor Riesgo + Mayor Vulnerabilidad):")
    print("-" * 100)
    print(f"{'Rank':<6} {'Municipio':<25} {'Mesorregión':<20} {'Riesgo':<10} {'Vuln':<10} {'Gob':<8} {'Biodiv':<8} {'Cuadrante':<15}")
    print("-" * 100)
    for i, (_, row) in enumerate(ranking.head(20).iterrows(), 1):
        print(f"{i:<6} {row['Municipio'][:24]:<25} {str(row['nome_mesorregiao'])[:19]:<20} "
              f"{row['idx_riesgo_total']:>9.3f} {row['idx_vulnerabilidad']:>9.3f} "
              f"{row['idx_gobernanza']:>7.3f} {row['idx_biodiv']:>7.3f} {row['cuadrante']:<15}")

    # Estadísticas por cuadrante
    print("\n--- Riesgo promedio por cuadrante ---")
    cuad_stats = df.groupby('cuadrante').agg({
        'idx_riesgo_total': 'mean',
        'idx_vulnerabilidad': 'mean',
        'idx_gobernanza': 'mean',
        'idx_biodiv': 'mean',
        'cod_ibge': 'count'
    }).round(3)
    cuad_stats.columns = ['Riesgo', 'Vulnerabilidad', 'Gobernanza', 'Biodiversidad', 'N']
    print(cuad_stats)

    return ranking


def analisis_cuadrantes(df):
    """Análisis detallado por cuadrantes UAI-Biodiversidad."""
    print("\n" + "=" * 70)
    print("7. ANÁLISIS DE CUADRANTES")
    print("=" * 70)

    # Crear figura con múltiples paneles
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    cuadrantes = df['cuadrante'].unique()
    colors_cuad = {
        'Q1_Modelo': '#27ae60',
        'Q2_Conservar': '#3498db',
        'Q3_Vulnerable': '#e74c3c',
        'Q4_Desarrollo': '#f39c12'
    }

    # Panel 1: Gobernanza vs Biodiversidad coloreado por cuadrante
    ax = axes[0, 0]
    for cuad in cuadrantes:
        if pd.isna(cuad):
            continue
        subset = df[df['cuadrante'] == cuad]
        color = colors_cuad.get(cuad, 'gray')
        ax.scatter(subset['idx_gobernanza'], subset['idx_biodiv'],
                  c=color, alpha=0.6, label=cuad, s=30)
    ax.axvline(df['idx_gobernanza'].median(), color='gray', linestyle='--', alpha=0.5)
    ax.axhline(df['idx_biodiv'].median(), color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Indice Gobernanza (UAI)')
    ax.set_ylabel('Indice Biodiversidad')
    ax.set_title('Distribución de Cuadrantes')
    ax.legend(loc='upper left', fontsize=8)

    # Panel 2: Boxplot de riesgo total por cuadrante
    ax = axes[0, 1]
    cuad_order = ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']
    cuad_order = [c for c in cuad_order if c in df['cuadrante'].values]

    df_plot = df[df['cuadrante'].isin(cuad_order)]
    box_data = [df_plot[df_plot['cuadrante'] == c]['idx_riesgo_total'].dropna() for c in cuad_order]
    bp = ax.boxplot(box_data, labels=cuad_order, patch_artist=True)
    for patch, cuad in zip(bp['boxes'], cuad_order):
        patch.set_facecolor(colors_cuad.get(cuad, 'gray'))
        patch.set_alpha(0.6)
    ax.set_ylabel('Indice Riesgo Total')
    ax.set_title('Distribución de Riesgo por Cuadrante')
    ax.tick_params(axis='x', rotation=15)

    # Panel 3: Riesgo vs Gobernanza por cuadrante
    ax = axes[1, 0]
    for cuad in cuadrantes:
        if pd.isna(cuad):
            continue
        subset = df[df['cuadrante'] == cuad]
        color = colors_cuad.get(cuad, 'gray')
        ax.scatter(subset['idx_gobernanza'], subset['idx_riesgo_total'],
                  c=color, alpha=0.6, label=cuad, s=30)
    ax.set_xlabel('Indice Gobernanza (UAI)')
    ax.set_ylabel('Indice Riesgo Total')
    ax.set_title('Relación Gobernanza-Riesgo por Cuadrante')

    # Panel 4: Riesgo vs Biodiversidad por cuadrante
    ax = axes[1, 1]
    for cuad in cuadrantes:
        if pd.isna(cuad):
            continue
        subset = df[df['cuadrante'] == cuad]
        color = colors_cuad.get(cuad, 'gray')
        ax.scatter(subset['idx_biodiv'], subset['idx_riesgo_total'],
                  c=color, alpha=0.6, label=cuad, s=30)
    ax.set_xlabel('Indice Biodiversidad')
    ax.set_ylabel('Indice Riesgo Total')
    ax.set_title('Relación Biodiversidad-Riesgo por Cuadrante')

    plt.suptitle('Análisis de Cuadrantes: Gobernanza × Biodiversidad', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES / "analisis_cuadrantes_nexus.png", dpi=150, bbox_inches='tight')
    plt.close()

    # Correlaciones por cuadrante
    print("\n--- Correlaciones clave por cuadrante ---")
    print(f"{'Cuadrante':<20} {'Gob->Riesgo':<15} {'Biodiv->Riesgo':<15} {'Gob->Biodiv':<15}")
    print("-" * 65)

    for cuad in cuad_order:
        subset = df[df['cuadrante'] == cuad]
        r1, _ = spearmanr(subset['idx_gobernanza'].dropna(), subset['idx_riesgo_total'].dropna())
        r2, _ = spearmanr(subset['idx_biodiv'].dropna(), subset['idx_riesgo_total'].dropna())
        r3, _ = spearmanr(subset['idx_gobernanza'].dropna(), subset['idx_biodiv'].dropna())
        print(f"{cuad:<20} {r1:>14.3f} {r2:>14.3f} {r3:>14.3f}")

    print("\nGráficos de cuadrantes guardados.")


def revisar_pearc_acciones(df):
    """Revisa acciones del PEARC aplicables a diferentes escenarios."""
    print("\n" + "=" * 70)
    print("8. ACCIONES PRIORITARIAS PEARC POR ESCENARIO")
    print("=" * 70)

    # Acciones del PEARC clasificadas por tipo de riesgo
    acciones_pearc = {
        'riesgo_climatico': [
            "Implementar sistemas de alerta temprana para eventos extremos",
            "Desarrollar infraestructura verde urbana para reducción de calor",
            "Mejorar drenaje urbano y sistemas de contención de inundaciones",
            "Crear corredores ecológicos para regulación hídrica",
            "Promover agricultura adaptada al clima"
        ],
        'riesgo_salud': [
            "Fortalecer vigilancia epidemiológica de enfermedades vectoriales",
            "Implementar programas de control de vectores integrado",
            "Mejorar saneamiento básico y acceso a agua potable",
            "Crear centros de atención para eventos de calor extremo",
            "Capacitar equipos de salud en enfermedades climáticas"
        ],
        'conservacion_biodiversidad': [
            "Expandir y conectar áreas protegidas",
            "Restaurar ecosistemas degradados",
            "Implementar pagos por servicios ambientales",
            "Promover manejo sustentable de paisajes agrícolas",
            "Proteger remanentes de vegetación nativa"
        ],
        'vulnerabilidad_social': [
            "Priorizar comunidades de mayor vulnerabilidad en políticas de adaptación",
            "Desarrollar programas de seguridad alimentaria",
            "Mejorar acceso a servicios básicos en áreas rurales",
            "Fortalecer capacidades locales de respuesta a emergencias",
            "Implementar programas de empleo verde"
        ],
        'gobernanza': [
            "Integrar adaptación climática en planes municipales",
            "Fortalecer capacidad tecnica de gestión ambiental",
            "Crear comités locales de adaptación al cambio climático",
            "Mejorar monitoreo y reporte de indicadores",
            "Promover participación comunitaria en decisiones ambientales"
        ]
    }

    # Asignar acciones prioritarias por cuadrante
    print("\n--- ACCIONES PRIORITARIAS POR CUADRANTE ---\n")

    recomendaciones = {
        'Q1_Modelo': {
            'descripcion': 'Alta gobernanza + Alta biodiversidad',
            'estrategia': 'MANTENER Y EXPANDIR',
            'acciones': [
                "Documentar y replicar buenas prácticas",
                "Mantener esfuerzos de conservación",
                "Servir como referencia para otros municipios",
                acciones_pearc['conservacion_biodiversidad'][2],  # PSA
                acciones_pearc['gobernanza'][4]  # Participación
            ]
        },
        'Q2_Conservar': {
            'descripcion': 'Baja gobernanza + Alta biodiversidad',
            'estrategia': 'FORTALECER GOBERNANZA URGENTE',
            'acciones': [
                acciones_pearc['gobernanza'][0],  # Integrar adaptación
                acciones_pearc['gobernanza'][1],  # Capacidad tecnica
                acciones_pearc['conservacion_biodiversidad'][0],  # Áreas protegidas
                acciones_pearc['conservacion_biodiversidad'][2],  # PSA
                "Prevenir degradación de ecosistemas valiosos"
            ]
        },
        'Q3_Vulnerable': {
            'descripcion': 'Baja gobernanza + Baja biodiversidad',
            'estrategia': 'INTERVENCIÓN INTEGRAL URGENTE',
            'acciones': [
                acciones_pearc['vulnerabilidad_social'][0],  # Priorizar vulnerables
                acciones_pearc['riesgo_salud'][2],  # Saneamiento
                acciones_pearc['gobernanza'][0],  # Integrar adaptación
                acciones_pearc['conservacion_biodiversidad'][1],  # Restauración
                acciones_pearc['riesgo_climatico'][0]  # Alerta temprana
            ]
        },
        'Q4_Desarrollo': {
            'descripcion': 'Alta gobernanza + Baja biodiversidad',
            'estrategia': 'RESTAURACIÓN ECOLÓGICA',
            'acciones': [
                acciones_pearc['conservacion_biodiversidad'][1],  # Restauración
                acciones_pearc['conservacion_biodiversidad'][0],  # Áreas protegidas
                acciones_pearc['riesgo_climatico'][3],  # Corredores
                acciones_pearc['conservacion_biodiversidad'][3],  # Paisajes agrícolas
                "Aprovechar capacidad institucional para restauración"
            ]
        }
    }

    # Contar municipios y estadísticas por cuadrante
    results = []
    for cuad, info in recomendaciones.items():
        subset = df[df['cuadrante'] == cuad]
        n_mun = len(subset)

        if n_mun > 0:
            print(f"{'='*60}")
            print(f"CUADRANTE: {cuad}")
            print(f"Descripcion: {info['descripcion']}")
            print(f"Municipios: {n_mun}")
            print(f"Estrategia: {info['estrategia']}")
            print(f"\nAcciones prioritarias:")
            for i, accion in enumerate(info['acciones'], 1):
                print(f"  {i}. {accion}")

            # Estadísticas del cuadrante
            print(f"\nIndicadores promedio:")
            print(f"  - Riesgo total: {subset['idx_riesgo_total'].mean():.3f}")
            print(f"  - Vulnerabilidad: {subset['idx_vulnerabilidad'].mean():.3f}")
            print(f"  - Gobernanza: {subset['idx_gobernanza'].mean():.3f}")
            print(f"  - Biodiversidad: {subset['idx_biodiv'].mean():.3f}")

            results.append({
                'cuadrante': cuad,
                'descripcion': info['descripcion'],
                'estrategia': info['estrategia'],
                'n_municipios': n_mun,
                'riesgo_promedio': subset['idx_riesgo_total'].mean(),
                'vulnerabilidad_promedio': subset['idx_vulnerabilidad'].mean(),
                'acciones': '; '.join(info['acciones'])
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUTS / "acciones_pearc_por_cuadrante.csv", index=False)

    print(f"\n{'='*60}")
    print("Acciones PEARC guardadas en: acciones_pearc_por_cuadrante.csv")

    return results_df


def generar_resumen_ejecutivo(df, corr_matrix, predictores, modelos, moduladores, ranking):
    """Genera resumen ejecutivo del análisis."""
    print("\n" + "=" * 70)
    print("9. RESUMEN EJECUTIVO")
    print("=" * 70)

    resumen = []

    # Hallazgos principales H1
    print("\n--- HIPÓTESIS H1: Gobernanza -> Reducción de Riesgos ---")
    gob_risk = corr_matrix.loc['idx_gobernanza', ['idx_clima', 'idx_carga_enfermedad', 'fire_risk_index']] if 'idx_gobernanza' in corr_matrix.index else None
    if gob_risk is not None:
        for col, r in gob_risk.items():
            direccion = "REDUCE" if r < 0 else "NO reduce"
            sig = "***" if abs(r) > 0.3 else "**" if abs(r) > 0.2 else "*" if abs(r) > 0.1 else ""
            print(f"  Gobernanza -> {col}: r={r:.3f} {sig} ({direccion} riesgo)")
            resumen.append(f"H1: Gobernanza {direccion.lower()} {col} (r={r:.3f})")

    # Hallazgos principales H2
    print("\n--- HIPÓTESIS H2: Biodiversidad -> Reducción de Riesgos ---")
    bio_risk = corr_matrix.loc['idx_biodiv', ['idx_clima', 'idx_carga_enfermedad', 'fire_risk_index']] if 'idx_biodiv' in corr_matrix.index else None
    if bio_risk is not None:
        for col, r in bio_risk.items():
            direccion = "REDUCE" if r < 0 else "NO reduce"
            sig = "***" if abs(r) > 0.3 else "**" if abs(r) > 0.2 else "*" if abs(r) > 0.1 else ""
            print(f"  Biodiversidad -> {col}: r={r:.3f} {sig} ({direccion} riesgo)")
            resumen.append(f"H2: Biodiversidad {direccion.lower()} {col} (r={r:.3f})")

    # Mejores moduladores
    print("\n--- PRINCIPALES EFECTOS MODULADORES ---")
    if len(moduladores) > 0:
        top_mod = moduladores.nlargest(5, 'diff_alto_bajo')
        for _, row in top_mod.iterrows():
            print(f"  {row['modulador_nombre']}: {row['efecto_modulador']} la relación {row['relacion']}")
            resumen.append(f"Modulador: {row['modulador_nombre']} {row['efecto_modulador'].lower()} {row['relacion']}")

    # Municipios críticos
    print("\n--- MUNICIPIOS DE MAYOR PRIORIDAD ---")
    top5 = ranking.head(5)
    for _, row in top5.iterrows():
        print(f"  {row['Municipio']}: Riesgo={row['idx_riesgo_total']:.3f}, Vuln={row['idx_vulnerabilidad']:.3f}")

    # Guardar resumen
    with open(OUTPUTS / "resumen_ejecutivo_nexus.txt", 'w', encoding='utf-8') as f:
        f.write("RESUMEN EJECUTIVO: ANÁLISIS NEXUS GOBERNANZA-BIODIVERSIDAD-BIENESTAR\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Fecha: {datetime.now()}\n")
        f.write(f"Municipios analizados: {len(df)}\n\n")

        f.write("HALLAZGOS PRINCIPALES:\n")
        for h in resumen:
            f.write(f"  • {h}\n")

        f.write("\n\nMUNICIPIOS PRIORITARIOS:\n")
        for _, row in ranking.head(10).iterrows():
            f.write(f"  {row['Municipio']} ({row['cuadrante']}): "
                   f"Riesgo={row['idx_riesgo_total']:.3f}, Vuln={row['idx_vulnerabilidad']:.3f}\n")

    print("\nResumen ejecutivo guardado.")


def main():
    """Funcion principal del análisis."""
    print("=" * 70)
    print("ANÁLISIS NEXUS: GOBERNANZA - BIODIVERSIDAD - BIENESTAR HUMANO")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # Cargar datos
    df = load_data()

    # 1. Matriz de correlaciones
    corr_matrix = calcular_correlaciones_completas(df)

    # 2. Selección de predictores
    predictores = tabla_seleccion_predictores(df)

    # 3. Modelos mixtos
    modelos = analisis_modelos_mixtos(df)

    # 4. Efectos moduladores
    moduladores = analisis_moduladores(df)

    # 5. Gráficos de hipótesis
    graficar_hipotesis(df, predictores)

    # 6. Ranking de municipios
    ranking = ranking_municipios_riesgo(df)

    # 7. Análisis de cuadrantes
    analisis_cuadrantes(df)

    # 8. Acciones PEARC
    acciones = revisar_pearc_acciones(df)

    # 9. Resumen ejecutivo
    generar_resumen_ejecutivo(df, corr_matrix, predictores, modelos, moduladores, ranking)

    print("\n" + "=" * 70)
    print("ANÁLISIS COMPLETADO")
    print("=" * 70)
    print("\nArchivos generados:")
    print("  - correlaciones_nexus_completas.csv")
    print("  - seleccion_predictores_nexus.csv")
    print("  - modelos_mixtos_nexus.csv")
    print("  - efectos_moduladores_nexus.csv")
    print("  - ranking_municipios_prioritarios.csv")
    print("  - acciones_pearc_por_cuadrante.csv")
    print("  - resumen_ejecutivo_nexus.txt")
    print("\nFiguras:")
    print("  - heatmap_correlaciones_nexus.png")
    print("  - hipotesis_h1_h2_nexus.png")
    print("  - analisis_cuadrantes_nexus.png")

    return df, corr_matrix, predictores, modelos, moduladores, ranking


if __name__ == "__main__":
    results = main()
