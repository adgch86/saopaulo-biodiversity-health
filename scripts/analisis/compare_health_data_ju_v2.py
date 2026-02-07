# =============================================================================
# Script para comparar datos de salud: Ju (manual) vs Procesados (DBC) - V2
# Con leishmaniasis combinada (visceral + tegumentar)
# =============================================================================

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path("C:/Users/arlex/Documents/Adrian David")
DATA_JU = Path("G:/My Drive/Adrian David/Datos/to check health data + prompts for new data/health_sp_Ju.csv")
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

def main():
    print("=" * 70)
    print("Comparacion de Datos de Salud V2 - Con Leishmaniasis Combinada")
    print("=" * 70)

    # Cargar datos de Ju
    ju_df = pd.read_csv(DATA_JU)
    ju_df = ju_df.rename(columns={'COD': 'cod_ibge'})
    ju_df['cod_ibge'] = ju_df['cod_ibge'].astype(str)

    # Cargar datos procesados
    proc_df = pd.read_csv(DATA_PROCESSED / "health_casos_provaveis_SP_2010_2019_regioes.csv")
    proc_df['cod_ibge'] = proc_df['cod_ibge'].astype(str)

    # Cargar diarrea
    diarrhea_df = pd.read_csv(DATA_PROCESSED / "diarrhea_annual_SP_2010_2019.csv")
    diarrhea_df['cod_ibge'] = diarrhea_df['cod_ibge'].astype(str)

    years = list(range(2010, 2020))

    print("\n" + "=" * 70)
    print("COMPARACION DETALLADA POR ENFERMEDAD")
    print("=" * 70)

    results = {}

    # 1. DENGUE
    print("\n--- DENGUE ---")
    dengue_comp = compare_simple(ju_df, proc_df, 'dengue', 'deng', years)
    results['dengue'] = dengue_comp
    print_summary(dengue_comp, 'Dengue')

    # 2. DIARRHEA
    print("\n--- DIARRHEA ---")
    diarrhea_pivot = diarrhea_df.pivot_table(
        index='cod_ibge', columns='year', values='diarrhea', fill_value=0
    ).reset_index()
    diarrhea_comp = compare_diarrhea(ju_df, diarrhea_pivot, years)
    results['diarrhea'] = diarrhea_comp
    print_summary(diarrhea_comp, 'Diarrhea')

    # 3. LEPTOSPIROSE
    print("\n--- LEPTOSPIROSE ---")
    lept_comp = compare_simple(ju_df, proc_df, 'leptospirose', 'lept', years)
    results['leptospirose'] = lept_comp
    print_summary(lept_comp, 'Leptospirose')

    # 4. MALARIA
    print("\n--- MALARIA ---")
    mala_comp = compare_simple(ju_df, proc_df, 'malaria', 'mala', years)
    results['malaria'] = mala_comp
    print_summary(mala_comp, 'Malaria')

    # 5. LEISHMANIASIS (VISCERAL + TEGUMENTAR)
    print("\n--- LEISHMANIASIS (Visceral + Tegumentar combinadas) ---")
    leish_comp = compare_leish_combined(ju_df, proc_df, years)
    results['leishmaniasis_combined'] = leish_comp
    print_summary(leish_comp, 'Leishmaniasis (V+T)')

    # 5b. LEISHMANIASIS VISCERAL sola
    print("\n--- LEISHMANIASIS VISCERAL (solo) ---")
    leiv_comp = compare_simple(ju_df, proc_df, 'leishmaniasis', 'leiv', years)
    results['leish_visceral'] = leiv_comp
    print_summary(leiv_comp, 'Leish. Visceral')

    # 5c. LEISHMANIASIS TEGUMENTAR sola
    print("\n--- LEISHMANIASIS TEGUMENTAR (solo) ---")
    ltan_comp = compare_simple(ju_df, proc_df, 'leishmaniasis', 'ltan', years)
    results['leish_tegumentar'] = ltan_comp
    print_summary(ltan_comp, 'Leish. Tegumentar')

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL DE VALIDACION")
    print("=" * 70)

    print(f"\n{'Enfermedad':<25} {'Corr':>8} {'Total Ju':>12} {'Total Proc':>12} {'Ratio':>8} {'Estado':>10}")
    print("-" * 80)

    for name, comp in results.items():
        corr = comp[['cases_ju', 'cases_proc']].corr().iloc[0,1]
        total_ju = comp['cases_ju'].sum()
        total_proc = comp['cases_proc'].sum()
        ratio = total_proc / total_ju if total_ju > 0 else 0

        if corr > 0.99:
            estado = "VALIDADO"
        elif corr > 0.95:
            estado = "~OK"
        else:
            estado = "REVISAR"

        print(f"{name:<25} {corr:>8.4f} {total_ju:>12,.0f} {total_proc:>12,.0f} {ratio:>7.1f}x {estado:>10}")

    # Hipotesis sobre las discrepancias
    print("\n" + "=" * 70)
    print("HIPOTESIS SOBRE DISCREPANCIAS")
    print("=" * 70)

    print("""
DENGUE y DIARRHEA: VALIDADOS (r > 0.99)
  - Datos practicamente identicos
  - Misma fuente y criterios de filtro

LEPTOSPIROSE (6.2x mas casos en nuestros datos):
  - HIPOTESIS: Ju descargo solo casos CONFIRMADOS POR LABORATORIO
  - Nuestros datos: "Casos Provaveis" (confirmados + en investigacion)
  - El criterio SINAN para "caso provavel" es menos restrictivo

MALARIA (2.4x mas casos):
  - Misma hipotesis: confirmados vs provaveis
  - Malaria tiene alto % de casos sin confirmacion laboratorial

LEISHMANIASIS:
  - Nuestros datos: Visceral (4,611) + Tegumentar (3,471) = 8,082 total
  - Ju: 2,609 casos
  - HIPOTESIS 1: Ju solo descargo VISCERAL
  - HIPOTESIS 2: Ju descargo solo casos confirmados

VERIFICACION NECESARIA:
  Preguntar a Ju:
  1. Que criterio de clasificacion uso? (Confirmado vs Provavel)
  2. Para Leishmaniasis, descargo Visceral, Tegumentar o ambas?
""")

    return results

