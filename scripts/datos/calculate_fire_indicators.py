# =============================================================================
# Script para calcular indicadores de riesgo de fuego
# Datos: INPE BDQueimadas (focos de calor/quemadas)
# =============================================================================
#
# Calcula indicadores para caracterizar riesgo de fuego por municipio:
# 1) Incidencia media de focos por municipio (media anual)
# 2) Incidencia maxima de focos por año
# 3) Intensidad media (FRP)
# 4) Intensidad maxima (FRP)
# + Indicadores adicionales basados en literatura
#
# Autor: Science Team
# Fecha: 2026-01-23
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import unicodedata
import warnings
warnings.filterwarnings('ignore')

# Configuracion de paths
PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
DATA_RAW = Path("G:/My Drive/Adrian David/Datos/to check health data + prompts for new data")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

def normalize_name(name):
    """Normaliza nombres de municipios para matching."""
    if pd.isna(name):
        return ""
    # Convertir a minusculas
    name = str(name).lower().strip()
    # Remover acentos
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    # Remover caracteres especiales
    name = name.replace("'", "").replace("-", " ").replace(".", "")
    # Limpiar espacios multiples
    name = ' '.join(name.split())
    return name

def load_municipalities():
    """Carga lista de municipios de SP con codigos IBGE."""
    mun_file = DATA_PROCESSED / "municipios_regioes_SP.csv"
    df = pd.read_csv(mun_file)
    df['nome_normalizado'] = df['nome_municipio'].apply(normalize_name)
    return df[['cod_ibge', 'nome_municipio', 'nome_normalizado']]

def load_fire_data():
    """Carga todos los archivos de focos de quemadas."""
    all_files = list(DATA_RAW.glob("bdqueimadas_*.csv"))

    print(f"Archivos encontrados: {len(all_files)}")

    dfs = []
    for f in sorted(all_files):
        print(f"  Procesando: {f.name}")
        try:
            df = pd.read_csv(f, encoding='utf-8')
            dfs.append(df)
        except Exception as e:
            print(f"    Error: {e}")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        print(f"\nRegistros totales: {len(combined):,}")
        return combined
    return None

def process_fire_data(fire_df, municipalities):
    """Procesa datos de focos y hace matching con municipios."""

    # Filtrar solo Sao Paulo
    fire_df = fire_df[fire_df['Estado'] == 'SÃO PAULO'].copy()
    print(f"Registros de Sao Paulo: {len(fire_df):,}")

    # Extraer año
    fire_df['DataHora'] = pd.to_datetime(fire_df['DataHora'], format='%Y/%m/%d %H:%M:%S')
    fire_df['ano'] = fire_df['DataHora'].dt.year
    fire_df['mes'] = fire_df['DataHora'].dt.month

    # Normalizar nombre de municipio
    fire_df['municipio_normalizado'] = fire_df['Municipio'].apply(normalize_name)

    # Crear diccionario de matching
    mun_dict = dict(zip(municipalities['nome_normalizado'], municipalities['cod_ibge']))

    # Hacer matching
    fire_df['cod_ibge'] = fire_df['municipio_normalizado'].map(mun_dict)

    # Verificar matching
    matched = fire_df['cod_ibge'].notna().sum()
    total = len(fire_df)
    print(f"Matching exitoso: {matched:,} / {total:,} ({100*matched/total:.1f}%)")

    # Municipios no encontrados
    not_matched = fire_df[fire_df['cod_ibge'].isna()]['Municipio'].unique()
    if len(not_matched) > 0:
        print(f"\nMunicipios sin match ({len(not_matched)}):")
        for m in sorted(not_matched)[:10]:
            print(f"  - {m}")
        if len(not_matched) > 10:
            print(f"  ... y {len(not_matched) - 10} mas")

    # Filtrar registros con matching exitoso
    fire_df = fire_df[fire_df['cod_ibge'].notna()].copy()
    fire_df['cod_ibge'] = fire_df['cod_ibge'].astype(int).astype(str)

    return fire_df

