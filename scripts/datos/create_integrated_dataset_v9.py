# =============================================================================
# Script para crear dataset integrado v9
# Integra: v8 + indicadores de estrés térmico (Xavier/BR-DWGD + MODIS LST)
# =============================================================================
#
# Autor: Science Team
# Fecha: 2026-01-26
#
# PREREQUISITOS:
#   1. Ejecutar gee_extract_heat_stress_xavier.js en GEE Code Editor
#      → Exporta: heat_stress_xavier_sp_2010_2019.csv
#   2. Ejecutar gee_extract_modis_lst.js en GEE Code Editor
#      → Exporta: modis_lst_sp_2010_2019.csv
#   3. Descargar ambos CSVs de Google Drive a data/processed/
#
# VARIABLES NUEVAS (hasta 8):
#   De Xavier/BR-DWGD:
#     - heat_persistence_mean: Días/año con Tmax > 34.7°C (promedio 2010-2019)
#     - heat_persistence_sd: Desviación estándar interanual
#     - heat_HAAT_mean: Grados-día acumulados sobre 34.7°C (promedio anual)
#     - heat_HAAT_sd: Desviación estándar interanual
#     - mmt_days_mean: Días/año con Tmedia > 22.3°C (promedio 2010-2019)
#     - mmt_days_sd: Desviación estándar interanual
#   De MODIS:
#     - lst_day_mean: LST diurna media (°C, promedio 2010-2019)
#     - lst_night_mean: LST nocturna media (°C, promedio 2010-2019)
# =============================================================================

import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
OUTPUTS = PROJECT_ROOT / "outputs"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

