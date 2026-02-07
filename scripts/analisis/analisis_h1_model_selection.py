"""
Análisis H1 - Selección de Modelos por AIC
Compara índices compuestos vs variables específicas dentro de cada dimensión
usando modelos mixtos lineales (lmer equivalent) con microrregião como efecto aleatorio.

Solicitud: Dr. Adrian David González Chaves (27/01/2026)
"Prefiero una variable por tipo de enfermedad, no una variable para todas las enfermedades,
a no ser que esté asociada a modelos con mejor ajuste."

Metodología:
- Modelos mixtos (statsmodels MixedLM) con (1|microrregião)
- Comparación por delta AIC (< 2 = equivalente)
- Para cada outcome Y y cada dimensión de predictores, se compara:
  m_composite: Y ~ idx_compuesto + (1|micro)
  m_var1: Y ~ var1 + (1|micro)
  m_var2: Y ~ var2 + (1|micro)
  ...

Además:
- Relaciones gobernanza → TODAS las dimensiones (no solo salud)
- Gráficos de dispersión y mapas bivariados

Autor: Science Team / AP Digital
Fecha: 2026-01-27
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
import os
import json

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# --- DIMENSION DEFINITIONS ---
# Each dimension: composite index vs specific variables

DIMENSIONS = {
    'governance': {
        'composite': 'idx_gobernanza_100',
        'specific': ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk'],
        'label': 'Gobernanza'
    },
    'climate_risk': {
        'composite': 'idx_clima',
        'specific': ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk'],
        'label': 'Riesgo Climático'
    },
    'biodiversity': {
        'composite': 'idx_biodiv',
        'specific': ['forest_cover', 'mean_species_richness', 'pol_deficit'],
        'label': 'Biodiversidad'
    },
    'vulnerability': {
        'composite': 'idx_vulnerabilidad',
        'specific': ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena'],
        'label': 'Vulnerabilidad'
    },
    'health': {
        'composite': 'idx_carga_enfermedad',
        'specific': [
            'incidence_mean_dengue', 'incidence_mean_malaria',
            'incidence_mean_leptospirose', 'incidence_mean_leishmaniose',
            'incidence_diarrhea_mean',
            'health_death_circ_mean', 'health_hosp_resp_mean'
        ],
        'label': 'Carga de Enfermedad'
    }
}

# Additional fire-specific variables for comparison
FIRE_VARS = ['fire_risk_index', 'fire_incidence_mean', 'fire_frp_mean', 'fire_recurrence']
FLOOD_VARS = ['flooding_risks', 'flooding_exposure']

# Labels for display
VAR_LABELS = {
    'idx_gobernanza_100': 'Gobernanza (idx)',
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentación',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Clim.',
    'idx_clima': 'Clima (idx)',
    'flooding_risks': 'Riesgo Inundación',
    'fire_risk_index': 'Riesgo Fuego (idx)',
    'hydric_stress_risk': 'Estrés Hídrico',
    'idx_biodiv': 'Biodiv (idx)',
    'forest_cover': 'Cobertura Forestal',
    'mean_species_richness': 'Riqueza Spp',
    'pol_deficit': 'Déf. Polinización',
    'idx_vulnerabilidad': 'Vulnerab. (idx)',
    'pct_pobreza': '% Pobreza',
    'pct_rural': '% Rural',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indígena',
    'idx_carga_enfermedad': 'Carga Enf. (idx)',
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_diarrhea_mean': 'Diarrea',
    'health_death_circ_mean': 'Mort. Cardiovasc.',
    'health_hosp_resp_mean': 'Hosp. Respiratoria',
    'fire_incidence_mean': 'Incidencia Fuego',
    'fire_frp_mean': 'Potencia Fuego (FRP)',
    'fire_recurrence': 'Recurrencia Fuego',
    'flooding_exposure': 'Exposición Inundación',
}


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load and prepare data"""
    print("\n" + "=" * 70)
    print("CARGANDO DATOS")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    print(f"Dataset: {len(df)} municipios × {len(df.columns)} variables")
    print(f"Microrregiones: {df['cod_microrregiao'].nunique()}")
    print(f"Mesorregiones: {df['cod_mesorregiao'].nunique()}")

    # Standardize variables for comparability
    scaler = StandardScaler()
    df_z = df.copy()
    all_vars = set()
    for dim in DIMENSIONS.values():
        all_vars.add(dim['composite'])
        all_vars.update(dim['specific'])
    all_vars.update(FIRE_VARS + FLOOD_VARS)

    for v in all_vars:
        if v in df.columns:
            vals = df[v].dropna()
            if len(vals) > 0:
                df_z[v + '_z'] = np.nan
                mask = df[v].notna()
                df_z.loc[mask, v + '_z'] = scaler.fit_transform(
                    df.loc[mask, v].values.reshape(-1, 1)).flatten()

    return df, df_z


