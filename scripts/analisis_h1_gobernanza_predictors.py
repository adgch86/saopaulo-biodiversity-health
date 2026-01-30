"""
Analisis H1 - Que Predice la Gobernanza (UAI)?
Invirtiendo la logica causal: Riesgos/Vulnerabilidad -> genera gobernanza

Modelo: logit(UAI) ~ Dimension + (1|microrregiao)
Distribucion Beta implicitamente via transformacion logit.

Hipotesis:
- H1.a: Gobernanza ~ Biodiversidad
- H1.b: Gobernanza ~ Riesgo Salud
- H1.c: Gobernanza ~ Riesgo Clima
- H1.d: Gobernanza ~ Vulnerabilidad

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
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h1_gobernanza")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Variables de gobernanza (outcomes) - valores 0-1
GOVERNANCE_VARS = {
    'UAI_housing': 'UAI Vivienda',
    'UAI_env': 'UAI Ambiental',
    'UAI_food': 'UAI Alimentacion',
    'UAI_mob': 'UAI Movilidad',
    'UAI_Crisk': 'UAI Riesgo Clim.',
    'idx_gobernanza': 'Gobernanza (idx 0-1)'
}

# Dimensiones predictoras
DIMENSIONS = {
    'biodiversidad': {
        'vars': ['forest_cover', 'mean_species_richness', 'pol_deficit', 'idx_biodiv'],
        'labels': {
            'forest_cover': 'Cobertura Forestal',
            'mean_species_richness': 'Riqueza Especies',
            'pol_deficit': 'Deficit Polinizacion',
            'idx_biodiv': 'Biodiversidad (idx)'
        },
        'label': 'Biodiversidad'
    },
    'salud': {
        'vars': [
            'incidence_mean_dengue', 'incidence_mean_malaria',
            'incidence_mean_leishmaniose', 'incidence_mean_leptospirose',
            'incidence_diarrhea_mean', 'health_death_circ_mean', 'health_hosp_resp_mean'
        ],
        'labels': {
            'incidence_mean_dengue': 'Dengue',
            'incidence_mean_malaria': 'Malaria',
            'incidence_mean_leishmaniose': 'Leishmaniasis',
            'incidence_mean_leptospirose': 'Leptospirosis',
            'incidence_diarrhea_mean': 'Diarrea',
            'health_death_circ_mean': 'Mort. Cardiovasc.',
            'health_hosp_resp_mean': 'Hosp. Respiratoria'
        },
        'label': 'Riesgo Salud'
    },
    'clima': {
        'vars': ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk', 'idx_clima'],
        'labels': {
            'flooding_risks': 'Riesgo Inundacion',
            'fire_risk_index': 'Riesgo Fuego',
            'hydric_stress_risk': 'Estres Hidrico',
            'idx_clima': 'Clima (idx)'
        },
        'label': 'Riesgo Climatico'
    },
    'vulnerabilidad': {
        'vars': ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena', 'idx_vulnerabilidad'],
        'labels': {
            'pct_pobreza': '% Pobreza',
            'pct_rural': '% Rural',
            'pct_preta': '% Pob. Negra',
            'pct_indigena': '% Pob. Indigena',
            'idx_vulnerabilidad': 'Vulnerabilidad (idx)'
        },
        'label': 'Vulnerabilidad'
    }
}


# ============================================================
# DATA LOADING & TRANSFORMATION
# ============================================================

def load_and_prepare_data():
    """Load data and apply logit transformation to governance variables"""
    print("\n" + "=" * 70)
    print("CARGANDO Y PREPARANDO DATOS")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    print(f"Dataset: {len(df)} municipios x {len(df.columns)} variables")
    print(f"Microrregiones: {df['cod_microrregiao'].nunique()}")
    print(f"Mesorregiones: {df['cod_mesorregiao'].nunique()}")

    # Logit transformation for governance variables (bounded 0-1)
    eps = 1e-6
    for var in GOVERNANCE_VARS.keys():
        if var in df.columns:
            # Clip to avoid 0 and 1 (undefined logit)
            clipped = df[var].clip(eps, 1 - eps)
            df[f'{var}_logit'] = np.log(clipped / (1 - clipped))

            # Check distribution
            valid = df[f'{var}_logit'].dropna()
            print(f"  {var}: min={df[var].min():.3f}, max={df[var].max():.3f}, "
                  f"logit range=[{valid.min():.2f}, {valid.max():.2f}]")

    # Standardize predictors for comparability
    scaler = StandardScaler()
    for dim_key, dim in DIMENSIONS.items():
        for var in dim['vars']:
            if var in df.columns:
                vals = df[var].dropna()
                if len(vals) > 0:
                    mask = df[var].notna()
                    df.loc[mask, f'{var}_z'] = scaler.fit_transform(
                        df.loc[mask, var].values.reshape(-1, 1)
                    ).flatten()

    return df


# ============================================================
# MIXED MODEL FITTING
# ============================================================

def fit_mixed_model_logit(df, outcome_logit, predictor, group_var='cod_microrregiao'):
    """
    Fit mixed model: logit(UAI) ~ predictor + (1|group)
    Uses ML for AIC comparison.
    """
    data = df[[outcome_logit, predictor, group_var]].dropna()
    if len(data) < 50:
        return None

    # Sanitize names
    data = data.rename(columns={outcome_logit: 'y', predictor: 'x'})

    try:
        model = smf.mixedlm('y ~ x', data, groups=data[group_var])
        result = model.fit(reml=False, method='powell')

        if not result.converged:
            return None

        # Compute metrics
        k = len(result.params) + 1  # params + random effect variance
        n = len(data)
        aic = -2 * result.llf + 2 * k
        bic = -2 * result.llf + k * np.log(n)
        aicc = aic + (2 * k * (k + 1)) / (n - k - 1) if n > k + 1 else np.inf

        # Marginal R2 (Nakagawa & Schielzeth 2013)
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
            'coef': result.params['x'],
            'se': result.bse['x'],
            'p_value': result.pvalues['x'],
            'r2_marginal': r2_marginal,
            'r2_conditional': r2_conditional,
            'n': n,
            'converged': True
        }
    except Exception as e:
        return None


def run_model_selection(df, outcome_var, dimension_key):
    """
    Compare all predictors within a dimension for a given outcome.
    Returns sorted results by AIC with delta AIC.
    """
    dim = DIMENSIONS[dimension_key]
    results = []

    outcome_logit = f'{outcome_var}_logit'
    if outcome_logit not in df.columns:
        return pd.DataFrame()

    for predictor in dim['vars']:
        if predictor not in df.columns:
            continue

        # Use standardized predictor for comparability
        predictor_z = f'{predictor}_z'
        if predictor_z not in df.columns:
            predictor_z = predictor

        model_result = fit_mixed_model_logit(df, outcome_logit, predictor_z)

        if model_result:
            results.append({
                'predictor': predictor,
                'predictor_label': dim['labels'].get(predictor, predictor),
                'outcome': outcome_var,
                'outcome_label': GOVERNANCE_VARS.get(outcome_var, outcome_var),
                'dimension': dim['label'],
                **model_result
            })

    if not results:
        return pd.DataFrame()

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('aic')
    results_df['delta_aic'] = results_df['aic'] - results_df['aic'].min()
    results_df['aic_weight'] = np.exp(-0.5 * results_df['delta_aic'])
    results_df['aic_weight'] = results_df['aic_weight'] / results_df['aic_weight'].sum()

    return results_df


# ============================================================
# MAIN ANALYSIS FOR EACH HYPOTHESIS
# ============================================================

def run_h1_analysis(df):
    """Run complete H1 analysis: What predicts governance?"""
    print("\n" + "=" * 70)
    print("H1: QUE PREDICE LA GOBERNANZA (UAI)?")
    print("Modelo: logit(UAI) ~ predictor + (1|microrregiao)")
    print("=" * 70)

    all_results = []
    best_by_combo = []

    for outcome_var in GOVERNANCE_VARS.keys():
        if f'{outcome_var}_logit' not in df.columns:
            continue

        print(f"\n{'='*60}")
        print(f"OUTCOME: {GOVERNANCE_VARS[outcome_var]}")
        print(f"{'='*60}")

        for dim_key in DIMENSIONS.keys():
            results_df = run_model_selection(df, outcome_var, dim_key)

            if len(results_df) == 0:
                continue

            all_results.append(results_df)

            # Print results
            print(f"\n  H1.{dim_key[0]}: {DIMENSIONS[dim_key]['label']}")
            print(f"  {'Variable':<25} {'AIC':>10} {'dAIC':>8} {'beta':>10} {'p':>10} {'R2m':>8} {'Peso':>8}")
            print(f"  {'-'*79}")

            for _, row in results_df.iterrows():
                sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
                marker = ' << BEST' if row['delta_aic'] == 0 else (' ~ equiv' if row['delta_aic'] < 2 else '')
                print(f"  {row['predictor_label']:<25} {row['aic']:>10.1f} {row['delta_aic']:>8.2f} "
                      f"{row['coef']:>10.4f}{sig:<3} {row['p_value']:>9.4f} {row['r2_marginal']:>8.4f} "
                      f"{row['aic_weight']:>7.3f}{marker}")

            # Store best
            best = results_df.iloc[0]
            equivalent = results_df[results_df['delta_aic'] < 2]
            best_by_combo.append({
                'outcome': outcome_var,
                'outcome_label': GOVERNANCE_VARS[outcome_var],
                'dimension': DIMENSIONS[dim_key]['label'],
                'dimension_key': dim_key,
                'best_predictor': best['predictor'],
                'best_predictor_label': best['predictor_label'],
                'aic': best['aic'],
                'delta_aic': 0,
                'coef': best['coef'],
                'se': best['se'],
                'p_value': best['p_value'],
                'r2_marginal': best['r2_marginal'],
                'n_equivalent': len(equivalent),
                'equivalent_vars': ', '.join(equivalent['predictor_label'].tolist()),
                'significant': best['p_value'] < 0.05
            })

    # Combine results
    all_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    best_df = pd.DataFrame(best_by_combo)

    return all_df, best_df


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_selection_heatmap(best_df, filename):
    """Heatmap of best predictors for each outcome × dimension"""
    print(f"\n  Generating selection heatmap...")

    # Pivot: outcomes as rows, dimensions as columns
    pivot_coef = best_df.pivot_table(
        values='coef', index='outcome_label', columns='dimension'
    )
    pivot_sig = best_df.pivot_table(
        values='significant', index='outcome_label', columns='dimension'
    )
    pivot_labels = best_df.pivot_table(
        values='best_predictor_label', index='outcome_label', columns='dimension',
        aggfunc='first'
    )

    fig, ax = plt.subplots(figsize=(14, 10))

    sns.heatmap(pivot_coef, annot=False, cmap='RdBu_r', center=0, ax=ax,
                linewidths=1, linecolor='white', cbar_kws={'label': 'beta (log-odds)'})

    # Add annotations
    for i in range(len(pivot_coef.index)):
        for j in range(len(pivot_coef.columns)):
            outcome = pivot_coef.index[i]
            dim = pivot_coef.columns[j]
            if outcome in pivot_labels.index and dim in pivot_labels.columns:
                label = pivot_labels.loc[outcome, dim]
                coef = pivot_coef.iloc[i, j]
                sig = pivot_sig.iloc[i, j]

                if pd.notna(coef):
                    sig_marker = '*' if sig else ''
                    p_row = best_df[(best_df['outcome_label'] == outcome) &
                                    (best_df['dimension'] == dim)]
                    if len(p_row) > 0:
                        p_val = p_row.iloc[0]['p_value']
                        sig_marker = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''

                    text = f"{label}\nb={coef:.3f}{sig_marker}"
                    color = 'white' if abs(coef) > pivot_coef.abs().max().max() * 0.5 else 'black'
                    ax.text(j + 0.5, i + 0.5, text, ha='center', va='center',
                            fontsize=8, color=color, fontweight='bold')

    ax.set_title('H1: Mejores Predictores de Gobernanza por Dimension\n'
                 'Modelo: logit(UAI) ~ predictor + (1|microrregiao)\n'
                 '*** p<0.001  ** p<0.01  * p<0.05',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Dimension Predictora', fontsize=12)
    ax.set_ylabel('Variable de Gobernanza (Outcome)', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_scatter_significant(df, all_results_df, top_n=12):
    """Generate scatter plots for significant relationships"""
    print(f"\n  Generating scatter plots for significant relationships...")

    sig_results = all_results_df[all_results_df['p_value'] < 0.05].sort_values('r2_marginal', ascending=False)

    for idx, row in sig_results.head(top_n).iterrows():
        predictor = row['predictor']
        outcome = row['outcome']
        outcome_logit = f'{outcome}_logit'

        if predictor not in df.columns or outcome_logit not in df.columns:
            continue

        data = df[[predictor, outcome_logit, outcome, 'cod_mesorregiao', 'nome_mesorregiao']].dropna()
        if len(data) < 50:
            continue

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Left: Scatter with logit(UAI)
        ax1 = axes[0]
        meso_codes = sorted(data['cod_mesorregiao'].unique())
        cmap = plt.cm.get_cmap('tab20', len(meso_codes))

        for i, meso in enumerate(meso_codes):
            subset = data[data['cod_mesorregiao'] == meso]
            ax1.scatter(subset[predictor], subset[outcome_logit],
                       c=[cmap(i)], alpha=0.4, s=15, label=subset['nome_mesorregiao'].iloc[0] if len(subset) > 30 else None)

        # Regression line
        slope, intercept, r, p, se = stats.linregress(data[predictor], data[outcome_logit])
        x_range = np.linspace(data[predictor].min(), data[predictor].max(), 100)
        ax1.plot(x_range, intercept + slope * x_range, 'k-', linewidth=2)

        ax1.set_xlabel(row['predictor_label'], fontsize=11)
        ax1.set_ylabel(f"logit({row['outcome_label']})", fontsize=11)

        # Stats box
        stats_text = (f"Mixed model (1|micro):\n"
                     f"beta = {row['coef']:.4f}\n"
                     f"p = {row['p_value']:.2e}\n"
                     f"R2m = {row['r2_marginal']:.4f}")
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=9,
                va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        # Right: Original scale
        ax2 = axes[1]
        for i, meso in enumerate(meso_codes):
            subset = data[data['cod_mesorregiao'] == meso]
            ax2.scatter(subset[predictor], subset[outcome],
                       c=[cmap(i)], alpha=0.4, s=15)

        ax2.set_xlabel(row['predictor_label'], fontsize=11)
        ax2.set_ylabel(row['outcome_label'], fontsize=11)

        fig.suptitle(f"H1: {row['predictor_label']} -> {row['outcome_label']}\n"
                    f"(Dimension: {row['dimension']})",
                    fontsize=13, fontweight='bold')

        plt.tight_layout()
        safe_pred = predictor.replace('incidence_mean_', '').replace('health_', '')[:15]
        safe_out = outcome.replace('UAI_', '').replace('idx_', '')[:15]
        fname = f"h1_scatter_{safe_pred}_{safe_out}.png"
        plt.savefig(os.path.join(FIG_DIR, fname), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  [SAVED] {fname}")


def plot_dimension_summary(best_df, filename):
    """Summary bar plot: coefficient by dimension for each governance variable"""
    print(f"\n  Generating dimension summary...")

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, outcome in enumerate(GOVERNANCE_VARS.keys()):
        ax = axes[idx]
        subset = best_df[best_df['outcome'] == outcome].sort_values('dimension')

        if len(subset) == 0:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            continue

        colors = ['#d73027' if not sig else ('#1a9850' if c < 0 else '#fc8d59')
                  for c, sig in zip(subset['coef'], subset['significant'])]

        bars = ax.barh(range(len(subset)), subset['coef'], color=colors, edgecolor='white')

        # Annotations
        for i, (_, row) in enumerate(subset.iterrows()):
            sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
            x_pos = row['coef'] + 0.01 * np.sign(row['coef'])
            ha = 'left' if row['coef'] >= 0 else 'right'
            ax.text(x_pos, i, f"{row['best_predictor_label'][:15]} {sig}", va='center', ha=ha, fontsize=8)

        ax.set_yticks(range(len(subset)))
        ax.set_yticklabels(subset['dimension'], fontsize=9)
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
        ax.set_xlabel('beta (log-odds)', fontsize=10)
        ax.set_title(GOVERNANCE_VARS[outcome], fontsize=11, fontweight='bold')

    # Hide unused subplot
    if len(GOVERNANCE_VARS) < 6:
        axes[-1].axis('off')

    fig.suptitle('H1: Que Predice Cada Componente de Gobernanza?\n'
                 'Mejor predictor por dimension (verde=sig neg, naranja=sig pos, rojo=ns)',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANALISIS H1 - QUE PREDICE LA GOBERNANZA?")
    print("Invirtiendo la logica causal del nexus")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load data
    df = load_and_prepare_data()

    # Run analysis
    all_results, best_results = run_h1_analysis(df)

    # Save results
    all_results.to_csv(os.path.join(OUTPUT_DIR, 'h1_all_models.csv'), index=False)
    best_results.to_csv(os.path.join(OUTPUT_DIR, 'h1_best_by_dimension.csv'), index=False)
    print(f"\n  [SAVED] h1_all_models.csv ({len(all_results)} models)")
    print(f"  [SAVED] h1_best_by_dimension.csv ({len(best_results)} selections)")

    # Create sub-hypothesis tables
    for dim_key, dim in DIMENSIONS.items():
        sub_df = all_results[all_results['dimension'] == dim['label']]
        if len(sub_df) > 0:
            fname = f"h1{dim_key[0]}_{dim_key}_models.csv"
            sub_df.to_csv(os.path.join(OUTPUT_DIR, fname), index=False)
            print(f"  [SAVED] {fname}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("RESUMEN H1: MEJORES PREDICTORES DE GOBERNANZA")
    print("=" * 70)

    sig_results = best_results[best_results['significant']]
    print(f"\n  Total relaciones significativas: {len(sig_results)} de {len(best_results)}")

    print(f"\n  Por dimension (significativos):")
    for dim in best_results['dimension'].unique():
        dim_sig = sig_results[sig_results['dimension'] == dim]
        print(f"    {dim}: {len(dim_sig)} significativos")
        for _, row in dim_sig.iterrows():
            direction = '+' if row['coef'] > 0 else '-'
            print(f"      {row['best_predictor_label']:<20} -> {row['outcome_label']:<15}: "
                  f"b={row['coef']:>7.3f} ({direction}), R2m={row['r2_marginal']:.3f}")

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_selection_heatmap(best_results, 'h1_selection_heatmap.png')
    plot_dimension_summary(best_results, 'h1_dimension_summary.png')
    plot_scatter_significant(df, all_results, top_n=12)

    # Final summary
    print("\n" + "=" * 70)
    print("H1 COMPLETADO")
    print("=" * 70)
    print(f"\n  Archivos generados en: {OUTPUT_DIR}")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if not f.startswith('.'):
            print(f"    {f}")

    if os.path.exists(FIG_DIR):
        print(f"\n  Figuras en: {FIG_DIR}")
        for f in sorted(os.listdir(FIG_DIR)):
            print(f"    {f}")

    # Key finding
    print("\n  HALLAZGO PRINCIPAL:")
    if len(sig_results) > 0:
        top_finding = sig_results.sort_values('r2_marginal', ascending=False).iloc[0]
        print(f"    La relacion mas fuerte es: {top_finding['best_predictor_label']} -> {top_finding['outcome_label']}")
        print(f"    beta = {top_finding['coef']:.4f}, R2m = {top_finding['r2_marginal']:.4f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
