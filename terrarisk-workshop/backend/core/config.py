"""
TerraRisk Workshop - Configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MAPS_DIR = DATA_DIR / "maps"
BIVARIATE_DIR = MAPS_DIR / "bivariate"

# Ensure directories exist
MAPS_DIR.mkdir(parents=True, exist_ok=True)
BIVARIATE_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "groups.db"

# Workshop settings
INITIAL_CREDITS = 10
MAX_ACTIVE_LAYERS = 2

# Layer configuration
# Cost tiers:
#   1 credit  - Easily accessible data
#   2 credits - Moderate processing
#   3 credits - Complex data
#   4 credits - Most complex (composite indices)
LAYERS_CONFIG = [
    # === GOVERNANCE (2 credits each) ===
    {
        "id": "governance_general",
        "name": "Governance Index",
        "category": "governance",
        "description": "UAI general index of institutional capacity",
        "cost": 2,
        "variable": "gobernanza_100",
        "imageFile": "02_Governance_UAI_General.png",
        "colorScale": "positive",
    },
    {
        "id": "governance_climatic",
        "name": "Climate Risk Governance Index",
        "category": "governance",
        "description": "UAI index of adaptive capacity to climate change",
        "cost": 2,
        "variable": "UAI_Crisk",
        "imageFile": "01_Governance_UAI_Climatic_Risk.png",
        "colorScale": "positive",
    },
    # === BIODIVERSITY ===
    {
        "id": "forest_cover",
        "name": "Forest Cover",
        "category": "biodiversity",
        "description": "Percentage of remaining natural vegetation cover",
        "cost": 1,
        "variable": "forest_cover",
        "imageFile": "04_Natural_Habitat_Vegetation.png",
        "colorScale": "positive",
    },
    {
        "id": "biodiversity",
        "name": "Mean Species Richness",
        "category": "biodiversity",
        "description": "Average species richness index across taxonomic groups",
        "cost": 2,
        "variable": "mean_species_richness",
        "imageFile": "03_Biodiversity_Species_Richness.png",
        "colorScale": "positive",
    },
    {
        "id": "pollination",
        "name": "Pollination Deficit",
        "category": "biodiversity",
        "description": "Agricultural pollination service deficit",
        "cost": 2,
        "variable": "pollination_deficit",
        "imageFile": "05_Pollination_Deficit.png",
        "colorScale": "negative",
    },
    {
        "id": "composite_biodiversity",
        "name": "Composite Biodiversity Index",
        "category": "biodiversity",
        "description": "Composite index combining multiple biodiversity metrics",
        "cost": 4,
        "variable": "idx_biodiv",
        "imageFile": "composite_biodiversity.png",
        "colorScale": "positive",
    },
    # === CLIMATE ===
    {
        "id": "flooding",
        "name": "Flooding Risks",
        "category": "climate",
        "description": "Flood risk index based on exposure and hazard",
        "cost": 1,
        "variable": "flooding_risk",
        "imageFile": "06_Flooding_Risk.png",
        "colorScale": "negative",
    },
    {
        "id": "fire_risk",
        "name": "Fire Risk Index",
        "category": "climate",
        "description": "Wildfire risk index based on recurrence and intensity",
        "cost": 3,
        "variable": "fire_risk_index",
        "imageFile": "07_Fire_Risk_Index.png",
        "colorScale": "negative",
    },
    {
        "id": "hydric_stress",
        "name": "Hydric Stress Risk",
        "category": "climate",
        "description": "Water stress risk index from drought exposure",
        "cost": 3,
        "variable": "hydric_stress_r",
        "imageFile": "08_Hydric_Stress_Risk.png",
        "colorScale": "negative",
    },
    {
        "id": "composite_climate",
        "name": "Climate Risk Composite Index",
        "category": "climate",
        "description": "Composite index combining flooding, fire, and hydric stress risks",
        "cost": 4,
        "variable": "idx_clima",
        "imageFile": "composite_climate.png",
        "colorScale": "negative",
    },
    # === HEALTH ===
    {
        "id": "dengue",
        "name": "Incidence Dengue",
        "category": "health",
        "description": "Dengue incidence rate per 100,000 inhabitants",
        "cost": 3,
        "variable": "dengue",
        "imageFile": "09_Zoonotic_Dengue_Incidence.png",
        "colorScale": "negative",
    },
    {
        "id": "diarrhea",
        "name": "Incidence Diarrhea",
        "category": "health",
        "description": "Hospitalization rate for diarrheal diseases",
        "cost": 3,
        "variable": "incidence_diarr",
        "imageFile": "10_Water_Pollution_Diarrhea.png",
        "colorScale": "negative",
    },
    {
        "id": "cv_mortality",
        "name": "Cardiovascular Health Death",
        "category": "health",
        "description": "Cardiovascular disease mortality rate",
        "cost": 3,
        "variable": "death_circ_mean",
        "imageFile": "11_Heat_Fire_CV_Mortality.png",
        "colorScale": "negative",
    },
    {
        "id": "resp_hosp",
        "name": "Respiratory Hospitalization",
        "category": "health",
        "description": "Respiratory disease hospitalization rate",
        "cost": 3,
        "variable": "hosp_resp_mean",
        "imageFile": "12_Heat_Fire_Resp_Hospitalization.png",
        "colorScale": "negative",
    },
    {
        "id": "composite_health",
        "name": "Composite Health Index",
        "category": "health",
        "description": "Composite disease burden index combining multiple health indicators",
        "cost": 4,
        "variable": "idx_carga_enfermedad",
        "imageFile": "composite_health.png",
        "colorScale": "negative",
    },
    # === SOCIAL ===
    {
        "id": "population",
        "name": "Population",
        "category": "social",
        "description": "Total municipal population",
        "cost": 1,
        "variable": "population",
        "imageFile": "population.png",
        "colorScale": "neutral",
    },
    {
        "id": "rural",
        "name": "Rural Percentage",
        "category": "social",
        "description": "Percentage of population in rural areas",
        "cost": 1,
        "variable": "pct_rural",
        "imageFile": "15_Rural_Population.png",
        "colorScale": "neutral",
    },
    {
        "id": "urban",
        "name": "Urban Percentage",
        "category": "social",
        "description": "Percentage of population in urban areas",
        "cost": 1,
        "variable": "pct_urbana",
        "imageFile": "urban_percentage.png",
        "colorScale": "neutral",
    },
    {
        "id": "poverty",
        "name": "Percentage of Population in Poverty",
        "category": "social",
        "description": "Percentage of population living in poverty",
        "cost": 2,
        "variable": "pct_pobreza",
        "imageFile": "13_Poverty_Percentage.png",
        "colorScale": "negative",
    },
    {
        "id": "vulnerability",
        "name": "Vulnerability Unified Index",
        "category": "social",
        "description": "Composite socioeconomic vulnerability index",
        "cost": 2,
        "variable": "vulnerabilidad",
        "imageFile": "14_Vulnerability_Index.png",
        "colorScale": "negative",
    },
]
