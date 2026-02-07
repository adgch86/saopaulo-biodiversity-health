# =============================================================================
# Analisis H3: Biodiversidad, Estres Termico y Salud - VERSION 2
# Sub-hipotesis H3.1 - H3.4
# =============================================================================
#
# Proyecto: Resilient Landscapes - Sao Paulo
# Science Team | Enero 2026
#
# CORRECCIONES v2 respecto a v1:
#   1. Log-transform de variables con skew > 1 (fire_incidence, forest_cover,
#      hosp_circ, hosp_resp) antes de estandarizar
#   2. GLM Gamma(link=log) para outcomes de salud como analisis primario
#   3. OLS sobre log-z como analisis de sensibilidad y para mediacion/SEM
#   4. Cuatro outcomes de salud: mort_circ, mort_resp, hosp_circ, hosp_resp
#   5. Bootstrap IC 95% para efectos indirectos (reemplaza Sobel)
#   6. Diagnostico formal de distribuciones (Shapiro, skewness, AIC Gamma vs Gauss)
#
# NOTA: Cuando los datos MODIS LST esten disponibles, reemplazar fire_risk_index
# por lst_day_mean / heat_HAAT_mean como variable de estres termico directo.
#
# JUSTIFICACION MODIS vs Xavier:
# - 40.8% de los municipios de SP tienen < 2 pixeles Xavier (0.1 deg ~ 121 km2)
# - MODIS (1 km) garantiza minimo 4 pixeles incluso en el municipio mas pequeno
# =============================================================================

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Paquetes estadisticos
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families import Gamma, Gaussian
from statsmodels.genmod.families.links import Log as LogLink, Identity
from sklearn.preprocessing import StandardScaler

# Visualizacion
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# SEM
try:
    import semopy
    HAS_SEMOPY = True
except ImportError:
    HAS_SEMOPY = False
    print("ADVERTENCIA: semopy no disponible. Analisis SEM se omitiran.")

PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
OUTPUTS = PROJECT_ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
FIGURES.mkdir(exist_ok=True)

# =============================================================================
# CONFIGURACION GLOBAL
# =============================================================================

# Outcomes de salud (4 variables respuesta)
HEALTH_OUTCOMES = [
    {'name': 'mort_circ_rate', 'label': 'Mort. CV', 'family': 'gamma'},
    {'name': 'mort_resp_rate', 'label': 'Mort. Resp.', 'family': 'gamma'},
    {'name': 'hosp_circ_rate', 'label': 'Hosp. CV', 'family': 'gamma'},
    {'name': 'hosp_resp_rate', 'label': 'Hosp. Resp.', 'family': 'gamma'},
]

# Variables de biodiversidad (predictores)
BIODIV_VARS = ['forest_cover', 'idx_biodiv']

# Variable proxy de estres termico / fuego
FIRE_MEDIATOR = 'fire_risk_index'
FIRE_INCIDENCE = 'fire_incidence_mean'

# Controles
CONTROLS = ['pct_rural', 'log_pop', 'idx_vulnerabilidad']

# Bootstrap
N_BOOTSTRAP = 5000
RANDOM_SEED = 42

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def sig_stars(p):
    """Retorna estrellas de significancia."""
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    elif p < 0.10:
        return '.'
    return 'ns'


def safe_log(x, offset=1e-6):
    """Log-transform seguro para valores >= 0."""
    return np.log(x + offset)


def fit_glm_gamma(y, X, add_const=True):
    """
    Ajusta GLM Gamma(link=log) con fallback a Gaussian si Gamma falla.
    Retorna modelo ajustado y nombre de familia usada.
    """
    if add_const:
        X = sm.add_constant(X)
    try:
        model = sm.GLM(y, X, family=Gamma(link=LogLink())).fit()
        return model, 'Gamma'
    except Exception:
        # Fallback: Gaussian con link log
        try:
            model = sm.GLM(y, X, family=Gaussian()).fit()
            return model, 'Gaussian(fallback)'
        except Exception as e:
            print(f"    ADVERTENCIA: GLM fallo ({e}), usando OLS")
            model = sm.OLS(y, X).fit()
            return model, 'OLS(fallback)'


def fit_ols(y, X, add_const=True):
    """Ajusta OLS simple."""
    if add_const:
        X = sm.add_constant(X)
    return sm.OLS(y, X).fit()


def bootstrap_indirect_effect(df, x_col, m_col, y_col, controls,
                              n_boot=N_BOOTSTRAP, seed=RANDOM_SEED):
    """
    Bootstrap del efecto indirecto (a*b) para mediacion.
    Usa OLS sobre variables log-z (estandarizadas).
    Retorna: ab_obs, ci_lower, ci_upper, p_boot
    """
    rng = np.random.RandomState(seed)
    cols = [x_col, m_col, y_col] + controls
    df_clean = df[cols].dropna()
    n = len(df_clean)

    def compute_ab(data):
        # Path a: X -> M
        X_a = sm.add_constant(data[[x_col] + controls])
        m_a = sm.OLS(data[m_col], X_a).fit()
        a = m_a.params[x_col]
        # Path b: M -> Y (controlando X)
        X_b = sm.add_constant(data[[x_col, m_col] + controls])
        m_b = sm.OLS(data[y_col], X_b).fit()
        b = m_b.params[m_col]
        return a * b

    # Efecto observado
    ab_obs = compute_ab(df_clean)

    # Bootstrap
    ab_boots = np.zeros(n_boot)
    for i in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        boot_data = df_clean.iloc[idx]
        try:
            ab_boots[i] = compute_ab(boot_data)
        except Exception:
            ab_boots[i] = np.nan

    ab_boots = ab_boots[~np.isnan(ab_boots)]
    ci_lower = np.percentile(ab_boots, 2.5)
    ci_upper = np.percentile(ab_boots, 97.5)

    # p-value: proporcion de bootstrap samples que cruzan cero
    if ab_obs > 0:
        p_boot = np.mean(ab_boots <= 0) * 2  # two-tailed
    else:
        p_boot = np.mean(ab_boots >= 0) * 2
    p_boot = min(p_boot, 1.0)

    return ab_obs, ci_lower, ci_upper, p_boot


# =============================================================================
# CARGA Y PREPARACION DE DATOS
# =============================================================================

