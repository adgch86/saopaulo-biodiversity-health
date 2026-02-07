"""
Download micro e mesorregiões do IBGE para municípios de São Paulo
API: https://servicodados.ibge.gov.br/api/v1/localidades/
"""
import requests
import pandas as pd
import json

# API do IBGE
BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"

print("=" * 70)
print("Download de Micro e Mesorregiões - IBGE")
print("Estado: São Paulo (UF 35)")
print("=" * 70)

# 1. Baixar municípios de SP com suas regiões
print("\n1. Baixando municípios de São Paulo...")
url = f"{BASE_URL}/estados/35/municipios"
response = requests.get(url)
municipios = response.json()

print(f"   Municípios encontrados: {len(municipios)}")

# 2. Extrair dados
data = []
for mun in municipios:
    data.append({
        'cod_ibge': str(mun['id'])[:6],  # 6 dígitos
        'cod_ibge_7': str(mun['id']),     # 7 dígitos
        'nome_municipio': mun['nome'],
        'cod_microrregiao': mun['microrregiao']['id'],
        'nome_microrregiao': mun['microrregiao']['nome'],
        'cod_mesorregiao': mun['microrregiao']['mesorregiao']['id'],
        'nome_mesorregiao': mun['microrregiao']['mesorregiao']['nome'],
    })

df = pd.DataFrame(data)

# 3. Verificar contagens
print("\n2. Resumo:")
print(f"   Municípios: {len(df)}")
print(f"   Microrregiões: {df['cod_microrregiao'].nunique()}")
print(f"   Mesorregiões: {df['cod_mesorregiao'].nunique()}")

# 4. Listar mesorregiões
print("\n3. Mesorregiões de São Paulo:")
meso = df[['cod_mesorregiao', 'nome_mesorregiao']].drop_duplicates().sort_values('cod_mesorregiao')
for _, row in meso.iterrows():
    n_mun = len(df[df['cod_mesorregiao'] == row['cod_mesorregiao']])
    print(f"   {row['cod_mesorregiao']}: {row['nome_mesorregiao']} ({n_mun} municípios)")

# 5. Listar microrregiões
print("\n4. Microrregiões de São Paulo:")
micro = df[['cod_microrregiao', 'nome_microrregiao', 'nome_mesorregiao']].drop_duplicates().sort_values('cod_microrregiao')
for _, row in micro.iterrows():
    n_mun = len(df[df['cod_microrregiao'] == row['cod_microrregiao']])
    print(f"   {row['cod_microrregiao']}: {row['nome_microrregiao']} ({n_mun} mun.) - {row['nome_mesorregiao']}")

# 6. Salvar
output_file = "data/processed/municipios_regioes_SP.csv"
df.to_csv(output_file, index=False)
print(f"\n5. Arquivo salvo: {output_file}")

# 7. Carregar dados de saúde e fazer merge
print("\n6. Fazendo merge com dados de saúde...")
health_file = "data/processed/health_casos_provaveis_SP_2010_2019.csv"
health = pd.read_csv(health_file, dtype={'cod_ibge': str})
health['cod_ibge'] = health['cod_ibge'].astype(str)
df['cod_ibge'] = df['cod_ibge'].astype(str)
print(f"   Municípios no arquivo de saúde: {len(health)}")

# Merge
merged = health.merge(
    df[['cod_ibge', 'nome_municipio', 'cod_microrregiao', 'nome_microrregiao',
        'cod_mesorregiao', 'nome_mesorregiao']],
    on='cod_ibge',
    how='left'
)

# Verificar
n_matched = merged['nome_municipio'].notna().sum()
n_missing = merged['nome_municipio'].isna().sum()
print(f"   Municípios com match: {n_matched}")
print(f"   Municípios sem match: {n_missing}")

if n_missing > 0:
    print("\n   Códigos sem match:")
    missing = merged[merged['nome_municipio'].isna()]['cod_ibge'].tolist()
    print(f"   {missing[:10]}...")

# Reordenar colunas
cols_info = ['cod_ibge', 'nome_municipio', 'cod_microrregiao', 'nome_microrregiao',
             'cod_mesorregiao', 'nome_mesorregiao']
cols_data = [c for c in merged.columns if c not in cols_info]
merged = merged[cols_info + cols_data]

# Salvar
output_merged = "data/processed/health_casos_provaveis_SP_2010_2019_regioes.csv"
merged.to_csv(output_merged, index=False)
print(f"\n7. Arquivo com regiões salvo: {output_merged}")
print(f"   Colunas: {len(merged.columns)}")
print(f"   Registros: {len(merged)}")

print("\n" + "=" * 70)
print("Concluído!")
print("=" * 70)