def calculate_indicators(fire_df, municipalities):
    """Calcula indicadores de riesgo de fuego por municipio."""

    anos = sorted(fire_df['ano'].unique())
    print(f"\nAnos disponibles: {anos}")

    # Filtrar ventana 2010-2019
    fire_df = fire_df[(fire_df['ano'] >= 2010) & (fire_df['ano'] <= 2019)]
    print(f"Registros 2010-2019: {len(fire_df):,}")

    # =========================================================================
    # Indicadores principales (solicitados)
    # =========================================================================

    # Agregar por municipio y año
    annual_stats = fire_df.groupby(['cod_ibge', 'ano']).agg(
        n_focos=('FRP', 'count'),
        frp_sum=('FRP', 'sum'),
        frp_mean=('FRP', 'mean'),
        frp_max=('FRP', 'max'),
        frp_std=('FRP', 'std')
    ).reset_index()

    # Calcular estadisticas por municipio
    indicators = annual_stats.groupby('cod_ibge').agg(
        # 1) Incidencia media de focos (media de focos anuales)
        fire_incidence_mean=('n_focos', 'mean'),
        # 2) Incidencia maxima de focos (max anual)
        fire_incidence_max=('n_focos', 'max'),
        # 3) Intensidad media (FRP promedio)
        fire_frp_mean=('frp_mean', 'mean'),
        # 4) Intensidad maxima (FRP max)
        fire_frp_max=('frp_max', 'max'),
        # Adicionales
        fire_total_foci=('n_focos', 'sum'),          # Total de focos 2010-2019
        fire_frp_total=('frp_sum', 'sum'),           # FRP acumulado total
        fire_years_with_fire=('n_focos', 'count'),   # Anos con al menos un foco
    ).reset_index()

    # =========================================================================
    # Indicadores adicionales (basados en literatura)
    # =========================================================================

    # 5) Recurrencia: proporcion de años con fuego (de 10 años posibles)
    indicators['fire_recurrence'] = indicators['fire_years_with_fire'] / 10.0

    # 6) Coeficiente de variacion de focos (variabilidad interanual)
    cv_stats = annual_stats.groupby('cod_ibge')['n_focos'].agg(['std', 'mean'])
    cv_stats['fire_cv'] = cv_stats['std'] / cv_stats['mean'].replace(0, np.nan)
    indicators = indicators.merge(
        cv_stats[['fire_cv']].reset_index(),
        on='cod_ibge',
        how='left'
    )

    # 7) Estacionalidad: concentracion en meses de seca (jun-oct)
    monthly_stats = fire_df.groupby(['cod_ibge', 'mes']).size().reset_index(name='n_focos')
    dry_season = monthly_stats[monthly_stats['mes'].isin([6, 7, 8, 9, 10])]
    dry_stats = dry_season.groupby('cod_ibge')['n_focos'].sum().reset_index(name='focos_seca')
    total_stats = fire_df.groupby('cod_ibge').size().reset_index(name='focos_total')
    seasonality = dry_stats.merge(total_stats, on='cod_ibge', how='outer')
    seasonality['fire_dry_season_pct'] = (
        seasonality['focos_seca'].fillna(0) /
        seasonality['focos_total'].replace(0, np.nan)
    )
    indicators = indicators.merge(
        seasonality[['cod_ibge', 'fire_dry_season_pct']],
        on='cod_ibge',
        how='left'
    )

    # 8) Indice de persistencia: focos en años consecutivos
    # (calculado como max racha de años consecutivos con fuego)
    def max_consecutive_years(group):
        years_with_fire = set(group['ano'].unique())
        max_streak = 0
        current_streak = 0
        for y in range(2010, 2020):
            if y in years_with_fire:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        return max_streak

    persistence = fire_df.groupby('cod_ibge').apply(max_consecutive_years).reset_index()
    persistence.columns = ['cod_ibge', 'fire_max_consecutive_years']
    indicators = indicators.merge(persistence, on='cod_ibge', how='left')

    # 9) Indice de riesgo compuesto (propuesta basada en literatura)
    # Combina frecuencia, intensidad y recurrencia
    # Normalizado 0-100
    for col in ['fire_incidence_mean', 'fire_frp_mean', 'fire_recurrence']:
        max_val = indicators[col].max()
        if max_val > 0:
            indicators[f'{col}_norm'] = indicators[col] / max_val
        else:
            indicators[f'{col}_norm'] = 0

    indicators['fire_risk_index'] = (
        0.4 * indicators['fire_incidence_mean_norm'] +
        0.3 * indicators['fire_frp_mean_norm'] +
        0.3 * indicators['fire_recurrence']
    ) * 100

    # Limpiar columnas temporales
    indicators = indicators.drop(columns=[
        'fire_incidence_mean_norm',
        'fire_frp_mean_norm'
    ])

    # =========================================================================
    # Completar con municipios sin focos
    # =========================================================================

    all_municipalities = municipalities[['cod_ibge']].copy()
    all_municipalities['cod_ibge'] = all_municipalities['cod_ibge'].astype(str)

    indicators = all_municipalities.merge(indicators, on='cod_ibge', how='left')

    # Llenar NaN con 0 para municipios sin focos
    fill_zero_cols = [
        'fire_incidence_mean', 'fire_incidence_max', 'fire_frp_mean',
        'fire_frp_max', 'fire_total_foci', 'fire_frp_total',
        'fire_years_with_fire', 'fire_recurrence', 'fire_dry_season_pct',
        'fire_max_consecutive_years', 'fire_risk_index'
    ]
    for col in fill_zero_cols:
        if col in indicators.columns:
            indicators[col] = indicators[col].fillna(0)

    return indicators, annual_stats

