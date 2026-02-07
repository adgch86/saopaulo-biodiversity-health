"""
Comparación de datos originales vs. nuevos (con filtro CLASSI_FIN != 5)
"""
import pandas as pd

# Cargar datos
old_data = pd.read_csv('data/processed/health_data_SP_2010_2019.csv')
new_data = pd.read_csv('data/processed/health_casos_provaveis_SP_2010_2019.csv')

print("=" * 70)
print("COMPARACIÓN: Datos Originales vs. Casos Prováveis")
print("=" * 70)

# Calcular totales del archivo original (formato largo)
print("\n1. TOTALES POR AÑO - ARCHIVO ORIGINAL (sin filtro CLASSI_FIN)")
print("-" * 60)
old_totals = old_data.groupby('year').agg({
    'cases_deng': 'sum',
    'cases_lept': 'sum',
    'cases_mala': 'sum',
    'cases_leiv': 'sum',
    'cases_ltan': 'sum'
}).reset_index()
print(old_totals.to_string(index=False))

# Calcular totales del archivo nuevo (formato ancho)
print("\n2. TOTALES POR AÑO - ARCHIVO NUEVO (Casos Prováveis)")
print("-" * 60)

diseases = {
    'dengue': 'deng',
    'leptospirose': 'lept',
    'malaria': 'mala',
    'leish_visceral': 'leiv',
    'leish_tegumentar': 'ltan'
}

new_totals = {}
for disease, prefix in diseases.items():
    cols = [c for c in new_data.columns if c.startswith(prefix + '_')]
    for col in cols:
        year = int(col.split('_')[1])
        if year not in new_totals:
            new_totals[year] = {}
        new_totals[year][disease] = new_data[col].sum()

new_df = pd.DataFrame(new_totals).T.sort_index()
new_df.index.name = 'year'
print(new_df.to_string())

# Comparación
print("\n3. DIFERENCIA (Nuevo - Original)")
print("-" * 60)
print("   Valores negativos = el filtro excluyó casos descartados")
print()

for disease, prefix in diseases.items():
    print(f"\n{disease.upper()}:")
    for year in range(2010, 2020):
        old_col = f'cases_{prefix}'
        old_val = old_data[old_data['year'] == year][old_col].sum()
        new_val = new_totals.get(year, {}).get(disease, 0)
        diff = new_val - old_val
        pct = (diff / old_val * 100) if old_val > 0 else 0
        print(f"  {year}: {new_val:>10,} - {old_val:>10,} = {diff:>+10,} ({pct:+.1f}%)")

print("\n" + "=" * 70)
print("CONCLUSIÓN")
print("=" * 70)
print("""
- DENGUE: El filtro CLASSI_FIN != 5 reduce significativamente los casos
  (excluyendo casos descartados como lo hace TABNET)

- LEPTOSPIROSE: Pequeñas diferencias (probablemente por filtrado de municipio ignorado)

- MALARIA: Pequeñas diferencias

- LEISHMANIOSE VISCERAL: Pequeñas diferencias

- LEISHMANIOSE TEGUMENTAR: Pequeñas diferencias (usa variable CRITERIO, no CLASSI_FIN)

El problema del filtro SOLO afectaba significativamente a DENGUE.
Las otras enfermedades no tenían CLASSI_FIN = 5 (descartados) en sus bases.
""")
