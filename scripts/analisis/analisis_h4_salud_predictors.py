"""
Analisis H4 - Predictores de Riesgo de Salud
Modelo: Riesgo_Salud ~ Vulnerabilidad * (Riesgo_clima + Biodiversidad) + (1|micro)

Preocupacion de Adrian: La relacion bosque-dengue esta mediada por tamano poblacional?
(mas bosque = menos gente = menos casos)

Validacion:
- Controlar por poblacion
- Comparar coeficientes con/sin control
- Si cambia significativamente -> efecto confundido por urbanizacion

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
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h4_salud")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Health outcomes (already as rates per 100k)
HEALTH_OUTCOMES = {
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_diarrhea_mean': 'Diarrea',
    'health_death_circ_mean': 'Mort. Cardiovasc.',
    'health_hosp_resp_mean': 'Hosp. Respiratoria'
}

# Predictors by dimension
BIODIV_VARS = ['forest_cover', 'mean_species_richness', 'pol_deficit']
CLIMATE_VARS = ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk']
VULN_VARS = ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena']

# Urbanization controls (for dilution effect validation)
URBAN_CONTROLS = ['population', 'pct_rural', 'pct_urbana']

VAR_LABELS = {
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_diarrhea_mean': 'Diarrea',
    'health_death_circ_mean': 'Mort. Cardiovasc.',
    'health_hosp_resp_mean': 'Hosp. Respiratoria',
    'forest_cover': 'Cobertura Forestal',
    'mean_species_richness': 'Riqueza Especies',
    'pol_deficit': 'Deficit Polinizacion',
    'flooding_risks': 'Riesgo Inundacion',
    'fire_risk_index': 'Riesgo Fuego',
    'hydric_stress_risk': 'Estres Hidrico',
    'pct_pobreza': '% Pobreza',
    'pct_rural': '% Rural',
    'pct_preta': '% Pob. Negra',
    'pct_indigena': '% Pob. Indigena',
    'population': 'Poblacion',
    'log_population': 'log(Poblacion)'
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

    # Log-transform health outcomes for normality
    for var in HEALTH_OUTCOMES.keys():
        if var in df.columns:
            # Add small constant to handle zeros
            df[f'{var}_log'] = np.log1p(df[var])

    # Log-transform population
    if 'population' in df.columns:
        df['log_population'] = np.log(df['population'])

    # Standardize predictors
    scaler = StandardScaler()
    all_vars = BIODIV_VARS + CLIMATE_VARS + VULN_VARS + ['log_population']

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

def fit_health_model(df, outcome, predictor, controls=None, group_var='cod_microrregiao'):
    """
    Fit: log(health) ~ predictor [+ controls] + (1|group)
    """
    outcome_log = f'{outcome}_log'
    predictor_z = f'{predictor}_z'

    if outcome_log not in df.columns or predictor_z not in df.columns:
        return None

    vars_needed = [outcome_log, predictor_z, group_var]

    # Build formula
    formula = f'{outcome_log} ~ {predictor_z}'
    if controls:
        for ctrl in controls:
            ctrl_z = f'{ctrl}_z' if f'{ctrl}_z' in df.columns else ctrl
            if ctrl_z in df.columns:
                vars_needed.append(ctrl_z)
                formula += f' + {ctrl_z}'

    data = df[vars_needed].dropna()
    if len(data) < 50:
        return None

    try:
        model = smf.mixedlm(formula, data, groups=data[group_var])
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
            'controls': ','.join(controls) if controls else 'none',
            'coef': result.params[predictor_z],
            'se': result.bse[predictor_z],
            'p_value': result.pvalues[predictor_z],
            'aic': aic,
            'r2_marginal': r2_marginal,
            'n': n
        }

    except Exception as e:
        return None


def validate_dilution_effect(df, outcome='incidence_mean_dengue', predictor='forest_cover'):
    """
    Test if forest-dengue relationship is confounded by urbanization.
    Compare model with and without population control.
    """
    print(f"\n  Validando efecto dilucion: {VAR_LABELS.get(predictor)} -> {VAR_LABELS.get(outcome)}")

    # Model without control
    result_no_ctrl = fit_health_model(df, outcome, predictor, controls=None)

    # Model with population control
    result_pop_ctrl = fit_health_model(df, outcome, predictor, controls=['log_population'])

    # Model with rural control
    result_rural_ctrl = fit_health_model(df, outcome, predictor, controls=['pct_rural'])

    # Model with both
    result_both_ctrl = fit_health_model(df, outcome, predictor, controls=['log_population', 'pct_rural'])

    results = []
    if result_no_ctrl:
        result_no_ctrl['model'] = 'Sin control'
        results.append(result_no_ctrl)
    if result_pop_ctrl:
        result_pop_ctrl['model'] = '+ log(Poblacion)'
        results.append(result_pop_ctrl)
    if result_rural_ctrl:
        result_rural_ctrl['model'] = '+ % Rural'
        results.append(result_rural_ctrl)
    if result_both_ctrl:
        result_both_ctrl['model'] = '+ Ambos'
        results.append(result_both_ctrl)

    return pd.DataFrame(results)


def run_model_selection(df, outcome):
    """Run model selection for one health outcome"""
    all_predictors = BIODIV_VARS + CLIMATE_VARS + VULN_VARS
    results = []

    for predictor in all_predictors:
        result = fit_health_model(df, outcome, predictor)
        if result:
            # Determine dimension
            if predictor in BIODIV_VARS:
                result['dimension'] = 'Biodiversidad'
            elif predictor in CLIMATE_VARS:
                result['dimension'] = 'Clima'
            else:
                result['dimension'] = 'Vulnerabilidad'
            results.append(result)

    if not results:
        return pd.DataFrame()

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('aic')
    results_df['delta_aic'] = results_df['aic'] - results_df['aic'].min()
    results_df['aic_weight'] = np.exp(-0.5 * results_df['delta_aic'])
    results_df['aic_weight'] = results_df['aic_weight'] / results_df['aic_weight'].sum()

    return results_df


def run_h4_analysis(df):
    """Run complete H4 analysis"""
    print("\n" + "=" * 70)
    print("H4: PREDICTORES DE RIESGO DE SALUD")
    print("Modelo: log(salud) ~ predictor + (1|micro)")
    print("=" * 70)

    all_results = []
    best_by_outcome = []

    for outcome in HEALTH_OUTCOMES.keys():
        print(f"\n{'='*60}")
        print(f"OUTCOME: {HEALTH_OUTCOMES[outcome]}")
        print(f"{'='*60}")

        results_df = run_model_selection(df, outcome)

        if len(results_df) == 0:
            continue

        all_results.append(results_df)

        # Print results
        print(f"\n  {'Predictor':<25} {'Dim':<15} {'beta':>10} {'p':>10} {'dAIC':>8} {'R2m':>8}")
        print(f"  {'-'*76}")

        for _, row in results_df.iterrows():
            sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
            marker = ' << BEST' if row['delta_aic'] == 0 else (' ~ equiv' if row['delta_aic'] < 2 else '')
            print(f"  {VAR_LABELS.get(row['predictor'], row['predictor']):<25} "
                  f"{row['dimension']:<15} {row['coef']:>10.4f}{sig:<3} "
                  f"{row['p_value']:>9.4f} {row['delta_aic']:>8.2f} {row['r2_marginal']:>8.4f}{marker}")

        # Store best
        best = results_df.iloc[0]
        equiv = results_df[results_df['delta_aic'] < 2]
        best_by_outcome.append({
            'outcome': outcome,
            'outcome_label': HEALTH_OUTCOMES[outcome],
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


# ============================================================
# DILUTION EFFECT VALIDATION
# ============================================================

def run_dilution_validation(df):
    """Validate dilution effect for key relationships"""
    print("\n" + "=" * 70)
    print("H4 VALIDACION: EFECTO DILUCION (BOSQUE-ENFERMEDAD)")
    print("Pregunta: La relacion esta confundida por urbanizacion?")
    print("=" * 70)

    # Key pairs to validate
    pairs = [
        ('incidence_mean_dengue', 'forest_cover'),
        ('incidence_mean_malaria', 'forest_cover'),
        ('incidence_mean_leishmaniose', 'forest_cover'),
        ('incidence_mean_leptospirose', 'forest_cover'),
        ('incidence_mean_dengue', 'pct_rural'),
    ]

    all_validations = []

    for outcome, predictor in pairs:
        validation_df = validate_dilution_effect(df, outcome, predictor)
        if len(validation_df) > 0:
            validation_df['outcome_label'] = HEALTH_OUTCOMES.get(outcome, outcome)
            validation_df['predictor_label'] = VAR_LABELS.get(predictor, predictor)
            all_validations.append(validation_df)

            print(f"\n  {HEALTH_OUTCOMES.get(outcome, outcome)} ~ {VAR_LABELS.get(predictor, predictor)}:")
            print(f"  {'Modelo':<20} {'beta':>10} {'p':>10} {'AIC':>12}")
            print(f"  {'-'*52}")
            for _, row in validation_df.iterrows():
                sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
                print(f"  {row['model']:<20} {row['coef']:>10.4f}{sig:<3} "
                      f"{row['p_value']:>9.4f} {row['aic']:>12.1f}")

            # Check if coefficient changes significantly
            if len(validation_df) >= 2:
                coef_no_ctrl = validation_df[validation_df['model'] == 'Sin control']['coef'].values[0]
                coef_ctrl = validation_df[validation_df['model'] != 'Sin control']['coef'].values[-1]
                pct_change = abs(coef_ctrl - coef_no_ctrl) / abs(coef_no_ctrl) * 100

                if pct_change > 20:
                    print(f"  ** ADVERTENCIA: Coeficiente cambia {pct_change:.1f}% con controles")
                    print(f"     Posible confundimiento por urbanizacion")
                else:
                    print(f"  OK: Coeficiente estable ({pct_change:.1f}% cambio)")

    return pd.concat(all_validations, ignore_index=True) if all_validations else pd.DataFrame()


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_selection_heatmap(all_df, filename):
    """Heatmap of predictor effects on health outcomes"""
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

    # Rename axes
    pivot.index = [HEALTH_OUTCOMES.get(i, i) for i in pivot.index]
    pivot.columns = [VAR_LABELS.get(c, c) for c in pivot.columns]
    pivot_p.index = [HEALTH_OUTCOMES.get(i, i) for i in pivot_p.index]
    pivot_p.columns = [VAR_LABELS.get(c, c) for c in pivot_p.columns]

    fig, ax = plt.subplots(figsize=(14, 8))

    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdBu_r', center=0, ax=ax,
                linewidths=0.5, cbar_kws={'label': 'beta (log scale)'})

    # Add significance markers
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            p = pivot_p.iloc[i, j]
            if pd.notna(p) and p < 0.05:
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*'
                ax.text(j + 0.5, i + 0.8, sig, ha='center', va='center',
                       fontsize=7, fontweight='bold')

    ax.set_title('H4: Predictores de Riesgo de Salud\n'
                 'Modelo: log(salud) ~ predictor + (1|micro) | *** p<0.001',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Predictor', fontsize=11)
    ax.set_ylabel('Outcome de Salud', fontsize=11)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_dilution_comparison(validation_df, filename):
    """Compare coefficients with and without controls"""
    print(f"\n  Generating dilution comparison plot...")

    # Pivot for plotting
    pairs = validation_df.groupby(['outcome_label', 'predictor_label']).size().reset_index()

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    plot_idx = 0
    for _, pair_row in pairs.iterrows():
        if plot_idx >= 6:
            break

        outcome = pair_row['outcome_label']
        predictor = pair_row['predictor_label']
        subset = validation_df[(validation_df['outcome_label'] == outcome) &
                               (validation_df['predictor_label'] == predictor)]

        ax = axes[plot_idx]

        models = subset['model'].tolist()
        coefs = subset['coef'].tolist()
        colors = ['#1a9850' if p < 0.05 else '#d73027' for p in subset['p_value']]

        bars = ax.bar(range(len(models)), coefs, color=colors, edgecolor='white')
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
        ax.axhline(0, color='black', linewidth=0.5, linestyle='--')

        ax.set_ylabel('beta', fontsize=10)
        ax.set_title(f'{predictor} -> {outcome}', fontsize=10, fontweight='bold')

        plot_idx += 1

    # Hide unused
    for i in range(plot_idx, 6):
        axes[i].axis('off')

    fig.suptitle('H4: Validacion Efecto Dilucion\n'
                 'Comparacion de coeficientes con/sin controles de urbanizacion\n'
                 'Verde = sig (p<0.05), Rojo = no sig',
                 fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_best_predictors(best_df, filename):
    """Summary of best predictor per health outcome"""
    print(f"\n  Generating best predictors plot...")

    fig, ax = plt.subplots(figsize=(12, 7))

    colors_dim = {'Biodiversidad': '#1a9850', 'Clima': '#fc8d59', 'Vulnerabilidad': '#d73027'}
    colors = [colors_dim.get(d, 'gray') for d in best_df['dimension']]

    y_pos = range(len(best_df))
    bars = ax.barh(y_pos, best_df['coef'], color=colors, edgecolor='white', height=0.6)

    # Annotations
    for i, (_, row) in enumerate(best_df.iterrows()):
        sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
        x_pos = row['coef'] + 0.01 * np.sign(row['coef'])
        ha = 'left' if row['coef'] >= 0 else 'right'
        ax.text(x_pos, i, f"{row['best_predictor_label'][:15]} {sig}", va='center', ha=ha, fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(best_df['outcome_label'], fontsize=10)
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlabel('beta (log scale)', fontsize=11)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=d) for d, c in colors_dim.items()]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    ax.set_title('H4: Mejor Predictor por Enfermedad (por AIC)\n'
                 'Modelo: log(salud) ~ predictor + (1|micro)',
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
    print("ANALISIS H4 - PREDICTORES DE RIESGO DE SALUD")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load data
    df = load_and_prepare_data()

    # Main analysis
    all_results, best_results = run_h4_analysis(df)

    # Dilution validation
    validation_results = run_dilution_validation(df)

    # Save results
    all_results.to_csv(os.path.join(OUTPUT_DIR, 'h4_all_models.csv'), index=False)
    best_results.to_csv(os.path.join(OUTPUT_DIR, 'h4_best_predictors.csv'), index=False)
    if len(validation_results) > 0:
        validation_results.to_csv(os.path.join(OUTPUT_DIR, 'h4_dilution_validation.csv'), index=False)

    print(f"\n  [SAVED] h4_all_models.csv ({len(all_results)} models)")
    print(f"  [SAVED] h4_best_predictors.csv ({len(best_results)} selections)")
    print(f"  [SAVED] h4_dilution_validation.csv ({len(validation_results)} tests)")

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_selection_heatmap(all_results, 'h4_selection_heatmap.png')
    plot_best_predictors(best_results, 'h4_best_predictors.png')
    if len(validation_results) > 0:
        plot_dilution_comparison(validation_results, 'h4_dilution_comparison.png')

    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN H4: MEJORES PREDICTORES DE SALUD")
    print("=" * 70)

    print(f"\n  {'Enfermedad':<20} {'Mejor Predictor':<25} {'Dimension':<15} {'beta':>10} {'p':>10}")
    print(f"  {'-'*80}")
    for _, row in best_results.iterrows():
        sig = '***' if row['p_value'] < 0.001 else '**' if row['p_value'] < 0.01 else '*' if row['p_value'] < 0.05 else 'ns'
        print(f"  {row['outcome_label']:<20} {row['best_predictor_label']:<25} "
              f"{row['dimension']:<15} {row['coef']:>10.4f}{sig:<3} {row['p_value']:>9.4f}")

    # Key finding about dilution
    print("\n" + "=" * 70)
    print("VALIDACION EFECTO DILUCION")
    print("=" * 70)

    if len(validation_results) > 0:
        forest_dengue = validation_results[
            (validation_results['predictor_label'] == 'Cobertura Forestal') &
            (validation_results['outcome_label'] == 'Dengue')
        ]
        if len(forest_dengue) >= 2:
            coef_sin = forest_dengue[forest_dengue['model'] == 'Sin control']['coef'].values
            coef_con = forest_dengue[forest_dengue['model'] == '+ Ambos']['coef'].values

            if len(coef_sin) > 0 and len(coef_con) > 0:
                pct_change = abs(coef_con[0] - coef_sin[0]) / abs(coef_sin[0]) * 100
                print(f"\n  Bosque -> Dengue:")
                print(f"    Sin control: beta = {coef_sin[0]:.4f}")
                print(f"    Con controles (poblacion + rural): beta = {coef_con[0]:.4f}")
                print(f"    Cambio: {pct_change:.1f}%")

                if pct_change > 20:
                    print(f"\n  ** CONCLUSION: El efecto bosque-dengue ESTA parcialmente")
                    print(f"     confundido por urbanizacion. Controlando por poblacion,")
                    print(f"     el efecto se {'reduce' if abs(coef_con[0]) < abs(coef_sin[0]) else 'aumenta'}.")
                else:
                    print(f"\n  ** CONCLUSION: El efecto bosque-dengue es ROBUSTO")
                    print(f"     a controles de urbanizacion.")

    print("\nDone!")


if __name__ == "__main__":
    main()
