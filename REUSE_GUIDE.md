# Reuse Guide

This guide provides practical instructions for researchers and practitioners who want to reuse this dataset, methodology, or code in their own work.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/adgch86/saopaulo-biodiversity-health.git
cd saopaulo-biodiversity-health
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Load the Data

```python
import pandas as pd

# Main dataset with all variables and classifications
df = pd.read_pickle('data/processed/df_sin_cuadrantes.pkl')

# Or load CSV output
df = pd.read_csv('outputs/municipios_integrado_v5.csv')
```

---

## Common Reuse Scenarios

### Scenario 1: Replicate the Analysis

If you want to reproduce our results exactly:

```python
import pandas as pd
import scipy.stats as stats

# Load processed data
df = pd.read_pickle('data/processed/df_sin_cuadrantes.pkl')

# Reproduce key correlations
biodiv_dengue = stats.pearsonr(df['mean_species_richness'], df['incidence_dengue'].dropna())
print(f"Biodiversity vs Dengue: r = {biodiv_dengue[0]:.3f}, p = {biodiv_dengue[1]:.4f}")
```

### Scenario 2: Apply to Different Region

To apply our methodology to another Brazilian state:

1. **Obtain equivalent data sources**:
   - AdaptaBrasil: https://adaptabrasil.mcti.gov.br/ (filter by your state)
   - DATASUS: http://tabnet.datasus.gov.br/ (filter by your state)
   - IBGE: https://www.ibge.gov.br/

2. **Match variable names** using our `data/metadata.json`

3. **Calculate IVM** following `docs/METHODOLOGY_IVM.md`

4. **Run correlation analysis**:

```python
# Template for new region analysis
def analyze_region(df, region_name):
    """
    Analyze biodiversity-health relationships for a new region.

    Parameters:
    -----------
    df : pandas.DataFrame
        Must contain columns: mean_species_richness, incidence_dengue,
        incidence_diarrhea, incidence_malaria, UAI_*, IVM
    region_name : str
        Name for outputs
    """

    # Key correlations
    health_vars = ['incidence_dengue', 'incidence_diarrhea', 'incidence_malaria']
    results = {}

    for var in health_vars:
        if var in df.columns:
            corr, p = stats.spearmanr(
                df['mean_species_richness'].dropna(),
                df[var].dropna()
            )
            results[var] = {'correlation': corr, 'p_value': p}

    return results
```

### Scenario 3: Use the IVM Index

To calculate the Multidimensional Vulnerability Index for your data:

```python
def calculate_ivm(df, config=None):
    """
    Calculate IVM for a municipality dataset.

    Required columns:
    - Poverty indicators
    - Service access indicators
    - Housing indicators
    - Climate vulnerability indicators

    See docs/METHODOLOGY_IVM.md for full specification.
    """

    default_config = {
        'weights': {
            'poverty': 0.25,
            'service': 0.25,
            'housing': 0.25,
            'climate': 0.25
        }
    }

    config = config or default_config

    # Normalize and aggregate (simplified)
    # See full implementation in scripts/science_team_analysis_v3.py

    return df['IVM']
```

### Scenario 4: Use the Quadrant Classification

```python
def classify_municipalities(df, uai_col='UAI_total', ivm_col='IVM'):
    """
    Classify municipalities into governance-vulnerability quadrants.

    Returns:
    --------
    Series with quadrant labels: Q1_Modelo, Q2_Conservar, Q3_Vulnerable, Q4_Desarrollo
    """

    median_uai = df[uai_col].median()
    median_ivm = df[ivm_col].median()

    def get_quadrant(row):
        high_uai = row[uai_col] >= median_uai
        high_ivm = row[ivm_col] >= median_ivm

        if high_uai and not high_ivm:
            return 'Q1_Modelo'
        elif not high_uai and not high_ivm:
            return 'Q2_Conservar'
        elif not high_uai and high_ivm:
            return 'Q3_Vulnerable'
        else:
            return 'Q4_Desarrollo'

    return df.apply(get_quadrant, axis=1)
```

---

## Data Dictionary

Quick reference for key variables (full details in `data/metadata.json`):

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `cod_ibge` | string | 7 digits | IBGE municipality code |
| `mean_species_richness` | float | 350-755 | Species count |
| `UAI_total` | float | 0-1 | Governance index |
| `IVM` | float | 0-100 | Vulnerability index |
| `cuadrante` | category | Q1-Q4 | Classification |
| `incidence_dengue` | float | 0+ | Cases per 100,000 |