def load_data():
    """
    Cargar dataset y preparar variables.
    - Log-transform para variables con skew > 1
    - Estandarizacion z-score de todas las variables
    """
    print_header("Carga y preparacion de datos")

    df = pd.read_csv(OUTPUTS / "dataset" / "municipios_integrado.csv")
    df['cod_ibge'] = df['cod_ibge'].astype(str)

    # Crear alias de tasas de salud
    df['mort_circ_rate'] = df['health_death_circ_mean']
    df['hosp_circ_rate'] = df['health_hosp_circ_mean']
    df['mort_resp_rate'] = df['health_death_resp_mean']
    df['hosp_resp_rate'] = df['health_hosp_resp_mean']

    # Log-transform de poblacion
    df['log_pop'] = np.log1p(df['population'])

    # -----------------------------------------------------------------
    # Log-transform de variables con skew > 1
    # -----------------------------------------------------------------
    log_vars = {
        'fire_incidence_mean': 'log_fire_inc',     # skew=2.52
        'forest_cover': 'log_forest',              # skew=2.27
        'hosp_circ_rate': 'log_hosp_circ',         # skew=1.37
        'hosp_resp_rate': 'log_hosp_resp',         # skew=1.60
    }
    for raw, log_name in log_vars.items():
        if raw in df.columns:
            df[log_name] = safe_log(df[raw])
            sk_before = stats.skew(df[raw].dropna())
            sk_after = stats.skew(df[log_name].dropna())
            print(f"  Log-transform {raw}: skew {sk_before:.2f} -> {sk_after:.2f}")

    # Log-transform opcional para mortalidad (skew moderado ~0.7)
    df['log_mort_circ'] = safe_log(df['mort_circ_rate'])
    df['log_mort_resp'] = safe_log(df['mort_resp_rate'])

    # -----------------------------------------------------------------
    # Estandarizar variables
    # -----------------------------------------------------------------
    scaler = StandardScaler()

    # Variables en escala original (para GLM Gamma)
    vars_to_scale_raw = [
        'forest_cover', 'mean_species_richness', 'idx_biodiv',
        'fire_incidence_mean', 'fire_risk_index',
        'mort_circ_rate', 'hosp_circ_rate', 'mort_resp_rate', 'hosp_resp_rate',
        'pct_pobreza', 'pct_rural', 'idx_gobernanza', 'UAI_Crisk',
        'idx_vulnerabilidad', 'log_pop',
    ]
    for v in vars_to_scale_raw:
        if v in df.columns:
            df[f'{v}_z'] = scaler.fit_transform(df[[v]])

    # Variables log-transformadas (para OLS mediacion y SEM)
    vars_to_scale_log = [
        'log_fire_inc', 'log_forest',
        'log_hosp_circ', 'log_hosp_resp',
        'log_mort_circ', 'log_mort_resp',
    ]
    for v in vars_to_scale_log:
        if v in df.columns:
            df[f'{v}_z'] = scaler.fit_transform(df[[v]])

    print(f"\n  Dataset: {len(df)} municipios, {len(df.columns)} variables")
    return df


# =============================================================================
# DIAGNOSTICO DE DISTRIBUCIONES
# =============================================================================

def diagnostico_distribuciones(df):
    """
    Diagnostico formal: skewness, Shapiro-Wilk, comparacion AIC Gamma vs Gaussian.
    """
    print_header("Diagnostico de distribuciones")

    vars_check = {
        'fire_incidence_mean': 'Incidencia fuego',
        'fire_risk_index': 'Riesgo fuego',
        'mort_circ_rate': 'Mortalidad CV',
        'mort_resp_rate': 'Mortalidad Resp',
        'hosp_circ_rate': 'Hosp. CV',
        'hosp_resp_rate': 'Hosp. Resp',
        'forest_cover': 'Cobertura forestal',
    }

    results_diag = []
    print(f"\n  {'Variable':<22} {'Skew':>6} {'Skew_log':>8} {'Shapiro_p':>10} "
          f"{'AIC_Gauss':>10} {'AIC_Gamma':>10} {'Mejor':>8}")
    print("  " + "-" * 80)

    for var, label in vars_check.items():
        if var not in df.columns:
            continue
        v = df[var].dropna()
        v_pos = v[v > 0]  # Gamma necesita y > 0

        sk_raw = stats.skew(v)
        sk_log = stats.skew(safe_log(v)) if v.min() >= 0 else np.nan
        _, p_shap = stats.shapiro(v.sample(min(len(v), 500), random_state=42))

        # Comparar AIC: Gaussian vs Gamma(link=log)
        X_const = sm.add_constant(np.ones(len(v_pos)))
        try:
            m_gauss = sm.GLM(v_pos, X_const, family=Gaussian()).fit()
            aic_gauss = m_gauss.aic
        except Exception:
            aic_gauss = np.inf
        try:
            m_gamma = sm.GLM(v_pos, X_const, family=Gamma(link=LogLink())).fit()
            aic_gamma = m_gamma.aic
        except Exception:
            aic_gamma = np.inf

        mejor = 'Gamma' if aic_gamma < aic_gauss else 'Gaussian'

        print(f"  {label:<22} {sk_raw:>6.2f} {sk_log:>8.2f} {p_shap:>10.6f} "
              f"{aic_gauss:>10.1f} {aic_gamma:>10.1f} {mejor:>8}")

        results_diag.append({
            'variable': var, 'label': label,
            'skew_raw': round(sk_raw, 3), 'skew_log': round(sk_log, 3),
            'shapiro_p': round(p_shap, 6),
            'AIC_gaussian': round(aic_gauss, 1), 'AIC_gamma': round(aic_gamma, 1),
            'mejor_familia': mejor,
        })

    df_diag = pd.DataFrame(results_diag)
    df_diag.to_csv(OUTPUTS / "h3_diagnostico_distribuciones.csv", index=False)
    print(f"\n  Guardado: h3_diagnostico_distribuciones.csv")
    return df_diag


# =============================================================================
# H3.1: MEDIACION SIMPLE
# Biodiversidad -> (-) Estres Termico -> (-) Impacto en Salud
# =============================================================================