# ============================================================
# MODEL SELECTION: AIC COMPARISON
# ============================================================

def fit_mixed_model(df, outcome, predictor, group_var='cod_microrregiao'):
    """
    Fit a linear mixed model: outcome ~ predictor + (1|group)
    Returns AIC, BIC, coefficients, p-values, R2 marginal
    Uses ML (not REML) for AIC comparison between models with different fixed effects.
    """
    data = df[[outcome, predictor, group_var]].dropna()
    if len(data) < 50:
        return None

    # Sanitize variable names for formula
    safe_outcome = 'y_var'
    safe_predictor = 'x_var'
    data = data.rename(columns={outcome: safe_outcome, predictor: safe_predictor})

    try:
        model = smf.mixedlm(
            f'{safe_outcome} ~ {safe_predictor}',
            data,
            groups=data[group_var]
        )
        result = model.fit(reml=False, method='powell')

        if not result.converged:
            return None

        # Compute AIC manually (statsmodels MixedLM AIC can be nan)
        k = len(result.params) + 1  # params + random effect variance
        n = len(data)
        aic = -2 * result.llf + 2 * k
        bic = -2 * result.llf + k * np.log(n)
        aicc = aic + (2 * k * (k + 1)) / (n - k - 1)  # corrected AIC

        # Marginal R2 (Nakagawa & Schielzeth 2013 approximation)
        var_fixed = np.var(result.fittedvalues)
        var_random = float(result.cov_re.iloc[0, 0]) if hasattr(result.cov_re, 'iloc') else float(result.cov_re)
        var_resid = result.scale
        r2_marginal = var_fixed / (var_fixed + var_random + var_resid)
        r2_conditional = (var_fixed + var_random) / (var_fixed + var_random + var_resid)

        return {
            'aic': aic,
            'bic': bic,
            'aicc': aicc,
            'llf': result.llf,
            'coef': result.params[safe_predictor],
            'se': result.bse[safe_predictor],
            'p_value': result.pvalues[safe_predictor],
            'r2_marginal': r2_marginal,
            'r2_conditional': r2_conditional,
            'n': n,
            'converged': True
        }
    except Exception as e:
        return None


def compare_models_for_dimension(df, outcome, dimension_key):
    """
    Compare composite vs specific variables for one dimension as predictors of outcome.
    Returns sorted results by AIC with delta AIC.
    """
    dim = DIMENSIONS[dimension_key]
    results = []

    # Fit composite model
    composite_result = fit_mixed_model(df, outcome, dim['composite'])
    if composite_result:
        results.append({
            'variable': dim['composite'],
            'type': 'composite',
            'label': VAR_LABELS.get(dim['composite'], dim['composite']),
            **composite_result
        })

    # Fit each specific variable
    for var in dim['specific']:
        if var not in df.columns:
            continue
        var_result = fit_mixed_model(df, outcome, var)
        if var_result:
            results.append({
                'variable': var,
                'type': 'specific',
                'label': VAR_LABELS.get(var, var),
                **var_result
            })

    if not results:
        return pd.DataFrame()

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('aic')
    results_df['delta_aic'] = results_df['aic'] - results_df['aic'].min()
    results_df['aic_weight'] = np.exp(-0.5 * results_df['delta_aic'])
    results_df['aic_weight'] = results_df['aic_weight'] / results_df['aic_weight'].sum()

    return results_df


