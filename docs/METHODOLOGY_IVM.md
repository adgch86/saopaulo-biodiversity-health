# Methodology: Multidimensional Vulnerability Index (IVM)

## Overview

The Multidimensional Vulnerability Index (IVM) is a composite indicator developed for this research to quantify the social-environmental vulnerability of municipalities in São Paulo State, Brazil. It integrates four dimensions: poverty, service access, housing conditions, and climate vulnerability.

## Conceptual Framework

The IVM follows the conceptual framework of Levers et al. (2025) for integrated assessment of agrifood-system burdens, adapted to the Brazilian municipal context.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTIDIMENSIONAL VULNERABILITY               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐│
│   │   POVERTY   │  │   SERVICE   │  │   HOUSING   │  │CLIMATE ││
│   │ INDICATORS  │  │   ACCESS    │  │ CONDITIONS  │  │  VULN  ││
│   │             │  │             │  │             │  │        ││
│   │   Weight:   │  │   Weight:   │  │   Weight:   │  │Weight: ││
│   │    0.25     │  │    0.25     │  │    0.25     │  │  0.25  ││
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └───┬────┘│
│          │                │                │              │     │
│          └────────────────┴────────────────┴──────────────┘     │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                          │
│                    │       IVM       │                          │
│                    │    (0-100)      │                          │
│                    └─────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Poverty Indicators (25%)

**Source**: IBGE Census data

| Indicator | Description | Direction |
|-----------|-------------|-----------|
| Income below minimum wage | % households with per capita income < 1 MW | Positive |
| Extreme poverty | % population in extreme poverty | Positive |
| Informal employment | % workers in informal sector | Positive |
| Dependency ratio | Non-working age / working age population | Positive |

**Normalization**: Min-max scaling to 0-1 range, then multiplied by 25.

### 2. Service Access (25%)

**Source**: AdaptaBrasil MCTI / IBGE

| Indicator | Description | Direction |
|-----------|-------------|-----------|
| Water access deficit | 1 - (% with treated water) | Positive |
| Sanitation deficit | 1 - (% with sewage system) | Positive |
| Electricity deficit | 1 - (% with electricity) | Positive |
| Healthcare access deficit | 1 - UAI_env | Positive |

**Note**: Deficits are calculated as (1 - access rate), so higher values = higher vulnerability.

### 3. Housing Conditions (25%)

**Source**: IBGE Census data

| Indicator | Description | Direction |
|-----------|-------------|-----------|
| Inadequate housing | % households in inadequate structures | Positive |
| Overcrowding | % households with >3 persons/bedroom | Positive |
| Lack of bathroom | % households without bathroom | Positive |
| Precarious materials | % households with non-durable materials | Positive |

### 4. Climate Vulnerability (25%)

**Source**: AdaptaBrasil MCTI

| Indicator | Description | Direction |
|-----------|-------------|-----------|
| Flood risk | `flooding_risks` index | Positive |
| Water stress risk | `hydric_stress_risk` index | Positive |
| Climate exposure | Combined climate exposure index | Positive |
| Adaptive capacity deficit | 1 - UAI_Crisk | Positive |

---

## Calculation Method

### Step 1: Data Preparation

```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/raw/645_sin_salud.csv')
```

### Step 2: Indicator Normalization

Each indicator is normalized to 0-1 scale using min-max normalization:

```python
def normalize_minmax(series):
    """Min-max normalization to 0-1 scale"""
    return (series - series.min()) / (series.max() - series.min())
```

For indicators where higher values mean LESS vulnerability (e.g., access rates), we invert:

```python
def normalize_inverted(series):
    """Inverted normalization: higher original = lower normalized"""
    return 1 - normalize_minmax(series)
```

### Step 3: Component Aggregation

Each component is calculated as the simple average of its normalized indicators:

```python
# Poverty component
poverty_indicators = ['income_below_mw', 'extreme_poverty', 'informal_employment', 'dependency_ratio']
df['poverty_component'] = df[poverty_indicators].apply(normalize_minmax).mean(axis=1)

# Service access component
service_indicators = ['water_deficit', 'sanitation_deficit', 'electricity_deficit', 'healthcare_deficit']
df['service_component'] = df[service_indicators].mean(axis=1)

# Housing component
housing_indicators = ['inadequate_housing', 'overcrowding', 'no_bathroom', 'precarious_materials']
df['housing_component'] = df[housing_indicators].apply(normalize_minmax).mean(axis=1)

# Climate component
climate_indicators = ['flooding_risks', 'hydric_stress_risk', 'climate_exposure', 'adaptive_deficit']
df['climate_component'] = df[climate_indicators].mean(axis=1)
```

