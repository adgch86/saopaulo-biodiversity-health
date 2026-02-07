"""
Analisis H2 - Interaccion Vulnerabilidad x Otras Dimensiones -> Gobernanza
Modelo: logit(Gobernanza) ~ Vulnerabilidad * (Riesgo_clima + Riesgo_Salud + Biodiversidad)

- Usa las variables de vulnerabilidad que mejor explicaron gobernanza en H1.d
- Efecto modulador de vulnerabilidad sobre las otras dimensiones
- Una variable por dimension por modelo (evitar colinealidad)
- Sin interacciones triples

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
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h2_vulnerabilidad")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Governance outcomes
GOVERNANCE_OUTCOMES = ['idx_gobernanza', 'UAI_Crisk', 'UAI_env']

# Vulnerability moderators (to be refined based on H1 results)
VULNERABILITY_VARS = ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena', 'idx_vulnerabilidad']

# Predictors from other dimensions (one per dimension)
OTHER_DIM_VARS = {
    'clima': ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk'],
    'salud': ['incidence_mean_dengue', 'incidence_mean_malaria', 'health_death_circ_mean'],
    'biodiversidad': ['forest_cover', 'mean_species_richness', 'pol_deficit']
}

VAR_LABELS = {
    'idx_gobernanza': 'Gobernanza (idx)',
    'UAI_Crisk': 'UAI Riesgo Clim.',
    'UAI_env': 'UAI Ambiental',
    'pct_pobreza': '% Pobreza',
    'pct_rural': '% Rural',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indigena',
    'idx_vulnerabilidad': 'Vulnerabilidad (idx)',
    'flooding_risks': 'Riesgo Inundacion',
    'fire_risk_index': 'Riesgo Fuego',
    'hydric_stress_risk': 'Estres Hidrico',
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'health_death_circ_mean': 'Mort. Cardiovasc.',
    'forest_cover': 'Cobertura Forestal',
    'mean_species_richness': 'Riqueza Especies',
    'pol_deficit': 'Deficit Polinizacion'
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

    # Standardize all predictors
    scaler = StandardScaler()
    all_vars = VULNERABILITY_VARS.copy()
    for vars_list in OTHER_DIM_VARS.values():
        all_vars.extend(vars_list)

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

def fit_interaction_model(df, outcome, moderator, predictor, group_var='cod_microrregiao'):
    """
    Fit: logit(outcome) ~ predictor * moderator + (1|group)
    Returns main effects, interaction, and model stats
    """
    outcome_logit = f'{outcome}_logit'
    mod_z = f'{moderator}_z'
    pred_z = f'{predictor}_z'

    # Check variables exist
    required = [outcome_logit, mod_z, pred_z, group_var]
    for v in required:
        if v not in df.columns:
            return None

    data = df[[outcome_logit, mod_z, pred_z, group_var]].dropna()
    if len(data) < 100:
        return None

    data = data.rename(columns={outcome_logit: 'y', mod_z: 'm', pred_z: 'x'})

    try:
        # Full model with interaction
        model_full = smf.mixedlm('y ~ x * m', data, groups=data[group_var])
        result_full = model_full.fit(reml=False, method='powell')

        if not result_full.converged:
            return None

        # Model without interaction (for comparison)
        model_add = smf.mixedlm('y ~ x + m', data, groups=data[group_var])
        result_add = model_add.fit(reml=False, method='powell')

        # Compute AICs
        k_full = len(result_full.params) + 1
        k_add = len(result_add.params) + 1
        n = len(data)
        aic_full = -2 * result_full.llf + 2 * k_full
        aic_add = -2 * result_add.llf + 2 * k_add

        # Marginal R2
        var_fixed = np.var(result_full.fittedvalues)
        var_random = float(result_full.cov_re.iloc[0, 0]) if hasattr(result_full.cov_re, 'iloc') else float(result_full.cov_re)
        var_resid = result_full.scale
        r2_marginal = var_fixed / (var_fixed + var_random + var_resid)

        # Check for interaction term
        if 'x:m' in result_full.params:
            int_coef = result_full.params['x:m']
            int_se = result_full.bse['x:m']
            int_p = result_full.pvalues['x:m']
        else:
            int_coef = np.nan
            int_se = np.nan
            int_p = 1.0

        return {
            'outcome': outcome,
            'moderator': moderator,
            'predictor': predictor,
            'coef_predictor': result_full.params['x'],
            'p_predictor': result_full.pvalues['x'],
            'coef_moderator': result_full.params['m'],
            'p_moderator': result_full.pvalues['m'],
            'coef_interaction': int_coef,
            'se_interaction': int_se,
            'p_interaction': int_p,
            'aic_interaction': aic_full,
            'aic_additive': aic_add,
            'delta_aic': aic_full - aic_add,  # negative = interaction model better
            'r2_marginal': r2_marginal,
            'n': n,
            'interaction_significant': int_p < 0.05 if pd.notna(int_p) else False,
            'interaction_improves_fit': aic_full < aic_add
        }

    except Exception as e:
        return None


def run_h2_analysis(df):
    """Run all interaction models"""
    print("\n" + "=" * 70)
    print("H2: INTERACCION VULNERABILIDAD x OTRAS DIMENSIONES -> GOBERNANZA")
    print("Modelo: logit(Gob) ~ Predictor * Vulnerabilidad + (1|micro)")
    print("=" * 70)

    results = []

    for outcome in GOVERNANCE_OUTCOMES:
        print(f"\n{'='*60}")
        print(f"OUTCOME: {VAR_LABELS.get(outcome, outcome)}")
        print(f"{'='*60}")

        for moderator in VULNERABILITY_VARS:
            print(f"\n  Moderador: {VAR_LABELS.get(moderator, moderator)}")
            print(f"  {'Predictor':<25} {'b_int':>10} {'p_int':>10} {'dAIC':>10} {'Signif':>8}")
            print(f"  {'-'*63}")

            for dim_key, predictors in OTHER_DIM_VARS.items():
                for predictor in predictors:
                    result = fit_interaction_model(df, outcome, moderator, predictor)

                    if result is None:
                        continue

                    results.append(result)

                    sig_marker = '***' if result['p_interaction'] < 0.001 else '**' if result['p_interaction'] < 0.01 else '*' if result['p_interaction'] < 0.05 else 'ns'
                    fit_marker = '<< MEJOR' if result['interaction_improves_fit'] and result['interaction_significant'] else ''

                    print(f"  {VAR_LABELS.get(predictor, predictor):<25} "
                          f"{result['coef_interaction']:>10.4f} {result['p_interaction']:>10.4f} "
                          f"{result['delta_aic']:>10.2f} {sig_marker:>8} {fit_marker}")

    results_df = pd.DataFrame(results)
    return results_df


# ============================================================
# SIMPLE SLOPES ANALYSIS
# ============================================================

def compute_simple_slopes(df, outcome, moderator, predictor, levels=[-1, 0, 1]):
    """
    Compute simple slopes at low (-1 SD), mean (0), high (+1 SD) of moderator
    """
    outcome_logit = f'{outcome}_logit'
    mod_z = f'{moderator}_z'
    pred_z = f'{predictor}_z'

    data = df[[outcome_logit, mod_z, pred_z, 'cod_microrregiao']].dropna()
    if len(data) < 100:
        return None

    data = data.rename(columns={outcome_logit: 'y', mod_z: 'm', pred_z: 'x'})

    try:
        model = smf.mixedlm('y ~ x * m', data, groups=data['cod_microrregiao'])
        result = model.fit(reml=False, method='powell')

        if not result.converged:
            return None

        # Simple slopes: dy/dx = b_x + b_int * m
        b_x = result.params['x']
        b_int = result.params.get('x:m', 0)
        var_bx = result.cov_params().loc['x', 'x']
        var_bint = result.cov_params().loc['x:m', 'x:m'] if 'x:m' in result.cov_params().index else 0
        cov_bx_bint = result.cov_params().loc['x', 'x:m'] if 'x:m' in result.cov_params().index else 0

        slopes = []
        for level in levels:
            slope = b_x + b_int * level
            se = np.sqrt(var_bx + (level ** 2) * var_bint + 2 * level * cov_bx_bint)
            t = slope / se
            p = 2 * (1 - stats.t.cdf(abs(t), len(data) - 4))

            level_name = 'Low (-1 SD)' if level == -1 else ('Mean' if level == 0 else 'High (+1 SD)')
            slopes.append({
                'level': level,
                'level_name': level_name,
                'slope': slope,
                'se': se,
                't': t,
                'p': p
            })

        return pd.DataFrame(slopes)

    except:
        return None


def plot_simple_slopes(df, outcome, moderator, predictor, filename):
    """Plot simple slopes at different levels of moderator"""
    outcome_logit = f'{outcome}_logit'
    mod_z = f'{moderator}_z'
    pred_z = f'{predictor}_z'

    data = df[[outcome_logit, mod_z, pred_z, 'cod_microrregiao']].dropna()
    if len(data) < 100:
        return

    data = data.rename(columns={outcome_logit: 'y', mod_z: 'm', pred_z: 'x'})

    try:
        model = smf.mixedlm('y ~ x * m', data, groups=data['cod_microrregiao'])
        result = model.fit(reml=False, method='powell')

        if not result.converged:
            return

        fig, ax = plt.subplots(figsize=(10, 7))

        # Plot at 3 levels of moderator
        x_range = np.linspace(data['x'].min(), data['x'].max(), 100)
        colors = ['#1a9850', '#fc8d59', '#d73027']  # green, orange, red
        levels = [data['m'].quantile(0.1), data['m'].median(), data['m'].quantile(0.9)]
        level_names = ['Low (P10)', 'Medium (P50)', 'High (P90)']

        b0 = result.params['Intercept']
        b_x = result.params['x']
        b_m = result.params['m']
        b_int = result.params.get('x:m', 0)

        for level, name, color in zip(levels, level_names, colors):
            y_pred = b0 + b_x * x_range + b_m * level + b_int * x_range * level
            ax.plot(x_range, y_pred, color=color, linewidth=2.5,
                    label=f'{name} {VAR_LABELS.get(moderator, moderator)}', zorder=3)

        # Scatter underlying data - colored by moderator value
        scatter = ax.scatter(data['x'], data['y'], alpha=0.4, s=15,
                            c=data['m'], cmap='RdYlGn_r', edgecolors='none',
                            zorder=1)
        cbar = plt.colorbar(scatter, ax=ax, pad=0.02, shrink=0.85)
        cbar.set_label(f'{VAR_LABELS.get(moderator, moderator)} (z-score)', fontsize=10)
        cbar.ax.tick_params(labelsize=9)

        # Stats
        int_p = result.pvalues.get('x:m', 1)
        sig = '***' if int_p < 0.001 else '**' if int_p < 0.01 else '*' if int_p < 0.05 else 'ns'
        stats_text = (f"Interaccion: b = {b_int:.4f} ({sig})\n"
                     f"p = {int_p:.4f}")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        ax.set_xlabel(f'{VAR_LABELS.get(predictor, predictor)} (z)', fontsize=11)
        ax.set_ylabel(f'logit({VAR_LABELS.get(outcome, outcome)})', fontsize=11)
        ax.set_title(f'H2: Efecto de {VAR_LABELS.get(predictor, predictor)} sobre Gobernanza\n'
                    f'Moderado por {VAR_LABELS.get(moderator, moderator)}',
                    fontsize=12, fontweight='bold')
        ax.legend(loc='lower right')

        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, filename), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  [SAVED] {filename}")

    except Exception as e:
        print(f"  [ERROR] Could not plot {filename}: {e}")


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_heatmap_2d(df, outcome, moderator, predictor, filename):
    """
    Heatmap 2D: hexbin of predictor vs governance outcome,
    colored by mean moderator value (e.g., poverty) per hexagon.
    """
    outcome_logit = f'{outcome}_logit'
    mod_z = f'{moderator}_z'
    pred_z = f'{predictor}_z'

    data = df[[outcome_logit, mod_z, pred_z]].dropna()
    if len(data) < 100:
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # --- Panel A: Hexbin colored by mean moderator value ---
    ax1 = axes[0]
    hb = ax1.hexbin(data[pred_z], data[outcome_logit],
                    C=data[mod_z], reduce_C_function=np.mean,
                    gridsize=25, cmap='RdYlGn_r', mincnt=3, edgecolors='white',
                    linewidths=0.3)
    cb1 = plt.colorbar(hb, ax=ax1, pad=0.02, shrink=0.85)
    cb1.set_label(f'Mean {VAR_LABELS.get(moderator, moderator)} (z)', fontsize=10)
    ax1.set_xlabel(f'{VAR_LABELS.get(predictor, predictor)} (z)', fontsize=11)
    ax1.set_ylabel(f'logit({VAR_LABELS.get(outcome, outcome)})', fontsize=11)
    ax1.set_title('A) Hexbin: Mean moderator per cell', fontsize=11, fontweight='bold')

    # --- Panel B: KDE contours by moderator tercile ---
    ax2 = axes[1]
    terciles = pd.qcut(data[mod_z], 3, labels=['Low', 'Medium', 'High'])
    kde_colors = {'Low': '#1a9850', 'Medium': '#fc8d59', 'High': '#d73027'}

    # Background scatter
    ax2.scatter(data[pred_z], data[outcome_logit], alpha=0.08, s=5, c='gray', zorder=1)

    for label in ['Low', 'Medium', 'High']:
        subset = data[terciles == label]
        if len(subset) < 30:
            continue
        try:
            sns.kdeplot(x=subset[pred_z], y=subset[outcome_logit],
                       ax=ax2, color=kde_colors[label], levels=3,
                       linewidths=1.5, label=f'{label} {VAR_LABELS.get(moderator, moderator)}',
                       warn_singular=False)
        except Exception:
            pass

    ax2.set_xlabel(f'{VAR_LABELS.get(predictor, predictor)} (z)', fontsize=11)
    ax2.set_ylabel(f'logit({VAR_LABELS.get(outcome, outcome)})', fontsize=11)
    ax2.set_title('B) KDE contours by moderator tercile', fontsize=11, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=9)

    fig.suptitle(f'H2 Heatmap: {VAR_LABELS.get(predictor, predictor)} vs Gobernanza\n'
                 f'Coloreado por {VAR_LABELS.get(moderator, moderator)}',
                 fontsize=13, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_interaction_heatmap(results_df, filename):
    """Heatmap of interaction coefficients"""
    print(f"\n  Generating interaction heatmap...")

    # Filter significant interactions
    sig_df = results_df[results_df['interaction_significant']]

    if len(sig_df) == 0:
        print("  No significant interactions found")
        return

    # Create label columns
    sig_df = sig_df.copy()
    sig_df['predictor_label'] = sig_df['predictor'].map(VAR_LABELS)
    sig_df['moderator_label'] = sig_df['moderator'].map(VAR_LABELS)

    # Pivot
    pivot = sig_df.pivot_table(
        values='coef_interaction',
        index='predictor_label',
        columns='moderator_label',
        aggfunc='first'
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Coef. Interaccion'})

    ax.set_title('H2: Coeficientes de Interaccion Significativos (p<0.05)\n'
                 'Vulnerabilidad x Otras Dimensiones -> Gobernanza',
                 fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_summary_forest(results_df, filename):
    """Forest plot of interaction effects"""
    print(f"\n  Generating forest plot...")

    # Filter models where interaction improves fit
    good_models = results_df[results_df['interaction_improves_fit']].copy()

    if len(good_models) == 0:
        print("  No models where interaction improves fit")
        return

    # Sort by interaction coefficient
    good_models = good_models.sort_values('coef_interaction')
    good_models['label'] = (good_models['predictor'].map(VAR_LABELS) + ' x ' +
                           good_models['moderator'].map(VAR_LABELS))

    fig, ax = plt.subplots(figsize=(12, max(6, len(good_models) * 0.3)))

    y_pos = range(len(good_models))
    colors = ['#1a9850' if p < 0.05 else '#d73027' for p in good_models['p_interaction']]

    ax.barh(y_pos, good_models['coef_interaction'], color=colors, edgecolor='white', height=0.6)

    # Error bars
    for i, (_, row) in enumerate(good_models.iterrows()):
        ci = 1.96 * row['se_interaction']
        ax.plot([row['coef_interaction'] - ci, row['coef_interaction'] + ci],
               [i, i], color='black', linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(good_models['label'], fontsize=9)
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlabel('Coeficiente de Interaccion', fontsize=11)
    ax.set_title('H2: Interacciones que Mejoran el Ajuste (dAIC < 0)\n'
                 'Verde = p<0.05, Rojo = p>=0.05',
                 fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANALISIS H2 - INTERACCION VULNERABILIDAD x OTRAS DIMENSIONES")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load data
    df = load_and_prepare_data()

    # Run analysis
    results_df = run_h2_analysis(df)

    # Save results
    results_df.to_csv(os.path.join(OUTPUT_DIR, 'h2_interactions.csv'), index=False)
    print(f"\n  [SAVED] h2_interactions.csv ({len(results_df)} models)")

    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN H2: INTERACCIONES SIGNIFICATIVAS")
    print("=" * 70)

    sig_results = results_df[results_df['interaction_significant']]
    print(f"\n  Interacciones significativas: {len(sig_results)} de {len(results_df)}")

    if len(sig_results) > 0:
        print(f"\n  {'Outcome':<20} {'Moderador':<20} {'Predictor':<20} {'b_int':>10} {'p':>10}")
        print(f"  {'-'*80}")
        for _, row in sig_results.sort_values('p_interaction').iterrows():
            print(f"  {VAR_LABELS.get(row['outcome'], row['outcome']):<20} "
                  f"{VAR_LABELS.get(row['moderator'], row['moderator']):<20} "
                  f"{VAR_LABELS.get(row['predictor'], row['predictor']):<20} "
                  f"{row['coef_interaction']:>10.4f} {row['p_interaction']:>10.4f}")

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_interaction_heatmap(results_df, 'h2_interaction_heatmap.png')
    plot_summary_forest(results_df, 'h2_forest_plot.png')

    # Simple slopes for significant interactions
    print("\n  Generating simple slopes plots...")
    for _, row in sig_results.head(6).iterrows():
        safe_mod = row['moderator'].replace('pct_', '').replace('idx_', '')[:10]
        safe_pred = row['predictor'].replace('incidence_mean_', '').replace('health_', '')[:10]
        fname = f"h2_slopes_{safe_pred}_{safe_mod}.png"
        plot_simple_slopes(df, row['outcome'], row['moderator'], row['predictor'], fname)

    # 2D Heatmaps for significant interactions
    print("\n  Generating 2D heatmaps...")
    for _, row in sig_results.head(6).iterrows():
        safe_mod = row['moderator'].replace('pct_', '').replace('idx_', '')[:10]
        safe_pred = row['predictor'].replace('incidence_mean_', '').replace('health_', '')[:10]
        fname = f"h2_heatmap_{safe_pred}_{safe_mod}.png"
        plot_heatmap_2d(df, row['outcome'], row['moderator'], row['predictor'], fname)

    # Key finding
    print("\n" + "=" * 70)
    print("HALLAZGO PRINCIPAL H2")
    print("=" * 70)

    if len(sig_results) > 0:
        top = sig_results.sort_values('p_interaction').iloc[0]
        print(f"\n  La interaccion mas significativa es:")
        print(f"    {VAR_LABELS.get(top['predictor'], top['predictor'])} x "
              f"{VAR_LABELS.get(top['moderator'], top['moderator'])} -> "
              f"{VAR_LABELS.get(top['outcome'], top['outcome'])}")
        print(f"    b_interaccion = {top['coef_interaction']:.4f}, p = {top['p_interaction']:.4f}")

        if top['coef_interaction'] > 0:
            print(f"    Interpretacion: El efecto de {VAR_LABELS.get(top['predictor'], top['predictor'])} sobre gobernanza")
            print(f"    es MAS FUERTE en municipios con mayor {VAR_LABELS.get(top['moderator'], top['moderator'])}")
        else:
            print(f"    Interpretacion: El efecto de {VAR_LABELS.get(top['predictor'], top['predictor'])} sobre gobernanza")
            print(f"    es MAS DEBIL en municipios con mayor {VAR_LABELS.get(top['moderator'], top['moderator'])}")
    else:
        print("\n  No se encontraron interacciones significativas.")
        print("  Esto sugiere que el efecto de las dimensiones sobre gobernanza")
        print("  no varia significativamente segun nivel de vulnerabilidad.")

    print("\nDone!")


if __name__ == "__main__":
    main()
