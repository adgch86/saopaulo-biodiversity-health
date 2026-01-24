# =============================================================================
# Script para comparar datos de salud: Ju (manual) vs Procesados (DBC)
# =============================================================================
#
# Compara los datos descargados manualmente por Ju con los procesados
# de los archivos DBC de DATASUS para validar consistencia.
#
# Autor: Science Team
# Fecha: 2026-01-23
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path

# Configuracion de paths
PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
DATA_JU = Path("G:/My Drive/Adrian David/Datos/to check health data + prompts for new data/health_sp_Ju.csv")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

def load_ju_data():
    """Carga datos descargados manualmente por Ju."""
    df = pd.read_csv(DATA_JU)
    df = df.rename(columns={'COD': 'cod_ibge'})
    df['cod_ibge'] = df['cod_ibge'].astype(str)
    return df

def load_processed_data():
    """Carga datos procesados de los DBC."""
    # Datos de casos provaveis (dengue, leptospirose, malaria, leishmaniasis)
    file_path = DATA_PROCESSED / "health_casos_provaveis_SP_2010_2019_regioes.csv"
    df = pd.read_csv(file_path)
    df['cod_ibge'] = df['cod_ibge'].astype(str)
    return df

def load_diarrhea_data():
    """Carga datos de diarrea procesados."""
    file_path = DATA_PROCESSED / "diarrhea_annual_SP_2010_2019.csv"
    df = pd.read_csv(file_path)
    df['cod_ibge'] = df['cod_ibge'].astype(str)
    return df

def compare_disease(ju_df, proc_df, disease_ju, disease_proc_prefix, years):
    """Compara una enfermedad entre datasets."""

    results = []

    for year in years:
        # Datos de Ju para este ano
        ju_year = ju_df[ju_df['year'] == year][['cod_ibge', disease_ju]].copy()
        ju_year = ju_year.rename(columns={disease_ju: 'cases_ju'})
        ju_year['cases_ju'] = ju_year['cases_ju'].fillna(0)

        # Datos procesados para este ano
        proc_col = f"{disease_proc_prefix}_{year}"
        if proc_col in proc_df.columns:
            proc_year = proc_df[['cod_ibge', proc_col]].copy()
            proc_year = proc_year.rename(columns={proc_col: 'cases_proc'})
            proc_year['cases_proc'] = proc_year['cases_proc'].fillna(0)
        else:
            proc_year = pd.DataFrame({'cod_ibge': proc_df['cod_ibge'].unique(), 'cases_proc': 0})

        # Merge
        merged = ju_year.merge(proc_year, on='cod_ibge', how='outer')
        merged['cases_ju'] = merged['cases_ju'].fillna(0)
        merged['cases_proc'] = merged['cases_proc'].fillna(0)
        merged['diff'] = merged['cases_proc'] - merged['cases_ju']
        merged['pct_diff'] = np.where(
            merged['cases_ju'] > 0,
            (merged['diff'] / merged['cases_ju']) * 100,
            np.where(merged['cases_proc'] > 0, np.inf, 0)
        )
        merged['year'] = year

        results.append(merged)

    return pd.concat(results, ignore_index=True)

