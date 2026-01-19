# Data Sources

Complete documentation of all data sources used in this research project, including URLs, access dates, and versioning information.

## Primary Sources

### 1. AdaptaBrasil MCTI

| Attribute | Value |
|-----------|-------|
| **Official Name** | Sistema de Informações e Análises sobre Impactos das Mudanças Climáticas no Brasil |
| **Provider** | Ministério da Ciência, Tecnologia e Inovação (MCTI) |
| **URL** | https://adaptabrasil.mcti.gov.br/ |
| **Access Date** | January 14, 2026 |
| **Data Version** | 2024 release |
| **Format** | CSV, Excel |
| **License** | Open Government Data (Brazil) |
| **Documentation** | https://adaptabrasil.mcti.gov.br/metodologia |

**Variables Obtained**:
| Variable Code | Description | Unit |
|---------------|-------------|------|
| `UAI_housing` | Universal Access Index - Housing | 0-1 scale |
| `UAI_env` | Universal Access Index - Environment | 0-1 scale |
| `UAI_food` | Universal Access Index - Food Security | 0-1 scale |
| `UAI_mob` | Universal Access Index - Mobility | 0-1 scale |
| `UAI_Crisk` | Universal Access Index - Climate Risk | 0-1 scale |
| `flooding_exposure` | Flood exposure indicator | Index |
| `flooding_risks` | Flood risk indicator | Index |
| `hydric_stress_exp` | Water stress exposure | Index |
| `hydric_stress_risk` | Water stress risk | Index |

**API/Download Path**:
```
Portal > Indicadores > Municipal > São Paulo > Exportar CSV
```

---

### 2. DATASUS - TabNet

| Attribute | Value |
|-----------|-------|
| **Official Name** | Departamento de Informática do Sistema Único de Saúde |
| **Provider** | Ministério da Saúde, Brazil |
| **URL** | http://tabnet.datasus.gov.br/ |
| **Access Date** | January 14, 2026 |
| **Data Period** | 2010-2019 |
| **Format** | CSV (TabNet export) |
| **License** | Open Government Data (Brazil) |
| **Documentation** | http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/niuf.def |

**Variables Obtained**:
| Variable Code | Description | Unit |
|---------------|-------------|------|
| `incidence_dengue` | Dengue fever incidence | per 100,000 pop |
| `incidence_diarrhea` | Diarrheal disease incidence | per 100,000 pop |
| `incidence_malaria` | Malaria incidence | per 100,000 pop |
| `incidence_leptospirosis` | Leptospirosis incidence | per 100,000 pop |
| `persist_dengue` | Dengue persistence (years detected) | count 0-10 |
| `persist_diarrhea` | Diarrhea persistence | count 0-10 |
| `persist_malaria` | Malaria persistence | count 0-10 |
| `copersistence` | Multi-disease copersistence index | 0-1 scale |

**Query Path**:
```
TABNET > Epidemiologia e Morbidade > Morbidade Hospitalar do SUS (SIH/SUS) >
Por local de residência > Estado: São Paulo > Período: 2010-2019
```

---

### 3. IBGE - Instituto Brasileiro de Geografia e Estatística

| Attribute | Value |
|-----------|-------|
| **Official Name** | Instituto Brasileiro de Geografia e Estatística |
| **Provider** | Brazilian Federal Government |
| **URL** | https://www.ibge.gov.br/ |
| **GeoFTP** | https://geoftp.ibge.gov.br/ |
| **SIDRA API** | https://sidra.ibge.gov.br/home/pms/brasil |
| **Access Date** | January 14, 2026 |
| **Census Years** | 2010, 2022 |
| **Format** | CSV, Shapefile, GeoPackage |
| **License** | Open Government Data (Brazil) |

**Variables Obtained**:
| Variable Code | Description | Source |
|---------------|-------------|--------|
| `population` | Total population | Census 2022 |
| `cod_ibge` | IBGE municipality code (7 digits) | Master list |
| `nome_municipio` | Municipality name | Master list |
| `area_km2` | Municipality area | Geographic |
| Shapefiles | Municipal boundaries | GEOFTP |

**Download Paths**:
```
# Municipal boundaries
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/

# Population data
https://sidra.ibge.gov.br/tabela/4714
```

---

### 4. INPE - Instituto Nacional de Pesquisas Espaciais

| Attribute | Value |
|-----------|-------|
| **Official Name** | Instituto Nacional de Pesquisas Espaciais |
| **Provider** | Brazilian Federal Government |
| **URL** | https://www.inpe.br/ |
| **TerraBrasilis** | http://terrabrasilis.dpi.inpe.br/ |
| **Access Date** | January 14, 2026 |
| **Format** | GeoTIFF, CSV |
| **License** | Open Government Data (Brazil) |

**Variables Obtained**:
| Variable Code | Description | Product |
|---------------|-------------|---------|
| `mean_species_richness` | Mean species richness | Biodiversity model |
| `Vert_rich_risk` | Vertebrate richness risk | Biodiversity model |
| `forest_cover_pct` | Forest cover percentage | PRODES/MapBiomas |

---

## Secondary/Reference Sources

### Academic Publications

| Reference | DOI | Used For |
|-----------|-----|----------|
| Barreto et al. (2025) | 10.1038/s43247-025-02620-7 | Dilution effect methodology |
| Levers et al. (2025) | 10.1088/1748-9326/ae20ac | Conceptual framework |

### Derived Data

| File | Derived From | Method |
|------|--------------|--------|
| `df_merged.pkl` | All sources above | Python pandas merge |
| `municipios_ivm_v3.csv` | Merged data | IVM calculation |
| `correlaciones_nexo_v5.csv` | Merged data | Pearson/Spearman |

---

## Version Control

### Raw Data Snapshots

| Date | Folder | Description |
|------|--------|-------------|
| 2026-01-14 | `data/raw/2026_01_14/` | Latest data pull |

### Source Verification

All sources were verified as active and accessible on: **January 19, 2026**

---

## Reproducibility Notes

### Data Collection Script (Future)
```python
# Planned automated data collection
# Currently manual download from portals
```

### Manual Download Protocol

1. Access each portal URL
2. Navigate to São Paulo state filter
3. Select all municipalities (645)
4. Export as CSV
5. Save with date stamp in `data/raw/YYYY_MM_DD/`
6. Record in this file

---

## Contact for Data Questions

**Adrian David González Chaves**
- Email: adgch86@gmail.com
- ORCID: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)

For issues with original data sources, contact the respective government agencies.