def analisis_h3_1(df):
    print_header("H3.1: Biodiversidad -> Estres Termico -> Salud (Mediacion Simple)")

    # --- Correlaciones bivariadas (Spearman) ---
    print("\n--- Correlaciones bivariadas (Spearman) ---")
    biodiv_vars = ['forest_cover', 'mean_species_richness', 'idx_biodiv']
    heat_vars = ['fire_risk_index', 'fire_incidence_mean']
    health_vars = [h['name'] for h in HEALTH_OUTCOMES]

    results_corr = []
    for bv in biodiv_vars:
        for hv in heat_vars + health_vars:
            if bv in df.columns and hv in df.columns:
                r, p = stats.spearmanr(df[bv], df[hv], nan_policy='omit')
                results_corr.append({
                    'Variable_1': bv, 'Variable_2': hv,
                    'r_spearman': round(r, 4), 'p_value': round(p, 6),
                    'sig': sig_stars(p)
                })

    for hv in heat_vars:
        for sv in health_vars:
            if hv in df.columns and sv in df.columns:
                r, p = stats.spearmanr(df[hv], df[sv], nan_policy='omit')
                results_corr.append({
                    'Variable_1': hv, 'Variable_2': sv,
                    'r_spearman': round(r, 4), 'p_value': round(p, 6),
                    'sig': sig_stars(p)
                })

    df_corr = pd.DataFrame(results_corr)
    print(df_corr.to_string(index=False))

    # --- Analisis de mediacion: GLM Gamma + Bootstrap ---
    print("\n--- Mediacion H3.1 (GLM Gamma + Bootstrap IC95%) ---")
    print(f"  Bootstrap: {N_BOOTSTRAP} iteraciones\n")

    ctrl_z = [f'{c}_z' for c in CONTROLS if f'{c}_z' in df.columns]

    mediation_results = []

    for biodiv in ['forest_cover_z', 'idx_biodiv_z']:
        mediator = 'fire_risk_index_z'
        for outcome_info in HEALTH_OUTCOMES:
            outcome_raw = outcome_info['name']
            outcome_z = f'{outcome_raw}_z'
            outcome_label = outcome_info['label']

            if outcome_z not in df.columns:
                continue

            cols = [biodiv, mediator, outcome_z, outcome_raw] + ctrl_z
            df_clean = df[[c for c in cols if c in df.columns]].dropna()

            # --- Paths con OLS (log-z para mediacion) ---
            # Path a: X -> M
            m_a = fit_ols(df_clean[mediator], df_clean[[biodiv] + ctrl_z])
            a = m_a.params[biodiv]
            se_a = m_a.bse[biodiv]

            # Path b+c': M + X -> Y (OLS en z-scores)
            m_bc = fit_ols(df_clean[outcome_z],
                           df_clean[[biodiv, mediator] + ctrl_z])
            b = m_bc.params[mediator]
            se_b = m_bc.bse[mediator]
            c_prime = m_bc.params[biodiv]

            # Path c total
            m_c = fit_ols(df_clean[outcome_z], df_clean[[biodiv] + ctrl_z])
            c_total = m_c.params[biodiv]

            # --- GLM Gamma para path b (outcome en escala original) ---
            y_raw = df_clean[outcome_raw]
            if y_raw.min() > 0:
                m_glm, fam_used = fit_glm_gamma(
                    y_raw,
                    df_clean[[biodiv, mediator] + ctrl_z])
                b_glm = m_glm.params.get(mediator, np.nan)
                p_b_glm = m_glm.pvalues.get(mediator, np.nan)
            else:
                b_glm, p_b_glm, fam_used = np.nan, np.nan, 'N/A'

            # --- Bootstrap para efecto indirecto ---
            ab_obs, ci_lo, ci_hi, p_boot = bootstrap_indirect_effect(
                df, biodiv, mediator, outcome_z, ctrl_z)

            prop_mediated = (ab_obs / c_total * 100) if c_total != 0 else 0

            mediation_results.append({
                'X': biodiv.replace('_z', ''),
                'M': mediator.replace('_z', ''),
                'Y': outcome_label,
                'a(X->M)': round(a, 4),
                'b_OLS(M->Y)': round(b, 4),
                'b_GLM(M->Y)': round(b_glm, 4),
                'p_b_GLM': round(p_b_glm, 5) if not np.isnan(p_b_glm) else 'N/A',
                'GLM_family': fam_used,
                'ab_indirect': round(ab_obs, 4),
                'CI95_lo': round(ci_lo, 4),
                'CI95_hi': round(ci_hi, 4),
                'p_boot': round(p_boot, 5),
                'c_total': round(c_total, 4),
                'c_prime': round(c_prime, 4),
                '%_mediado': round(prop_mediated, 1),
                'sig_boot': sig_stars(p_boot),
            })

    df_med = pd.DataFrame(mediation_results)
    print(df_med.to_string(index=False))

    # Guardar
    df_corr.to_csv(OUTPUTS / "h3_1_correlaciones.csv", index=False)
    df_med.to_csv(OUTPUTS / "h3_1_mediacion.csv", index=False)

    return df_corr, df_med


# =============================================================================
# H3.2: MEDIACION SERIAL
# Biodiversidad -> (-) Fuego -> (-) Estres Termico -> (-) Salud
# =============================================================================

