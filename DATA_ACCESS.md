# Data Access Protocol

This document describes how to access, obtain, and use the data associated with this research project.

## Quick Reference

| Data Type | Location | Access |
|-----------|----------|--------|
| Code & Scripts | GitHub | Open |
| Processed Data | GitHub | Open |
| Raw Data (small) | GitHub | Open |
| Raw Data (large) | On request | Restricted |
| Geographic Data | On request | Restricted |

---

## Open Access Data (GitHub)

### Repository
```
https://github.com/adgch86/saopaulo-biodiversity-health
```

### Available Files

**Processed Data** (`data/processed/`):
| File | Format | Size | Description |
|------|--------|------|-------------|
| `df_sin_cuadrantes.pkl` | Pickle | ~5 MB | Main dataset with quadrant classification |
| `df_merged.pkl` | Pickle | ~3 MB | Merged environmental + health data |
| `corr_matrix.pkl` | Pickle | <1 MB | Precomputed correlation matrices |

**Output Data** (`outputs/`):
| File | Format | Description |
|------|--------|-------------|
| `correlaciones_nexo_v5.csv` | CSV | Complete correlation matrix |
| `municipios_integrado_v5.csv` | CSV | Integrated municipal dataset |
| `municipios_ivm_v3.csv` | CSV | IVM classification |

**Figures** (`outputs/figures/`):
- All visualization PNG files
- Dashboard mockups (HTML + PNG)

### How to Access

```bash
# Clone repository
git clone https://github.com/adgch86/saopaulo-biodiversity-health.git

# Or download specific files
wget https://raw.githubusercontent.com/adgch86/saopaulo-biodiversity-health/main/outputs/correlaciones_nexo_v5.csv
```

---

## Restricted Access Data

### Large Raw Files

These files are NOT included in the GitHub repository due to size constraints:

| File | Size | Records | Request Required |
|------|------|---------|------------------|
| `645_sin_salud.csv` | 55 MB | 645 | Yes |
| `187_con_salud.csv` | 19 MB | 187 | Yes |
| Geographic shapefiles | ~100 MB | - | Yes |

### How to Request

**Option 1: Direct Request**

Email the principal investigator:
- **To**: Adrian David González Chaves
- **Email**: adgch86@gmail.com
- **Subject**: Data Request - São Paulo Biodiversity-Health Dataset

Include in your request:
1. Your name and institutional affiliation
2. Intended use of the data
3. Specific files needed
4. Agreement to citation requirements

**Option 2: Institutional Access**

For researchers at partner institutions:
- University of São Paulo (USP)
- Partner institutions through formal data sharing agreements

Contact your institution's data governance office for existing agreements.

### Expected Response Time

- Academic researchers: 1-2 weeks
- Government agencies: 1 week
- Commercial use: Case-by-case evaluation

---

## Original Data Sources

All data can be independently obtained from official Brazilian government sources:

### 1. AdaptaBrasil MCTI
- **URL**: https://adaptabrasil.mcti.gov.br/
- **Data**: UAI indices, climate vulnerability
- **Access**: Open, free registration required
- **Format**: CSV, API available

### 2. DATASUS TabNet
- **URL**: http://tabnet.datasus.gov.br/
- **Data**: Health statistics, disease incidence
- **Access**: Open, no registration
- **Format**: CSV download
- **Navigation**: TABNET > Epidemiologia e Morbidade > Morbidade Hospitalar

### 3. IBGE
- **URL**: https://www.ibge.gov.br/
- **Data**: Demographics, geography, socioeconomics
- **Access**: Open
- **Format**: CSV, shapefiles (GEOFTP)
- **Geographic data**: https://geoftp.ibge.gov.br/

### 4. INPE
- **URL**: https://www.inpe.br/
- **Data**: Environmental, biodiversity proxies
- **Access**: Open
- **Format**: Varies by product

---

## Data Use Agreement

By accessing this data, you agree to:

### Attribution
- Cite this dataset using the `CITATION.cff` file
- Acknowledge data sources in publications
- Include DOI when available

### Ethical Use
- Use data for legitimate research purposes
- Not attempt to identify individuals
- Comply with Brazilian data protection laws (LGPD)
- Not redistribute restricted data without permission

### Reporting
- Notify the PI of publications using this data
- Share derivative datasets back to the community when possible

---

## Technical Requirements

### Software Requirements
```
Python >= 3.8
pandas >= 1.3.0
numpy >= 1.20.0
scipy >= 1.7.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
geopandas >= 0.10.0 (for geographic data)
```

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Loading Data
```python
import pandas as pd

# Load main dataset
df = pd.read_pickle('data/processed/df_sin_cuadrantes.pkl')

# Load correlation matrix
corr = pd.read_pickle('data/processed/corr_matrix.pkl')

# Load CSV outputs
municipios = pd.read_csv('outputs/municipios_integrado_v5.csv')
```

---

## API Access (Future)

A REST API for programmatic access is planned for future releases.

**Planned endpoints**:
```
GET /api/v1/municipalities
GET /api/v1/municipalities/{code}
GET /api/v1/correlations
GET /api/v1/quadrants/{quadrant}
```

Status: Not yet implemented

---

## Support

### Technical Issues
- Open an issue on GitHub: https://github.com/adgch86/saopaulo-biodiversity-health/issues

### Data Questions
- Email: adgch86@gmail.com
- Response time: 1-2 business days

### Collaboration Inquiries
- For research collaborations, contact the PI directly
- Include your research proposal and institutional affiliation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-19 | Initial data access protocol |

---

## License

- **Code**: MIT License (see `LICENSE`)
- **Data**: Open Government Data (Brazil) - original sources
- **Derived data**: MIT License
