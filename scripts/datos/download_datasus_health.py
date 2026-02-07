"""
Script para descargar datos de salud del DATASUS usando PySUS
============================================================

Enfermedades a descargar:
- DENG: Dengue
- LEPT: Leptospirose
- MALA: Malaria
- LEIV: Leishmaniose Visceral
- LTAN: Leishmaniose Tegumentar Americana

Nota: Diarrea (DDA) no está en SINAN regular - se obtiene del SIH o SIVEP-DDA

Período: 2010-2019
Estado: São Paulo (SP)
Unidad: Municipio (código IBGE)

Autor: Science Team / Data Engineer
Fecha: 2026-01-20
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuración de paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "datasus"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Crear directorios si no existen
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# Código UF de São Paulo
UF_SP = "35"
YEARS = list(range(2010, 2020))  # 2010 a 2019

# Enfermedades a descargar
DISEASES = {
    "DENG": "Dengue",
    "LEPT": "Leptospirose",
    "MALA": "Malaria",
    "LEIV": "Leishmaniose_Visceral",
    "LTAN": "Leishmaniose_Tegumentar"
}

def check_pysus_installed():
    """Verifica si PySUS está instalado"""
    try:
        from pysus.online_data.sinan import SINAN
        print("✓ PySUS está instalado correctamente")
        return True
    except ImportError:
        print("✗ PySUS no está instalado")
        print("\nPara instalar PySUS, ejecuta:")
        print("  pip install pysus")
        print("\nO con conda:")
        print("  conda install -c conda-forge pysus")
        return False

def download_disease_data(disease_code: str, years: list) -> pd.DataFrame:
    """
    Descarga datos de una enfermedad específica del SINAN

    Args:
        disease_code: Código de la enfermedad (DENG, LEPT, etc.)
        years: Lista de años a descargar

    Returns:
        DataFrame con los datos consolidados
    """
    from pysus.online_data.sinan import SINAN

    print(f"\n{'='*60}")
    print(f"Descargando datos de {DISEASES[disease_code]} ({disease_code})")
    print(f"Años: {min(years)} - {max(years)}")
    print('='*60)

    sinan = SINAN().load()
    all_data = []

    for year in years:
        try:
            print(f"  Año {year}...", end=" ")
            files = sinan.get_files(dis_code=[disease_code], year=year)

            if files.empty:
                print("Sin datos disponibles")
                continue

            df = sinan.download(files).to_dataframe()

            # Filtrar solo São Paulo (UF = 35)
            if 'SG_UF_NOT' in df.columns:
                df = df[df['SG_UF_NOT'] == 'SP']
            elif 'ID_MUNICIP' in df.columns:
                # Filtrar por código de municipio que empiece con 35
                df['ID_MUNICIP'] = df['ID_MUNICIP'].astype(str)
                df = df[df['ID_MUNICIP'].str.startswith(UF_SP)]

            df['YEAR'] = year
            df['DISEASE'] = disease_code
            all_data.append(df)
            print(f"✓ {len(df)} registros")

        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            continue

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal {disease_code}: {len(result)} registros")
        return result
    else:
        return pd.DataFrame()

def aggregate_by_municipality(df: pd.DataFrame, disease_code: str) -> pd.DataFrame:
    """
    Agrega casos por municipio y año

    Args:
        df: DataFrame con datos crudos del SINAN
        disease_code: Código de la enfermedad

    Returns:
        DataFrame con casos agregados por municipio y año
    """
    if df.empty:
        return pd.DataFrame()

    # Identificar columna de municipio
    mun_col = None
    for col in ['ID_MUNICIP', 'ID_MN_RESI', 'CO_MUN_RES']:
        if col in df.columns:
            mun_col = col
            break

    if mun_col is None:
        print(f"  ⚠ No se encontró columna de municipio para {disease_code}")
        return pd.DataFrame()

    # Convertir a string y extraer código de 6 dígitos
    df[mun_col] = df[mun_col].astype(str).str[:6]

    # Agregar por municipio y año
    agg = df.groupby([mun_col, 'YEAR']).size().reset_index(name='cases')
    agg.columns = ['cod_ibge_6', 'year', f'cases_{disease_code.lower()}']

    return agg

def calculate_incidence(df_cases: pd.DataFrame, df_pop: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la tasa de incidencia por 100,000 habitantes

    Args:
        df_cases: DataFrame con casos por municipio y año
        df_pop: DataFrame con población por municipio

    Returns:
        DataFrame con tasas de incidencia
    """
    # TODO: Implementar cuando tengamos datos de población por año
    return df_cases