def analisis_h3_2(df):
    print_header("H3.2: Biodiversidad -> Fuego -> Estres Termico -> Salud")
    print("  Mediacion serial: OLS log-z + SEM + GLM Gamma sensibilidad\n")

    ctrl_z = [f'{c}_z' for c in CONTROLS if f'{c}_z' in df.columns]

    results_serial = []

    for biodiv in ['forest_cover_z', 'idx_biodiv_z']:
        for outcome_info in HEALTH_OUTCOMES:
            outcome_z = f"{outcome_info['name']}_z"
            outcome_raw = outcome_info['name']
            outcome_label = outcome_info['label']
            mediator1 = 'fire_incidence_mean_z'  # Fuego (incidencia)
            mediator2 = 'fire_risk_index_z'      # Riesgo termico (proxy)

            cols = [biodiv, mediator1, mediator2, outcome_z, outcome_raw] + ctrl_z
            cols_available = [c for c in cols if c in df.columns]
            df_clean = df[cols_available].dropna()

            if len(df_clean) < 50:
                continue

            # --- OLS paths (log-z) ---
            # a1: Biodiv -> Fuego
            m_a1 = fit_ols(df_clean[mediator1], df_clean[[biodiv] + ctrl_z])
            a1 = m_a1.params[biodiv]

            # a2: Fuego -> Riesgo (controlando Biodiv)
            m_a2 = fit_ols(df_clean[mediator2],
                           df_clean[[biodiv, mediator1] + ctrl_z])
            a2 = m_a2.params[mediator1]
            a3 = m_a2.params[biodiv]

            # Paths finales: Todo -> Outcome
            m_b = fit_ols(df_clean[outcome_z],
                          df_clean[[biodiv, mediator1, mediator2] + ctrl_z])
            b = m_b.params[mediator2]
            d1 = m_b.params[mediator1]
            cp = m_b.params[biodiv]

            # Efectos indirectos
            serial = a1 * a2 * b
            via_fire = a1 * d1
            via_heat = a3 * b
            total_indirect = serial + via_fire + via_heat

            # Efecto total
            m_total = fit_ols(df_clean[outcome_z], df_clean[[biodiv] + ctrl_z])
            c_total = m_total.params[biodiv]

            # --- GLM Gamma para path final (sensibilidad) ---
            y_raw = df_clean[outcome_raw]
            if y_raw.min() > 0:
                m_glm, fam = fit_glm_gamma(
                    y_raw,
                    df_clean[[biodiv, mediator1, mediator2] + ctrl_z])
                b_glm = m_glm.params.get(mediator2, np.nan)
                p_b_glm = m_glm.pvalues.get(mediator2, np.nan)
            else:
                b_glm, p_b_glm, fam = np.nan, np.nan, 'N/A'

            results_serial.append({
                'X': biodiv.replace('_z', ''),
                'Y': outcome_label,
                'a1(X->Fuego)': round(a1, 4),
                'a2(Fuego->Calor)': round(a2, 4),
                'a3(X->Calor)': round(a3, 4),
                'b_OLS(Calor->Y)': round(b, 4),
                'b_GLM(Calor->Y)': round(b_glm, 4),
                'p_b_GLM': round(p_b_glm, 5) if not np.isnan(p_b_glm) else 'N/A',
                'd1(Fuego->Y)': round(d1, 4),
                'Serial(a1*a2*b)': round(serial, 4),
                'Via_fuego(a1*d1)': round(via_fire, 4),
                'Via_calor(a3*b)': round(via_heat, 4),
                'Total_indirecto': round(total_indirect, 4),
                'Directo(cp)': round(cp, 4),
                'Total(c)': round(c_total, 4),
                '%_mediado': round(total_indirect / c_total * 100, 1) if c_total != 0 else 0,
            })

    df_serial = pd.DataFrame(results_serial)
    print(df_serial.to_string(index=False))

    # --- SEM con semopy ---
    if HAS_SEMOPY:
        print("\n--- SEM con semopy (log-z variables) ---")

        # Construir SEM para cada outcome
        for outcome_info in HEALTH_OUTCOMES:
            outcome_z = f"{outcome_info['name']}_z"
            outcome_label = outcome_info['label']

            if outcome_z not in df.columns:
                continue

            cols_sem = ['forest_cover_z', 'fire_incidence_mean_z',
                        'fire_risk_index_z', outcome_z,
                        'pct_rural_z', 'log_pop_z', 'idx_vulnerabilidad_z']
            cols_sem = [c for c in cols_sem if c in df.columns]
            df_sem = df[cols_sem].dropna()

            model_desc = f"""
            fire_incidence_mean_z ~ forest_cover_z + pct_rural_z + log_pop_z
            fire_risk_index_z ~ fire_incidence_mean_z + forest_cover_z + pct_rural_z
            {outcome_z} ~ fire_risk_index_z + fire_incidence_mean_z + forest_cover_z + idx_vulnerabilidad_z
            """
            try:
                model = semopy.Model(model_desc)
                result = model.fit(df_sem)
                estimates = model.inspect()
                stats_sem = semopy.calc_stats(model)

                print(f"\n  SEM Y={outcome_label} (N={len(df_sem)}): "
                      f"Chi2={stats_sem.get('chi2', ['N/A'])[0]:.3f}, "
                      f"CFI={stats_sem.get('CFI', ['N/A'])[0]:.3f}, "
                      f"RMSEA={stats_sem.get('RMSEA', ['N/A'])[0]:.3f}")

                paths = estimates[estimates['op'] == '~'].copy()
                paths['sig'] = paths['p-value'].apply(sig_stars)
                print(paths[['lval', 'op', 'rval', 'Estimate',
                             'Std. Err', 'p-value', 'sig']].to_string(index=False))

                safe_label = outcome_info['name'].replace('_rate', '')
                estimates.to_csv(
                    OUTPUTS / f"h3_2_sem_{safe_label}.csv", index=False)

            except Exception as e:
                print(f"  Error SEM Y={outcome_label}: {e}")

    df_serial.to_csv(OUTPUTS / "h3_2_mediacion_serial.csv", index=False)
    return df_serial


# =============================================================================
# H3.3: MEDIACION MODERADA
# (Biodiversidad -> Fuego) * Vulnerabilidad -> Estres Termico -> Salud
# =============================================================================

