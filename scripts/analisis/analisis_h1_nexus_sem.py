"""
Análisis Nexus H1: Biodiversidad/Vegetación reduce riesgos ambientales, de salud y sociales
Estructura de 4 sub-hipótesis con cadenas causales progresivas (SEM)

H1.1: Forest/Biodiversity → (−) Climate Risk → (−) Health Impact
H1.2: Forest/Biodiversity → (−) Pollination Deficit → (−) Climate Risk → (−) Health Impact
H1.3: (Forest/Biodiversity → Pollination) * Vulnerability → (−) Climate Risk → (−) Health
H1.4: Governance → (Forest/Biodiversity → Pollination) * Vulnerability → (−) Climate Risk → (−) Health

Autor: Science Team / AP Digital
Fecha: 2026-01-26
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
import warnings
warnings.filterwarnings('ignore')

# Try semopy, fall back to manual path analysis if not available
try:
    import semopy
    HAS_SEMOPY = True
    print("[OK] semopy available — will use full SEM")
except ImportError:
    HAS_SEMOPY = False
    print("[WARN] semopy not available — using manual path analysis with OLS")

from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import os

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/dataset/municipios_integrado.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Variables by dimension
BIODIVERSITY = ['forest_cover', 'mean_species_richness', 'pol_deficit']
CLIMATE_RISK = ['flooding_risks', 'fire_risk_index', 'hydric_stress_risk']
HEALTH = [
    'incidence_mean_dengue', 'incidence_mean_malaria',
    'incidence_mean_leptospirose', 'incidence_mean_leishmaniose',
    'incidence_diarrhea_mean',
    'health_death_circ_mean', 'health_hosp_resp_mean'
]
HEALTH_LABELS = {
    'incidence_mean_dengue': 'Dengue',
    'incidence_mean_malaria': 'Malaria',
    'incidence_mean_leptospirose': 'Leptospirosis',
    'incidence_mean_leishmaniose': 'Leishmaniasis',
    'incidence_diarrhea_mean': 'Diarrhea',
    'health_death_circ_mean': 'CV Mortality',
    'health_hosp_resp_mean': 'Resp. Hospitalization'
}
VULNERABILITY = ['pct_pobreza', 'pct_rural', 'pct_preta', 'pct_indigena']
GOVERNANCE = ['idx_gobernanza_100', 'UAI_Crisk']

ALL_VARS = BIODIVERSITY + CLIMATE_RISK + HEALTH + VULNERABILITY + GOVERNANCE


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load and prepare data"""
    print("\n" + "=" * 70)
    print("LOADING DATA")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    print(f"Dataset: {len(df)} municipalities × {len(df.columns)} variables")

    # Check completeness
    for v in ALL_VARS:
        valid = df[v].notna().sum()
        if valid < 600:
            print(f"  [WARN] {v}: only {valid} valid values")

    # Standardize all variables for SEM
    scaler = StandardScaler()
    df_z = df.copy()
    for v in ALL_VARS:
        if v in df.columns:
            vals = df[v].values.reshape(-1, 1)
            df_z[v + '_z'] = scaler.fit_transform(vals)

    return df, df_z


# ============================================================
# H1.1 — BIVARIATE CORRELATIONS: Biodiversity → Climate Risk → Health
# ============================================================