def main():
    print("=" * 70)
    print("Creacion de Dataset Integrado v9")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # =========================================================================
    # Cargar datasets
    # =========================================================================
    print("\n--- Cargando datasets ---")

    # Dataset principal v8
    v8_file = OUTPUTS / "dataset" / "municipios_integrado.csv"
    df_v8 = pd.read_csv(v8_file)
    df_v8['cod_ibge'] = df_v8['cod_ibge'].astype(str)
    print(f"Dataset v8: {len(df_v8)} municipios, {len(df_v8.columns)} columnas")

    # Indicadores de estrés térmico (Xavier/BR-DWGD)
    heat_file = DATA_PROCESSED / "heat_stress_xavier_sp_2010_2019.csv"
    if not heat_file.exists():
        print(f"\nADVERTENCIA: No se encontro {heat_file}")
        print("Ejecute primero gee_extract_heat_stress_xavier.js en GEE")
        print("y descargue el CSV de Google Drive a data/processed/")
        df_heat = None
    else:
        df_heat = pd.read_csv(heat_file)
        # Normalizar código IBGE (GEE puede exportar como int o string)
        if 'cd_mun' in df_heat.columns:
            df_heat = df_heat.rename(columns={'cd_mun': 'cod_ibge'})
        df_heat['cod_ibge'] = df_heat['cod_ibge'].astype(str).str[:7]
        # Eliminar columna de nombre si existe (ya está en v8)
        if 'nm_mun' in df_heat.columns:
            df_heat = df_heat.drop(columns=['nm_mun'])
        # Eliminar columna system:index de GEE si existe
        if 'system:index' in df_heat.columns:
            df_heat = df_heat.drop(columns=['system:index'])
        if '.geo' in df_heat.columns:
            df_heat = df_heat.drop(columns=['.geo'])
        print(f"Estres termico (Xavier): {len(df_heat)} municipios, "
              f"{len(df_heat.columns)-1} indicadores")

    # Indicadores MODIS LST
    lst_file = DATA_PROCESSED / "modis_lst_sp_2010_2019.csv"
    if not lst_file.exists():
        print(f"\nADVERTENCIA: No se encontro {lst_file}")
        print("Ejecute primero gee_extract_modis_lst.js en GEE")
        print("y descargue el CSV de Google Drive a data/processed/")
        df_lst = None
    else:
        df_lst = pd.read_csv(lst_file)
        if 'cd_mun' in df_lst.columns:
            df_lst = df_lst.rename(columns={'cd_mun': 'cod_ibge'})
        df_lst['cod_ibge'] = df_lst['cod_ibge'].astype(str).str[:7]
        if 'nm_mun' in df_lst.columns:
            df_lst = df_lst.drop(columns=['nm_mun'])
        if 'system:index' in df_lst.columns:
            df_lst = df_lst.drop(columns=['system:index'])
        if '.geo' in df_lst.columns:
            df_lst = df_lst.drop(columns=['.geo'])
        # Seleccionar solo las columnas principales para el dataset
        lst_cols = ['cod_ibge']
        for col in ['lst_day_mean', 'lst_night_mean', 'lst_day_p95',
                     'lst_day_sd', 'lst_amplitude']:
            if col in df_lst.columns:
                lst_cols.append(col)
        df_lst = df_lst[lst_cols]
        print(f"MODIS LST: {len(df_lst)} municipios, "
              f"{len(df_lst.columns)-1} indicadores")

    # =========================================================================
    # Integrar datasets
    # =========================================================================
    print("\n--- Integrando datasets ---")

    df_v9 = df_v8.copy()
    new_vars = 0

    if df_heat is not None:
        heat_cols_before = len(df_v9.columns)
        df_v9 = df_v9.merge(df_heat, on='cod_ibge', how='left')
        new_vars += len(df_v9.columns) - heat_cols_before
        print(f"Merge con estres termico: +{len(df_v9.columns) - heat_cols_before} columnas")

    if df_lst is not None:
        lst_cols_before = len(df_v9.columns)
        df_v9 = df_v9.merge(df_lst, on='cod_ibge', how='left')
        new_vars += len(df_v9.columns) - lst_cols_before
        print(f"Merge con MODIS LST: +{len(df_v9.columns) - lst_cols_before} columnas")

    if new_vars == 0:
        print("\nERROR: No se integraron nuevas variables.")
        print("Descargue los CSVs de GEE a data/processed/ primero.")
        return

    # =========================================================================
    # Verificar integridad
    # =========================================================================
    print("\n--- Verificando integridad ---")

    assert len(df_v9) == len(df_v8), "ERROR: Se perdieron municipios en el merge"
    print(f"Municipios: {len(df_v9)} (sin perdidas)")

    # Verificar NaN en nuevas columnas
    new_cols = [c for c in df_v9.columns if c not in df_v8.columns]
    for col in new_cols:
        nan_count = df_v9[col].isna().sum()
        nan_pct = nan_count / len(df_v9) * 100
        print(f"  {col}: {nan_count} NaN ({nan_pct:.1f}%)")

    # =========================================================================
    # Estadísticas descriptivas de nuevas variables
    # =========================================================================
    print("\n--- Estadisticas descriptivas (nuevas variables) ---")
    if new_cols:
        stats = df_v9[new_cols].describe().round(2)
        print(stats.to_string())

    # =========================================================================
    # Correlaciones preliminares con biodiversidad
    # =========================================================================
    print("\n--- Correlaciones preliminares ---")

    biodiv_vars = ['forest_cover', 'mean_species_richness', 'idx_biodiv']
    health_vars = ['mort_circ_rate', 'hosp_circ_rate']
    heat_vars = [c for c in new_cols if c.endswith('_mean') or c == 'mmt_days_mean']

    for heat_var in heat_vars:
        if heat_var in df_v9.columns:
            print(f"\n  {heat_var}:")
            for bv in biodiv_vars:
                if bv in df_v9.columns:
                    r = df_v9[heat_var].corr(df_v9[bv])
                    print(f"    vs {bv}: r = {r:.3f}")
            for hv in health_vars:
                if hv in df_v9.columns:
                    r = df_v9[heat_var].corr(df_v9[hv])
                    print(f"    vs {hv}: r = {r:.3f}")

    # =========================================================================
    # Guardar dataset v9
    # =========================================================================
    print("\n--- Guardando dataset ---")

    output_file = OUTPUTS / "dataset" / "municipios_integrado.csv"
    df_v9.to_csv(output_file, index=False)
    print(f"Archivo guardado: {output_file}")

    # =========================================================================
    # Resumen
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESUMEN DEL DATASET v9")
    print("=" * 70)

    print(f"\nDimensiones: {len(df_v9)} municipios x {len(df_v9.columns)} variables")
    print(f"Variables nuevas: {len(new_cols)}")
    print(f"Periodo: 2010-2019")

    print("\nNuevas variables de estres termico:")
    for col in new_cols:
        if 'persistence' in col:
            desc = "Dias/ano con Tmax > 34.7C"
        elif 'HAAT' in col:
            desc = "Grados-dia acumulados sobre 34.7C"
        elif 'mmt' in col:
            desc = "Dias/ano con Tmedia > 22.3C"
        elif 'lst_day_mean' in col:
            desc = "LST diurna media (MODIS, C)"
        elif 'lst_night' in col:
            desc = "LST nocturna media (MODIS, C)"
        elif 'lst_day_p95' in col:
            desc = "Percentil 95 LST diurna (MODIS, C)"
        elif 'lst_day_sd' in col:
            desc = "Desviacion estandar LST diurna"
        elif 'lst_amplitude' in col:
            desc = "Amplitud termica dia-noche (MODIS, C)"
        elif '_sd' in col:
            desc = "Desviacion estandar interanual"
        else:
            desc = "Variable nueva"
        print(f"  - {col}: {desc}")

    print(f"\nDataset anterior (v8): {len(df_v8.columns)} variables")
    print(f"Dataset nuevo (v9): {len(df_v9.columns)} variables")
    print(f"Incremento: +{len(df_v9.columns) - len(df_v8.columns)} variables")

    print("\n" + "=" * 70)
    print("PROXIMOS PASOS")
    print("=" * 70)
    print("1. Verificar correlaciones heat_persistence vs forest_cover")
    print("2. Modelar: Biodiversidad -> Estres termico -> Mortalidad CV")
    print("3. Actualizar analisis nexus con nueva hipotesis H3")
    print("4. Generar mapas de estres termico para workshop")
    print("=" * 70)


if __name__ == '__main__':
    main()