def main():
    """Función principal de descarga"""
    print("="*70)
    print("DATASUS Health Data Downloader")
    print("Science Team - São Paulo Biodiversity & Health Project")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # Verificar instalación de PySUS
    if not check_pysus_installed():
        print("\n" + "="*70)
        print("INSTRUCCIONES PARA INSTALAR PYSUS")
        print("="*70)
        print("""
1. Abre una terminal/cmd en este directorio

2. Crea un ambiente virtual (opcional pero recomendado):
   python -m venv venv
   venv\\Scripts\\activate  # Windows
   source venv/bin/activate  # Linux/Mac

3. Instala PySUS:
   pip install pysus

4. Ejecuta este script de nuevo:
   python scripts/download_datasus_health.py
        """)
        return

    # Descargar datos de cada enfermedad
    all_diseases = {}

    for disease_code, disease_name in DISEASES.items():
        try:
            df = download_disease_data(disease_code, YEARS)
            if not df.empty:
                # Guardar datos crudos
                output_path = DATA_RAW / f"{disease_code}_SP_2010_2019.parquet"
                df.to_parquet(output_path)
                print(f"  Guardado: {output_path}")

                # Agregar por municipio
                df_agg = aggregate_by_municipality(df, disease_code)
                all_diseases[disease_code] = df_agg

        except Exception as e:
            print(f"Error procesando {disease_code}: {e}")
            continue

    # Consolidar todos los datos
    if all_diseases:
        print("\n" + "="*60)
        print("Consolidando datos de todas las enfermedades...")
        print("="*60)

        # Crear DataFrame base con todos los municipios y años
        from itertools import product

        # Obtener lista única de municipios
        all_munis = set()
        for df in all_diseases.values():
            if 'cod_ibge_6' in df.columns:
                all_munis.update(df['cod_ibge_6'].unique())

        base = pd.DataFrame(list(product(all_munis, YEARS)),
                           columns=['cod_ibge_6', 'year'])

        # Merge con cada enfermedad
        for disease_code, df in all_diseases.items():
            if not df.empty and 'cod_ibge_6' in df.columns:
                base = base.merge(df, on=['cod_ibge_6', 'year'], how='left')

        # Rellenar NaN con 0 (sin casos = 0)
        case_cols = [c for c in base.columns if c.startswith('cases_')]
        base[case_cols] = base[case_cols].fillna(0).astype(int)

        # Guardar dataset consolidado
        output_final = DATA_PROCESSED / "health_data_SP_2010_2019.csv"
        base.to_csv(output_final, index=False)
        print(f"\n✓ Dataset consolidado guardado: {output_final}")

        # Resumen
        print("\n" + "="*60)
        print("RESUMEN DE DATOS DESCARGADOS")
        print("="*60)
        print(f"Municipios: {base['cod_ibge_6'].nunique()}")
        print(f"Años: {base['year'].min()} - {base['year'].max()}")
        print(f"Total registros: {len(base)}")
        print("\nCasos por enfermedad:")
        for col in case_cols:
            total = base[col].sum()
            print(f"  - {col}: {total:,}")

    print("\n" + "="*60)
    print("Proceso completado")
    print("="*60)

if __name__ == "__main__":
    main()