def analyze_h1_1(df):
    """H1.1: Direct chains Forest/Biodiv → Climate Risk → Health"""
    print("\n" + "=" * 70)
    print("H1.1: BIODIVERSITY → CLIMATE RISK → HEALTH IMPACT")
    print("=" * 70)

    results = []

    # Path A: Biodiversity → Climate Risk
    print("\n--- Path A: Biodiversity → Climate Risk ---")
    for bio in BIODIVERSITY:
        for clim in CLIMATE_RISK:
            r, p = stats.spearmanr(df[bio], df[clim])
            results.append({
                'hypothesis': 'H1.1',
                'path': 'Biodiv → Climate',
                'predictor': bio,
                'outcome': clim,
                'r_spearman': r,
                'p_value': p,
                'significant': p < 0.05
            })
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            print(f"  {bio} → {clim}: r={r:.3f} {sig}")

    # Path B: Climate Risk → Health
    print("\n--- Path B: Climate Risk → Health ---")
    for clim in CLIMATE_RISK:
        for health in HEALTH:
            r, p = stats.spearmanr(df[clim], df[health])
            results.append({
                'hypothesis': 'H1.1',
                'path': 'Climate → Health',
                'predictor': clim,
                'outcome': health,
                'r_spearman': r,
                'p_value': p,
                'significant': p < 0.05
            })
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            if abs(r) > 0.1:
                print(f"  {clim} → {HEALTH_LABELS.get(health, health)}: r={r:.3f} {sig}")

    # Path C: Biodiversity → Health (direct)
    print("\n--- Path C: Biodiversity → Health (direct) ---")
    for bio in BIODIVERSITY:
        for health in HEALTH:
            r, p = stats.spearmanr(df[bio], df[health])
            results.append({
                'hypothesis': 'H1.1',
                'path': 'Biodiv → Health',
                'predictor': bio,
                'outcome': health,
                'r_spearman': r,
                'p_value': p,
                'significant': p < 0.05
            })
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            if abs(r) > 0.1:
                print(f"  {bio} → {HEALTH_LABELS.get(health, health)}: r={r:.3f} {sig}")

    return pd.DataFrame(results)


# ============================================================
# H1.2 — MEDIATION: Biodiversity → Pollination Deficit → Climate Risk → Health
# ============================================================

def mediation_test(df, X, M, Y):
    """Sobel test for mediation: X → M → Y"""
    # Path a: X → M
    X_data = sm.add_constant(df[[X]])
    model_a = sm.OLS(df[M], X_data).fit()
    a = model_a.params[X]
    se_a = model_a.bse[X]

    # Path b: M → Y (controlling for X)
    XM_data = sm.add_constant(df[[X, M]])
    model_b = sm.OLS(df[Y], XM_data).fit()
    b = model_b.params[M]
    se_b = model_b.bse[M]
    c_prime = model_b.params[X]  # direct effect

    # Total effect: X → Y
    model_c = sm.OLS(df[Y], X_data).fit()
    c = model_c.params[X]

    # Indirect effect
    indirect = a * b

    # Sobel test
    se_indirect = np.sqrt(a**2 * se_b**2 + b**2 * se_a**2)
    z_sobel = indirect / se_indirect if se_indirect > 0 else 0
    p_sobel = 2 * (1 - stats.norm.cdf(abs(z_sobel)))

    # Proportion mediated
    prop_mediated = indirect / c if abs(c) > 0.001 else np.nan

    return {
        'a_path': a, 'b_path': b,
        'c_total': c, 'c_prime_direct': c_prime,
        'indirect': indirect,
        'sobel_z': z_sobel, 'sobel_p': p_sobel,
        'prop_mediated': prop_mediated,
        'r2_full': model_b.rsquared
    }


