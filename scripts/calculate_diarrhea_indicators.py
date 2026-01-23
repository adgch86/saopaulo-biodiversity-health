# =============================================================================
# Script para calcular indicadores de diarrea y gastroenteritis
# Relacionado con: Inundaciones -> Contaminacion del agua -> Diarrea
# =============================================================================
#
# Calcula por municipio:
# 1) Incidencia media de hospitalizaciones (2010-2019)
# 2) Incidencia maxima de hospitalizaciones
# 3) Persistencia: numero de anos con casos (0-10)
#
# Autor: Science Team
# Fecha: 2026-01-23
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuracion de paths
PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
DATA_RAW = Path("G:/My Drive/Adrian David/Datos/to check health data + prompts for new data")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"

def load_health_data():
    """Carga datos de salud del archivo health_sp_Ju.csv"""
    file_path = DATA_RAW / "health_sp_Ju.csv"
    df = pd.read_csv(file_path)

    # Renombrar columnas para claridad
    df = df.rename(columns={'COD': 'cod_ibge'})
    df['cod_ibge'] = df['cod_ibge'].astype(str)

    print(f"Registros cargados: {len(df)}")
    print(f"Municipios unicos: {df['cod_ibge'].nunique()}")
    print(f"Anos: {sorted(df['year'].unique())}")

    return df

def load_population():
    """Carga datos de poblacion para calcular incidencia."""
    pop_file = DATA_PROCESSED / "populacao_SP_2010_2019.csv"
    df = pd.read_csv(pop_file)
    df['cod_ibge'] = df['cod_ibge'].astype(str)

    # Convertir de wide a long format (solo columnas pop_20XX, excluir pop_mean)
    pop_cols = [c for c in df.columns if c.startswith('pop_20')]
    id_cols = ['cod_ibge']

    pop_long = pd.melt(
        df[id_cols + pop_cols],
        id_vars=id_cols,
        var_name='year',
        value_name='population'
    )
    pop_long['year'] = pop_long['year'].str.replace('pop_', '').astype(int)

    return pop_long

def load_municipalities():
    """Carga lista de municipios de SP."""
    mun_file = DATA_PROCESSED / "municipios_regioes_SP.csv"
    df = pd.read_csv(mun_file)
    df['cod_ibge'] = df['cod_ibge'].astype(str)
    return df[['cod_ibge', 'nome_municipio']]

def calculate_diarrhea_indicators(health_df, pop_df, municipalities):
    """Calcula indicadores de diarrea por municipio."""

    # Filtrar solo columnas relevantes
    diarrhea_df = health_df[['cod_ibge', 'municipality', 'year', 'diarrhea']].copy()

    # Crear grid completo de municipios x anos (645 x 10 = 6450)
    all_mun = municipalities['cod_ibge'].unique()
    anos = list(range(2010, 2020))

    grid = pd.DataFrame([(m, y) for m in all_mun for y in anos],
                       columns=['cod_ibge', 'year'])

    # Merge con datos de diarrea
    grid = grid.merge(
        diarrhea_df[['cod_ibge', 'year', 'diarrhea']],
        on=['cod_ibge', 'year'],
        how='left'
    )

    # Llenar NA con 0 (no hubo casos reportados)
    grid['diarrhea'] = grid['diarrhea'].fillna(0)

    # Merge con poblacion
    grid = grid.merge(pop_df, on=['cod_ibge', 'year'], how='left')

    # Calcular incidencia (por 100,000 habitantes)
    grid['incidence_diarrhea'] = np.where(
        grid['population'] > 0,
        grid['diarrhea'] / grid['population'] * 100000,
        0
    )

    print(f"\nGrid completo: {len(grid)} registros")
    print(f"Municipios: {grid['cod_ibge'].nunique()}")
    print(f"Anos: {sorted(grid['year'].unique())}")

    # =========================================================================
    # Calcular indicadores por municipio
    # =========================================================================

    indicators = grid.groupby('cod_ibge').agg(
        # Incidencia media (por 100,000 hab)
        incidence_diarrhea_mean=('incidence_diarrhea', 'mean'),
        # Incidencia maxima
        incidence_diarrhea_max=('incidence_diarrhea', 'max'),
        # Casos totales
        total_cases_diarrhea=('diarrhea', 'sum'),
        # Anos con casos (persistencia)
        persist_diarrhea=('diarrhea', lambda x: (x > 0).sum())
    ).reset_index()

    # Completar con todos los municipios
    indicators = municipalities[['cod_ibge']].merge(
        indicators, on='cod_ibge', how='left'
    )

    # Llenar NA con 0
    for col in ['incidence_diarrhea_mean', 'incidence_diarrhea_max',
                'total_cases_diarrhea', 'persist_diarrhea']:
        indicators[col] = indicators[col].fillna(0)

    return indicators, grid