def main():
    print("=" * 70)
    print("Calculo de Indicadores de Riesgo de Fuego - BDQueimadas INPE")
    print(f"Fecha: {datetime.now()}")
    print("=" * 70)

    # Cargar municipios
    print("\nCargando lista de municipios...")
    municipalities = load_municipalities()
    print(f"Municipios cargados: {len(municipalities)}")

    # Cargar datos de focos
    print("\nCargando datos de focos de calor...")
    fire_df = load_fire_data()

    if fire_df is None:
        print("ERROR: No se pudieron cargar los datos")
        return

    # Procesar datos
    print("\nProcesando datos...")
    fire_df = process_fire_data(fire_df, municipalities)

    # Calcular indicadores
    print("\nCalculando indicadores...")
    indicators, annual_stats = calculate_indicators(fire_df, municipalities)

    # Guardar resultados
    print("\n" + "=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    # Indicadores por municipio
    output_file = DATA_PROCESSED / "fire_indicators_SP_2010_2019.csv"
    indicators.to_csv(output_file, index=False)
    print(f"Indicadores por municipio: {output_file}")

    # Datos anuales
    annual_file = DATA_PROCESSED / "fire_annual_SP_2010_2019.csv"
    annual_stats.to_csv(annual_file, index=False)
    print(f"Datos anuales: {annual_file}")

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE INDICADORES")
    print("=" * 70)
    print(f"Municipios: {len(indicators)}")
    print(f"Municipios con focos: {(indicators['fire_total_foci'] > 0).sum()}")
    print(f"Municipios sin focos: {(indicators['fire_total_foci'] == 0).sum()}")

    print("\n--- Indicadores Principales ---")
    print(f"1) Incidencia media (focos/año):")
    print(f"   Media: {indicators['fire_incidence_mean'].mean():.2f}")
    print(f"   Max: {indicators['fire_incidence_mean'].max():.2f}")

    print(f"\n2) Incidencia maxima anual:")
    print(f"   Media: {indicators['fire_incidence_max'].mean():.2f}")
    print(f"   Max: {indicators['fire_incidence_max'].max():.0f}")

    print(f"\n3) Intensidad media (FRP MW):")
    print(f"   Media: {indicators['fire_frp_mean'].mean():.2f}")
    print(f"   Max: {indicators['fire_frp_mean'].max():.2f}")

    print(f"\n4) Intensidad maxima (FRP MW):")
    print(f"   Media: {indicators['fire_frp_max'].mean():.2f}")
    print(f"   Max: {indicators['fire_frp_max'].max():.2f}")

    print("\n--- Indicadores Adicionales ---")
    print(f"5) Recurrencia (prop. años con fuego):")
    print(f"   Media: {indicators['fire_recurrence'].mean():.2f}")

    print(f"\n6) Coef. variacion (variabilidad interanual):")
    print(f"   Media: {indicators['fire_cv'].mean():.2f}")

    print(f"\n7) % focos en estacion seca (jun-oct):")
    print(f"   Media: {indicators['fire_dry_season_pct'].mean()*100:.1f}%")

    print(f"\n8) Max años consecutivos con fuego:")
    print(f"   Media: {indicators['fire_max_consecutive_years'].mean():.1f}")
    print(f"   Max: {indicators['fire_max_consecutive_years'].max():.0f}")

    print(f"\n9) Indice de riesgo compuesto (0-100):")
    print(f"   Media: {indicators['fire_risk_index'].mean():.2f}")
    print(f"   Max: {indicators['fire_risk_index'].max():.2f}")

    # Top 10 municipios con mayor riesgo
    print("\n--- Top 10 Municipios Mayor Riesgo de Fuego ---")
    top10 = indicators.nlargest(10, 'fire_risk_index')
    top10_names = municipalities.set_index('cod_ibge')['nome_municipio'].to_dict()
    for i, row in top10.iterrows():
        name = top10_names.get(int(row['cod_ibge']), row['cod_ibge'])
        print(f"  {name}: {row['fire_risk_index']:.1f} (focos={row['fire_total_foci']:.0f}, FRP_mean={row['fire_frp_mean']:.1f})")

    return indicators

if __name__ == "__main__":
    result = main()
