# Data Provenance

This document describes the origin, processing, and lineage of all data used in this research project.

## Overview

| Aspect | Description |
|--------|-------------|
| **Project** | Biodiversity, Health and Universal Access in São Paulo |
| **Principal Investigator** | Adrian David González Chaves |
| **Institution** | University of São Paulo (USP) |
| **Data Period** | 2010-2019 (varies by variable) |
| **Geographic Scope** | 645 municipalities of São Paulo State, Brazil |

---

## Primary Data Sources

### 1. AdaptaBrasil MCTI

| Attribute | Value |
|-----------|-------|
| **URL** | https://adaptabrasil.mcti.gov.br/ |
| **Provider** | Ministry of Science, Technology and Innovation (MCTI), Brazil |
| **Access Date** | January 2026 |
| **License** | Open Government Data (Brazil) |
| **Variables Obtained** | UAI indices, climate risk indicators, vulnerability metrics |

**Description**: AdaptaBrasil is the official Brazilian platform for climate change adaptation information. It provides municipality-level indicators for vulnerability, adaptive capacity, and sectoral risks.

**UAI Variables Extracted**:
- `UAI_housing`: Universal Access Index - Housing
- `UAI_env`: Universal Access Index - Environment
- `UAI_food`: Universal Access Index - Food Security
- `UAI_mob`: Universal Access Index - Mobility
- `UAI_Crisk`: Universal Access Index - Climate Risk

### 2. DATASUS

| Attribute | Value |
|-----------|-------|
| **URL** | http://tabnet.datasus.gov.br/ |
| **Provider** | Ministry of Health, Brazil |
| **Access Date** | January 2026 |
| **License** | Open Government Data (Brazil) |
| **Variables Obtained** | Disease incidence and hospitalization rates |

**Description**: DATASUS is the IT department of Brazil's Unified Health System (SUS). TabNet provides aggregated health statistics by municipality.

**Health Variables Extracted**:
- `incidence_dengue`: Dengue fever incidence per 100,000
- `incidence_diarrhea`: Diarrheal disease incidence per 100,000
- `incidence_malaria`: Malaria incidence per 100,000
- `incidence_leptospirosis`: Leptospirosis incidence per 100,000
- `persist_*`: Disease persistence indicators (2010-2019)
- `copersistence`: Multi-disease copersistence index

### 3. IBGE (Brazilian Institute of Geography and Statistics)

| Attribute | Value |
|-----------|-------|
| **URL** | https://www.ibge.gov.br/ |
| **Provider** | IBGE, Brazil |
| **Access Date** | January 2026 |
| **License** | Open Government Data (Brazil) |
| **Variables Obtained** | Demographics, geographic boundaries, socioeconomic indicators |

**Description**: IBGE is Brazil's official statistical agency, providing census data, geographic information, and socioeconomic indicators.

**Data Extracted**:
- Municipal boundaries (shapefiles)
- Population data
- Demographic indicators
- Socioeconomic variables

### 4. INPE (National Institute for Space Research)

| Attribute | Value |
|-----------|-------|
| **URL** | https://www.inpe.br/ |
| **Provider** | INPE, Brazil |
| **Access Date** | January 2026 |
| **License** | Open Government Data (Brazil) |
| **Variables Obtained** | Biodiversity metrics, forest cover |

**Description**: INPE provides satellite-derived environmental data including biodiversity proxies and land use information.

**Biodiversity Variables Extracted**:
- `mean_species_richness`: Mean species richness
- `Vert_rich_risk`: Vertebrate richness risk
- Forest cover percentage

---

## Data Processing Pipeline

### Stage 1: Data Collection
```
Source APIs/Portals → Raw CSV/Excel files → data/raw/
```
- Manual download from government portals
- API queries where available
- Date stamped in folder names (e.g., `2026_01_14/`)

### Stage 2: Data Cleaning
```
data/raw/*.csv → Python scripts → data/processed/*.pkl
```
- Missing value handling
- Variable standardization
- Unit conversions
- Geographic matching (municipality codes)

### Stage 3: Data Integration
```
data/processed/*.pkl → Merge by municipality code → df_merged.pkl
```
- Join on IBGE municipality codes
- Handling of missing municipalities (645 → 187 for health data)
- Creation of derived variables

### Stage 4: Analysis
```
df_merged.pkl → Analysis scripts → outputs/
```
- Correlation analysis
- IVM calculation
- Quadrant classification
- Statistical testing

---

## Processing Scripts

| Script | Version | Purpose | Input | Output |
|--------|---------|---------|-------|--------|
| `science_team_analysis.py` | v1 | Initial analysis | Raw CSVs | Correlations |
| `science_team_analysis_v2.py` | v2 | Statistical improvements | v1 outputs | Enhanced stats |
| `science_team_analysis_v3.py` | v3 | IVM implementation | v2 outputs | IVM scores |
| `science_team_analysis_v4.py` | v4 | Refinements | v3 outputs | Final indices |
| `science_team_analysis_v5_clima.py` | v5 | Climate integration | v4 outputs | Complete dataset |

---

## Derived Variables

### Multidimensional Vulnerability Index (IVM)

| Component | Weight | Source Variables |
|-----------|--------|------------------|
| Poverty indicators | 0.25 | IBGE census data |
| Service access | 0.25 | UAI indices |
| Housing conditions | 0.25 | IBGE census data |
| Climate vulnerability | 0.25 | AdaptaBrasil |

**Formula**: See `docs/METHODOLOGY_IVM.md`

### Quadrant Classification

Based on median splits of UAI (governance) and IVM (vulnerability):

| Quadrant | UAI | IVM | Label |
|----------|-----|-----|-------|
| Q1 | High | Low | Modelo |
| Q2 | Low | Low | Conservar |
| Q3 | Low | High | Vulnerable |
| Q4 | High | High | Desarrollo |

---

## Quality Assurance

### Data Validation
- [x] Municipality codes verified against IBGE master list
- [x] Range checks on all numeric variables
- [x] Cross-validation with published statistics
- [x] Outlier detection and verification

### Reproducibility
- [x] All raw data preserved with timestamps
- [x] Processing scripts versioned
- [x] Random seeds documented where applicable
- [x] Environment specifications in `requirements.txt`

---

## Data Limitations

See `LIMITATIONS.md` for complete discussion of:
- Temporal mismatches between datasets
- Ecological fallacy considerations
- Missing data patterns
- Geographic aggregation issues

---

## Contact

For questions about data provenance:

**Adrian David González Chaves**
- Email: adgch86@gmail.com
- ORCID: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)
- GitHub: [@adgch86](https://github.com/adgch86)
