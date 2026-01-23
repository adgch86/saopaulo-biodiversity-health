"""
=============================================================================
Creación de Dataset Integrado v6 - 645 Municipios Completos
=============================================================================

Combina:
- all_tabela.csv (645 municipios): gobernanza, biodiversidad, clima, vulnerabilidad
- health_indicators_SP_2010_2019.csv (645 municipios): salud actualizada

Autor: Science Team
Fecha: 2026-01-21
=============================================================================
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

PROJECT_ROOT = "C:/Users/arlex/Documents/Adrian David"

print("=" * 70)
print("CREACION DE DATASET INTEGRADO v6 - 645 MUNICIPIOS")
print("=" * 70)

# =============================================================================
# 1. CARGAR DATOS BASE
# =============================================================================
print("\n1. Cargando datos base...")

# Datos de Adrian (645 municipios - todo excepto salud actualizada)
df_base = pd.read_csv(f"{PROJECT_ROOT}/data/raw/2026_01_14/all_tabela.csv")
print(f"   all_tabela.csv: {len(df_base)} municipios, {len(df_base.columns)} columnas")

# Datos de salud actualizados (645 municipios)
df_salud = pd.read_csv(f"{PROJECT_ROOT}/data/processed/health_indicators_SP_2010_2019.csv")
print(f"   health_indicators: {len(df_salud)} municipios, {len(df_salud.columns)} columnas")

# =============================================================================
# 2. PREPARAR DATOS BASE
# =============================================================================
print("\n2. Preparando datos base...")

# Eliminar columna index si existe
if 'Unnamed: 0' in df_base.columns:
    df_base = df_base.drop('Unnamed: 0', axis=1)

# Estandarizar codigo IBGE a 6 digitos string
df_base['cod_ibge'] = df_base['Cod_ibge'].astype(str).str[:6]

# Columnas de salud antiguas a eliminar
old_health_cols = [
    'persist_malaria', 'persist_leptospirose', 'persist_diarrhea',
    'persist_dengue', 'persist_chagas',
    'incidence_malaria', 'incidence_leptospirose', 'incidence_diarrhea',
    'incidence_dengue', 'incidence_chagas',
    'copersistence',
    'malaria_leptospirose', 'malaria_diarrhea', 'malaria_dengue', 'malaria_chagas',
    'leptospirose_diarrhea', 'leptospirose_dengue', 'leptospirose_chagas',
    'diarrhea_dengue', 'diarrhea_chagas', 'dengue_chagas'
]

# Eliminar columnas de salud antiguas
cols_to_drop = [c for c in old_health_cols if c in df_base.columns]
df_base = df_base.drop(columns=cols_to_drop)
print(f"   Eliminadas {len(cols_to_drop)} columnas de salud antiguas")

# Eliminar columnas redundantes
if 'Cod_ibge' in df_base.columns and 'cod_ibge' in df_base.columns:
    df_base = df_base.drop('Cod_ibge', axis=1)
if 'COD' in df_base.columns:
    df_base = df_base.drop('COD', axis=1)
if 'municipality' in df_base.columns:
    df_base = df_base.drop('municipality', axis=1)

print(f"   Columnas restantes en base: {len(df_base.columns)}")

# =============================================================================
# 3. PREPARAR DATOS DE SALUD
# =============================================================================
print("\n3. Preparando datos de salud...")

# Estandarizar codigo IBGE
df_salud['cod_ibge'] = df_salud['cod_ibge'].astype(str).str[:6]

# Seleccionar columnas relevantes de salud
salud_cols = [
    'cod_ibge', 'cod_microrregiao', 'nome_microrregiao',
    'cod_mesorregiao', 'nome_mesorregiao',
    'persist_dengue', 'persist_leishmaniose', 'persist_leptospirose', 'persist_malaria',
    'incidence_mean_dengue', 'incidence_mean_leishmaniose',
    'incidence_mean_leptospirose', 'incidence_mean_malaria',
    'incidence_max_dengue', 'incidence_max_leishmaniose',
    'incidence_max_leptospirose', 'incidence_max_malaria',
    'total_cases_dengue', 'total_cases_leishmaniose',
    'total_cases_leptospirose', 'total_cases_malaria',
    'copresence_years', 'copresence_3plus', 'copresence_all4',
    'dengue_leptospirose', 'dengue_malaria', 'dengue_leishmaniose',
    'leptospirose_malaria', 'leptospirose_leishmaniose', 'malaria_leishmaniose'
]

df_salud_select = df_salud[[c for c in salud_cols if c in df_salud.columns]]
print(f"   Columnas de salud seleccionadas: {len(df_salud_select.columns)}")

# =============================================================================
# 4. MERGE DE DATASETS
# =============================================================================
print("\n4. Integrando datasets...")

df_integrado = df_base.merge(
    df_salud_select,
    on='cod_ibge',
    how='left'
)

print(f"   Municipios integrados: {len(df_integrado)}")
print(f"   Columnas totales: {len(df_integrado.columns)}")

# =============================================================================
# 5. CREAR INDICES DERIVADOS
# =============================================================================
print("\n5. Creando indices derivados...")

# Indice de gobernanza (promedio UAI)
uai_cols = ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']
df_integrado['idx_gobernanza'] = df_integrado[uai_cols].mean(axis=1)
df_integrado['idx_gobernanza_100'] = df_integrado['idx_gobernanza'] * 100

# Indice de biodiversidad (normalizado)
df_integrado['idx_biodiv'] = (
    (df_integrado['mean_species_richness'] - df_integrado['mean_species_richness'].min()) /
    (df_integrado['mean_species_richness'].max() - df_integrado['mean_species_richness'].min())
) * 100

# Indice de clima (promedio de riesgos)
clima_cols = ['flooding_risks', 'hydric_stress_risk']
df_integrado['idx_clima'] = df_integrado[clima_cols].mean(axis=1) * 100

# Indice de vulnerabilidad socio-economica
df_integrado['pct_pobreza'] = (df_integrado['n_pessoas_pobreza'] / df_integrado['population'] * 100).fillna(0)
df_integrado['pct_preta'] = (df_integrado['population_preta'] / df_integrado['population'] * 100).fillna(0)
df_integrado['pct_indigena'] = (df_integrado['population_indigena'] / df_integrado['population'] * 100).fillna(0)

# Normalizar componentes de vulnerabilidad
def normalize_0_100(series):
    min_val, max_val = series.min(), series.max()
    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index)
    return ((series - min_val) / (max_val - min_val)) * 100

df_integrado['idx_vulnerabilidad'] = (
    normalize_0_100(df_integrado['pct_rural'].fillna(0)) * 0.25 +
    normalize_0_100(df_integrado['pct_pobreza']) * 0.35 +
    normalize_0_100(df_integrado['pct_preta']) * 0.25 +
    normalize_0_100(df_integrado['pct_indigena']) * 0.15
)

# Indice de carga de enfermedad (basado en incidencia)
inc_cols = ['incidence_mean_dengue', 'incidence_mean_leishmaniose',
            'incidence_mean_leptospirose', 'incidence_mean_malaria']
inc_available = [c for c in inc_cols if c in df_integrado.columns]

if inc_available:
    for col in inc_available:
        df_integrado[f'{col}_norm'] = normalize_0_100(df_integrado[col].fillna(0))
    norm_cols = [f'{c}_norm' for c in inc_available]
    df_integrado['idx_carga_enfermedad'] = df_integrado[norm_cols].mean(axis=1)
    # Eliminar columnas temporales
    df_integrado = df_integrado.drop(columns=norm_cols)

print("   Indices creados: idx_gobernanza, idx_biodiv, idx_clima, idx_vulnerabilidad, idx_carga_enfermedad")

# =============================================================================
# 6. CLASIFICACION EN CUADRANTES
# =============================================================================
print("\n6. Clasificando en cuadrantes...")

# Terciles para biodiversidad y clima
df_integrado['tercil_biodiv'] = pd.qcut(
    df_integrado['idx_biodiv'],
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

df_integrado['tercil_clima'] = pd.qcut(
    df_integrado['idx_clima'].rank(method='first'),
    q=3,
    labels=['Bajo', 'Medio', 'Alto']
)

df_integrado['tercil_vuln'] = pd.qcut(
    df_integrado['idx_vulnerabilidad'].rank(method='first'),
    q=3,
    labels=['Baja', 'Media', 'Alta']
)

# Clasificacion clima-biodiversidad
def clasificar_clima_biodiv(row):
    clima = row['tercil_clima']
    biodiv = row['tercil_biodiv']
    return f"{clima} Clima / {biodiv} Biodiv"

df_integrado['grupo_clima_biodiv'] = df_integrado.apply(clasificar_clima_biodiv, axis=1)

# Cuadrantes gobernanza-vulnerabilidad
mediana_gob = df_integrado['idx_gobernanza'].median()
mediana_vuln = df_integrado['idx_vulnerabilidad'].median()

def clasificar_cuadrante(row):
    alta_gob = row['idx_gobernanza'] >= mediana_gob
    alta_vuln = row['idx_vulnerabilidad'] >= mediana_vuln

    if alta_gob and not alta_vuln:
        return 'Q1_Modelo'
    elif not alta_gob and not alta_vuln:
        return 'Q2_Conservar'
    elif not alta_gob and alta_vuln:
        return 'Q3_Vulnerable'
    else:
        return 'Q4_Desarrollo'

df_integrado['cuadrante'] = df_integrado.apply(clasificar_cuadrante, axis=1)

print(f"   Distribucion cuadrantes:")
for q in ['Q1_Modelo', 'Q2_Conservar', 'Q3_Vulnerable', 'Q4_Desarrollo']:
    n = (df_integrado['cuadrante'] == q).sum()
    print(f"     {q}: {n} ({100*n/len(df_integrado):.1f}%)")

# =============================================================================
# 7. ORDENAR COLUMNAS
# =============================================================================
print("\n7. Ordenando columnas...")

# Orden logico de columnas
col_order = [
    # Identificacion
    'cod_ibge', 'Municipio',
    'cod_microrregiao', 'nome_microrregiao',
    'cod_mesorregiao', 'nome_mesorregiao',

    # Poblacion y vulnerabilidad social
    'population', 'pct_rural', 'pct_urbana',
    'population_preta', 'population_branca', 'population_indigena',
    'pct_pobreza', 'pct_preta', 'pct_indigena',
    'n_pessoas_pobreza', 'n_familias_rua',
    'mort_infantil', 'IDESP_ensino_medio', 'esgoto_tratado',

    # Gobernanza (UAI)
    'UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk',
    'idx_gobernanza', 'idx_gobernanza_100',

    # Biodiversidad
    'mean_species_richness', 'max_species_richness', 'Vert_rich_risk',
    'forest_cover', 'pol_deficit',
    'idx_biodiv',

    # Clima
    'flooding_exposure', 'flooding_risks',
    'hydric_stress_exp', 'hydric_stress_risk',
    'idx_clima',

    # Salud - Persistencia
    'persist_dengue', 'persist_leishmaniose', 'persist_leptospirose', 'persist_malaria',

    # Salud - Incidencia
    'incidence_mean_dengue', 'incidence_mean_leishmaniose',
    'incidence_mean_leptospirose', 'incidence_mean_malaria',
    'incidence_max_dengue', 'incidence_max_leishmaniose',
    'incidence_max_leptospirose', 'incidence_max_malaria',

    # Salud - Casos totales
    'total_cases_dengue', 'total_cases_leishmaniose',
    'total_cases_leptospirose', 'total_cases_malaria',

    # Salud - Co-presencia
    'copresence_years', 'copresence_3plus', 'copresence_all4',
    'dengue_leptospirose', 'dengue_malaria', 'dengue_leishmaniose',
    'leptospirose_malaria', 'leptospirose_leishmaniose', 'malaria_leishmaniose',

    # Indices derivados
    'idx_vulnerabilidad', 'idx_carga_enfermedad',

    # Clasificaciones
    'tercil_biodiv', 'tercil_clima', 'tercil_vuln',
    'grupo_clima_biodiv', 'cuadrante'
]

# Mantener solo columnas que existen
final_cols = [c for c in col_order if c in df_integrado.columns]
# Agregar columnas que no estan en el orden (por si acaso)
extra_cols = [c for c in df_integrado.columns if c not in final_cols]
final_cols.extend(extra_cols)

df_integrado = df_integrado[final_cols]

print(f"   Columnas finales: {len(df_integrado.columns)}")

# =============================================================================
# 8. GUARDAR DATASET
# =============================================================================
print("\n8. Guardando dataset...")

output_path = f"{PROJECT_ROOT}/outputs/municipios_integrado_v6.csv"
df_integrado.to_csv(output_path, index=False)
print(f"   Guardado: {output_path}")

# =============================================================================
# 9. RESUMEN FINAL
# =============================================================================
print("\n" + "=" * 70)
print("RESUMEN DEL DATASET INTEGRADO v6")
print("=" * 70)

print(f"\nMunicipios: {len(df_integrado)}")
print(f"Columnas: {len(df_integrado.columns)}")

print("\nCobertura de variables clave:")
for var in ['idx_gobernanza', 'idx_biodiv', 'idx_clima', 'idx_vulnerabilidad',
            'idx_carga_enfermedad', 'persist_dengue', 'incidence_mean_dengue']:
    if var in df_integrado.columns:
        n_valid = df_integrado[var].notna().sum()
        pct = 100 * n_valid / len(df_integrado)
        print(f"  {var}: {n_valid}/645 ({pct:.1f}%)")

print("\n" + "=" * 70)
print("Dataset v6 creado exitosamente!")
print("=" * 70)
