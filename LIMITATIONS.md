# Limitations and Potential Biases

This document transparently describes the limitations, assumptions, and potential biases in this research project. Understanding these limitations is essential for appropriate interpretation and use of the findings.

## Data Limitations

### 1. Temporal Mismatches

| Dataset | Temporal Coverage | Issue |
|---------|-------------------|-------|
| Health data (DATASUS) | 2010-2019 | 10-year aggregation |
| UAI indices | 2020-2024 | More recent |
| Biodiversity metrics | ~2015 | Point estimate |
| Census data | 2010, 2022 | Decennial gaps |

**Impact**: Cross-sectional analysis assumes temporal stability of relationships. Changes in land use, climate, or governance between data collection periods may affect correlations.

**Mitigation**: Focus on persistent patterns; sensitivity analyses with different temporal windows.

### 2. Geographic Aggregation

- **Unit of analysis**: Municipality (n=645)
- **Issue**: Ecological fallacy - relationships at municipal level may not hold at individual or neighborhood level
- **Average municipality area**: ~380 km²
- **Population range**: 823 (Borá) to 12.3 million (São Paulo city)

**Impact**: Within-municipality heterogeneity is masked. Urban vs. rural differences not captured.

**Mitigation**: Stratified analyses by municipality size; acknowledgment of scale limitations.

### 3. Missing Health Data

| Dataset | Municipalities | Coverage |
|---------|---------------|----------|
| Environmental/UAI | 645 | 100% |
| Epidemiological | 187 | 29% |

**Impact**: Health correlations based on subset that may not be representative. Municipalities with health data may have better health surveillance systems.

**Selection bias**: Municipalities reporting health data are likely more urbanized with better infrastructure.

**Mitigation**: Comparison of environmental characteristics between municipalities with and without health data.

### 4. Reporting Biases

**Underreporting expected for**:
- Malaria (low incidence, asymptomatic cases)
- Diarrheal diseases (mild cases untreated)
- Leptospirosis (misdiagnosis as dengue)

**Overreporting possible for**:
- Dengue during epidemic years (media attention)

**Impact**: Disease incidence rates are underestimates; relative patterns more reliable than absolute numbers.

---

## Methodological Limitations

### 1. Correlation vs. Causation

All relationships reported are **correlational**. This study cannot establish:
- Whether biodiversity directly protects against disease (dilution effect) or is confounded by other factors
- Direction of causality for governance-vulnerability relationships
- Temporal precedence of exposures and outcomes

**Confounders not fully controlled**:
- Socioeconomic status at household level
- Healthcare access and quality
- Individual behaviors
- Microclimate variations

### 2. Index Construction

**Multidimensional Vulnerability Index (IVM)**:
- Equal weighting of components (25% each) is arbitrary
- Sensitivity to weight changes not fully explored
- Normalization method affects rankings

**UAI (Universal Access Index)**:
- Developed for national policy purposes
- May not capture local governance nuances
- Composite indices mask component variation

### 3. Statistical Assumptions

| Assumption | Violation Potential | Impact |
|------------|---------------------|--------|
| Linear relationships | Possible thresholds exist | Underestimation of effects |
| Normality | Some variables skewed | Pearson r may be biased |
| Independence | Spatial autocorrelation | Inflated significance |
| Homoscedasticity | Variable variance | Standard errors affected |

**Mitigation**: Spearman correlations used alongside Pearson; spatial analyses planned.

---

## Conceptual Limitations

### 1. Dilution Effect Complexity

The dilution effect theory has important caveats:
- Works for some disease-host systems, not universally
- Depends on specific community composition
- May be offset by habitat fragmentation effects
- Biodiversity metrics (species richness) are crude proxies

**Our finding**: Negative correlation between biodiversity and disease is consistent with dilution effect but does not prove mechanism.

### 2. Paradox Interpretation

**Conservation-Poverty Paradox**:
- Correlation (r=+0.23) between biodiversity and vulnerability
- Could reflect: (a) development pressure reducing biodiversity in wealthy areas, (b) land use patterns, (c) historical settlement patterns

**Alternative explanations**: Agricultural expansion, urbanization patterns, economic development history.

### 3. Policy Applicability

**Limitations for policy translation**:
- Municipal averages may not identify priority neighborhoods
- Intervention effects may differ from observed correlations
- Political and economic feasibility not assessed
- Implementation capacity varies widely

---

## Data Quality Issues

### Known Quality Concerns

| Variable | Quality Issue | Severity |
|----------|---------------|----------|
| `mean_species_richness` | Model-based estimate | Medium |
| `UAI_*` | Composite construction varies | Low |
| `incidence_*` | Underreporting | High |
| `population` | Intercensal estimates | Low |

### Geographic Matching

- 2% of records required manual municipality matching
- Boundary changes between census years
- Metropolitan region definitions inconsistent

---

## Scope Limitations

### What This Study Does NOT Address

1. **Causal mechanisms**: No experimental or quasi-experimental design
2. **Individual risk**: Only aggregate municipal patterns
3. **Temporal dynamics**: Cross-sectional snapshot, not trends
4. **Intervention effectiveness**: Observational associations only
5. **Economic costs**: No cost-benefit analysis
6. **Climate projections**: Current state, not future scenarios

### Generalizability

**Findings may not generalize to**:
- Other Brazilian states (different biomes, governance)
- Other countries (different health systems)
- Different time periods (changing climate, development)
- Sub-municipal scales (neighborhoods, households)

**São Paulo specifics**:
- Largest economy in Brazil
- Relatively good health infrastructure
- Atlantic Forest biome
- Advanced statistical capacity

---

## Recommendations for Users

### Do
- Consider correlations as hypothesis-generating
- Account for uncertainty in rankings
- Use quadrant classification as general guidance
- Combine with local knowledge for interventions
- Cite limitations when presenting findings

### Don't
- Interpret correlations as causal
- Apply findings to individual households
- Use exact IVM scores as definitive rankings
- Ignore local context in policy application
- Extrapolate to other regions without validation

---

## Future Improvements Needed

1. **Longitudinal data**: Track changes over time
2. **Finer spatial resolution**: Neighborhood-level analysis
3. **Mechanistic studies**: Test dilution effect directly
4. **Intervention evaluation**: Natural experiments
5. **Expanded geographic scope**: Include other states
6. **Community validation**: Ground-truth with local stakeholders

---

## Contact for Clarifications

For questions about limitations or methodology:

**Adrian David González Chaves**
- Email: adgch86@gmail.com
- ORCID: [0000-0002-5233-8957](https://orcid.org/0000-0002-5233-8957)