def main():
    print("=" * 70)
    print("Calculo de Indicadores de Diarrea/Gastroenteritis")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # Cargar datos
    print("\n--- Cargando datos ---")
    health_df = load_health_data()
    pop_df = load_population()
    municipalities = load_municipalities()

    print(f"Poblacion: {len(pop_df)} registros")
    print(f"Municipios SP: {len(municipalities)}")

    # Calcular indicadores
    print("\n--- Calculando indicadores ---")
    indicators, annual_data = calculate_diarrhea_indicators(
        health_df, pop_df, municipalities
    )

    # Guardar resultados
    print("\n--- Guardando archivos ---")

    # Indicadores por municipio
    output_file = DATA_PROCESSED / "diarrhea_indicators_SP_2010_2019.csv"
    indicators.to_csv(output_file, index=False)
    print(f"Indicadores: {output_file}")

    # Datos anuales
    annual_file = DATA_PROCESSED / "diarrhea_annual_SP_2010_2019.csv"
    annual_data.to_csv(annual_file, index=False)
    print(f"Datos anuales: {annual_file}")

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print(f"\nMunicipios: {len(indicators)}")
    print(f"Municipios con casos: {(indicators['total_cases_diarrhea'] > 0).sum()}")
    print(f"Municipios sin casos: {(indicators['total_cases_diarrhea'] == 0).sum()}")

    print(f"\nCasos totales (2010-2019): {indicators['total_cases_diarrhea'].sum():,.0f}")

    print(f"\nIncidencia media (por 100,000 hab):")
    print(f"  Media: {indicators['incidence_diarrhea_mean'].mean():.2f}")
    print(f"  Max: {indicators['incidence_diarrhea_mean'].max():.2f}")

    print(f"\nIncidencia maxima:")
    print(f"  Media: {indicators['incidence_diarrhea_max'].mean():.2f}")
    print(f"  Max: {indicators['incidence_diarrhea_max'].max():.2f}")

    print(f"\nPersistencia (anos con casos, 0-10):")
    print(f"  Media: {indicators['persist_diarrhea'].mean():.1f}")
    print(f"  Distribucion:")
    persist_dist = indicators['persist_diarrhea'].value_counts().sort_index()
    for p, count in persist_dist.items():
        print(f"    {int(p)} anos: {count} municipios")

    # Top 10 municipios con mayor incidencia
    print("\n--- Top 10 Municipios Mayor Incidencia de Diarrea ---")
    mun_names = municipalities.set_index('cod_ibge')['nome_municipio'].to_dict()
    top10 = indicators.nlargest(10, 'incidence_diarrhea_mean')
    for _, row in top10.iterrows():
        name = mun_names.get(row['cod_ibge'], row['cod_ibge'])
        print(f"  {name}: {row['incidence_diarrhea_mean']:.1f} (casos={row['total_cases_diarrhea']:.0f}, persist={int(row['persist_diarrhea'])})")

    return indicators

if __name__ == "__main__":
    result = main()
