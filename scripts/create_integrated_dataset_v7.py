# =============================================================================
# Script para crear dataset integrado v7
# Integra: v6 + indicadores de fuego + indicadores de salud
# =============================================================================
#
# Autor: Science Team
# Fecha: 2026-01-23
# =============================================================================

import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
OUTPUTS = PROJECT_ROOT / "outputs"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

def main():
    print("=" * 70)
    print("Creación de Dataset Integrado v7")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # =========================================================================
    # Cargar datasets
    # =========================================================================
    print("\n--- Cargando datasets ---")

    # Dataset principal v6
    v6_file = OUTPUTS / "municipios_integrado_v6.csv"
    df_v6 = pd.read_csv(v6_file)
    df_v6['cod_ibge'] = df_v6['cod_ibge'].astype(str)
    print(f"Dataset v6: {len(df_v6)} municipios, {len(df_v6.columns)} columnas")

    # Indicadores de fuego
    fire_file = DATA_PROCESSED / "fire_indicators_SP_2010_2019.csv"
    df_fire = pd.read_csv(fire_file)
    df_fire['cod_ibge'] = df_fire['cod_ibge'].astype(str)
    # Seleccionar columnas relevantes (excluir las normalizadas temporales)
    fire_cols = [c for c in df_fire.columns if not c.endswith('_norm') or c == 'cod_ibge']
    df_fire = df_fire[fire_cols]
    print(f"Indicadores de fuego: {len(df_fire)} municipios, {len(df_fire.columns)-1} indicadores")

    # Indicadores de salud
    health_file = DATA_PROCESSED / "health_heat_indicators_SP_2010_2019.csv"
    df_health = pd.read_csv(health_file)
    df_health['cod_ibge'] = df_health['cod_ibge'].astype(str)
    # Renombrar columnas para claridad
    health_rename = {
        'inc_hosp_circ_media': 'health_hosp_circ_mean',
        'inc_hosp_resp_media': 'health_hosp_resp_mean',
        'inc_hosp_calor_media': 'health_hosp_heat_mean',
        'inc_hosp_circ_max': 'health_hosp_circ_max',
        'inc_hosp_resp_max': 'health_hosp_resp_max',
        'inc_hosp_calor_max': 'health_hosp_heat_max',
        'inc_obit_circ_media': 'health_death_circ_mean',
        'inc_obit_resp_media': 'health_death_resp_mean',
        'inc_obit_calor_media': 'health_death_heat_mean',
        'inc_obit_circ_max': 'health_death_circ_max',
        'inc_obit_resp_max': 'health_death_resp_max',
        'inc_obit_calor_max': 'health_death_heat_max',
        'total_hosp_circ': 'health_total_hosp_circ',
        'total_hosp_resp': 'health_total_hosp_resp',
        'total_hosp_calor': 'health_total_hosp_heat',
        'total_obit_circ': 'health_total_death_circ',
        'total_obit_resp': 'health_total_death_resp',
        'total_obit_calor': 'health_total_death_heat'
    }
    df_health = df_health.rename(columns=health_rename)
    print(f"Indicadores de salud: {len(df_health)} municipios, {len(df_health.columns)-1} indicadores")

    # =========================================================================
    # Integrar datasets
    # =========================================================================
    print("\n--- Integrando datasets ---")

    # Merge con fire indicators
    df_v7 = df_v6.merge(df_fire, on='cod_ibge', how='left')
    print(f"Después de merge con fuego: {len(df_v7.columns)} columnas")

    # Merge con health indicators
    df_v7 = df_v7.merge(df_health, on='cod_ibge', how='left')
    print(f"Después de merge con salud: {len(df_v7.columns)} columnas")

    # =========================================================================
    # Verificar integridad
    # =========================================================================
    print("\n--- Verificando integridad ---")

    # Verificar que no perdimos municipios
    assert len(df_v7) == len(df_v6), "ERROR: Se perdieron municipios en el merge"
    print(f"Municipios: {len(df_v7)} (sin pérdidas)")

    # Verificar NaN en nuevas columnas
    fire_cols_new = [c for c in df_fire.columns if c != 'cod_ibge']
    health_cols_new = [c for c in df_health.columns if c != 'cod_ibge']

    fire_nan = df_v7[fire_cols_new].isna().sum().sum()
    health_nan = df_v7[health_cols_new].isna().sum().sum()

    print(f"NaN en indicadores de fuego: {fire_nan}")
    print(f"NaN en indicadores de salud: {health_nan}")

    # =========================================================================
    # Guardar dataset v7
    # =========================================================================
    print("\n--- Guardando dataset ---")

    output_file = OUTPUTS / "municipios_integrado_v7.csv"
    df_v7.to_csv(output_file, index=False)
    print(f"Archivo guardado: {output_file}")

    # =========================================================================
    # Resumen
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESUMEN DEL DATASET v7")
    print("=" * 70)

    print(f"\nDimensiones: {len(df_v7)} municipios x {len(df_v7.columns)} variables")

    # Agrupar columnas por categoría
    col_groups = {
        'Identificación': ['cod_ibge', 'Municipio', 'cod_microrregiao', 'nome_microrregiao',
                          'cod_mesorregiao', 'nome_mesorregiao'],
        'Demografía': ['population', 'pct_rural', 'pct_urbana', 'population_preta',
                      'population_branca', 'population_indigena', 'pct_pobreza',
                      'pct_preta', 'pct_indigena', 'n_pessoas_pobreza', 'n_familias_rua',
                      'mort_infantil', 'IDESP_ensino_medio', 'esgoto_tratado'],
        'UAI (Adaptación)': [c for c in df_v7.columns if c.startswith('UAI_')],
        'Gobernanza': [c for c in df_v7.columns if 'gobernanza' in c.lower()],
        'Biodiversidad': ['mean_species_richness', 'max_species_richness', 'Vert_rich_risk',
                         'forest_cover', 'pol_deficit', 'idx_biodiv'],
        'Clima/Riesgo': ['flooding_exposure', 'flooding_risks', 'hydric_stress_exp',
                        'hydric_stress_risk', 'idx_clima'],
        'Enfermedades (persistencia)': [c for c in df_v7.columns if c.startswith('persist_')],
        'Enfermedades (incidencia)': [c for c in df_v7.columns if c.startswith('incidence_')],
        'Enfermedades (totales)': [c for c in df_v7.columns if c.startswith('total_cases_')],
        'Enfermedades (copresencia)': [c for c in df_v7.columns if 'copresence' in c.lower() or
                                       any(x in c for x in ['dengue_', 'leptospirose_', 'malaria_'])
                                       and not c.startswith(('persist_', 'incidence_', 'total_'))],
        'Fuego (NUEVO)': [c for c in df_v7.columns if c.startswith('fire_')],
        'Salud-Calor (NUEVO)': [c for c in df_v7.columns if c.startswith('health_')],
        'Índices sintéticos': ['idx_vulnerabilidad', 'idx_carga_enfermedad'],
        'Clasificación': ['tercil_biodiv', 'tercil_clima', 'tercil_vuln',
                         'grupo_clima_biodiv', 'cuadrante']
    }

    print("\nVariables por categoría:")
    for group, cols in col_groups.items():
        existing_cols = [c for c in cols if c in df_v7.columns]
        if existing_cols:
            print(f"  {group}: {len(existing_cols)} variables")

    # Nuevas variables agregadas
    print("\n--- NUEVAS VARIABLES AGREGADAS (v6 → v7) ---")

    print("\nIndicadores de Fuego (13 variables):")
    for col in fire_cols_new:
        print(f"  - {col}")

    print("\nIndicadores de Salud-Calor (18 variables):")
    for col in health_cols_new:
        print(f"  - {col}")

    # Estadísticas de nuevas variables
    print("\n--- Estadísticas de nuevas variables ---")

    print("\nFuego:")
    print(f"  fire_incidence_mean: {df_v7['fire_incidence_mean'].mean():.2f} (media)")
    print(f"  fire_frp_mean: {df_v7['fire_frp_mean'].mean():.2f} MW (media)")
    print(f"  fire_risk_index: {df_v7['fire_risk_index'].mean():.2f} (media)")

    print("\nSalud (por 100,000 hab):")
    print(f"  health_hosp_circ_mean: {df_v7['health_hosp_circ_mean'].mean():.1f}")
    print(f"  health_hosp_resp_mean: {df_v7['health_hosp_resp_mean'].mean():.1f}")
    print(f"  health_death_circ_mean: {df_v7['health_death_circ_mean'].mean():.1f}")
    print(f"  health_death_resp_mean: {df_v7['health_death_resp_mean'].mean():.1f}")

    return df_v7

if __name__ == "__main__":
    df = main()
