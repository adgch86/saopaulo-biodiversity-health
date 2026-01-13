# Biodiversidad, Salud y Acceso Universal en Sao Paulo

Analisis de correlaciones entre biodiversidad, riesgos climaticos, acceso universal a servicios (UAI) y resultados de salud en los 645 municipios del Estado de Sao Paulo, Brasil.

## Estructura del Proyecto

```
saopaulo-biodiversity-health/
├── data/
│   ├── raw/           # Datos crudos (CSVs - no en git)
│   ├── processed/     # Datos procesados (pickles)
│   └── geo/           # Datos geograficos (shapefiles - no en git)
├── docs/              # Documentacion y metadata
├── outputs/figures/   # Visualizaciones generadas
├── src/               # Codigo Python (futuro)
└── notebooks/         # Jupyter notebooks (futuro)
```

## Datos

### Fuentes
- **AdaptaBrasil MCTI**: Indices de vulnerabilidad climatica y UAI
- **DATASUS**: Datos epidemiologicos (dengue, malaria, diarrea, leptospirosis)
- **IBGE**: Datos demograficos y geograficos

### Datasets Principales

| Archivo | Registros | Descripcion |
|---------|-----------|-------------|
| 645_sin_salud.csv | 645 | Municipios con datos ambientales y UAI |
| 187_con_salud.csv | 187 | Municipios con datos epidemiologicos |

> **Nota**: Los CSVs grandes no estan en el repositorio. Ver `data/raw/README.md` para instrucciones.

## Variables Principales

### Biodiversidad
- `mean_species_richness`: Riqueza media de especies
- `Vert_rich_risk`: Riesgo para vertebrados

### Riesgos Climaticos
- `flooding_exposure/risks`: Exposicion/riesgo de inundaciones
- `hydric_stress_exp/risk`: Estres hidrico

### Indice de Acceso Universal (UAI)
- `UAI_housing`: Acceso a vivienda
- `UAI_env`: Acceso ambiental
- `UAI_food`: Acceso alimentario
- `UAI_mob`: Acceso a movilidad
- `UAI_Crisk`: Riesgo climatico

### Salud (187 municipios)
- `incidence_*`: Incidencia de enfermedades
- `persist_*`: Persistencia de enfermedades (2010-2019)
- `copersistence`: Indice de copersistencia de enfermedades

## Hallazgos Principales

1. **Biodiversidad vs Deficit Politico**: Correlacion negativa fuerte (r = -0.57)
2. **UAI como factor protector**: Correlacion negativa con malaria (r = -0.59)
3. **Riesgos climaticos y salud**: Asociados a copersistencia de enfermedades (r = 0.28)

### Clasificacion de Municipios (4 Cuadrantes)

| Cuadrante | Descripcion | N | % |
|-----------|-------------|---|---|
| Q1 - Modelo | Alto UAI + Alta Biodiversidad | 195 | 30.2% |
| Q2 - Conservar | Bajo UAI + Alta Biodiversidad | 128 | 19.8% |
| Q3 - Vulnerable | Bajo UAI + Baja Biodiversidad | 192 | 29.8% |
| Q4 - Desarrollo | Alto UAI + Baja Biodiversidad | 130 | 20.2% |

## Instalacion

```bash
# Clonar repositorio
git clone https://github.com/[usuario]/saopaulo-biodiversity-health.git
cd saopaulo-biodiversity-health

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```python
import pandas as pd

# Cargar datos procesados
df = pd.read_pickle('data/processed/df_sin_cuadrantes.pkl')

# Ver distribucion de cuadrantes
print(df['cuadrante'].value_counts())
```

## Documentacion

- `docs/metadata.xlsx` - Definiciones de variables con fuentes
- `docs/INFORME_ANALISIS_CORRELACIONES.md` - Analisis completo de correlaciones

## Autor

Adrian Gonzalez-Chaves

## Licencia

MIT License