def run_full_model_selection(df):
    """
    Run model selection across all dimension × outcome combinations.
    """
    print("\n" + "=" * 70)
    print("SELECCIÓN DE MODELOS: ÍNDICE COMPUESTO vs VARIABLES ESPECÍFICAS")
    print("Criterio: deltaAIC < 2 → modelos equivalentes")
    print("Método: lmer(Y ~ X + (1|microrregião), REML=FALSE)")
    print("=" * 70)

    all_results = []
    selection_summary = []

    # For each outcome dimension...
    for out_dim_key, out_dim in DIMENSIONS.items():
        # Use both composite and specific outcomes
        outcomes = [out_dim['composite']] + out_dim['specific']

        for outcome in outcomes:
            if outcome not in df.columns:
                continue

            # For each predictor dimension (different from outcome dimension)
            for pred_dim_key, pred_dim in DIMENSIONS.items():
                if pred_dim_key == out_dim_key:
                    continue

                results_df = compare_models_for_dimension(df, outcome, pred_dim_key)

                if len(results_df) == 0:
                    continue

                results_df['outcome'] = outcome
                results_df['outcome_label'] = VAR_LABELS.get(outcome, outcome)
                results_df['outcome_dimension'] = out_dim['label']
                results_df['predictor_dimension'] = pred_dim['label']
                all_results.append(results_df)

                # Determine best variable
                best = results_df.iloc[0]
                equivalent = results_df[results_df['delta_aic'] < 2]

                selection_summary.append({
                    'outcome': outcome,
                    'outcome_label': VAR_LABELS.get(outcome, outcome),
                    'outcome_dim': out_dim['label'],
                    'predictor_dim': pred_dim['label'],
                    'best_variable': best['variable'],
                    'best_label': best['label'],
                    'best_type': best['type'],
                    'best_aic': best['aic'],
                    'best_coef': best['coef'],
                    'best_p': best['p_value'],
                    'best_r2m': best['r2_marginal'],
                    'n_equivalent': len(equivalent),
                    'equivalent_vars': ', '.join(equivalent['label'].tolist()),
                    'composite_preferred': best['type'] == 'composite'
                })

    all_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    summary_df = pd.DataFrame(selection_summary)

    return all_df, summary_df


# ============================================================
# FOCUSED ANALYSIS: Each disease as outcome, each dimension as predictor
# ============================================================

def run_disease_focused_selection(df):
    """
    For each specific disease, compare composite vs specific predictors
    within each dimension. This is what Adrian specifically asked for.
    """
    print("\n" + "=" * 70)
    print("SELECCIÓN FOCALIZADA: POR ENFERMEDAD Y DIMENSIÓN")
    print("=" * 70)

    diseases = DIMENSIONS['health']['specific']
    predictor_dims = ['governance', 'climate_risk', 'biodiversity', 'vulnerability']

    all_results = []
    best_per_combo = []

    for disease in diseases:
        disease_label = VAR_LABELS.get(disease, disease)
        print(f"\n{'─' * 50}")
        print(f"  OUTCOME: {disease_label}")
        print(f"{'─' * 50}")

        for dim_key in predictor_dims:
            dim = DIMENSIONS[dim_key]
            results_df = compare_models_for_dimension(df, disease, dim_key)

            if len(results_df) == 0:
                continue

            results_df['outcome'] = disease
            results_df['outcome_label'] = disease_label
            results_df['predictor_dimension'] = dim['label']
            all_results.append(results_df)

            # Print comparison
            best = results_df.iloc[0]
            print(f"\n  {dim['label']}:")
            print(f"  {'Variable':<30} {'AIC':>10} {'ΔAIC':>8} {'β':>10} {'p':>10} {'R²m':>8} {'Peso':>8}")
            print(f"  {'─' * 86}")

            for _, row in results_df.iterrows():
                sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
                marker = ' ◄ BEST' if row['delta_aic'] == 0 else (' ≈ equiv' if row['delta_aic'] < 2 else '')
                print(f"  {row['label']:<30} {row['aic']:>10.1f} {row['delta_aic']:>8.1f} "
                      f"{row['coef']:>10.4f}{sig} {row['p_value']:>9.4f} {row['r2_marginal']:>8.3f} "
                      f"{row['aic_weight']:>7.3f}{marker}")

            equivalent = results_df[results_df['delta_aic'] < 2]
            best_per_combo.append({
                'outcome': disease,
                'outcome_label': disease_label,
                'predictor_dimension': dim['label'],
                'selected_variable': best['variable'],
                'selected_label': best['label'],
                'selected_is_composite': best['type'] == 'composite',
                'aic': best['aic'],
                'coef': best['coef'],
                'p_value': best['p_value'],
                'r2_marginal': best['r2_marginal'],
                'n_equivalent': len(equivalent),
                'all_equivalent': ', '.join(equivalent['label'].tolist())
            })

    all_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    best_df = pd.DataFrame(best_per_combo)

    return all_df, best_df


# ============================================================
# GOVERNANCE → ALL DIMENSIONS
# ============================================================