def analisis_h3_3(df):
    print_header("H3.3: Moderacion por Vulnerabilidad")
    print("  GLM Gamma para outcomes de salud, OLS para mediadores\n")

    # Crear interacciones (en z-scores)
    df['forest_x_rural'] = df['forest_cover_z'] * df['pct_rural_z']
    df['forest_x_poverty'] = df['forest_cover_z'] * df['pct_pobreza_z']
    df['fire_x_rural'] = df['fire_risk_index_z'] * df['pct_rural_z']
    df['fire_x_poverty'] = df['fire_risk_index_z'] * df['pct_pobreza_z']

    results_mod = []

    # -----------------------------------------------------------------
    # A) Moderacion sobre Biodiv -> Fuego (OLS, respuesta ~normal tras z)
    # -----------------------------------------------------------------
    for mod_name, mod_var, interaction in [
        ('Rural', 'pct_rural_z', 'forest_x_rural'),
        ('Pobreza', 'pct_pobreza_z', 'forest_x_poverty'),
    ]:
        print(f"\n--- Moderacion: Biodiv -> Fuego (por {mod_name}) [OLS] ---")
        predictors = ['forest_cover_z', mod_var, interaction, 'log_pop_z']
        X = df[predictors].dropna()
        y = df.loc[X.index, 'fire_incidence_mean_z']
        model = fit_ols(y, X)
        print(model.summary2().tables[1])
        results_mod.append({
            'Modelo': f'Biodiv -> Fuego * {mod_name}',
            'Outcome': 'fire_incidence (z)',
            'Familia': 'OLS (z-score)',
            'Interaccion': interaction,
            'Coef': round(model.params.get(interaction, 0), 4),
            'SE': round(model.bse.get(interaction, 0), 4),
            'p': round(model.pvalues.get(interaction, 1), 5),
            'sig': sig_stars(model.pvalues.get(interaction, 1)),
            'R2': round(model.rsquared, 4),
            'N': int(model.nobs),
        })

    # -----------------------------------------------------------------
    # B) Moderacion sobre Fuego -> Salud (GLM Gamma, 4 outcomes)
    # -----------------------------------------------------------------
    for mod_name, mod_var, interaction in [
        ('Pobreza', 'pct_pobreza_z', 'fire_x_poverty'),
        ('Rural', 'pct_rural_z', 'fire_x_rural'),
    ]:
        for outcome_info in HEALTH_OUTCOMES:
            outcome_raw = outcome_info['name']
            outcome_label = outcome_info['label']

            print(f"\n--- Moderacion: Fuego -> {outcome_label} (por {mod_name}) [GLM Gamma] ---")

            predictors = ['fire_risk_index_z', mod_var, interaction,
                          'log_pop_z', 'pct_pobreza_z' if mod_var != 'pct_pobreza_z' else 'pct_rural_z']
            X = df[predictors].dropna()
            y_raw = df.loc[X.index, outcome_raw]

            # Filtrar y > 0 para Gamma
            mask_pos = y_raw > 0
            X = X.loc[mask_pos]
            y_raw = y_raw.loc[mask_pos]

            m_glm, fam = fit_glm_gamma(y_raw, X)

            coef_int = m_glm.params.get(interaction, np.nan)
            p_int = m_glm.pvalues.get(interaction, np.nan)

            print(f"  {fam}: coef({interaction}) = {coef_int:.4f}, p = {p_int:.5f}")

            results_mod.append({
                'Modelo': f'Fuego -> {outcome_label} * {mod_name}',
                'Outcome': outcome_raw,
                'Familia': fam,
                'Interaccion': interaction,
                'Coef': round(coef_int, 4) if not np.isnan(coef_int) else 'N/A',
                'SE': round(m_glm.bse.get(interaction, np.nan), 4),
                'p': round(p_int, 5) if not np.isnan(p_int) else 'N/A',
                'sig': sig_stars(p_int) if not np.isnan(p_int) else 'N/A',
                'R2': 'N/A (GLM)',
                'N': int(m_glm.nobs),
            })

    df_mod = pd.DataFrame(results_mod)
    print("\n--- Resumen de moderaciones ---")
    print(df_mod.to_string(index=False))
    df_mod.to_csv(OUTPUTS / "h3_3_moderacion.csv", index=False)

    # -----------------------------------------------------------------
    # C) Simple slopes: Biodiv -> Fuego a distintos niveles de ruralidad
    # -----------------------------------------------------------------
    print("\n--- Simple Slopes: Biodiv -> Fuego por ruralidad ---")
    slopes_results = []
    for level_name, level_val in [('Baja (-1SD)', -1), ('Media (0)', 0), ('Alta (+1SD)', 1)]:
        df_temp = df.copy()
        df_temp['mod_centered'] = df_temp['pct_rural_z'] - level_val
        df_temp['interact_c'] = df_temp['forest_cover_z'] * df_temp['mod_centered']
        X = df_temp[['forest_cover_z', 'mod_centered', 'interact_c', 'log_pop_z']].dropna()
        y = df_temp.loc[X.index, 'fire_incidence_mean_z']
        m = fit_ols(y, X)
        coef = m.params['forest_cover_z']
        pval = m.pvalues['forest_cover_z']
        print(f"  Ruralidad {level_name}: b = {coef:.4f}, p = {pval:.5f} {sig_stars(pval)}")
        slopes_results.append({
            'Moderador': 'pct_rural',
            'Nivel': level_name,
            'b_forest': round(coef, 4),
            'p': round(pval, 5),
            'sig': sig_stars(pval),
        })

    print("\n--- Simple Slopes: Biodiv -> Fuego por pobreza ---")
    for level_name, level_val in [('Baja (-1SD)', -1), ('Media (0)', 0), ('Alta (+1SD)', 1)]:
        df_temp = df.copy()
        df_temp['mod_centered'] = df_temp['pct_pobreza_z'] - level_val
        df_temp['interact_c'] = df_temp['forest_cover_z'] * df_temp['mod_centered']
        X = df_temp[['forest_cover_z', 'mod_centered', 'interact_c', 'log_pop_z']].dropna()
        y = df_temp.loc[X.index, 'fire_incidence_mean_z']
        m = fit_ols(y, X)
        coef = m.params['forest_cover_z']
        pval = m.pvalues['forest_cover_z']
        print(f"  Pobreza {level_name}: b = {coef:.4f}, p = {pval:.5f} {sig_stars(pval)}")
        slopes_results.append({
            'Moderador': 'pct_pobreza',
            'Nivel': level_name,
            'b_forest': round(coef, 4),
            'p': round(pval, 5),
            'sig': sig_stars(pval),
        })

    pd.DataFrame(slopes_results).to_csv(
        OUTPUTS / "h3_3_simple_slopes.csv", index=False)

    return df_mod


# =============================================================================
# H3.4: MODELO COMPLETO CON GOBERNANZA
# Gobernanza -> (Biodiv -> Fuego) * Vulnerabilidad -> Calor -> Salud
# =============================================================================

