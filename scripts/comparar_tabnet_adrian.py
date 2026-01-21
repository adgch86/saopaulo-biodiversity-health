"""
Comparación: Datos TABNET Adrian vs DATASUS DBC
Objetivo: Identificar el filtro correcto que usa TABNET para "Casos Prováveis"
"""

import pandas as pd
import re

# ============================================================
# PARTE 1: Cargar datos de Adrian (TABNET - Casos Prováveis)
# ============================================================
print("="*80)
print("CARGANDO DATOS DE ADRIAN (TABNET)")
print("="*80)

# Leer el CSV que Adrian exportó de TABNET
adrian_file = "data/raw/sinannet_cnv_denguebsp213738186_212_98_169_paraArlex.csv"
df_adrian = pd.read_csv(adrian_file, sep=';', encoding='latin-1', skiprows=3)

# Limpiar nombres de columnas
df_adrian.columns = ['municipio', '2013', '2014', '2015', '2016', 'Total']

# Extraer código de municipio
df_adrian['cod'] = df_adrian['municipio'].str.extract(r'^(\d{6})')

# Convertir a numérico (reemplazar '-' por 0)
for col in ['2013', '2014', '2015', '2016', 'Total']:
    df_adrian[col] = pd.to_numeric(df_adrian[col].replace('-', 0), errors='coerce').fillna(0).astype(int)

print(f"Municipios cargados: {len(df_adrian)}")
print(f"\nPrimeros registros:")
print(df_adrian[['cod', 'municipio', '2014', '2015', '2016']].head(10))

# ============================================================
# PARTE 2: Cargar datos de nuestro análisis DATASUS
# ============================================================
print("\n" + "="*80)
print("CARGANDO DATOS DATASUS (ANÁLISIS PREVIO)")
print("="*80)

# Datos que habíamos extraído de los archivos DBC
df_datasus = pd.read_csv("outputs/dengue_datasus_vs_adrian.csv")
print(f"Municipios: {len(df_datasus)}")
print(f"Columnas: {df_datasus.columns.tolist()}")

# ============================================================
# PARTE 3: Comparación detallada
# ============================================================
print("\n" + "="*80)
print("COMPARACIÓN DETALLADA")
print("="*80)

# Municipios de prueba
test_municipios = {
    '351300': 'COTIA',
    '351310': 'CRAVINHOS',
    '351380': 'DIADEMA',
    '351390': 'DIVINOLANDIA',
    '351400': 'DOBRADA',
    '351110': 'CATANDUVA',
    '350950': 'CAMPINAS',
    '355030': 'SAO PAULO',
    '354340': 'RIBEIRAO PRETO'
}

print("\n" + "-"*100)
print(f"{'Municipio':<25} {'Año':<6} {'TABNET':<10} {'DBC_Tot':<10} {'DBC_Conf':<10} {'Diff_Tab-Tot':<15} {'Diff_Tab-Conf':<15}")
print("-"*100)

for cod, nome in test_municipios.items():
    # Datos Adrian
    adrian_row = df_adrian[df_adrian['cod'] == cod]

    # Datos nuestros
    datasus_row = df_datasus[df_datasus['cod'].astype(str) == cod]

    if len(adrian_row) > 0 and len(datasus_row) > 0:
        for year in ['2014', '2015', '2016']:
            tabnet = adrian_row[year].values[0]
            tot = datasus_row[f'tot_{year}'].values[0]
            conf = datasus_row[f'conf_{year}'].values[0]
            diff_tot = tabnet - tot
            diff_conf = tabnet - conf

            print(f"{nome:<25} {year:<6} {tabnet:<10} {tot:<10} {conf:<10} {diff_tot:<15} {diff_conf:<15}")

# ============================================================
# PARTE 4: Análisis estadístico
# ============================================================
print("\n" + "="*80)
print("ANÁLISIS ESTADÍSTICO")
print("="*80)

# Merge ambos datasets
df_merge = pd.merge(
    df_adrian[['cod', '2014', '2015', '2016']].rename(columns={'2014': 'tab_2014', '2015': 'tab_2015', '2016': 'tab_2016'}),
    df_datasus.rename(columns={'cod': 'cod_num'}),
    left_on='cod',
    right_on=df_datasus['cod'].astype(str),
    how='inner'
)

if len(df_merge) > 0:
    for year in ['2014', '2015', '2016']:
        tab_col = f'tab_{year}'
        tot_col = f'tot_{year}'
        conf_col = f'conf_{year}'

        # Calcular diferencias
        df_merge[f'diff_tot_{year}'] = df_merge[tab_col] - df_merge[tot_col]
        df_merge[f'diff_conf_{year}'] = df_merge[tab_col] - df_merge[conf_col]

        print(f"\n{year}:")
        print(f"  TABNET vs Total:       Media diff = {df_merge[f'diff_tot_{year}'].mean():.2f}")
        print(f"  TABNET vs Confirmados: Media diff = {df_merge[f'diff_conf_{year}'].mean():.2f}")

        # Casos donde TABNET > Confirmados (esperado)
        n_mayor = (df_merge[f'diff_conf_{year}'] > 0).sum()
        print(f"  Casos donde TABNET > Conf: {n_mayor}/{len(df_merge)}")

        # Casos donde TABNET < Total (esperado)
        n_menor = (df_merge[f'diff_tot_{year}'] < 0).sum()
        print(f"  Casos donde TABNET < Total: {n_menor}/{len(df_merge)}")

# ============================================================
# PARTE 5: Conclusión
# ============================================================
print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)

print("""
HALLAZGO CLAVE:
---------------
Los datos de TABNET ("Casos Prováveis") son DIFERENTES de:
1. Total de notificaciones (TABNET < Total)
2. Casos confirmados (TABNET > Confirmados en la mayoría)

Esto significa que:
- TABNET filtra: Total - Descartados (CLASSI_FIN excluidos)
- Nuestros "Confirmados": Solo CLASSI_FIN in (5, 10, 11, 12) para 2014-2016

RECOMENDACIÓN:
--------------
Para replicar TABNET necesitamos:
1. Excluir solo los casos DESCARTADOS (CLASSI_FIN = 5 en 2014+)
2. NO excluir los casos sin clasificación final (NA)
3. NO excluir los inconclusivos

O mejor aún: USAR DIRECTAMENTE los datos de TABNET que Adrian proveyó,
ya que vienen con el filtro oficial de DATASUS.
""")

# Guardar resumen
summary = df_adrian[['cod', 'municipio', '2014', '2015', '2016', 'Total']].copy()
summary = summary[summary['cod'].notna()]
summary.to_csv('outputs/tabnet_casos_provaveis_2014_2016.csv', index=False, encoding='utf-8')
print(f"\nArchivo guardado: outputs/tabnet_casos_provaveis_2014_2016.csv")
print(f"Total municipios: {len(summary)}")