def analyze_h1_2(df_z):
    """H1.2: Biodiversity → Pollination Deficit → Climate Risk → Health"""
    print("\n" + "=" * 70)
    print("H1.2: BIODIVERSITY → POLL. DEFICIT → CLIMATE RISK → HEALTH")
    print("=" * 70)

    results = []

    # Chain: forest_cover → pol_deficit → climate_risk → health
    for bio in ['forest_cover', 'mean_species_richness']:
        bio_z = bio + '_z'
        M1 = 'pol_deficit_z'

        print(f"\n--- Mediator chain starting from {bio} ---")

        # Step 1: bio → pol_deficit
        med1 = mediation_test(df_z, bio_z, M1, M1)  # just for path a
        r, p = stats.spearmanr(df_z[bio_z], df_z[M1])
        print(f"  {bio} → pol_deficit: r={r:.3f}")

        for clim in CLIMATE_RISK:
            clim_z = clim + '_z'

            # Step 2: pol_deficit mediates bio → climate_risk?
            med_clim = mediation_test(df_z, bio_z, M1, clim_z)
            sig = "***" if med_clim['sobel_p'] < 0.001 else "**" if med_clim['sobel_p'] < 0.01 else "*" if med_clim['sobel_p'] < 0.05 else "ns"

            if abs(med_clim['indirect']) > 0.01:
                print(f"  {bio} → pol_deficit → {clim}: indirect={med_clim['indirect']:.3f} {sig}, prop_mediated={med_clim['prop_mediated']:.1%}")

            for health in HEALTH:
                health_z = health + '_z'

                # Step 3: climate_risk mediates → health?
                med_health = mediation_test(df_z, clim_z, M1, health_z)

                results.append({
                    'hypothesis': 'H1.2',
                    'biodiversity': bio,
                    'climate_risk': clim,
                    'health_outcome': health,
                    'bio_to_poldef_r': stats.spearmanr(df_z[bio_z], df_z[M1])[0],
                    'poldef_mediation_indirect': med_clim['indirect'],
                    'poldef_mediation_p': med_clim['sobel_p'],
                    'poldef_mediation_prop': med_clim['prop_mediated'],
                    'climate_to_health_r': stats.spearmanr(df_z[clim_z], df_z[health_z])[0],
                    'full_chain_significant': med_clim['sobel_p'] < 0.05
                })

    return pd.DataFrame(results)


# ============================================================
# H1.3 — MODERATION BY VULNERABILITY
# ============================================================

def analyze_h1_3(df, df_z):
    """H1.3: (Biodiversity → Pollination) * Vulnerability → Climate → Health"""
    print("\n" + "=" * 70)
    print("H1.3: VULNERABILITY MODERATION OF BIODIVERSITY EFFECTS")
    print("=" * 70)

    results = []

    for vuln in VULNERABILITY:
        vuln_z = vuln + '_z'
        # Split into high/low vulnerability groups (median split)
        median_v = df[vuln].median()
        high_vuln = df[vuln] >= median_v
        low_vuln = df[vuln] < median_v

        print(f"\n--- Moderator: {vuln} (median={median_v:.3f}) ---")

        for bio in ['forest_cover', 'mean_species_richness']:
            for health in HEALTH:
                # Correlation in high vulnerability group
                r_high, p_high = stats.spearmanr(
                    df.loc[high_vuln, bio], df.loc[high_vuln, health])
                # Correlation in low vulnerability group
                r_low, p_low = stats.spearmanr(
                    df.loc[low_vuln, bio], df.loc[low_vuln, health])

                # Interaction test (OLS with interaction term)
                X_interact = df_z[[bio + '_z', vuln_z]].copy()
                X_interact['interaction'] = X_interact[bio + '_z'] * X_interact[vuln_z]
                X_interact = sm.add_constant(X_interact)
                model = sm.OLS(df_z[health + '_z'], X_interact).fit()

                interact_coef = model.params.get('interaction', 0)
                interact_p = model.pvalues.get('interaction', 1)

                results.append({
                    'hypothesis': 'H1.3',
                    'biodiversity': bio,
                    'health_outcome': health,
                    'moderator': vuln,
                    'r_high_vuln': r_high,
                    'r_low_vuln': r_low,
                    'diff_r': abs(r_high) - abs(r_low),
                    'interaction_coef': interact_coef,
                    'interaction_p': interact_p,
                    'significant_moderation': interact_p < 0.05
                })

                if interact_p < 0.05 and abs(interact_coef) > 0.05:
                    sig = "***" if interact_p < 0.001 else "**" if interact_p < 0.01 else "*"
                    print(f"  {bio} × {vuln} → {HEALTH_LABELS.get(health, health)}: "
                          f"β_interact={interact_coef:.3f}{sig} "
                          f"(high_vuln: r={r_high:.3f}, low_vuln: r={r_low:.3f})")

    return pd.DataFrame(results)


# ============================================================
# H1.4 — GOVERNANCE EFFECTS (SEM OR PATH ANALYSIS)
# ============================================================

