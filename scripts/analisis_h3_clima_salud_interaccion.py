"""
Analisis H3 - Interaccion Clima x Salud -> Gobernanza
Modelo: logit(Gobernanza) ~ Riesgo_salud * Riesgo_clima + (1|micro)

Priorizar pares teoricamente vinculados:
- diarrea x flooding
- dengue x hydric_stress
- malaria x forest_cover
- enfermedades respiratorias x fire_risk

Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)
Autor: Science Team / AP Digital
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
import os

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/municipios_integrado_v8.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h3_clima_salud")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Governance outcomes
GOVERNANCE_OUTCOMES = ['idx_gobernanza', 'UAI_Crisk', 'UAI_env']

# Theoretically linked pairs: (salud, clima) - hypothesis-driven
THEORY_PAIRS = [
    ('incidence_diarrhea_mean', 'flooding_risks', 'Diarrea-Inundacion'),
    ('incidence_mean_dengue', 'hydric_stress_risk', 'Dengue-Estres Hidrico'),
    ('incidence_mean_dengue', 'flooding_risks', 'Dengue-Inundacion'),
    ('incidence_mean_malaria', 'forest_cover', 'Malaria-Bosque'),
    ('health_hosp_resp_mean', 'fire_risk_index', 'Resp-Fuego'),
    ('health_death_circ_mean', 'fire_risk_index', 'Cardiovasc-Fuego'),
    ('incidence_mean_leptospirose', 'flooding_risks', 'Leptospirosis-Inundacion'),
    ('incidence_mean_leishmaniose', 'forest_cover', 'Leishmaniasis-Bosque'),
]

# All climate and health variables for exploratory analysis
CLIMATE_VARS = ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk']
HEALTH_VARS = [
    'incidence_mean_dengue', 'incidence_mean_malaria',
    'incidence_mean_leishmaniose', 'incidence_mean_leptospirose',
    'incidence_diarrhea_mean', 'health_death_circ_mean', 'health_hosp_resp_mean'
]

VAR_LABELS = {
    'idx_gobernanza': 'Gobernanza (idx)',
    'UAI_Crisk': 'UAI Riesgo Clim.',
    'UAI_env': 'UAI Ambiental',
    'flooding_risks': 'Riesgo Inundacion',
    'fire_risk_index': 'Riesgo Fuego',
    'hydric_stress_risk': 'Estres Hidrico',
    'forest_cover': 'Cobertura Forestal',
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_diarrhea_mean': 'Diarrea',
    'health_death_circ_mean': 'Mort. Cardiovasc.',
    'health_hosp_resp_mean': 'Hosp. Respiratoria'
}


# ============================================================
# DATA LOADING
# ============================================================

def load_and_prepare_data():
    """Load data and apply transformations"""
    print("\n" + "=" * 70)
    print("CARGANDO Y PREPARANDO DATOS")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    print(f"Dataset: {len(df)} municipios")

    # Logit transformation for governance
    eps = 1e-6
    for var in GOVERNANCE_OUTCOMES:
        if var in df.columns:
            clipped = df[var].clip(eps, 1 - eps)
            df[f'{var}_logit'] = np.log(clipped / (1 - clipped))

    # Standardize predictors
    scaler = StandardScaler()
    all_vars = CLIMATE_VARS + HEALTH_VARS + ['forest_cover']

    for var in all_vars:
        if var in df.columns:
            mask = df[var].notna()
            if mask.sum() > 0:
                df.loc[mask, f'{var}_z'] = scaler.fit_transform(
                    df.loc[mask, var].values.reshape(-1, 1)
                ).flatten()

    return df


# ============================================================
# INTERACTION MODEL
# ============================================================

def fit_climate_health_interaction(df, outcome, health_var, climate_var, group_var='cod_microrregiao'):
    """
    Fit: logit(outcome) ~ health * climate + (1|group)
    """
    outcome_logit = f'{outcome}_logit'
    health_z = f'{health_var}_z'
    climate_z = f'{climate_var}_z'

    for v in [outcome_logit, health_z, climate_z]:
        if v not in df.columns:
            return None

    data = df[[outcome_logit, health_z, climate_z, group_var]].dropna()
    if len(data) < 100:
        return None

    data = data.rename(columns={outcome_logit: 'y', health_z: 'h', climate_z: 'c'})

    try:
        # Full model
        model_full = smf.mixedlm('y ~ h * c', data, groups=data[group_var])
        result_full = model_full.fit(reml=False, method='powell')

        if not result_full.converged:
            return None

        # Additive model
        model_add = smf.mixedlm('y ~ h + c', data, groups=data[group_var])
        result_add = model_add.fit(reml=False, method='powell')

        # AICs
        k_full = len(result_full.params) + 1
        k_add = len(result_add.params) + 1
        n = len(data)
        aic_full = -2 * result_full.llf + 2 * k_full
        aic_add = -2 * result_add.llf + 2 * k_add

        # R2
        var_fixed = np.var(result_full.fittedvalues)
        var_random = float(result_full.cov_re.iloc[0, 0]) if hasattr(result_full.cov_re, 'iloc') else float(result_full.cov_re)
        var_resid = result_full.scale
        r2_marginal = var_fixed / (var_fixed + var_random + var_resid)

        # Interaction
        int_coef = result_full.params.get('h:c', np.nan)
        int_se = result_full.bse.get('h:c', np.nan)
        int_p = result_full.pvalues.get('h:c', 1.0)

        return {
            'outcome': outcome,
            'health_var': health_var,
            'climate_var': climate_var,
            'coef_health': result_full.params['h'],
            'p_health': result_full.pvalues['h'],
            'coef_climate': result_full.params['c'],
            'p_climate': result_full.pvalues['c'],
            'coef_interaction': int_coef,
            'se_interaction': int_se,
            'p_interaction': int_p,
            'aic_interaction': aic_full,
            'aic_additive': aic_add,
            'delta_aic': aic_full - aic_add,
            'r2_marginal': r2_marginal,
            'n': n,
            'interaction_significant': int_p < 0.05 if pd.notna(int_p) else False,
            'interaction_improves_fit': aic_full < aic_add
        }

    except Exception as e:
        return None


def run_theory_driven_analysis(df):
    """Run analysis for theoretically linked pairs"""
    print("\n" + "=" * 70)
    print("H3a: PARES TEORICAMENTE VINCULADOS")
    print("Modelo: logit(Gob) ~ Salud * Clima + (1|micro)")
    print("=" * 70)

    results = []

    for health_var, climate_var, pair_name in THEORY_PAIRS:
        print(f"\n  {pair_name}:")
        print(f"  {'Outcome':<20} {'b_int':>10} {'p_int':>10} {'dAIC':>10} {'Signif':>10}")
        print(f"  {'-'*60}")

        for outcome in GOVERNANCE_OUTCOMES:
            result = fit_climate_health_interaction(df, outcome, health_var, climate_var)

            if result is None:
                continue

            result['pair_name'] = pair_name
            result['theory_driven'] = True
            results.append(result)

            sig = '***' if result['p_interaction'] < 0.001 else '**' if result['p_interaction'] < 0.01 else '*' if result['p_interaction'] < 0.05 else 'ns'
            fit_mark = '<< MEJOR' if result['interaction_improves_fit'] and result['interaction_significant'] else ''

            print(f"  {VAR_LABELS.get(outcome, outcome):<20} "
                  f"{result['coef_interaction']:>10.4f} {result['p_interaction']:>10.4f} "
                  f"{result['delta_aic']:>10.2f} {sig:>10} {fit_mark}")

    return pd.DataFrame(results)


def run_exploratory_analysis(df):
    """Run all climate x health combinations"""
    print("\n" + "=" * 70)
    print("H3b: ANALISIS EXPLORATORIO (TODAS LAS COMBINACIONES)")
    print("=" * 70)

    results = []
    total = len(HEALTH_VARS) * len(CLIMATE_VARS) * len(GOVERNANCE_OUTCOMES)
    done = 0

    for outcome in GOVERNANCE_OUTCOMES:
        for health_var in HEALTH_VARS:
            for climate_var in CLIMATE_VARS:
                result = fit_climate_health_interaction(df, outcome, health_var, climate_var)
                done += 1

                if result is None:
                    continue

                result['theory_driven'] = False
                result['pair_name'] = f"{VAR_LABELS.get(health_var, health_var)[:10]}-{VAR_LABELS.get(climate_var, climate_var)[:10]}"
                results.append(result)

    print(f"  Modelos evaluados: {done}")
    print(f"  Modelos convergentes: {len(results)}")

    return pd.DataFrame(results)


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_interaction_matrix(results_df, filename):
    """Matrix of interaction effects: Health (rows) x Climate (cols)"""
    print(f"\n  Generating interaction matrix...")

    # Use idx_gobernanza as outcome
    subset = results_df[results_df['outcome'] == 'idx_gobernanza'].copy()

    if len(subset) == 0:
        print("  No data for idx_gobernanza")
        return

    subset['health_label'] = subset['health_var'].map(VAR_LABELS)
    subset['climate_label'] = subset['climate_var'].map(VAR_LABELS)

    pivot = subset.pivot_table(
        values='coef_interaction',
        index='health_label',
        columns='climate_label',
        aggfunc='first'
    )

    pivot_p = subset.pivot_table(
        values='p_interaction',
        index='health_label',
        columns='climate_label',
        aggfunc='first'
    )

    fig, ax = plt.subplots(figsize=(10, 8))

    # Mask non-significant
    mask = pivot_p >= 0.05
    pivot_masked = pivot.copy()

    sns.heatmap(pivot_masked, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Coef. Interaccion'})

    # Add significance markers
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            p = pivot_p.iloc[i, j]
            if pd.notna(p) and p < 0.05:
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*'
                ax.text(j + 0.5, i + 0.8, sig, ha='center', va='center',
                       fontsize=8, fontweight='bold', color='black')

    ax.set_title('H3: Interaccion Salud x Clima -> Gobernanza\n'
                 'Outcome: idx_gobernanza | *** p<0.001, ** p<0.01, * p<0.05',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Variable Climatica', fontsize=11)
    ax.set_ylabel('Variable de Salud', fontsize=11)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_theory_pairs(df, results_df, filename_prefix='h3_theory'):
    """Plot significant theory-driven pairs"""
    print(f"\n  Generating theory pair plots...")

    theory_results = results_df[results_df['theory_driven'] == True]
    sig_theory = theory_results[theory_results['interaction_significant']]

    if len(sig_theory) == 0:
        print("  No significant theory-driven interactions")
        return

    for _, row in sig_theory.iterrows():
        health_var = row['health_var']
        climate_var = row['climate_var']
        outcome = row['outcome']
        pair_name = row['pair_name']

        outcome_logit = f'{outcome}_logit'
        health_z = f'{health_var}_z'
        climate_z = f'{climate_var}_z'

        data = df[[outcome_logit, health_z, climate_z, 'cod_microrregiao']].dropna()
        if len(data) < 100:
            continue

        data = data.rename(columns={outcome_logit: 'y', health_z: 'h', climate_z: 'c'})

        try:
            model = smf.mixedlm('y ~ h * c', data, groups=data['cod_microrregiao'])
            result = model.fit(reml=False, method='powell')

            if not result.converged:
                continue

            fig, ax = plt.subplots(figsize=(10, 7))

            # Plot at 3 levels of climate
            h_range = np.linspace(data['h'].min(), data['h'].max(), 100)
            colors = ['#1a9850', '#fc8d59', '#d73027']
            levels = [data['c'].quantile(0.1), data['c'].median(), data['c'].quantile(0.9)]
            level_names = ['Low', 'Med', 'High']

            b0 = result.params['Intercept']
            b_h = result.params['h']
            b_c = result.params['c']
            b_int = result.params.get('h:c', 0)

            for level, name, color in zip(levels, level_names, colors):
                y_pred = b0 + b_h * h_range + b_c * level + b_int * h_range * level
                ax.plot(h_range, y_pred, color=color, linewidth=2.5,
                       label=f'{name} {VAR_LABELS.get(climate_var, climate_var)}')

            ax.scatter(data['h'], data['y'], alpha=0.15, s=10, c='gray')

            int_p = result.pvalues.get('h:c', 1)
            sig = '***' if int_p < 0.001 else '**' if int_p < 0.01 else '*' if int_p < 0.05 else 'ns'
            stats_text = f"b_interaccion = {b_int:.4f} ({sig})\np = {int_p:.4f}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                   va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

            ax.set_xlabel(f'{VAR_LABELS.get(health_var, health_var)} (z)', fontsize=11)
            ax.set_ylabel(f'logit({VAR_LABELS.get(outcome, outcome)})', fontsize=11)
            ax.set_title(f'H3: {pair_name}\n{VAR_LABELS.get(health_var, health_var)} x '
                        f'{VAR_LABELS.get(climate_var, climate_var)} -> '
                        f'{VAR_LABELS.get(outcome, outcome)}',
                        fontsize=12, fontweight='bold')
            ax.legend(loc='lower right')

            plt.tight_layout()
            safe_name = pair_name.replace(' ', '_').replace('-', '_')[:20]
            fname = f"{filename_prefix}_{safe_name}.png"
            plt.savefig(os.path.join(FIG_DIR, fname), dpi=150, bbox_inches='tight')
            plt.close()
            print(f"  [SAVED] {fname}")

        except Exception as e:
            continue


def plot_summary_table(results_df, filename):
    """Summary table of all results"""
    print(f"\n  Generating summary table figure...")

    # Top 15 by delta AIC (most improved)
    top_results = results_df.nsmallest(15, 'delta_aic').copy()

    top_results['outcome_label'] = top_results['outcome'].map(VAR_LABELS)
    top_results['health_label'] = top_results['health_var'].map(VAR_LABELS)
    top_results['climate_label'] = top_results['climate_var'].map(VAR_LABELS)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')

    # Create table
    cell_text = []
    for _, row in top_results.iterrows():
        sig = '***' if row['p_interaction'] < 0.001 else '**' if row['p_interaction'] < 0.01 else '*' if row['p_interaction'] < 0.05 else 'ns'
        theory = 'Si' if row['theory_driven'] else 'No'
        cell_text.append([
            row['outcome_label'],
            row['health_label'],
            row['climate_label'],
            f"{row['coef_interaction']:.4f}",
            f"{row['p_interaction']:.4f}",
            sig,
            f"{row['delta_aic']:.2f}",
            theory
        ])

    columns = ['Outcome', 'Salud', 'Clima', 'b_int', 'p_int', 'Sig', 'dAIC', 'Teoria']

    table = ax.table(cellText=cell_text, colLabels=columns, loc='center',
                    cellLoc='center', colLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)

    # Style header
    for j, col in enumerate(columns):
        table[(0, j)].set_facecolor('#4a86e8')
        table[(0, j)].set_text_props(color='white', fontweight='bold')

    ax.set_title('H3: Top 15 Interacciones Clima x Salud (por mejora AIC)\n'
                 'dAIC < 0 indica que el modelo con interaccion tiene mejor ajuste',
                 fontsize=12, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANALISIS H3 - INTERACCION CLIMA x SALUD -> GOBERNANZA")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load data
    df = load_and_prepare_data()

    # Theory-driven analysis
    theory_results = run_theory_driven_analysis(df)

    # Exploratory analysis
    explore_results = run_exploratory_analysis(df)

    # Combine
    all_results = pd.concat([theory_results, explore_results], ignore_index=True)

    # Save
    all_results.to_csv(os.path.join(OUTPUT_DIR, 'h3_interactions.csv'), index=False)
    theory_results.to_csv(os.path.join(OUTPUT_DIR, 'h3_theory_pairs.csv'), index=False)
    print(f"\n  [SAVED] h3_interactions.csv ({len(all_results)} models)")
    print(f"  [SAVED] h3_theory_pairs.csv ({len(theory_results)} models)")

    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN H3")
    print("=" * 70)

    sig_all = all_results[all_results['interaction_significant']]
    sig_theory = theory_results[theory_results['interaction_significant']] if len(theory_results) > 0 else pd.DataFrame()

    print(f"\n  Interacciones significativas (total): {len(sig_all)} de {len(all_results)}")
    print(f"  Interacciones significativas (teoria): {len(sig_theory)} de {len(theory_results)}")

    if len(sig_theory) > 0:
        print(f"\n  PARES TEORICOS SIGNIFICATIVOS:")
        for _, row in sig_theory.iterrows():
            print(f"    {row['pair_name']}: b={row['coef_interaction']:.4f}, p={row['p_interaction']:.4f}")

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_interaction_matrix(all_results, 'h3_interaction_matrix.png')
    plot_theory_pairs(df, all_results)
    plot_summary_table(all_results, 'h3_summary_table.png')

    # Key finding
    print("\n" + "=" * 70)
    print("HALLAZGO PRINCIPAL H3")
    print("=" * 70)

    if len(sig_all) > 0:
        best = sig_all.nsmallest(1, 'delta_aic').iloc[0]
        print(f"\n  La interaccion con mejor ajuste (dAIC mas negativo):")
        print(f"    {VAR_LABELS.get(best['health_var'], best['health_var'])} x "
              f"{VAR_LABELS.get(best['climate_var'], best['climate_var'])} -> "
              f"{VAR_LABELS.get(best['outcome'], best['outcome'])}")
        print(f"    b_int = {best['coef_interaction']:.4f}, dAIC = {best['delta_aic']:.2f}")

        if best['coef_interaction'] > 0:
            print(f"\n  Interpretacion: El efecto conjunto de altos riesgos de salud Y clima")
            print(f"  se asocia con MAYOR gobernanza (posible respuesta reactiva)")
        else:
            print(f"\n  Interpretacion: El efecto conjunto de altos riesgos de salud Y clima")
            print(f"  se asocia con MENOR gobernanza (posible sobrecarga institucional)")
    else:
        print("\n  No se encontraron interacciones significativas.")

    print("\nDone!")


if __name__ == "__main__":
    main()