def analyze_governance_to_all(df):
    """
    Analyze governance effects on ALL dimensions, not just health.
    This addresses Adrian's concern about only focusing on health outcomes.
    """
    print("\n" + "=" * 70)
    print("GOBERNANZA → TODAS LAS DIMENSIONES")
    print("Relaciones desde gobernanza hacia todos los niveles de riesgo")
    print("=" * 70)

    gov_vars = ['idx_gobernanza_100'] + DIMENSIONS['governance']['specific']

    # All outcome variables across dimensions
    target_vars = {
        'Biodiversidad': ['forest_cover', 'mean_species_richness', 'pol_deficit', 'idx_biodiv'],
        'Riesgo Climático': ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk', 'idx_clima',
                             'fire_incidence_mean', 'fire_frp_mean'],
        'Vulnerabilidad': ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena', 'idx_vulnerabilidad'],
        'Salud': DIMENSIONS['health']['specific'] + ['idx_carga_enfermedad'],
    }

    results = []

    for target_dim, targets in target_vars.items():
        print(f"\n{'─' * 60}")
        print(f"  GOBERNANZA → {target_dim}")
        print(f"{'─' * 60}")

        for target in targets:
            if target not in df.columns:
                continue
            target_label = VAR_LABELS.get(target, target)

            for gov in gov_vars:
                if gov not in df.columns:
                    continue
                gov_label = VAR_LABELS.get(gov, gov)

                result = fit_mixed_model(df, target, gov)
                if result is None:
                    continue

                # Also compute Spearman correlation
                r_sp, p_sp = stats.spearmanr(
                    df[gov].dropna(),
                    df.loc[df[gov].notna() & df[target].notna(), target]
                )
                # Recompute properly
                mask = df[gov].notna() & df[target].notna()
                r_sp, p_sp = stats.spearmanr(df.loc[mask, gov], df.loc[mask, target])

                results.append({
                    'governance_var': gov,
                    'governance_label': gov_label,
                    'target_var': target,
                    'target_label': target_label,
                    'target_dimension': target_dim,
                    'coef': result['coef'],
                    'se': result['se'],
                    'p_value': result['p_value'],
                    'r2_marginal': result['r2_marginal'],
                    'r2_conditional': result['r2_conditional'],
                    'aic': result['aic'],
                    'r_spearman': r_sp,
                    'p_spearman': p_sp,
                    'n': result['n']
                })

                sig = '***' if result['p_value'] < 0.001 else '**' if result['p_value'] < 0.01 else '*' if result['p_value'] < 0.05 else 'ns'
                if result['p_value'] < 0.05:
                    direction = '↑' if result['coef'] > 0 else '↓'
                    print(f"  {gov_label:<25} → {target_label:<25}: β={result['coef']:>8.4f}{sig} "
                          f"r²m={result['r2_marginal']:.3f} {direction}")

    results_df = pd.DataFrame(results)
    return results_df


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_model_selection_heatmap(best_df, filename):
    """
    Heatmap showing which variable was selected for each outcome × dimension combo
    """
    print(f"\n  Generating model selection heatmap...")

    # Pivot: outcomes as rows, predictor dimensions as columns
    # Value: coefficient of selected variable
    pivot_coef = best_df.pivot_table(
        values='coef', index='outcome_label', columns='predictor_dimension'
    )
    pivot_is_composite = best_df.pivot_table(
        values='selected_is_composite', index='outcome_label', columns='predictor_dimension'
    )
    pivot_labels = best_df.pivot_table(
        values='selected_label', index='outcome_label', columns='predictor_dimension',
        aggfunc='first'
    )

    fig, ax = plt.subplots(figsize=(14, 10))

    sns.heatmap(pivot_coef, annot=False, cmap='RdBu_r', center=0, ax=ax,
                linewidths=1, linecolor='white', cbar_kws={'label': 'β coefficient (mixed model)'})

    # Add annotations with variable name + coefficient
    for i in range(len(pivot_coef.index)):
        for j in range(len(pivot_coef.columns)):
            outcome = pivot_coef.index[i]
            dim = pivot_coef.columns[j]
            if outcome in pivot_labels.index and dim in pivot_labels.columns:
                label = pivot_labels.loc[outcome, dim]
                coef = pivot_coef.iloc[i, j]
                is_comp = pivot_is_composite.iloc[i, j] if not pd.isna(pivot_is_composite.iloc[i, j]) else False

                if pd.notna(coef):
                    marker = '●' if is_comp else '○'
                    p_row = best_df[(best_df['outcome_label'] == outcome) &
                                    (best_df['predictor_dimension'] == dim)]
                    if len(p_row) > 0:
                        p_val = p_row.iloc[0]['p_value']
                        sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
                    else:
                        sig = ''

                    text = f"{marker} {label}\nβ={coef:.3f}{sig}"
                    color = 'white' if abs(coef) > pivot_coef.abs().max().max() * 0.5 else 'black'
                    ax.text(j + 0.5, i + 0.5, text, ha='center', va='center',
                            fontsize=7, color=color, fontweight='bold')

    ax.set_title('Selección de Modelos por AIC: Variable Óptima por Dimensión\n'
                 '● = Índice compuesto seleccionado  ○ = Variable específica seleccionada\n'
                 'lmer(Y ~ X + (1|microrregião))',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Dimensión Predictora', fontsize=12)
    ax.set_ylabel('Outcome (Enfermedad)', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_governance_effects(gov_df, filename):
    """
    Comprehensive visualization of governance effects on all dimensions
    """
    print(f"\n  Generating governance effects panel...")

    fig, axes = plt.subplots(2, 2, figsize=(18, 16))

    dims = ['Biodiversidad', 'Riesgo Climático', 'Vulnerabilidad', 'Salud']
    gov_idx = 'idx_gobernanza_100'

    for ax, dim in zip(axes.flatten(), dims):
        subset = gov_df[(gov_df['target_dimension'] == dim) &
                        (gov_df['governance_var'] == gov_idx)]

        if len(subset) == 0:
            ax.text(0.5, 0.5, f'No data for {dim}', ha='center', va='center',
                    transform=ax.transAxes)
            continue

        # Sort by coefficient
        subset = subset.sort_values('coef')

        colors = ['#d73027' if p >= 0.05 else ('#1a9850' if c < 0 else '#fc8d59')
                  for c, p in zip(subset['coef'], subset['p_value'])]

        bars = ax.barh(range(len(subset)), subset['coef'], color=colors, edgecolor='white', height=0.7)

        # Add significance stars
        for i, (_, row) in enumerate(subset.iterrows()):
            sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
            x_pos = row['coef'] + 0.002 if row['coef'] >= 0 else row['coef'] - 0.002
            ha = 'left' if row['coef'] >= 0 else 'right'
            ax.text(x_pos, i, f" {sig} (R²m={row['r2_marginal']:.3f})",
                    va='center', ha=ha, fontsize=8, fontweight='bold')

        ax.set_yticks(range(len(subset)))
        ax.set_yticklabels([VAR_LABELS.get(v, v) for v in subset['target_var']], fontsize=9)
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
        ax.set_xlabel('β (mixed model coefficient)', fontsize=10)
        ax.set_title(f'Gobernanza → {dim}', fontsize=12, fontweight='bold')

    fig.suptitle('Efecto de Gobernanza (idx_gobernanza_100) sobre TODAS las Dimensiones\n'
                 'lmer(Y ~ gobernanza + (1|microrregião))\n'
                 'Verde = sig. negativo (protector) | Naranja = sig. positivo | Rojo = no significativo',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_governance_by_component(gov_df, filename):
    """
    Heatmap: each UAI component vs all target variables
    """
    print(f"\n  Generating governance component heatmap...")

    gov_vars = ['idx_gobernanza_100', 'UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']

    # Create pivot of coefficients
    subset = gov_df[gov_df['governance_var'].isin(gov_vars)].copy()
    pivot = subset.pivot_table(values='coef', index='target_label',
                                columns='governance_label', aggfunc='first')

    # Create significance mask
    pivot_p = subset.pivot_table(values='p_value', index='target_label',
                                  columns='governance_label', aggfunc='first')

    # Order columns
    col_order = [VAR_LABELS[v] for v in gov_vars if VAR_LABELS[v] in pivot.columns]
    pivot = pivot[col_order]
    pivot_p = pivot_p[col_order]

    fig, ax = plt.subplots(figsize=(14, 16))

    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'β coefficient'})

    # Mark significant cells
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            p = pivot_p.iloc[i, j]
            if pd.notna(p) and p < 0.05:
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*'
                ax.text(j + 0.5, i + 0.8, sig, ha='center', va='center',
                        fontsize=7, fontweight='bold', color='black')

    ax.set_title('Componentes de Gobernanza (UAI) → Todas las Variables\n'
                 'β from lmer(Y ~ UAI_component + (1|microrregião))\n'
                 '*** p<0.001  ** p<0.01  * p<0.05',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Componente de Gobernanza', fontsize=12)
    ax.set_ylabel('Variable Target', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_scatter_with_micro(df, x_var, y_var, filename, highlight_micro=True):
    """
    Scatter plot with microrregião colors, regression line, and statistics
    """
    data = df[[x_var, y_var, 'nome_microrregiao', 'cod_microrregiao', 'Municipio']].dropna()
    if len(data) < 50:
        return

    fig, ax = plt.subplots(figsize=(12, 8))

    if highlight_micro:
        # Color by mesorregião for readability (15 vs 63)
        meso_data = df[['cod_microrregiao', 'cod_mesorregiao', 'nome_mesorregiao']].drop_duplicates()
        data = data.merge(meso_data, on='cod_microrregiao', how='left')

        meso_codes = sorted(data['cod_mesorregiao'].unique())
        cmap = plt.cm.get_cmap('tab20', len(meso_codes))
        color_map = {m: cmap(i) for i, m in enumerate(meso_codes)}

        for meso, group in data.groupby('cod_mesorregiao'):
            ax.scatter(group[x_var], group[y_var], c=[color_map[meso]], alpha=0.4,
                      s=15, label=group['nome_mesorregiao'].iloc[0] if len(group) > 10 else None)
    else:
        ax.scatter(data[x_var], data[y_var], alpha=0.4, s=15, c='steelblue')

    # Overall regression
    slope, intercept, r_val, p_val, se = stats.linregress(data[x_var], data[y_var])
    x_range = np.linspace(data[x_var].min(), data[x_var].max(), 100)
    ax.plot(x_range, intercept + slope * x_range, 'k-', linewidth=2, alpha=0.8)

    # Spearman
    r_sp, p_sp = stats.spearmanr(data[x_var], data[y_var])

    # Mixed model result
    result = fit_mixed_model(data, y_var, x_var)
    if result:
        sig = '***' if result['p_value'] < 0.001 else '**' if result['p_value'] < 0.01 else '*' if result['p_value'] < 0.05 else 'ns'
        stats_text = (f"Spearman r = {r_sp:.3f} (p={p_sp:.2e})\n"
                      f"Mixed model: β = {result['coef']:.4f}{sig}\n"
                      f"R²m = {result['r2_marginal']:.3f}, R²c = {result['r2_conditional']:.3f}\n"
                      f"n = {result['n']}")
    else:
        stats_text = f"Spearman r = {r_sp:.3f} (p={p_sp:.2e})\nn = {len(data)}"

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    x_label = VAR_LABELS.get(x_var, x_var)
    y_label = VAR_LABELS.get(y_var, y_var)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(f'{x_label} vs {y_label}\n(colored by mesorregião, n=645)',
                fontsize=13, fontweight='bold')

    if highlight_micro:
        # Only show legend for larger groups
        handles, labels = ax.get_legend_handles_labels()
        if len(handles) <= 15:
            ax.legend(loc='lower right', fontsize=7, ncol=2, markerscale=2)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_bivariate_map(df, var1, var2, filename):
    """
    Bivariate choropleth (requires geopandas + shapefile)
    Falls back to scatter if shapefile not available
    """
    try:
        import geopandas as gpd
        shp_path = os.path.join(BASE_DIR, "data/geo/ibge_sp/SP_Municipios_2022.shp")
        if not os.path.exists(shp_path):
            # Try alternative paths
            from glob import glob
            shp_files = glob(os.path.join(BASE_DIR, "data/geo/**/*.shp"), recursive=True)
            if shp_files:
                shp_path = shp_files[0]
            else:
                print(f"  [SKIP] No shapefile found for bivariate map")
                return

        gdf = gpd.read_file(shp_path)

        # Match municipality codes
        # IBGE shapefile uses 7-digit codes (with verification digit)
        # CSV uses 6-digit codes (without verification digit)
        # Solution: truncate shapefile codes to 6 digits
        if 'CD_MUN' in gdf.columns:
            gdf['cod_ibge'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)
        elif 'codigo_ibge' in gdf.columns:
            gdf['cod_ibge'] = gdf['codigo_ibge'].astype(str).str[:6].astype(int)
        else:
            code_col = [c for c in gdf.columns if 'cod' in c.lower() or 'ibge' in c.lower()]
            if code_col:
                gdf['cod_ibge'] = gdf[code_col[0]].astype(str).str[:6].astype(int)
            else:
                print(f"  [SKIP] Cannot match shapefile codes")
                return

        # Merge data
        merged = gdf.merge(df[['cod_ibge', var1, var2]], on='cod_ibge', how='left')

        # Create bivariate classes (3x3)
        q1 = merged[var1].quantile([0.33, 0.66]).values
        q2 = merged[var2].quantile([0.33, 0.66]).values

        def bivar_class(row):
            if pd.isna(row[var1]) or pd.isna(row[var2]):
                return -1
            x = 0 if row[var1] <= q1[0] else (1 if row[var1] <= q1[1] else 2)
            y = 0 if row[var2] <= q2[0] else (1 if row[var2] <= q2[1] else 2)
            return x * 3 + y

        merged['bivar_class'] = merged.apply(bivar_class, axis=1)

        # Bivariate color scheme (Joshua Stevens style)
        colors_9 = [
            '#e8e8e8', '#ace4e4', '#5ac8c8',  # low X
            '#dfb0d6', '#a5add3', '#5698b9',  # mid X
            '#be64ac', '#8c62aa', '#3b4994',  # high X
        ]

        fig, ax = plt.subplots(figsize=(14, 12))

        for cls in range(-1, 9):
            subset = merged[merged['bivar_class'] == cls]
            if len(subset) == 0:
                continue
            color = '#f0f0f0' if cls == -1 else colors_9[cls]
            subset.plot(ax=ax, color=color, edgecolor='white', linewidth=0.3)

        # Legend
        legend_ax = fig.add_axes([0.15, 0.12, 0.12, 0.12])
        for i in range(3):
            for j in range(3):
                legend_ax.add_patch(plt.Rectangle((j, i), 1, 1,
                    facecolor=colors_9[i * 3 + j], edgecolor='white', linewidth=0.5))
        legend_ax.set_xlim(0, 3)
        legend_ax.set_ylim(0, 3)
        legend_ax.set_xlabel(VAR_LABELS.get(var2, var2), fontsize=8)
        legend_ax.set_ylabel(VAR_LABELS.get(var1, var1), fontsize=8)
        legend_ax.set_xticks([0.5, 2.5])
        legend_ax.set_xticklabels(['Low', 'High'], fontsize=7)
        legend_ax.set_yticks([0.5, 2.5])
        legend_ax.set_yticklabels(['Low', 'High'], fontsize=7)

        ax.axis('off')
        ax.set_title(f'Mapa Bivariado: {VAR_LABELS.get(var1, var1)} × {VAR_LABELS.get(var2, var2)}\n'
                     f'São Paulo (n={len(merged[merged["bivar_class"] >= 0])} municipios)',
                     fontsize=14, fontweight='bold')

        plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
        plt.close()
        print(f"  [SAVED] {filename}")

    except ImportError:
        print(f"  [SKIP] geopandas not available for bivariate map")
    except Exception as e:
        print(f"  [ERROR] Bivariate map: {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANÁLISIS H1 - SELECCIÓN DE MODELOS Y GOBERNANZA EXPANDIDA")
    print("Solicitud: Dr. Adrian David González Chaves (27/01/2026)")
    print("=" * 70)

    # Load data
    df, df_z = load_data()

    # ================================================================
    # PART 1: Disease-focused model selection
    # ================================================================
    all_selection, best_selection = run_disease_focused_selection(df)

    # Save results
    all_selection.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_model_selection_all.csv'), index=False)
    best_selection.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_model_selection_best.csv'), index=False)
    print(f"\n  [SAVED] h1_model_selection_all.csv ({len(all_selection)} comparisons)")
    print(f"  [SAVED] h1_model_selection_best.csv ({len(best_selection)} selections)")

    # Print summary table
    print("\n" + "=" * 70)
    print("TABLA RESUMEN: VARIABLE SELECCIONADA POR DIMENSIÓN/ENFERMEDAD")
    print("=" * 70)
    print(f"\n  {'Enfermedad':<22} {'Dimensión':<20} {'Variable Seleccionada':<28} {'Tipo':<12} {'β':>8} {'p':>10} {'R²m':>7} {'Equiv':>5}")
    print(f"  {'─' * 112}")

    for _, row in best_selection.sort_values(['outcome_label', 'predictor_dimension']).iterrows():
        tipo = 'COMPUESTO' if row['selected_is_composite'] else 'específico'
        sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
        print(f"  {row['outcome_label']:<22} {row['predictor_dimension']:<20} {row['selected_label']:<28} {tipo:<12} "
              f"{row['coef']:>8.4f}{sig:<3} {row['p_value']:>9.4f} {row['r2_marginal']:>7.3f} {row['n_equivalent']:>5}")

    # ================================================================
    # PART 2: Governance → All dimensions
    # ================================================================
    gov_results = analyze_governance_to_all(df)
    gov_results.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_governance_all_dimensions.csv'), index=False)
    print(f"\n  [SAVED] h1_governance_all_dimensions.csv ({len(gov_results)} relationships)")

    # Print governance summary
    print("\n" + "=" * 70)
    print("RESUMEN: GOBERNANZA → TODAS LAS DIMENSIONES (significativos)")
    print("=" * 70)

    sig_gov = gov_results[gov_results['p_value'] < 0.05].sort_values('target_dimension')
    for dim in sig_gov['target_dimension'].unique():
        print(f"\n  {dim}:")
        dim_data = sig_gov[sig_gov['target_dimension'] == dim]
        for _, row in dim_data.sort_values('coef').iterrows():
            direction = '↑' if row['coef'] > 0 else '↓'
            sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*'
            print(f"    {row['governance_label']:<25} → {row['target_label']:<25}: β={row['coef']:>8.4f}{sig} "
                  f"r²m={row['r2_marginal']:.3f} rₛ={row['r_spearman']:.3f} {direction}")

    # ================================================================
    # PART 3: Visualizations
    # ================================================================
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    # 3.1 Model selection heatmap
    plot_model_selection_heatmap(best_selection, 'h1_model_selection_heatmap.png')

    # 3.2 Governance effects panel
    plot_governance_effects(gov_results, 'h1_governance_all_dimensions.png')

    # 3.3 Governance by component heatmap
    plot_governance_by_component(gov_results, 'h1_governance_components_heatmap.png')

    # 3.4 Key scatter plots with mixed model stats
    print("\n  Generating scatter plots...")

    # Most important relationships based on model selection
    key_scatters = []

    # Get top relationships from best_selection
    for _, row in best_selection.iterrows():
        if row['p_value'] < 0.05:
            key_scatters.append((row['selected_variable'], row['outcome']))

    # Add governance → biodiversity/climate scatters
    sig_gov_key = gov_results[
        (gov_results['p_value'] < 0.01) &
        (gov_results['governance_var'] == 'idx_gobernanza_100')
    ]
    for _, row in sig_gov_key.iterrows():
        key_scatters.append((row['governance_var'], row['target_var']))

    # Deduplicate and limit
    seen = set()
    unique_scatters = []
    for pair in key_scatters:
        if pair not in seen:
            seen.add(pair)
            unique_scatters.append(pair)

    # Generate top 20 scatter plots
    for x_var, y_var in unique_scatters[:20]:
        safe_x = x_var.replace('incidence_mean_', '').replace('health_', '').replace('idx_', '')[:15]
        safe_y = y_var.replace('incidence_mean_', '').replace('health_', '').replace('idx_', '')[:15]
        fname = f'h1_ms_scatter_{safe_x}_{safe_y}.png'
        plot_scatter_with_micro(df, x_var, y_var, fname)

    # 3.5 Bivariate maps (most important pairs)
    print("\n  Generating bivariate maps...")
    biv_pairs = [
        ('forest_cover', 'incidence_mean_dengue', 'h1_MAP1_bivariate_forest_dengue.png'),
        ('idx_gobernanza_100', 'idx_biodiv', 'h1_MAP2_bivariate_governance_biodiv.png'),
        ('idx_gobernanza_100', 'idx_clima', 'h1_MAP3_bivariate_governance_climate.png'),
        ('forest_cover', 'pol_deficit', 'h1_MAP4_bivariate_forest_poldeficit.png'),
        ('pct_pobreza', 'idx_carga_enfermedad', 'h1_MAP5_bivariate_poverty_disease.png'),
    ]

    for var1, var2, fname in biv_pairs:
        if var1 in df.columns and var2 in df.columns:
            plot_bivariate_map(df, var1, var2, fname)

    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("ANÁLISIS COMPLETADO - RESUMEN FINAL")
    print("=" * 70)

    # Count composite vs specific selections
    n_composite = best_selection['selected_is_composite'].sum()
    n_specific = len(best_selection) - n_composite
    print(f"\n  Total selecciones: {len(best_selection)}")
    print(f"  Índice compuesto preferido: {n_composite} ({n_composite/len(best_selection)*100:.0f}%)")
    print(f"  Variable específica preferida: {n_specific} ({n_specific/len(best_selection)*100:.0f}%)")

    # Top findings
    print(f"\n  Relaciones gobernanza más fuertes (p<0.01):")
    top_gov = gov_results[
        (gov_results['p_value'] < 0.01) &
        (gov_results['governance_var'] == 'idx_gobernanza_100')
    ].sort_values('r2_marginal', ascending=False).head(10)

    for _, row in top_gov.iterrows():
        direction = '↑' if row['coef'] > 0 else '↓'
        print(f"    {row['target_label']:<25}: β={row['coef']:.4f} R²m={row['r2_marginal']:.3f} {direction}")

    print(f"\n  Archivos generados:")
    print(f"    outputs/h1_model_selection_all.csv")
    print(f"    outputs/h1_model_selection_best.csv")
    print(f"    outputs/h1_governance_all_dimensions.csv")

    for f in sorted(os.listdir(FIG_DIR)):
        if f.startswith('h1_') and ('model_selection' in f or 'governance' in f or 'ms_scatter' in f or 'MAP' in f):
            print(f"    figures/{f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
