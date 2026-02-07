"""
Download população estimada do IBGE para municípios de São Paulo (2010-2019)
API: SIDRA - Tabela 6579 (Estimativa de população)
"""
import requests
import pandas as pd
import time

print("=" * 70)
print("Download de População Estimada - IBGE SIDRA")
print("Estado: São Paulo | Período: 2010-2019")
print("=" * 70)

# API SIDRA - Tabela 6579: População estimada
# Variável 9324: População residente estimada
BASE_URL = "https://apisidra.ibge.gov.br/values"

# Parâmetros
# t = tabela, n6 = nível município, v = variável, p = período
params = {
    't': '6579',           # Tabela de população estimada
    'n6': 'N3[35]',        # Municípios de SP (N3 = estado, 35 = SP)
    'v': '9324',           # População residente estimada
    'p': '2010,2011,2012,2013,2014,2015,2016,2017,2018,2019',
    'f': 'n'               # Formato numérico
}

print("\n1. Baixando dados do SIDRA...")

try:
    # Construir URL
    url = f"{BASE_URL}/t/{params['t']}/n6/{params['n6']}/v/{params['v']}/p/{params['p']}/f/{params['f']}"
    print(f"   URL: {url[:80]}...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()
    print(f"   Registros recebidos: {len(data)}")

    # Processar dados (pular header)
    records = []
    for row in data[1:]:  # Pular primeira linha (header)
        try:
            cod_ibge = row['D1C'][:6]  # Código município (6 dígitos)
            nome = row['D1N']
            year = row['D2C']
            pop = int(row['V']) if row['V'] and row['V'] != '-' else 0

            records.append({
                'cod_ibge': cod_ibge,
                'nome_municipio': nome,
                'year': int(year),
                'population': pop
            })
        except (KeyError, ValueError) as e:
            continue

    df_long = pd.DataFrame(records)
    print(f"   Registros processados: {len(df_long)}")

except Exception as e:
    print(f"   Erro na API SIDRA: {e}")
    print("\n   Tentando API alternativa (localidades + estimativas)...")

    # Alternativa: usar API de localidades para obter lista e estimar
    url_mun = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"
    response = requests.get(url_mun)
    municipios = response.json()

    records = []
    for mun in municipios:
        cod = str(mun['id'])[:6]
        nome = mun['nome']

        # Buscar população por município individual
        for year in range(2010, 2020):
            try:
                url_pop = f"https://apisidra.ibge.gov.br/values/t/6579/n6/{cod}/v/9324/p/{year}/f/n"
                resp = requests.get(url_pop, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if len(data) > 1:
                        pop = int(data[1]['V']) if data[1]['V'] else 0
                        records.append({
                            'cod_ibge': cod,
                            'nome_municipio': nome,
                            'year': year,
                            'population': pop
                        })
            except:
                continue

        if len(records) % 100 == 0:
            print(f"   Processados: {len(records)} registros...")

    df_long = pd.DataFrame(records)

# Verificar dados
print(f"\n2. Resumo dos dados:")
print(f"   Municípios únicos: {df_long['cod_ibge'].nunique()}")
print(f"   Anos: {sorted(df_long['year'].unique())}")
print(f"   População total 2019: {df_long[df_long['year']==2019]['population'].sum():,}")

# Pivotar para formato largo
print("\n3. Convertendo para formato largo...")
df_wide = df_long.pivot_table(
    index=['cod_ibge', 'nome_municipio'],
    columns='year',
    values='population',
    aggfunc='first'
).reset_index()

# Renomear colunas
df_wide.columns = ['cod_ibge', 'nome_municipio'] + [f'pop_{y}' for y in range(2010, 2020)]

# Calcular população média
df_wide['pop_mean'] = df_wide[[f'pop_{y}' for y in range(2010, 2020)]].mean(axis=1)

print(f"   Municípios: {len(df_wide)}")
print(f"   Colunas: {list(df_wide.columns)}")

# Salvar
output_file = "data/processed/populacao_SP_2010_2019.csv"
df_wide.to_csv(output_file, index=False)
print(f"\n4. Arquivo salvo: {output_file}")

# Mostrar amostra
print("\n5. Amostra dos dados:")
print(df_wide.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("Concluído!")
print("=" * 70)
