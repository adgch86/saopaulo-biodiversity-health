# Biodiversity, Health and Universal Access in São Paulo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FAIR](https://img.shields.io/badge/FAIR-Compliant-green.svg)](https://www.go-fair.org/fair-principles/)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](https://zenodo.org/)

Analysis of correlations between biodiversity, climate risks, universal access to services (UAI), and health outcomes across the 645 municipalities of São Paulo State, Brazil.

**Author**: [Adrian David González Chaves](https://orcid.org/0000-0002-5233-8957) | **Institution**: University of São Paulo (USP)

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
# Clone repository
git clone https://github.com/adgch86/saopaulo-biodiversity-health.git
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

## FAIR Compliance

This project follows [FAIR principles](https://www.go-fair.org/fair-principles/) for scientific data management:

| Principle | Implementation |
|-----------|----------------|
| **Findable** | `CITATION.cff` for citation, structured `metadata.json`, ORCID linked |
| **Accessible** | `DATA_ACCESS.md` protocol, open GitHub repository |
| **Interoperable** | Standard vocabularies (AGROVOC, ICD-10), JSON Schema validation |
| **Reusable** | MIT License, `PROVENANCE.md`, `REUSE_GUIDE.md`, documented methodology |

### FAIR Documentation

| Document | Description |
|----------|-------------|
| [CITATION.cff](CITATION.cff) | Standard citation format |
| [DATA_ACCESS.md](DATA_ACCESS.md) | How to access the data |
| [PROVENANCE.md](PROVENANCE.md) | Data origin and lineage |
| [LIMITATIONS.md](LIMITATIONS.md) | Known limitations and biases |
| [REUSE_GUIDE.md](REUSE_GUIDE.md) | Guide for reusing this work |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [data/metadata.json](data/metadata.json) | Structured metadata |
| [data/schema.json](data/schema.json) | JSON Schema for validation |
| [data/vocabulary_mapping.json](data/vocabulary_mapping.json) | Standard vocabulary mappings |
| [docs/METHODOLOGY_IVM.md](docs/METHODOLOGY_IVM.md) | IVM index methodology |

## Author

**Adrian David González Chaves**
- ORCID: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)
- Email: adgch86@gmail.com
- GitHub: [@adgch86](https://github.com/adgch86)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use this dataset or methodology, please cite:

```bibtex
@dataset{gonzalez_chaves_2026,
  author = {González Chaves, Adrian David},
  title = {Biodiversity, Health and Universal Access in São Paulo},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/adgch86/saopaulo-biodiversity-health}
}
```