def run_sem_for_health(df_z, health_var):
    """Run full SEM model for one health outcome"""
    h_z = health_var + '_z'

    if HAS_SEMOPY:
        # Full SEM specification
        model_spec = f"""
        # Biodiversity → Pollination
        pol_deficit_z ~ forest_cover_z + mean_species_richness_z

        # Governance → Biodiversity
        forest_cover_z ~ idx_gobernanza_100_z

        # Climate risks
        flooding_risks_z ~ forest_cover_z + pol_deficit_z
        fire_risk_index_z ~ forest_cover_z + pol_deficit_z

        # Health outcome
        {h_z} ~ flooding_risks_z + fire_risk_index_z + forest_cover_z + mean_species_richness_z + pol_deficit_z + idx_gobernanza_100_z
        """

        try:
            model = semopy.Model(model_spec)
            cols_needed = [
                'forest_cover_z', 'mean_species_richness_z', 'pol_deficit_z',
                'flooding_risks_z', 'fire_risk_index_z', 'idx_gobernanza_100_z', h_z
            ]
            data = df_z[cols_needed].dropna()
            result = model.fit(data)
            estimates = model.inspect()
            return estimates, True
        except Exception as e:
            print(f"  [WARN] semopy failed for {health_var}: {e}")
            return None, False

    # Fallback: manual path analysis with OLS
    paths = {}

    # Path: governance → forest_cover
    X = sm.add_constant(df_z[['idx_gobernanza_100_z']])
    m = sm.OLS(df_z['forest_cover_z'], X).fit()
    paths['gov→forest'] = {'coef': m.params['idx_gobernanza_100_z'], 'p': m.pvalues['idx_gobernanza_100_z'], 'r2': m.rsquared}

    # Path: forest + species → pol_deficit
    X = sm.add_constant(df_z[['forest_cover_z', 'mean_species_richness_z']])
    m = sm.OLS(df_z['pol_deficit_z'], X).fit()
    paths['forest→poldef'] = {'coef': m.params['forest_cover_z'], 'p': m.pvalues['forest_cover_z'], 'r2': m.rsquared}
    paths['species→poldef'] = {'coef': m.params['mean_species_richness_z'], 'p': m.pvalues['mean_species_richness_z'], 'r2': m.rsquared}

    # Path: forest + poldef → flooding
    X = sm.add_constant(df_z[['forest_cover_z', 'pol_deficit_z']])
    m = sm.OLS(df_z['flooding_risks_z'], X).fit()
    paths['forest→flooding'] = {'coef': m.params['forest_cover_z'], 'p': m.pvalues['forest_cover_z'], 'r2': m.rsquared}
    paths['poldef→flooding'] = {'coef': m.params['pol_deficit_z'], 'p': m.pvalues['pol_deficit_z'], 'r2': m.rsquared}

    # Path: forest + poldef → fire
    X = sm.add_constant(df_z[['forest_cover_z', 'pol_deficit_z']])
    m = sm.OLS(df_z['fire_risk_index_z'], X).fit()
    paths['forest→fire'] = {'coef': m.params['forest_cover_z'], 'p': m.pvalues['forest_cover_z'], 'r2': m.rsquared}
    paths['poldef→fire'] = {'coef': m.params['pol_deficit_z'], 'p': m.pvalues['pol_deficit_z'], 'r2': m.rsquared}

    # Path: all → health
    predictors = ['flooding_risks_z', 'fire_risk_index_z', 'forest_cover_z',
                  'mean_species_richness_z', 'pol_deficit_z', 'idx_gobernanza_100_z']
    X = sm.add_constant(df_z[predictors])
    m = sm.OLS(df_z[h_z], X).fit()
    for pred in predictors:
        short_name = pred.replace('_z', '')
        paths[f'{short_name}→health'] = {'coef': m.params[pred], 'p': m.pvalues[pred], 'r2': m.rsquared}

    return paths, False


