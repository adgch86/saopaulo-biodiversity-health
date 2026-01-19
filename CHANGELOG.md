# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-19

### Added
- Initial public release of the São Paulo Biodiversity-Health-Governance dataset
- Complete analysis pipeline for 645 municipalities
- Multidimensional Vulnerability Index (IVM) methodology
- Quadrant classification system (Q1-Q4)
- Correlation analysis between biodiversity, health, and governance variables
- Interactive dashboard mockups for February workshop
- Policy recommendations based on findings

### Data
- 645 municipalities with environmental and UAI data (`645_sin_salud.csv`)
- 187 municipalities with epidemiological data (`187_con_salud.csv`)
- Processed datasets in pickle format
- Geographic data (shapefiles) for São Paulo municipalities

### Documentation
- Technical reports (V3, V5)
- Policy brief for PEAC integration
- Methodology documentation for IVM
- FAIR compliance documentation

### Analysis Scripts
- `science_team_analysis.py` - Initial analysis (v1)
- `science_team_analysis_v2.py` - Statistical improvements (v2)
- `science_team_analysis_v3.py` - IVM implementation (v3)
- `science_team_analysis_v4.py` - Refinements (v4)
- `science_team_analysis_v5_clima.py` - Climate integration (v5)
- `create_branco_weiss_proposal.py` - Proposal generator

### Key Findings
- Local dilution effect confirmed (biodiversity reduces disease transmission)
- Conservation-poverty paradox documented (r = +0.23)
- Governance gap identified (UAI vs IVM: r = -0.293)
- Q3 municipalities identified as priority for intervention

## [Unreleased]

### Planned
- Integration of extreme climate variables (CDD, TX35, RX5, FD)
- Forest Landscape Integrity Index (FLII) analysis
- Multi-year time series analysis
- National scaling (Maranhão pilot)

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-19 | Initial FAIR-compliant public release |
