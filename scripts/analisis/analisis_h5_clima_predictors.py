"""
Analisis H5 - Predictores de Riesgo Climatico
Modelo: Riesgo_clima ~ Vulnerabilidad * (Biodiversidad + Gobernanza) + (1|micro)

Variable respuesta: flooding_risks, fire_risk_index, hydric_stress_risk
Identificar que predice exposicion a riesgos climaticos.

Outputs:
- Tabla de seleccion de modelos
- Scatter plots de relaciones significativas
- Mapas bivariados para modelos con 2+ predictores significativos

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
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h5_clima")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Climate outcomes
CLIMATE_OUTCOMES = {
    'flooding_risks': 'Riesgo Inundacion',
    'fire_risk_index': 'Riesgo Fuego',
    'hydric_stress_risk': 'Estres Hidrico'
}

# Predictors
BIODIV_VARS = ['forest_cover', 'mean_species_richness', 'pol_deficit']
VULN_VARS = ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena']
GOV_VARS = ['idx_gobernanza', 'UAI_env', 'UAI_Crisk']

VAR_LABELS = {
    'flooding_risks': 'Riesgo Inundacion',
    'fire_risk_index': 'Riesgo Fuego',
    'hydric_stress_risk': 'Estres Hidrico',
    'forest_cover': 'Cobertura Forestal',
    'mean_species_richness': 'Riqueza Especies',
    'pol_deficit': 'Deficit Polinizacion',
    'pct_pobreza': '% Pobreza',
    'pct_rural': '% Rural',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indigena',
    'idx_gobernanza': 'Gobernanza (idx)',
    'UAI_env': 'UAI Ambiental',
    'UAI_Crisk': 'UAI Riesgo Clim.',
    'idx_vulnerabilidad': 'Vulnerabilidad (idx)',
    'idx_biodiv': 'Biodiversidad (idx)'
}


# ============================================================
# DATA LOADING
# ============================================================

def load_and_prepare_data():
    """Load data and prepare transformations"""
    print("\n" + "=" * 70)
    print("CARGANDO Y PREPARANDO DATOS")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    print(f"Dataset: {len(df)} municipios")

    # Standardize predictors
    scaler = StandardScaler()
    all_vars = BIODIV_VARS + VULN_VARS + GOV_VARS + list(CLIMATE_OUTCOMES.keys())

    for var in all_vars:
        if var in df.columns:
            mask = df[var].notna()
            if mask.sum() > 0:
                df.loc[mask, f'{var}_z'] = scaler.fit_transform(
                    df.loc[mask, var].values.reshape(-1, 1)
                ).flatten()

    return df


# ============================================================
# MODEL FITTING
# ============================================================

def fit_climate_model(df, outcome, predictor, group_var='cod_microrregiao'):
    """Fit: climate ~ predictor + (1|group)"""
    predictor_z = f'{predictor}_z'

    if outcome not in df.columns or predictor_z not in df.columns:
        return None

    data = df[[outcome, predictor_z, group_var]].dropna()
    if len(data) < 50:
        return None

    data = data.rename(columns={outcome: 'y', predictor_z: 'x'})

    try:
        model = smf.mixedlm('y ~ x', data, groups=data[group_var])
        result = model.fit(reml=False, method='powell')

        if not result.converged:
            return None

        k = len(result.params) + 1
        n = len(data)
        aic = -2 * result.llf + 2 * k

        var_fixed = np.var(result.fittedvalues)
        var_random = float(result.cov_re.iloc[0, 0]) if hasattr(result.cov_re, 'iloc') else float(result.cov_re)
        var_resid = result.scale
        r2_marginal = var_fixed / (var_fixed + var_random + var_resid)

        return {
            'outcome': outcome,
            'predictor': predictor,
            'coef': result.params['x'],
            'se': result.bse['x'],
            'p_value': result.pvalues['x'],
            'aic': aic,
            'r2_marginal': r2_marginal,
            'n': n
        }

    except:
        return None


def fit_interaction_model(df, outcome, predictor, moderator, group_var='cod_microrregiao'):
    """Fit: climate ~ predictor * moderator + (1|group)"""
    predictor_z = f'{predictor}_z'
    moderator_z = f'{moderator}_z'

    for v in [outcome, predictor_z, moderator_z]:
        if v not in df.columns:
            return None

    data = df[[outcome, predictor_z, moderator_z, group_var]].dropna()
    if len(data) < 100:
        return None

    data = data.rename(columns={outcome: 'y', predictor_z: 'x', moderator_z: 'm'})

    try:
        model_full = smf.mixedlm('y ~ x * m', data, groups=data[group_var])
        result_full = model_full.fit(reml=False, method='powell')

        if not result_full.converged:
            return None

        model_add = smf.mixedlm('y ~ x + m', data, groups=data[group_var])
        result_add = model_add.fit(reml=False, method='powell')

        k_full = len(result_full.params) + 1
        k_add = len(result_add.params) + 1
        n = len(data)
        aic_full = -2 * result_full.llf + 2 * k_full
        aic_add = -2 * result_add.llf + 2 * k_add

        int_coef = result_full.params.get('x:m', np.nan)
        int_p = result_full.pvalues.get('x:m', 1.0)

        var_fixed = np.var(result_full.fittedvalues)
        var_random = float(result_full.cov_re.iloc[0, 0]) if hasattr(result_full.cov_re, 'iloc') else float(result_full.cov_re)
        var_resid = result_full.scale
        r2_marginal = var_fixed / (var_fixed + var_random + var_resid)

        return {
            'outcome': outcome,
            'predictor': predictor,
            'moderator': moderator,
            'coef_predictor': result_full.params['x'],
            'p_predictor': result_full.pvalues['x'],
            'coef_moderator': result_full.params['m'],
            'p_moderator': result_full.pvalues['m'],
            'coef_interaction': int_coef,
            'p_interaction': int_p,
            'aic_interaction': aic_full,
            'aic_additive': aic_add,
            'delta_aic': aic_full - aic_add,
            'r2_marginal': r2_marginal,
            'n': n
        }

    except:
        return None


def run_model_selection(df, outcome):
    """Run model selection for one climate outcome"""
    all_predictors = BIODIV_VARS + VULN_VARS + GOV_VARS
    results = []

    for predictor in all_predictors:
        result = fit_climate_model(df, outcome, predictor)
        if result:
            if predictor in BIODIV_VARS:
                result['dimension'] = 'Biodiversidad'
            elif predictor in VULN_VARS:
                result['dimension'] = 'Vulnerabilidad'
            else:
                result['dimension'] = 'Gobernanza'
            results.append(result)

    if not results:
        return pd.DataFrame()

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('aic')
    results_df['delta_aic'] = results_df['aic'] - results_df['aic'].min()
    results_df['aic_weight'] = np.exp(-0.5 * results_df['delta_aic'])
    results_df['aic_weight'] = results_df['aic_weight'] / results_df['aic_weight'].sum()

    return results_df


def run_h5_analysis(df):
    """Run complete H5 analysis"""
    print("\n" + "=" * 70)
    print("H5: PREDICTORES DE RIESGO CLIMATICO")
    print("Modelo: clima ~ predictor + (1|micro)")
    print("=" * 70)

    all_results = []
    best_by_outcome = []

    for outcome in CLIMATE_OUTCOMES.keys():
        print(f"\n{'='*60}")
        print(f"OUTCOME: {CLIMATE_OUTCOMES[outcome]}")
        print(f"{'='*60}")

        results_df = run_model_selection(df, outcome)

        if len(results_df) == 0:
            continue

        all_results.append(results_df)

        print(f"\n  {'Predictor':<25} {'Dim':<15} {'beta':>10} {'p':>10} {'dAIC':>8} {'R2m':>8}")
        print(f"  {'-'*76}")

        for _, row in results_df.iterrows():
            sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
            marker = ' << BEST' if row['delta_aic'] == 0 else (' ~ equiv' if row['delta_aic'] < 2 else '')
            print(f"  {VAR_LABELS.get(row['predictor'], row['predictor']):<25} "
                  f"{row['dimension']:<15} {row['coef']:>10.4f}{sig:<3} "
                  f"{row['p_value']:>9.4f} {row['delta_aic']:>8.2f} {row['r2_marginal']:>8.4f}{marker}")

        best = results_df.iloc[0]
        equiv = results_df[results_df['delta_aic'] < 2]
        best_by_outcome.append({
            'outcome': outcome,
            'outcome_label': CLIMATE_OUTCOMES[outcome],
            'best_predictor': best['predictor'],
            'best_predictor_label': VAR_LABELS.get(best['predictor'], best['predictor']),
            'dimension': best['dimension'],
            'coef': best['coef'],
            'p_value': best['p_value'],
            'aic': best['aic'],
            'r2_marginal': best['r2_marginal'],
            'n_equivalent': len(equiv),
            'equivalent_vars': ', '.join(equiv['predictor'].tolist())
        })

    all_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    best_df = pd.DataFrame(best_by_outcome)

    return all_df, best_df


def run_interaction_analysis(df):
    """Run vulnerability × biodiversity/governance interactions"""
    print("\n" + "=" * 70)
    print("H5b: INTERACCIONES VULNERABILIDAD x (BIODIV/GOB) -> CLIMA")
    print("=" * 70)

    results = []

    for outcome in CLIMATE_OUTCOMES.keys():
        print(f"\n  {CLIMATE_OUTCOMES[outcome]}:")

        for vuln in VULN_VARS:
            for predictor in BIODIV_VARS + GOV_VARS:
                result = fit_interaction_model(df, outcome, predictor, vuln)
                if result:
                    results.append(result)

    results_df = pd.DataFrame(results)

    # Print significant interactions
    sig = results_df[results_df['p_interaction'] < 0.05]
    if len(sig) > 0:
        print(f"\n  Interacciones significativas:")
        for _, row in sig.iterrows():
            print(f"    {VAR_LABELS.get(row['predictor'], row['predictor'])} x "
                  f"{VAR_LABELS.get(row['moderator'], row['moderator'])} -> "
                  f"{CLIMATE_OUTCOMES.get(row['outcome'], row['outcome'])}: "
                  f"b={row['coef_interaction']:.4f}, p={row['p_interaction']:.4f}")

    return results_df


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_selection_heatmap(all_df, filename):
    """Heatmap of predictor effects"""
    print(f"\n  Generating selection heatmap...")

    pivot = all_df.pivot_table(
        values='coef',
        index='outcome',
        columns='predictor',
        aggfunc='first'
    )

    pivot_p = all_df.pivot_table(
        values='p_value',
        index='outcome',
        columns='predictor',
        aggfunc='first'
    )

    pivot.index = [CLIMATE_OUTCOMES.get(i, i) for i in pivot.index]
    pivot.columns = [VAR_LABELS.get(c, c) for c in pivot.columns]
    pivot_p.index = [CLIMATE_OUTCOMES.get(i, i) for i in pivot_p.index]
    pivot_p.columns = [VAR_LABELS.get(c, c) for c in pivot_p.columns]

    fig, ax = plt.subplots(figsize=(14, 6))

    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'beta'})

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            p = pivot_p.iloc[i, j]
            if pd.notna(p) and p < 0.05:
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*'
                ax.text(j + 0.5, i + 0.8, sig, ha='center', va='center',
                       fontsize=7, fontweight='bold')

    ax.set_title('H5: Predictores de Riesgo Climatico\n'
                 'Modelo: clima ~ predictor + (1|micro) | *** p<0.001',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Predictor', fontsize=11)
    ax.set_ylabel('Riesgo Climatico', fontsize=11)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_scatter_significant(df, all_df, top_n=6):
    """Scatter plots for significant relationships"""
    print(f"\n  Generating scatter plots...")

    sig_df = all_df[all_df['p_value'] < 0.05].sort_values('r2_marginal', ascending=False)

    for _, row in sig_df.head(top_n).iterrows():
        outcome = row['outcome']
        predictor = row['predictor']

        if outcome not in df.columns or predictor not in df.columns:
            continue

        data = df[[outcome, predictor, 'cod_mesorregiao', 'nome_mesorregiao']].dropna()
        if len(data) < 50:
            continue

        fig, ax = plt.subplots(figsize=(10, 7))

        meso_codes = sorted(data['cod_mesorregiao'].unique())
        cmap = plt.cm.get_cmap('tab20', len(meso_codes))

        for i, meso in enumerate(meso_codes):
            subset = data[data['cod_mesorregiao'] == meso]
            ax.scatter(subset[predictor], subset[outcome],
                      c=[cmap(i)], alpha=0.4, s=15)

        slope, intercept, r, p, se = stats.linregress(data[predictor], data[outcome])
        x_range = np.linspace(data[predictor].min(), data[predictor].max(), 100)
        ax.plot(x_range, intercept + slope * x_range, 'k-', linewidth=2)

        r_sp, p_sp = stats.spearmanr(data[predictor], data[outcome])
        stats_text = (f"Mixed model:\nbeta = {row['coef']:.4f}\np = {row['p_value']:.2e}\n"
                     f"R2m = {row['r2_marginal']:.4f}\n\nSpearman r = {r_sp:.3f}")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
               va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        ax.set_xlabel(VAR_LABELS.get(predictor, predictor), fontsize=11)
        ax.set_ylabel(CLIMATE_OUTCOMES.get(outcome, outcome), fontsize=11)
        ax.set_title(f'H5: {VAR_LABELS.get(predictor, predictor)} -> {CLIMATE_OUTCOMES.get(outcome, outcome)}',
                    fontsize=12, fontweight='bold')

        plt.tight_layout()
        safe_pred = predictor.replace('pct_', '').replace('idx_', '')[:15]
        safe_out = outcome.replace('_risk', '').replace('_index', '')[:15]
        fname = f"h5_scatter_{safe_pred}_{safe_out}.png"
        plt.savefig(os.path.join(FIG_DIR, fname), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  [SAVED] {fname}")


def plot_bivariate_map(df, var1, var2, filename):
    """Bivariate choropleth map"""
    print(f"\n  Generating bivariate map: {var1} x {var2}...")

    try:
        import geopandas as gpd
        from glob import glob

        shp_files = glob(os.path.join(BASE_DIR, "data/geo/**/*.shp"), recursive=True)
        if not shp_files:
            print("  [SKIP] No shapefile found")
            return

        gdf = gpd.read_file(shp_files[0])

        # Match codes
        code_col = None
        for col in gdf.columns:
            if 'cod' in col.lower() and ('mun' in col.lower() or 'ibge' in col.lower()):
                code_col = col
                break
        if code_col is None:
            code_col = [c for c in gdf.columns if c.startswith('CD_')][0] if any(c.startswith('CD_') for c in gdf.columns) else None

        if code_col is None:
            print("  [SKIP] Cannot find code column in shapefile")
            return

        # IBGE shapefile uses 7-digit codes (with verification digit)
        # CSV uses 6-digit codes (without verification digit)
        # Solution: truncate shapefile codes to 6 digits
        gdf['cod_ibge'] = gdf[code_col].astype(str).str[:6].astype(int)

        merged = gdf.merge(df[['cod_ibge', var1, var2]], on='cod_ibge', how='left')

        # Bivariate classes
        q1 = merged[var1].quantile([0.33, 0.66]).values
        q2 = merged[var2].quantile([0.33, 0.66]).values

        def bivar_class(row):
            if pd.isna(row[var1]) or pd.isna(row[var2]):
                return -1
            x = 0 if row[var1] <= q1[0] else (1 if row[var1] <= q1[1] else 2)
            y = 0 if row[var2] <= q2[0] else (1 if row[var2] <= q2[1] else 2)
            return x * 3 + y

        merged['bivar_class'] = merged.apply(bivar_class, axis=1)

        colors_9 = [
            '#e8e8e8', '#ace4e4', '#5ac8c8',
            '#dfb0d6', '#a5add3', '#5698b9',
            '#be64ac', '#8c62aa', '#3b4994',
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
        ax.set_title(f'H5: Mapa Bivariado\n{VAR_LABELS.get(var1, var1)} x {VAR_LABELS.get(var2, var2)}',
                    fontsize=14, fontweight='bold')

        plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
        plt.close()
        print(f"  [SAVED] {filename}")

    except ImportError:
        print("  [SKIP] geopandas not available")
    except Exception as e:
        print(f"  [ERROR] {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANALISIS H5 - PREDICTORES DE RIESGO CLIMATICO")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load data
    df = load_and_prepare_data()

    # Main analysis
    all_results, best_results = run_h5_analysis(df)

    # Interaction analysis
    interaction_results = run_interaction_analysis(df)

    # Save
    all_results.to_csv(os.path.join(OUTPUT_DIR, 'h5_all_models.csv'), index=False)
    best_results.to_csv(os.path.join(OUTPUT_DIR, 'h5_best_predictors.csv'), index=False)
    interaction_results.to_csv(os.path.join(OUTPUT_DIR, 'h5_interactions.csv'), index=False)

    print(f"\n  [SAVED] h5_all_models.csv ({len(all_results)} models)")
    print(f"  [SAVED] h5_best_predictors.csv ({len(best_results)} selections)")
    print(f"  [SAVED] h5_interactions.csv ({len(interaction_results)} models)")

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_selection_heatmap(all_results, 'h5_selection_heatmap.png')
    plot_scatter_significant(df, all_results)

    # Bivariate maps for significant pairs
    print("\n  Generating bivariate maps...")
    sig_results = all_results[all_results['p_value'] < 0.01]
    bivar_pairs_done = set()

    for _, row in sig_results.head(6).iterrows():
        var1 = row['outcome']
        var2 = row['predictor']
        pair_key = tuple(sorted([var1, var2]))
        if pair_key not in bivar_pairs_done:
            safe_v1 = var1.replace('_risk', '').replace('_index', '')[:10]
            safe_v2 = var2.replace('pct_', '').replace('idx_', '')[:10]
            plot_bivariate_map(df, var1, var2, f'h5_bivar_{safe_v1}_{safe_v2}.png')
            bivar_pairs_done.add(pair_key)

    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN H5: MEJORES PREDICTORES DE RIESGO CLIMATICO")
    print("=" * 70)

    print(f"\n  {'Riesgo Clim.':<20} {'Mejor Predictor':<25} {'Dim':<15} {'beta':>10} {'p':>10}")
    print(f"  {'-'*80}")
    for _, row in best_results.iterrows():
        sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
        print(f"  {row['outcome_label']:<20} {row['best_predictor_label']:<25} "
              f"{row['dimension']:<15} {row['coef']:>10.4f}{sig:<3} {row['p_value']:>9.4f}")

    # Key finding
    print("\n" + "=" * 70)
    print("HALLAZGO PRINCIPAL H5")
    print("=" * 70)

    sig_gov = all_results[(all_results['dimension'] == 'Gobernanza') & (all_results['p_value'] < 0.05)]
    if len(sig_gov) > 0:
        print(f"\n  Gobernanza predice riesgo climatico:")
        for _, row in sig_gov.iterrows():
            direction = 'MAYOR' if row['coef'] > 0 else 'MENOR'
            print(f"    Mayor {VAR_LABELS.get(row['predictor'], row['predictor'])} asociado con "
                  f"{direction} {CLIMATE_OUTCOMES.get(row['outcome'], row['outcome'])}")

    print("\nDone!")


if __name__ == "__main__":
    main()