def compare_simple(ju_df, proc_df, ju_col, proc_prefix, years):
    """Compara enfermedad simple."""
    results = []
    for year in years:
        ju_year = ju_df[ju_df['year'] == year][['cod_ibge', ju_col]].copy()
        ju_year = ju_year.rename(columns={ju_col: 'cases_ju'})
        ju_year['cases_ju'] = ju_year['cases_ju'].fillna(0)

        proc_col = f"{proc_prefix}_{year}"
        if proc_col in proc_df.columns:
            proc_year = proc_df[['cod_ibge', proc_col]].copy()
            proc_year = proc_year.rename(columns={proc_col: 'cases_proc'})
            proc_year['cases_proc'] = proc_year['cases_proc'].fillna(0)
        else:
            proc_year = pd.DataFrame({'cod_ibge': proc_df['cod_ibge'].unique(), 'cases_proc': 0})

        merged = ju_year.merge(proc_year, on='cod_ibge', how='outer').fillna(0)
        merged['diff'] = merged['cases_proc'] - merged['cases_ju']
        merged['year'] = year
        results.append(merged)

    return pd.concat(results, ignore_index=True)

def compare_diarrhea(ju_df, proc_pivot, years):
    """Compara diarrea."""
    results = []
    for year in years:
        ju_year = ju_df[ju_df['year'] == year][['cod_ibge', 'diarrhea']].copy()
        ju_year = ju_year.rename(columns={'diarrhea': 'cases_ju'})
        ju_year['cases_ju'] = ju_year['cases_ju'].fillna(0)

        if year in proc_pivot.columns:
            proc_year = proc_pivot[['cod_ibge', year]].copy()
            proc_year = proc_year.rename(columns={year: 'cases_proc'})
        else:
            proc_year = pd.DataFrame({'cod_ibge': proc_pivot['cod_ibge'], 'cases_proc': 0})

        merged = ju_year.merge(proc_year, on='cod_ibge', how='outer').fillna(0)
        merged['diff'] = merged['cases_proc'] - merged['cases_ju']
        merged['year'] = year
        results.append(merged)

    return pd.concat(results, ignore_index=True)

def compare_leish_combined(ju_df, proc_df, years):
    """Compara leishmaniasis combinando visceral + tegumentar."""
    results = []
    for year in years:
        ju_year = ju_df[ju_df['year'] == year][['cod_ibge', 'leishmaniasis']].copy()
        ju_year = ju_year.rename(columns={'leishmaniasis': 'cases_ju'})
        ju_year['cases_ju'] = ju_year['cases_ju'].fillna(0)

        # Combinar visceral + tegumentar
        leiv_col = f"leiv_{year}"
        ltan_col = f"ltan_{year}"

        proc_year = proc_df[['cod_ibge']].copy()
        proc_year['cases_proc'] = 0
        if leiv_col in proc_df.columns:
            proc_year['cases_proc'] += proc_df[leiv_col].fillna(0)
        if ltan_col in proc_df.columns:
            proc_year['cases_proc'] += proc_df[ltan_col].fillna(0)

        merged = ju_year.merge(proc_year, on='cod_ibge', how='outer').fillna(0)
        merged['diff'] = merged['cases_proc'] - merged['cases_ju']
        merged['year'] = year
        results.append(merged)

    return pd.concat(results, ignore_index=True)

def print_summary(comp, name):
    """Imprime resumen de comparacion."""
    annual = comp.groupby('year').agg(
        total_ju=('cases_ju', 'sum'),
        total_proc=('cases_proc', 'sum')
    ).reset_index()
    annual['diff'] = annual['total_proc'] - annual['total_ju']
    annual['ratio'] = annual['total_proc'] / annual['total_ju'].replace(0, np.nan)

    print(f"\n{'Ano':<6} {'Ju':>10} {'Proc':>10} {'Diff':>10} {'Ratio':>8}")
    print("-" * 48)
    for _, row in annual.iterrows():
        ratio = row['ratio'] if not pd.isna(row['ratio']) else 0
        print(f"{int(row['year']):<6} {row['total_ju']:>10,.0f} {row['total_proc']:>10,.0f} {row['diff']:>10,.0f} {ratio:>7.2f}x")

    total_ju = annual['total_ju'].sum()
    total_proc = annual['total_proc'].sum()
    print("-" * 48)
    ratio_total = total_proc / total_ju if total_ju > 0 else 0
    print(f"{'TOTAL':<6} {total_ju:>10,.0f} {total_proc:>10,.0f} {total_proc-total_ju:>10,.0f} {ratio_total:>7.2f}x")

    corr = comp[['cases_ju', 'cases_proc']].corr().iloc[0,1]
    print(f"\nCorrelacion: r = {corr:.4f}")

    # Top discrepantes
    comp['abs_diff'] = abs(comp['diff'])
    top5 = comp.nlargest(5, 'abs_diff')
    if top5['abs_diff'].max() > 0:
        print(f"\nTop 5 discrepantes:")
        for _, row in top5.iterrows():
            print(f"  {row['cod_ibge']} ({int(row['year'])}): Ju={row['cases_ju']:.0f}, Proc={row['cases_proc']:.0f}, Diff={row['diff']:.0f}")

if __name__ == "__main__":
    results = main()