def analyze_h1_4(df_z):
    """H1.4: Full SEM with governance for each health outcome"""
    print("\n" + "=" * 70)
    print("H1.4: FULL PATH ANALYSIS — GOVERNANCE → BIODIV → CLIMATE → HEALTH")
    print("=" * 70)

    all_paths = {}

    for health in HEALTH:
        print(f"\n--- {HEALTH_LABELS.get(health, health)} ---")
        result, is_semopy = run_sem_for_health(df_z, health)

        if result is None:
            print("  [SKIP] Could not fit model")
            continue

        if is_semopy:
            print("  [SEM] Full structural equation model:")
            sig_rows = result[result['p-value'] < 0.05]
            for _, row in sig_rows.iterrows():
                print(f"    {row['lval']} ← {row['rval']}: β={row['Estimate']:.3f} (p={row['p-value']:.4f})")
            all_paths[health] = result
        else:
            print("  [PATH] Manual path coefficients (standardized β):")
            for name, vals in result.items():
                sig = "***" if vals['p'] < 0.001 else "**" if vals['p'] < 0.01 else "*" if vals['p'] < 0.05 else "ns"
                if vals['p'] < 0.05:
                    print(f"    {name}: β={vals['coef']:.3f} {sig}")
            all_paths[health] = result

    return all_paths


# ============================================================
# VISUALIZATION: SEM PATH DIAGRAMS
# ============================================================