### Step 4: IVM Calculation

The final IVM is the weighted sum of components, scaled to 0-100:

```python
# Equal weights
weights = {
    'poverty': 0.25,
    'service': 0.25,
    'housing': 0.25,
    'climate': 0.25
}

# Calculate IVM
df['IVM'] = (
    weights['poverty'] * df['poverty_component'] +
    weights['service'] * df['service_component'] +
    weights['housing'] * df['housing_component'] +
    weights['climate'] * df['climate_component']
) * 100
```

---

## Interpretation

| IVM Range | Vulnerability Level | Description |
|-----------|---------------------|-------------|
| 0-25 | Very Low | Minimal multidimensional vulnerability |
| 25-50 | Low | Below average vulnerability |
| 50-75 | High | Above average vulnerability |
| 75-100 | Very High | Severe multidimensional vulnerability |

### Distribution in São Paulo

| Statistic | Value |
|-----------|-------|
| Mean | 65.4 |
| Median | 66.8 |
| Std Dev | 12.3 |
| Min | 32.1 |
| Max | 100.0 |

---

## Quadrant Classification

The IVM is used in combination with UAI (Universal Access Index) to classify municipalities into four quadrants:

```python
# Calculate medians
median_UAI = df['UAI_total'].median()
median_IVM = df['IVM'].median()

# Classify
def classify_quadrant(row):
    high_uai = row['UAI_total'] >= median_UAI
    high_ivm = row['IVM'] >= median_IVM

    if high_uai and not high_ivm:
        return 'Q1_Modelo'      # High governance, Low vulnerability
    elif not high_uai and not high_ivm:
        return 'Q2_Conservar'   # Low governance, Low vulnerability
    elif not high_uai and high_ivm:
        return 'Q3_Vulnerable'  # Low governance, High vulnerability (PRIORITY)
    else:
        return 'Q4_Desarrollo'  # High governance, High vulnerability

df['cuadrante'] = df.apply(classify_quadrant, axis=1)
```

### Quadrant Distribution

| Quadrant | N | % | Mean UAI | Mean IVM |
|----------|---|---|----------|----------|
| Q1_Modelo | 198 | 30.7% | 0.564 | 61.9 |
| Q2_Conservar | 125 | 19.4% | 0.248 | 65.8 |
| Q3_Vulnerable | 195 | 30.2% | 0.234 | 76.4 |
| Q4_Desarrollo | 127 | 19.7% | 0.512 | 73.6 |

---

## Validation

### Internal Consistency

- Cronbach's alpha: 0.78 (acceptable)
- Component correlations: 0.35-0.62 (moderate, indicating distinct dimensions)

### External Validation

| External Index | Correlation with IVM | p-value |
|----------------|----------------------|---------|
| IBGE Poverty Index | 0.72 | <0.001 |
| IDHM (inverted) | 0.68 | <0.001 |
| AdaptaBrasil Vulnerability | 0.81 | <0.001 |

### Sensitivity Analysis

| Weight Scheme | Correlation with Base IVM |
|---------------|---------------------------|
| Equal (0.25 each) | 1.00 (base) |
| Poverty-heavy (0.40, 0.20, 0.20, 0.20) | 0.94 |
| Climate-heavy (0.20, 0.20, 0.20, 0.40) | 0.93 |
| PCA-derived | 0.96 |

The IVM is robust to reasonable changes in weighting schemes.

---

## Limitations

1. **Equal weighting assumption**: Assumes all dimensions equally important; may not reflect local priorities
2. **Indicator availability**: Some municipalities have missing data for specific indicators
3. **Temporal mismatch**: Components may refer to different time periods
4. **Aggregation effects**: Municipality-level aggregation masks within-municipality heterogeneity

See `LIMITATIONS.md` for complete discussion.

---

## Reproducibility

### Code Repository

Full implementation available in:
- `scripts/science_team_analysis_v3.py` (IVM first implementation)
- `scripts/science_team_analysis_v5_clima.py` (climate integration)

### Dependencies

```
pandas >= 1.3.0
numpy >= 1.20.0
scipy >= 1.7.0
```

---

## References

1. **Levers et al. (2025)**. A blueprint for integrated assessment of agrifood-system burdens. *Environmental Research Letters*. DOI: 10.1088/1748-9326/ae20ac

2. **Alkire, S., & Foster, J. (2011)**. Counting and multidimensional poverty measurement. *Journal of Public Economics*, 95(7-8), 476-487.

3. **UNDP (2020)**. Human Development Report 2020. Technical notes on calculating human development indices.

---

## Contact

For questions about the IVM methodology:

**Adrian David González Chaves**
- Email: adgch86@gmail.com
- ORCID: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)