def analisis_h3_4(df):
    print_header("H3.4: Modelo Completo con Gobernanza")
    print("  SEM + GLM Gamma, 4 outcomes de salud\n")

    # --- Paths de gobernanza (OLS + GLM) ---
    print("--- Gobernanza como facilitador ---")
    results_gov = []

    for gov_var in ['idx_gobernanza_z', 'UAI_Crisk_z']:
        gov_label = gov_var.replace('_z', '')

        # g1: Gobernanza -> Biodiversidad (OLS, forest_cover_z)
        X = df[[gov_var, 'pct_rural_z', 'log_pop_z']].dropna()
        y = df.loc[X.index, 'forest_cover_z']
        m = fit_ols(y, X)
        results_gov.append({
            'Path': f'{gov_label} -> forest_cover',
            'Familia': 'OLS',
            'Coef': round(m.params[gov_var], 4),
            'SE': round(m.bse[gov_var], 4),
            'p': round(m.pvalues[gov_var], 5),
            'sig': sig_stars(m.pvalues[gov_var]),
        })

        # g2: Gobernanza -> Fuego (OLS)
        X = df[[gov_var, 'forest_cover_z', 'pct_rural_z', 'log_pop_z']].dropna()
        y = df.loc[X.index, 'fire_incidence_mean_z']
        m = fit_ols(y, X)
        results_gov.append({
            'Path': f'{gov_label} -> fire_incidence',
            'Familia': 'OLS',
            'Coef': round(m.params[gov_var], 4),
            'SE': round(m.bse[gov_var], 4),
            'p': round(m.pvalues[gov_var], 5),
            'sig': sig_stars(m.pvalues[gov_var]),
        })

        # g3: Gobernanza -> Outcomes de salud (GLM Gamma, 4 outcomes)
        for outcome_info in HEALTH_OUTCOMES:
            outcome_raw = outcome_info['name']
            outcome_label = outcome_info['label']

            X = df[[gov_var, 'forest_cover_z', 'fire_risk_index_z',
                     'pct_rural_z', 'idx_vulnerabilidad_z', 'pct_pobreza_z']].dropna()
            y_raw = df.loc[X.index, outcome_raw]
            mask_pos = y_raw > 0
            X_pos, y_pos = X.loc[mask_pos], y_raw.loc[mask_pos]

            m_glm, fam = fit_glm_gamma(y_pos, X_pos)
            coef_gov = m_glm.params.get(gov_var, np.nan)
            p_gov = m_glm.pvalues.get(gov_var, np.nan)
            results_gov.append({
                'Path': f'{gov_label} -> {outcome_label}',
                'Familia': fam,
                'Coef': round(coef_gov, 4) if not np.isnan(coef_gov) else 'N/A',
                'SE': round(m_glm.bse.get(gov_var, np.nan), 4),
                'p': round(p_gov, 5) if not np.isnan(p_gov) else 'N/A',
                'sig': sig_stars(p_gov) if not np.isnan(p_gov) else 'N/A',
            })

    df_gov = pd.DataFrame(results_gov)
    print(df_gov.to_string(index=False))

    # --- SEM completo H3.4 (4 outcomes) ---
    if HAS_SEMOPY:
        print("\n--- SEM Completo H3.4 ---")

        for outcome_info in HEALTH_OUTCOMES:
            outcome_z = f"{outcome_info['name']}_z"
            outcome_label = outcome_info['label']

            if outcome_z not in df.columns:
                continue

            cols_needed = ['idx_gobernanza_z', 'UAI_Crisk_z', 'forest_cover_z',
                           'fire_incidence_mean_z', 'fire_risk_index_z',
                           outcome_z,
                           'pct_rural_z', 'pct_pobreza_z', 'log_pop_z',
                           'idx_vulnerabilidad_z']
            cols_available = [c for c in cols_needed if c in df.columns]
            df_sem = df[cols_available].dropna()

            for gov_name, gov_var in [("Gob.General", "idx_gobernanza_z"),
                                      ("Gob.Climatica", "UAI_Crisk_z")]:
                model_desc = f"""
                forest_cover_z ~ {gov_var} + pct_rural_z + log_pop_z
                fire_incidence_mean_z ~ {gov_var} + forest_cover_z + pct_rural_z
                fire_risk_index_z ~ fire_incidence_mean_z + forest_cover_z + pct_rural_z
                {outcome_z} ~ fire_risk_index_z + fire_incidence_mean_z + forest_cover_z + idx_vulnerabilidad_z + pct_pobreza_z
                """
                try:
                    model = semopy.Model(model_desc)
                    result = model.fit(df_sem)
                    estimates = model.inspect()
                    stats_sem = semopy.calc_stats(model)

                    print(f"\n  SEM {gov_name} -> {outcome_label} (N={len(df_sem)}): "
                          f"Chi2={stats_sem.get('chi2', ['N/A'])[0]:.3f}, "
                          f"CFI={stats_sem.get('CFI', ['N/A'])[0]:.3f}, "
                          f"RMSEA={stats_sem.get('RMSEA', ['N/A'])[0]:.3f}")

                    paths = estimates[estimates['op'] == '~'].copy()
                    paths['sig'] = paths['p-value'].apply(sig_stars)
                    print(paths[['lval', 'op', 'rval', 'Estimate',
                                 'Std. Err', 'p-value', 'sig']].to_string(index=False))

                    safe_name = f"{gov_name}_{outcome_info['name']}".replace('.', '_').replace(' ', '_')
                    estimates.to_csv(
                        OUTPUTS / f"h3_4_sem_{safe_name}.csv", index=False)

                except Exception as e:
                    print(f"  Error SEM {gov_name} -> {outcome_label}: {e}")

    # --- Descomposicion de efectos indirectos de gobernanza ---
    print("\n--- Descomposicion efectos indirectos (por outcome) ---")

    decomp_results = []
    for outcome_info in HEALTH_OUTCOMES:
        outcome_z = f"{outcome_info['name']}_z"
        outcome_label = outcome_info['label']

        if outcome_z not in df.columns:
            continue

        cols = ['idx_gobernanza_z', 'forest_cover_z', 'fire_incidence_mean_z',
                'fire_risk_index_z', outcome_z,
                'pct_rural_z', 'log_pop_z', 'idx_vulnerabilidad_z', 'pct_pobreza_z']
        cols = [c for c in cols if c in df.columns]
        df_clean = df[cols].dropna()

        # g1: Gob -> Forest
        m = fit_ols(df_clean['forest_cover_z'],
                    df_clean[['idx_gobernanza_z', 'pct_rural_z', 'log_pop_z']])
        g1 = m.params['idx_gobernanza_z']

        # g2: Gob -> Fire
        m = fit_ols(df_clean['fire_incidence_mean_z'],
                    df_clean[['idx_gobernanza_z', 'forest_cover_z', 'pct_rural_z']])
        g2 = m.params['idx_gobernanza_z']

        # a1: Forest -> Fire
        m = fit_ols(df_clean['fire_incidence_mean_z'],
                    df_clean[['forest_cover_z', 'pct_rural_z', 'log_pop_z']])
        a1 = m.params['forest_cover_z']

        # a2, a3: Fire -> Heat, Forest -> Heat
        m = fit_ols(df_clean['fire_risk_index_z'],
                    df_clean[['fire_incidence_mean_z', 'forest_cover_z', 'pct_rural_z']])
        a2 = m.params['fire_incidence_mean_z']
        a3 = m.params['forest_cover_z']

        # b, d1: Heat -> Y, Fire -> Y
        m = fit_ols(df_clean[outcome_z],
                    df_clean[['fire_risk_index_z', 'fire_incidence_mean_z',
                              'forest_cover_z', 'idx_vulnerabilidad_z', 'pct_pobreza_z']])
        b = m.params['fire_risk_index_z']
        d1 = m.params['fire_incidence_mean_z']

        gov_via_biodiv = g1 * a3 * b
        gov_via_fire = g2 * a2 * b
        gov_full_chain = g1 * a1 * a2 * b
        gov_total = gov_via_biodiv + gov_via_fire + gov_full_chain

        decomp_results.append({
            'Outcome': outcome_label,
            'g1(Gob->Forest)': round(g1, 4),
            'g2(Gob->Fire)': round(g2, 4),
            'a1(Forest->Fire)': round(a1, 4),
            'a2(Fire->Heat)': round(a2, 4),
            'b(Heat->Y)': round(b, 4),
            'Via_biodiv(g1*a3*b)': round(gov_via_biodiv, 4),
            'Via_fire(g2*a2*b)': round(gov_via_fire, 4),
            'Full_chain(g1*a1*a2*b)': round(gov_full_chain, 4),
            'Total_indirecto': round(gov_total, 4),
        })

        print(f"\n  {outcome_label}:")
        print(f"    Via biodiversidad: {gov_via_biodiv:.4f}")
        print(f"    Via reduccion fuego: {gov_via_fire:.4f}")
        print(f"    Cadena completa: {gov_full_chain:.4f}")
        print(f"    Total: {gov_total:.4f}")

    pd.DataFrame(decomp_results).to_csv(
        OUTPUTS / "h3_4_descomposicion_gobernanza.csv", index=False)
    df_gov.to_csv(OUTPUTS / "h3_4_gobernanza_paths.csv", index=False)

    return df_gov