def main():
    print("=" * 70)
    print("Comparacion de Datos de Salud: Ju (manual) vs Procesados (DBC)")
    print("=" * 70)

    # Cargar datos
    print("\n--- Cargando datos ---")
    ju_df = load_ju_data()
    proc_df = load_processed_data()
    diarrhea_df = load_diarrhea_data()

    print(f"Datos Ju: {len(ju_df)} registros, {ju_df['cod_ibge'].nunique()} municipios")
    print(f"Datos Procesados: {len(proc_df)} municipios")
    print(f"Datos Diarrea: {len(diarrhea_df)} registros")

    # Anos a comparar
    years = list(range(2010, 2020))

    # Mapeo de enfermedades
    diseases = {
        'dengue': ('dengue', 'deng'),
        'leptospirose': ('leptospirose', 'lept'),
        'malaria': ('malaria', 'mala'),
        'leishmaniasis': ('leishmaniasis', 'leiv'),  # leishmaniasis visceral
    }

    print("\n" + "=" * 70)
    print("COMPARACION POR ENFERMEDAD")
    print("=" * 70)

    all_comparisons = {}

    for disease_name, (ju_col, proc_prefix) in diseases.items():
        print(f"\n--- {disease_name.upper()} ---")

        comparison = compare_disease(ju_df, proc_df, ju_col, proc_prefix, years)
        all_comparisons[disease_name] = comparison

        # Totales por ano
        annual_totals = comparison.groupby('year').agg(
            total_ju=('cases_ju', 'sum'),
            total_proc=('cases_proc', 'sum')
        ).reset_index()
        annual_totals['diff'] = annual_totals['total_proc'] - annual_totals['total_ju']
        annual_totals['pct_diff'] = (annual_totals['diff'] / annual_totals['total_ju'].replace(0, np.nan)) * 100

        print(f"\nTotales por ano:")
        print(f"{'Ano':<6} {'Ju':>12} {'Procesado':>12} {'Diff':>10} {'%Diff':>8}")
        print("-" * 50)
        for _, row in annual_totals.iterrows():
            print(f"{int(row['year']):<6} {row['total_ju']:>12,.0f} {row['total_proc']:>12,.0f} {row['diff']:>10,.0f} {row['pct_diff']:>7.1f}%")

        total_ju = annual_totals['total_ju'].sum()
        total_proc = annual_totals['total_proc'].sum()
        print("-" * 50)
        print(f"{'TOTAL':<6} {total_ju:>12,.0f} {total_proc:>12,.0f} {total_proc-total_ju:>10,.0f} {(total_proc-total_ju)/total_ju*100:>7.1f}%")

        # Correlacion
        corr = comparison[['cases_ju', 'cases_proc']].corr().iloc[0,1]
        print(f"\nCorrelacion (municipio-ano): r = {corr:.4f}")

        # Casos mas discrepantes
        comparison['abs_diff'] = abs(comparison['diff'])
        top_discrepant = comparison.nlargest(10, 'abs_diff')

        if top_discrepant['abs_diff'].max() > 0:
            print(f"\nTop 10 casos mas discrepantes:")
            print(f"{'Municipio':<12} {'Ano':<6} {'Ju':>8} {'Proc':>8} {'Diff':>8}")
            print("-" * 45)
            for _, row in top_discrepant.iterrows():
                print(f"{row['cod_ibge']:<12} {int(row['year']):<6} {row['cases_ju']:>8,.0f} {row['cases_proc']:>8,.0f} {row['diff']:>8,.0f}")

    # Comparacion de DIARREA (usando archivo separado)
    print(f"\n--- DIARRHEA ---")

    # Pivotar datos de diarrea procesados a formato anual
    diarrhea_pivot = diarrhea_df.pivot_table(
        index='cod_ibge', columns='year', values='diarrhea', fill_value=0
    ).reset_index()

    diarrhea_comparison = []
    for year in years:
        ju_year = ju_df[ju_df['year'] == year][['cod_ibge', 'diarrhea']].copy()
        ju_year = ju_year.rename(columns={'diarrhea': 'cases_ju'})
        ju_year['cases_ju'] = ju_year['cases_ju'].fillna(0)

        if year in diarrhea_pivot.columns:
            proc_year = diarrhea_pivot[['cod_ibge', year]].copy()
            proc_year = proc_year.rename(columns={year: 'cases_proc'})
        else:
            proc_year = pd.DataFrame({'cod_ibge': diarrhea_pivot['cod_ibge'], 'cases_proc': 0})

        merged = ju_year.merge(proc_year, on='cod_ibge', how='outer')
        merged['cases_ju'] = merged['cases_ju'].fillna(0)
        merged['cases_proc'] = merged['cases_proc'].fillna(0)
        merged['diff'] = merged['cases_proc'] - merged['cases_ju']
        merged['year'] = year
        diarrhea_comparison.append(merged)

    diarrhea_comparison = pd.concat(diarrhea_comparison, ignore_index=True)
    all_comparisons['diarrhea'] = diarrhea_comparison

    # Totales diarrea
    annual_totals = diarrhea_comparison.groupby('year').agg(
        total_ju=('cases_ju', 'sum'),
        total_proc=('cases_proc', 'sum')
    ).reset_index()
    annual_totals['diff'] = annual_totals['total_proc'] - annual_totals['total_ju']
    annual_totals['pct_diff'] = (annual_totals['diff'] / annual_totals['total_ju'].replace(0, np.nan)) * 100

    print(f"\nTotales por ano:")
    print(f"{'Ano':<6} {'Ju':>12} {'Procesado':>12} {'Diff':>10} {'%Diff':>8}")
    print("-" * 50)
    for _, row in annual_totals.iterrows():
        pct = row['pct_diff'] if not pd.isna(row['pct_diff']) else 0
        print(f"{int(row['year']):<6} {row['total_ju']:>12,.0f} {row['total_proc']:>12,.0f} {row['diff']:>10,.0f} {pct:>7.1f}%")

    total_ju = annual_totals['total_ju'].sum()
    total_proc = annual_totals['total_proc'].sum()
    print("-" * 50)
    pct_total = (total_proc-total_ju)/total_ju*100 if total_ju > 0 else 0
    print(f"{'TOTAL':<6} {total_ju:>12,.0f} {total_proc:>12,.0f} {total_proc-total_ju:>10,.0f} {pct_total:>7.1f}%")

    corr = diarrhea_comparison[['cases_ju', 'cases_proc']].corr().iloc[0,1]
    print(f"\nCorrelacion (municipio-ano): r = {corr:.4f}")

    diarrhea_comparison['abs_diff'] = abs(diarrhea_comparison['diff'])
    top_discrepant = diarrhea_comparison.nlargest(10, 'abs_diff')

    if top_discrepant['abs_diff'].max() > 0:
        print(f"\nTop 10 casos mas discrepantes:")
        print(f"{'Municipio':<12} {'Ano':<6} {'Ju':>8} {'Proc':>8} {'Diff':>8}")
        print("-" * 45)
        for _, row in top_discrepant.iterrows():
            print(f"{row['cod_ibge']:<12} {int(row['year']):<6} {row['cases_ju']:>8,.0f} {row['cases_proc']:>8,.0f} {row['diff']:>8,.0f}")

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VALIDACION")
    print("=" * 70)

    print(f"\n{'Enfermedad':<15} {'Corr':>8} {'Total Ju':>12} {'Total Proc':>12} {'%Diff':>8}")
    print("-" * 60)

    for disease_name, comp_df in all_comparisons.items():
        corr = comp_df[['cases_ju', 'cases_proc']].corr().iloc[0,1]
        total_ju = comp_df['cases_ju'].sum()
        total_proc = comp_df['cases_proc'].sum()
        pct_diff = (total_proc - total_ju) / total_ju * 100 if total_ju > 0 else 0
        print(f"{disease_name:<15} {corr:>8.4f} {total_ju:>12,.0f} {total_proc:>12,.0f} {pct_diff:>7.1f}%")

    print("\n" + "=" * 70)
    print("INTERPRETACION")
    print("=" * 70)
    print("""
Criterios de validacion:
- Correlacion > 0.99: Datos practicamente identicos
- Correlacion 0.95-0.99: Diferencias menores, aceptable
- Correlacion < 0.95: Revisar metodologia

Posibles fuentes de diferencias:
1. Filtro CLASSI_FIN: Nuestros datos excluyen casos descartados (CLASSI_FIN=5)
2. Municipio de residencia vs notificacion: Usamos ID_MN_RESI
3. Leishmaniasis: Combinamos visceral + tegumentar (Ju puede tener solo una)
4. Diarrea: Fuente diferente (SIH vs SINAN)
""")

    return all_comparisons

if __name__ == "__main__":
    comparisons = main()