---

## Code Examples

### Example 1: Correlation Heatmap

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_pickle('data/processed/df_sin_cuadrantes.pkl')

# Select key variables
vars_of_interest = [
    'mean_species_richness', 'forest_cover_pct',
    'UAI_total', 'IVM',
    'incidence_dengue', 'incidence_diarrhea'
]

# Calculate correlations
corr_matrix = df[vars_of_interest].corr()

# Plot
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0)
plt.title('Biodiversity-Health-Governance Correlations')
plt.tight_layout()
plt.savefig('my_correlation_heatmap.png', dpi=300)
```

### Example 2: Quadrant Visualization

```python
import matplotlib.pyplot as plt

# Scatter plot with quadrants
fig, ax = plt.subplots(figsize=(10, 8))

colors = {
    'Q1_Modelo': 'green',
    'Q2_Conservar': 'blue',
    'Q3_Vulnerable': 'red',
    'Q4_Desarrollo': 'orange'
}

for quadrant, color in colors.items():
    mask = df['cuadrante'] == quadrant
    ax.scatter(
        df.loc[mask, 'UAI_total'],
        df.loc[mask, 'IVM'],
        c=color, label=quadrant, alpha=0.6
    )

ax.axhline(df['IVM'].median(), color='gray', linestyle='--')
ax.axvline(df['UAI_total'].median(), color='gray', linestyle='--')
ax.set_xlabel('UAI (Governance)')
ax.set_ylabel('IVM (Vulnerability)')
ax.legend()
plt.savefig('quadrant_classification.png', dpi=300)
```

### Example 3: Priority Municipality List

```python
# Identify Q3 municipalities with highest vulnerability
q3_priority = df[df['cuadrante'] == 'Q3_Vulnerable'].nlargest(20, 'IVM')

print("Top 20 Priority Municipalities (Q3 - High Vulnerability, Low Governance):")
print(q3_priority[['nome_municipio', 'UAI_total', 'IVM']].to_string())
```

---

## Extending the Analysis

### Add New Variables

1. Ensure new variables are at municipality level with `cod_ibge` key
2. Merge with existing dataset:

```python
new_data = pd.read_csv('my_new_variables.csv')
df_extended = df.merge(new_data, on='cod_ibge', how='left')
```

3. Document new variables in your fork's `data/metadata.json`

### Modify IVM Weights

```python
# Custom weighting scheme emphasizing climate
custom_weights = {
    'poverty': 0.20,
    'service': 0.20,
    'housing': 0.20,
    'climate': 0.40  # Increased weight
}

df['IVM_climate_weighted'] = calculate_ivm(df, config={'weights': custom_weights})
```

### Add Time Series

For longitudinal analysis, structure data as:

```python
# Panel data format
df_panel = df.assign(year=2019)  # Add year column
# Append historical years...
```

---

## Citation Requirements

When reusing this data or methodology, please cite:

```bibtex
@dataset{gonzalez_chaves_2026,
  author = {González Chaves, Adrian David},
  title = {Biodiversity, Health and Universal Access in São Paulo},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/adgch86/saopaulo-biodiversity-health},
  version = {1.0.0}
}
```

Or in text:
> González Chaves, A.D. (2026). Biodiversity, Health and Universal Access in São Paulo [Dataset]. GitHub. https://github.com/adgch86/saopaulo-biodiversity-health

---

## Common Issues

### Issue: Missing Health Data

Only 187 of 645 municipalities have health data. For full-coverage analysis:

```python
# Use only environmental/UAI variables (n=645)
df_full = df[['cod_ibge', 'mean_species_richness', 'UAI_total', 'IVM']].dropna()

# Or health-focused analysis (n=187)
df_health = df.dropna(subset=['incidence_dengue'])
```

### Issue: Pickle Version Mismatch

If pickle files don't load:

```bash
# Recreate from CSV
python scripts/create_pickles_from_csv.py
```

### Issue: Geographic Data

Shapefiles not included due to size. Obtain from IBGE:
```
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/
```

---

## Support

- **GitHub Issues**: https://github.com/adgch86/saopaulo-biodiversity-health/issues
- **Email**: adgch86@gmail.com
- **ORCID**: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)

---

## License

This work is licensed under the MIT License. You are free to:
- Use for any purpose (academic, commercial, personal)
- Modify and adapt
- Distribute

With the requirement to:
- Include the original copyright notice
- Cite appropriately in publications