def draw_path_diagram(paths, health_var, filename):
    """Draw a path diagram for one health outcome"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    health_label = HEALTH_LABELS.get(health_var, health_var)
    ax.set_title(f'H1.4 Path Diagram: Nexus Assessment → {health_label}',
                 fontsize=16, fontweight='bold', pad=20)

    # Node positions
    nodes = {
        'Governance': (1, 6.5),
        'Forest Cover': (3, 7),
        'Species Richness': (3, 5.5),
        'Poll. Deficit': (5, 6.5),
        'Flood Risk': (7, 7),
        'Fire Risk': (7, 5.5),
        health_label: (9, 6.5),
    }

    # Draw nodes
    for name, (x, y) in nodes.items():
        color = '#2171b5' if name == 'Governance' else \
                '#1a9850' if name in ['Forest Cover', 'Species Richness'] else \
                '#fc8d59' if name == 'Poll. Deficit' else \
                '#d73027' if name in ['Flood Risk', 'Fire Risk'] else \
                '#7b3294'

        box = mpatches.FancyBboxPatch((x - 0.8, y - 0.3), 1.6, 0.6,
                                        boxstyle="round,pad=0.1",
                                        facecolor=color, alpha=0.3,
                                        edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

    # Draw paths with coefficients
    path_mapping = {
        ('Governance', 'Forest Cover'): 'gov→forest',
        ('Forest Cover', 'Poll. Deficit'): 'forest→poldef',
        ('Species Richness', 'Poll. Deficit'): 'species→poldef',
        ('Forest Cover', 'Flood Risk'): 'forest→flooding',
        ('Poll. Deficit', 'Flood Risk'): 'poldef→flooding',
        ('Forest Cover', 'Fire Risk'): 'forest→fire',
        ('Poll. Deficit', 'Fire Risk'): 'poldef→fire',
        ('Flood Risk', health_label): 'flooding_risks→health',
        ('Fire Risk', health_label): 'fire_risk_index→health',
        ('Forest Cover', health_label): 'forest_cover→health',
        ('Species Richness', health_label): 'mean_species_richness→health',
        ('Poll. Deficit', health_label): 'pol_deficit→health',
        ('Governance', health_label): 'idx_gobernanza_100→health',
    }

    is_semopy_result = not isinstance(paths, dict) or (isinstance(paths, dict) and
                        any(isinstance(v, dict) and 'coef' in v for v in paths.values()))

    for (src, dst), path_key in path_mapping.items():
        if src not in nodes or dst not in nodes:
            continue

        x1, y1 = nodes[src]
        x2, y2 = nodes[dst]

        # Get coefficient
        if isinstance(paths, dict) and path_key in paths:
            coef = paths[path_key]['coef']
            p_val = paths[path_key]['p']
        elif isinstance(paths, pd.DataFrame):
            # semopy result
            row = paths[(paths['lval'].str.contains(dst[:5], case=False)) &
                       (paths['rval'].str.contains(src[:5], case=False))]
            if len(row) > 0:
                coef = row.iloc[0]['Estimate']
                p_val = row.iloc[0]['p-value']
            else:
                continue
        else:
            continue

        # Arrow style based on significance
        if p_val >= 0.05:
            arrow_color = '#cccccc'
            ls = '--'
            lw = 0.8
        else:
            arrow_color = '#d73027' if coef > 0 else '#1a9850'
            ls = '-'
            lw = min(abs(coef) * 5 + 1, 4)

        ax.annotate('', xy=(x2 - 0.8, y2), xytext=(x1 + 0.8, y1),
                    arrowprops=dict(arrowstyle='->', color=arrow_color,
                                   lw=lw, linestyle=ls))

        # Label
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.2
        sig_str = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        ax.text(mx, my, f'β={coef:.2f}{sig_str}', ha='center', va='center',
                fontsize=8, color=arrow_color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    # Legend
    legend_text = (
        "Green arrow = negative effect (protective)\n"
        "Red arrow = positive effect (risk-increasing)\n"
        "Dashed gray = not significant (p≥0.05)\n"
        "Line width ∝ effect size\n"
        "*** p<0.001  ** p<0.01  * p<0.05"
    )
    ax.text(0.5, 1, legend_text, fontsize=8, va='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

    # Hypothesis chain
    ax.text(5, 0.5,
            'H1.4: Governance → Biodiversity/Forest → Pollination Deficit → Climate Risk → Health Impact',
            ha='center', fontsize=10, fontstyle='italic', color='#555555')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# VISUALIZATION: SCATTER PLOTS WITH SOCIAL MODULATION
# ============================================================

def plot_scatter_modulation(df, x_var, y_var, mod_var, filename):
    """Scatter plot of x vs y, colored by moderator (tercile split)"""

    data = df[[x_var, y_var, mod_var]].dropna()
    if len(data) < 50:
        print(f"  [SKIP] Not enough data for {x_var} vs {y_var} by {mod_var}")
        return

    # Tercile split
    q33, q66 = data[mod_var].quantile([0.33, 0.66])
    data['group'] = pd.cut(data[mod_var], bins=[-np.inf, q33, q66, np.inf],
                           labels=['Low', 'Medium', 'High'])

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = {'Low': '#1a9850', 'Medium': '#fee08b', 'High': '#d73027'}

    for group, color in colors.items():
        mask = data['group'] == group
        subset = data[mask]
        ax.scatter(subset[x_var], subset[y_var], c=color, alpha=0.4, s=20,
                  label=f'{mod_var} {group} (n={len(subset)})', edgecolors='none')

        # Regression line per group
        if len(subset) > 10:
            z = np.polyfit(subset[x_var], subset[y_var], 1)
            p = np.poly1d(z)
            x_range = np.linspace(subset[x_var].min(), subset[x_var].max(), 100)
            ax.plot(x_range, p(x_range), color=color, linewidth=2, alpha=0.8)

            r, pv = stats.spearmanr(subset[x_var], subset[y_var])
            sig = "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else "ns"
            ax.text(0.02, 0.98 - list(colors.keys()).index(group) * 0.05,
                    f'{group}: r={r:.3f}{sig}', transform=ax.transAxes,
                    fontsize=9, color=color, fontweight='bold', va='top')

    x_label = x_var.replace('_', ' ').title()
    y_label = HEALTH_LABELS.get(y_var, y_var.replace('_', ' ').title())
    mod_label = mod_var.replace('_', ' ').title()

    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(f'{x_label} vs {y_label}\nModerated by {mod_label}',
                fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)

    # Overall correlation
    r_all, p_all = stats.spearmanr(data[x_var], data[y_var])
    ax.text(0.98, 0.02, f'Overall: r={r_all:.3f} (p={p_all:.2e})',
            transform=ax.transAxes, ha='right', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# SUMMARY HEATMAP
# ============================================================

def plot_correlation_heatmap(df, filename):
    """Full correlation heatmap: biodiv × climate × health"""
    print("\n  Generating correlation heatmap...")

    vars_for_heatmap = BIODIVERSITY + CLIMATE_RISK + HEALTH
    labels = {
        'forest_cover': 'Forest Cover',
        'mean_species_richness': 'Species Richness',
        'pol_deficit': 'Poll. Deficit',
        'flooding_risks': 'Flood Risk',
        'fire_risk_index': 'Fire Risk',
        'hydric_stress_risk': 'Hydric Stress',
        'incidence_mean_dengue': 'Dengue',
        'incidence_mean_malaria': 'Malaria',
        'incidence_mean_leptospirose': 'Leptospirosis',
        'incidence_mean_leishmaniose': 'Leishmaniasis',
        'incidence_diarrhea_mean': 'Diarrhea',
        'health_death_circ_mean': 'CV Mortality',
        'health_hosp_resp_mean': 'Resp. Hosp.'
    }

    corr_matrix = df[vars_for_heatmap].corr(method='spearman')
    corr_matrix.index = [labels.get(v, v) for v in corr_matrix.index]
    corr_matrix.columns = [labels.get(v, v) for v in corr_matrix.columns]

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn_r',
                center=0, vmin=-1, vmax=1, ax=ax,
                linewidths=0.5, square=True,
                cbar_kws={'label': 'Spearman r'})
    ax.set_title('H1 Nexus: Biodiversity × Climate Risk × Health\n(Spearman correlations, n=645)',
                fontsize=14, fontweight='bold')

    # Add dimension labels
    ax.axhline(3, color='black', linewidth=2)
    ax.axhline(6, color='black', linewidth=2)
    ax.axvline(3, color='black', linewidth=2)
    ax.axvline(6, color='black', linewidth=2)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("NEXUS ASSESSMENT H1: BIODIVERSITY REDUCES ENVIRONMENTAL,")
    print("HEALTH AND SOCIAL RISKS")
    print("=" * 70)

    # Load data
    df, df_z = load_data()

    # ---- H1.1 ----
    results_h1_1 = analyze_h1_1(df)
    results_h1_1.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_1_correlations.csv'), index=False)
    print(f"\n  [SAVED] h1_1_correlations.csv ({len(results_h1_1)} pairs)")

    # ---- H1.2 ----
    results_h1_2 = analyze_h1_2(df_z)
    results_h1_2.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_2_mediation.csv'), index=False)
    print(f"\n  [SAVED] h1_2_mediation.csv ({len(results_h1_2)} chains)")

    # ---- H1.3 ----
    results_h1_3 = analyze_h1_3(df, df_z)
    results_h1_3.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_3_moderation.csv'), index=False)
    print(f"\n  [SAVED] h1_3_moderation.csv ({len(results_h1_3)} interactions)")

    # ---- H1.4 (SEM / Path Analysis) ----
    all_paths = analyze_h1_4(df_z)

    # Save path results
    path_rows = []
    for health, paths in all_paths.items():
        if isinstance(paths, dict):
            for pname, pvals in paths.items():
                path_rows.append({
                    'health_outcome': health,
                    'path': pname,
                    'coefficient': pvals['coef'],
                    'p_value': pvals['p'],
                    'r_squared': pvals.get('r2', np.nan)
                })
        elif isinstance(paths, pd.DataFrame):
            for _, row in paths.iterrows():
                path_rows.append({
                    'health_outcome': health,
                    'path': f"{row['rval']}→{row['lval']}",
                    'coefficient': row['Estimate'],
                    'p_value': row['p-value'],
                    'r_squared': np.nan
                })

    df_paths = pd.DataFrame(path_rows)
    df_paths.to_csv(os.path.join(OUTPUT_DIR, '../modelos/h1_4_sem_paths.csv'), index=False)
    print(f"\n  [SAVED] h1_4_sem_paths.csv ({len(df_paths)} paths)")

    # ---- VISUALIZATIONS ----
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)

    # 1. Correlation heatmap
    plot_correlation_heatmap(df, 'h1_heatmap_nexus.png')

    # 2. Path diagrams for health outcomes with complete chains
    print("\n  Generating path diagrams...")
    for health, paths in all_paths.items():
        safe_name = health.replace('incidence_mean_', '').replace('health_', '')
        draw_path_diagram(paths, health, f'h1_sem_{safe_name}.png')

    # 3. Scatter plots with social modulation (most relevant combinations)
    print("\n  Generating modulated scatter plots...")
    key_combos = [
        ('forest_cover', 'incidence_mean_dengue', 'pct_pobreza'),
        ('forest_cover', 'incidence_mean_dengue', 'pct_preta'),
        ('forest_cover', 'incidence_diarrhea_mean', 'pct_rural'),
        ('mean_species_richness', 'incidence_mean_dengue', 'pct_pobreza'),
        ('mean_species_richness', 'health_death_circ_mean', 'pct_rural'),
        ('mean_species_richness', 'health_hosp_resp_mean', 'pct_preta'),
        ('forest_cover', 'health_death_circ_mean', 'pct_indigena'),
        ('pol_deficit', 'incidence_mean_dengue', 'pct_pobreza'),
        ('pol_deficit', 'health_hosp_resp_mean', 'pct_rural'),
        ('flooding_risks', 'incidence_mean_dengue', 'pct_pobreza'),
        ('fire_risk_index', 'health_death_circ_mean', 'pct_rural'),
        ('fire_risk_index', 'health_hosp_resp_mean', 'pct_preta'),
    ]

    for x, y, mod in key_combos:
        safe = f"h1_scatter_{x.split('_')[0]}_{y.split('_')[-1]}_{mod.split('_')[-1]}.png"
        plot_scatter_modulation(df, x, y, mod, safe)

    # ---- SUMMARY ----
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE — SUMMARY")
    print("=" * 70)

    # Count significant results per hypothesis
    sig_h11 = results_h1_1['significant'].sum()
    sig_h12 = results_h1_2['full_chain_significant'].sum()
    sig_h13 = results_h1_3['significant_moderation'].sum()
    sig_h14 = len([r for r in path_rows if r['p_value'] < 0.05])

    print(f"\n  H1.1 Significant correlations: {sig_h11}/{len(results_h1_1)}")
    print(f"  H1.2 Significant mediations: {sig_h12}/{len(results_h1_2)}")
    print(f"  H1.3 Significant moderations: {sig_h13}/{len(results_h1_3)}")
    print(f"  H1.4 Significant paths: {sig_h14}/{len(path_rows)}")

    # Key findings
    print("\n  KEY FINDINGS:")

    # Strongest biodiv → health
    strong = results_h1_1[results_h1_1['path'] == 'Biodiv → Health'].sort_values('r_spearman')
    if len(strong) > 0:
        top = strong.iloc[0]
        print(f"  • Strongest protective: {top['predictor']} → {HEALTH_LABELS.get(top['outcome'], top['outcome'])}: r={top['r_spearman']:.3f}")
        bottom = strong.iloc[-1]
        if bottom['r_spearman'] > 0:
            print(f"  • Unexpected positive: {bottom['predictor']} → {HEALTH_LABELS.get(bottom['outcome'], bottom['outcome'])}: r={bottom['r_spearman']:.3f}")

    # Strongest moderation
    strong_mod = results_h1_3[results_h1_3['significant_moderation']].sort_values('interaction_coef')
    if len(strong_mod) > 0:
        top_mod = strong_mod.iloc[0]
        print(f"  • Strongest moderation: {top_mod['biodiversity']} × {top_mod['moderator']} → "
              f"{HEALTH_LABELS.get(top_mod['health_outcome'], top_mod['health_outcome'])}: β={top_mod['interaction_coef']:.3f}")

    print(f"\n  Output files in: {OUTPUT_DIR}")
    print(f"  Figures in: {FIG_DIR}")

    # List all generated files
    print("\n  CSV files:")
    for f in ['h1_1_correlations.csv', 'h1_2_mediation.csv', 'h1_3_moderation.csv', 'h1_4_sem_paths.csv']:
        path = os.path.join(OUTPUT_DIR, f)
        if os.path.exists(path):
            print(f"    ✓ {f}")

    print("\n  Figures:")
    for f in sorted(os.listdir(FIG_DIR)):
        if f.startswith('h1_'):
            print(f"    ✓ {f}")

    print("\nDone!")


if __name__ == "__main__":
    main()