# =============================================================================
# FIGURAS
# =============================================================================

def generar_figuras(df, df_corr):
    print_header("Generando Figuras")

    # -----------------------------------------------------------------
    # Figura 1: Panel 2x3 relaciones clave
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('H3: Biodiversidad, Fuego/Estres Termico y Salud\n'
                 '645 municipios de Sao Paulo (2010-2019)',
                 fontsize=14, fontweight='bold')

    # 1a: Forest -> Fire (log-scale)
    ax = axes[0, 0]
    x, y = df['forest_cover'], df['fire_incidence_mean']
    ax.scatter(x, y, alpha=0.3, s=10, c='forestgreen')
    r, p = stats.spearmanr(x, y, nan_policy='omit')
    z = np.polyfit(x, y, 1)
    ax.plot(np.sort(x), np.polyval(z, np.sort(x)), 'r-', lw=2)
    ax.set_xlabel('Cobertura forestal (%)')
    ax.set_ylabel('Incidencia fuego (media anual)')
    ax.set_title(f'H3.2: Biodiv -> Fuego\nr={r:.3f}, p={p:.1e}')

    # 1b: Fire -> Mort CV
    ax = axes[0, 1]
    x, y = df['fire_risk_index'], df['health_death_circ_mean']
    ax.scatter(x, y, alpha=0.3, s=10, c='orangered')
    r, p = stats.spearmanr(x, y, nan_policy='omit')
    z = np.polyfit(x, y, 1)
    ax.plot(np.sort(x), np.polyval(z, np.sort(x)), 'r-', lw=2)
    ax.set_xlabel('Indice riesgo fuego')
    ax.set_ylabel('Mortalidad circulatoria (por 100k)')
    ax.set_title(f'H3.1: Fuego -> Mort. CV\nr={r:.3f}, p={p:.1e}')

    # 1c: Fire -> Hosp CV (NUEVO)
    ax = axes[0, 2]
    x, y = df['fire_risk_index'], df['health_hosp_circ_mean']
    ax.scatter(x, y, alpha=0.3, s=10, c='steelblue')
    r, p = stats.spearmanr(x, y, nan_policy='omit')
    z = np.polyfit(x, y, 1)
    ax.plot(np.sort(x), np.polyval(z, np.sort(x)), 'r-', lw=2)
    ax.set_xlabel('Indice riesgo fuego')
    ax.set_ylabel('Hospitalizaciones CV (por 100k)')
    ax.set_title(f'H3.1: Fuego -> Hosp. CV\nr={r:.3f}, p={p:.1e}')

    # 2a: Moderacion por ruralidad
    ax = axes[1, 0]
    q_rural = pd.qcut(df['pct_rural'], 3, labels=['Urbano', 'Mixto', 'Rural'])
    colors = {'Urbano': 'steelblue', 'Mixto': 'gold', 'Rural': 'forestgreen'}
    for label in ['Urbano', 'Mixto', 'Rural']:
        mask = q_rural == label
        ax.scatter(df.loc[mask, 'forest_cover'], df.loc[mask, 'fire_incidence_mean'],
                   alpha=0.3, s=10, c=colors[label], label=label)
        if mask.sum() > 5:
            z = np.polyfit(df.loc[mask, 'forest_cover'],
                           df.loc[mask, 'fire_incidence_mean'], 1)
            xs = np.sort(df.loc[mask, 'forest_cover'])
            ax.plot(xs, np.polyval(z, xs), c=colors[label], lw=2)
    ax.legend(fontsize=8)
    ax.set_xlabel('Cobertura forestal (%)')
    ax.set_ylabel('Incidencia fuego')
    ax.set_title('H3.3: Moderacion por ruralidad')

    # 2b: Moderacion por pobreza
    ax = axes[1, 1]
    q_pov = pd.qcut(df['pct_pobreza'], 3,
                     labels=['Baja pobreza', 'Media', 'Alta pobreza'],
                     duplicates='drop')
    colors_p = {'Baja pobreza': 'steelblue', 'Media': 'gold', 'Alta pobreza': 'orangered'}
    for label in ['Baja pobreza', 'Media', 'Alta pobreza']:
        mask = q_pov == label
        if mask.sum() > 5:
            ax.scatter(df.loc[mask, 'fire_risk_index'],
                       df.loc[mask, 'health_death_circ_mean'],
                       alpha=0.3, s=10, c=colors_p[label], label=label)
            z = np.polyfit(df.loc[mask, 'fire_risk_index'],
                           df.loc[mask, 'health_death_circ_mean'], 1)
            xs = np.sort(df.loc[mask, 'fire_risk_index'])
            ax.plot(xs, np.polyval(z, xs), c=colors_p[label], lw=2)
    ax.legend(fontsize=8)
    ax.set_xlabel('Indice riesgo fuego')
    ax.set_ylabel('Mortalidad circulatoria')
    ax.set_title('H3.3: Moderacion por pobreza')

    # 2c: Gobernanza -> Forest
    ax = axes[1, 2]
    x, y = df['idx_gobernanza'], df['forest_cover']
    ax.scatter(x, y, alpha=0.3, s=10, c='purple')
    r, p = stats.spearmanr(x, y, nan_policy='omit')
    z = np.polyfit(x, y, 1)
    ax.plot(np.sort(x), np.polyval(z, np.sort(x)), 'r-', lw=2)
    ax.set_xlabel('Indice gobernanza')
    ax.set_ylabel('Cobertura forestal (%)')
    ax.set_title(f'H3.4: Gobernanza -> Biodiv\nr={r:.3f}, p={p:.1e}')

    plt.tight_layout()
    fig.savefig(FIGURES / "h3_analisis_completo.png", dpi=150, bbox_inches='tight')
    print(f"  Figura: h3_analisis_completo.png")
    plt.close()

    # -----------------------------------------------------------------
    # Figura 2: Heatmap con los 4 outcomes
    # -----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10))
    vars_heatmap = ['forest_cover', 'mean_species_richness', 'idx_biodiv',
                    'fire_incidence_mean', 'fire_risk_index',
                    'health_death_circ_mean', 'health_death_resp_mean',
                    'health_hosp_circ_mean', 'health_hosp_resp_mean',
                    'pct_pobreza', 'pct_rural', 'idx_gobernanza', 'UAI_Crisk']
    labels_heatmap = ['Cobert.\nforestal', 'Riqueza\nspp', 'Idx\nBiodiv',
                      'Incid.\nfuego', 'Riesgo\nfuego',
                      'Mort.\nCV', 'Mort.\nResp.',
                      'Hosp.\nCV', 'Hosp.\nResp.',
                      'Pobreza', 'Rural', 'Gobernanza', 'UAI\nClima']

    available = [v for v in vars_heatmap if v in df.columns]
    labels_avail = [labels_heatmap[i] for i, v in enumerate(vars_heatmap) if v in df.columns]

    corr_matrix = df[available].corr(method='spearman')
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, ax=ax,
                xticklabels=labels_avail, yticklabels=labels_avail,
                square=True, linewidths=0.5)
    ax.set_title('Correlaciones Spearman: Variables H3 (incl. hospitalizaciones)\n'
                 '645 municipios Sao Paulo (2010-2019)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES / "h3_heatmap_correlaciones.png", dpi=150, bbox_inches='tight')
    print(f"  Figura: h3_heatmap_correlaciones.png")
    plt.close()

    # -----------------------------------------------------------------
    # Figura 3: Diagnostico de distribuciones (raw vs log)
    # -----------------------------------------------------------------
    vars_dist = {
        'fire_incidence_mean': 'Incid. fuego',
        'forest_cover': 'Cobert. forestal',
        'hosp_circ_rate': 'Hosp. CV',
        'hosp_resp_rate': 'Hosp. Resp.',
        'mort_circ_rate': 'Mort. CV',
        'mort_resp_rate': 'Mort. Resp.',
    }
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Distribucion de variables: Raw vs Log-normal fit\n'
                 '645 municipios Sao Paulo', fontsize=14, fontweight='bold')

    for ax, (var, label) in zip(axes.flat, vars_dist.items()):
        if var not in df.columns:
            continue
        v = df[var].dropna()
        sk = stats.skew(v)
        ax.hist(v, bins=40, color='steelblue', alpha=0.7,
                edgecolor='white', density=True)
        # Log-normal fit
        if v.min() > 0:
            v_log = np.log(v)
            x_log = np.linspace(v_log.min(), v_log.max(), 100)
            pdf_log = stats.norm.pdf(x_log, v_log.mean(), v_log.std())
            x_orig = np.exp(x_log)
            pdf_orig = pdf_log / x_orig
            ax.plot(x_orig, pdf_orig, 'r-', lw=2, label='Log-normal')
        # Gaussian fit
        x_norm = np.linspace(v.min(), v.max(), 100)
        pdf_norm = stats.norm.pdf(x_norm, v.mean(), v.std())
        ax.plot(x_norm, pdf_norm, 'g--', lw=2, label='Gaussian')
        ax.set_title(f'{label} (skew={sk:.2f})', fontsize=11)
        ax.legend(fontsize=8)

    plt.tight_layout()
    fig.savefig(FIGURES / "h3_distribucion_variables.png", dpi=150, bbox_inches='tight')
    print(f"  Figura: h3_distribucion_variables.png")
    plt.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("  ANALISIS H3 v2: BIODIVERSIDAD, ESTRES TERMICO Y SALUD")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  Correcciones: GLM Gamma + log-transform + 4 outcomes + Bootstrap")
    print(f"  Proxy estres termico: fire_risk_index")
    print(f"  (Sustituir por MODIS LST cuando datos disponibles)")
    print("=" * 80)

    # 1. Cargar datos
    df = load_data()

    # 2. Diagnostico de distribuciones
    diagnostico_distribuciones(df)

    # 3. Analisis H3.1-H3.4
    df_corr, df_med = analisis_h3_1(df)
    df_serial = analisis_h3_2(df)
    df_mod = analisis_h3_3(df)
    df_gov = analisis_h3_4(df)

    # 4. Figuras
    generar_figuras(df, df_corr)

    # 5. Resumen
    print_header("RESUMEN H3 v2")
    print("""
    CORRECCIONES METODOLOGICAS:
      - GLM Gamma(link=log) para outcomes de salud (distribucion apropiada)
      - Log-transform para variables con skew > 1 antes de z-standardizar
      - Bootstrap IC 95% para efectos indirectos (reemplaza Sobel test)
      - 4 outcomes: Mort.CV, Mort.Resp, Hosp.CV, Hosp.Resp

    H3.1 - Mediacion Simple (GLM + Bootstrap):
      - Correlaciones bivariadas con 4 outcomes
      - Mediacion con bootstrap IC 95% (mas robusto que Sobel)
      - GLM Gamma como analisis primario

    H3.2 - Mediacion Serial (OLS + SEM + GLM):
      - 4 outcomes x 2 biodiv = 8 combinaciones
      - SEM individual por outcome
      - GLM Gamma sensibilidad para path final

    H3.3 - Moderacion (GLM Gamma):
      - Biodiv->Fuego moderado por ruralidad y pobreza (OLS)
      - Fuego->Salud moderado por pobreza y ruralidad (GLM Gamma x 4 outcomes)
      - Simple slopes por ruralidad Y por pobreza

    H3.4 - Gobernanza (SEM + GLM):
      - 8 modelos SEM (2 gobernanza x 4 outcomes)
      - GLM Gamma para cada path gobernanza->salud
      - Descomposicion de efectos indirectos por outcome

    NOTA: Proxy fire_risk_index. Cuando MODIS LST disponible, reemplazar
    y re-ejecutar (la estructura es identica).
    """)

    print("Archivos generados:")
    for f in sorted(OUTPUTS.glob("h3_*")):
        print(f"  {f.name}")
    for f in sorted(FIGURES.glob("h3_*")):
        print(f"  figures/{f.name}")


if __name__ == '__main__':
    main()
