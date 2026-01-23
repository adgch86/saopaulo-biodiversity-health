# =============================================================================
# Script para crear dataset integrado v8
# Integra: v7 + indicadores de diarrea
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
    print("Creacion de Dataset Integrado v8")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # =========================================================================
    # Cargar datasets
    # =========================================================================
    print("\n--- Cargando datasets ---")

    # Dataset principal v7
    v7_file = OUTPUTS / "municipios_integrado_v7.csv"
    df_v7 = pd.read_csv(v7_file)
    df_v7['cod_ibge'] = df_v7['cod_ibge'].astype(str)
    print(f"Dataset v7: {len(df_v7)} municipios, {len(df_v7.columns)} columnas")

    # Indicadores de diarrea
    diarrhea_file = DATA_PROCESSED / "diarrhea_indicators_SP_2010_2019.csv"
    df_diarrhea = pd.read_csv(diarrhea_file)
    df_diarrhea['cod_ibge'] = df_diarrhea['cod_ibge'].astype(str)
    print(f"Indicadores de diarrea: {len(df_diarrhea)} municipios, {len(df_diarrhea.columns)-1} indicadores")

    # =========================================================================
    # Integrar datasets
    # =========================================================================
    print("\n--- Integrando datasets ---")

    # Merge con diarrhea indicators
    df_v8 = df_v7.merge(df_diarrhea, on='cod_ibge', how='left')
    print(f"Despues de merge con diarrea: {len(df_v8.columns)} columnas")

    # =========================================================================
    # Verificar integridad
    # =========================================================================
    print("\n--- Verificando integridad ---")

    # Verificar que no perdimos municipios
    assert len(df_v8) == len(df_v7), "ERROR: Se perdieron municipios en el merge"
    print(f"Municipios: {len(df_v8)} (sin perdidas)")

    # Verificar NaN en nuevas columnas
    diarrhea_cols = [c for c in df_diarrhea.columns if c != 'cod_ibge']
    diarrhea_nan = df_v8[diarrhea_cols].isna().sum().sum()
    print(f"NaN en indicadores de diarrea: {diarrhea_nan}")

    # =========================================================================
    # Guardar dataset v8
    # =========================================================================
    print("\n--- Guardando dataset ---")

    output_file = OUTPUTS / "municipios_integrado_v8.csv"
    df_v8.to_csv(output_file, index=False)
    print(f"Archivo guardado: {output_file}")

    # =========================================================================
    # Resumen
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESUMEN DEL DATASET v8")
    print("=" * 70)

    print(f"\nDimensiones: {len(df_v8)} municipios x {len(df_v8.columns)} variables")

    # Nuevas variables agregadas
    print("\n--- NUEVAS VARIABLES AGREGADAS (v7 -> v8) ---")
    print("\nIndicadores de Diarrea (4 variables):")
    for col in diarrhea_cols:
        print(f"  - {col}")

    # Estadisticas de nuevas variables
    print("\n--- Estadisticas de diarrea ---")
    print(f"  incidence_diarrhea_mean: {df_v8['incidence_diarrhea_mean'].mean():.2f} (por 100,000 hab)")
    print(f"  incidence_diarrhea_max: {df_v8['incidence_diarrhea_max'].mean():.2f} (por 100,000 hab)")
    print(f"  total_cases_diarrhea: {df_v8['total_cases_diarrhea'].sum():,.0f} casos totales")
    print(f"  persist_diarrhea: {df_v8['persist_diarrhea'].mean():.1f} anos promedio")

    # Resumen de categorias de variables
    print("\n--- Variables por categoria ---")
    col_groups = {
        'Identificacion': ['cod_ibge', 'Municipio'],
        'Demografia': [c for c in df_v8.columns if 'population' in c.lower() or 'pct_' in c.lower()],
        'UAI (Adaptacion)': [c for c in df_v8.columns if c.startswith('UAI_')],
        'Biodiversidad': [c for c in df_v8.columns if 'biodiv' in c.lower() or 'species' in c.lower() or 'forest' in c.lower()],
        'Clima/Riesgo': [c for c in df_v8.columns if 'flooding' in c.lower() or 'hydric' in c.lower() or 'clima' in c.lower()],
        'Enfermedades vectoriales': [c for c in df_v8.columns if any(d in c.lower() for d in ['dengue', 'leptospirose', 'malaria', 'leishmaniasis'])],
        'Diarrea (NUEVO)': [c for c in df_v8.columns if 'diarrhea' in c.lower()],
        'Fuego': [c for c in df_v8.columns if c.startswith('fire_')],
        'Salud-Calor': [c for c in df_v8.columns if c.startswith('health_')],
    }

    for group, cols in col_groups.items():
        existing_cols = [c for c in cols if c in df_v8.columns]
        if existing_cols:
            print(f"  {group}: {len(existing_cols)} variables")

    return df_v8

if __name__ == "__main__":
    df = main()
