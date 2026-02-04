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

# Free layers (always available)
FREE_LAYERS = ["governance_general", "vulnerability"]

# Layer costs
DEFAULT_LAYER_COST = 1

# Layer configuration
LAYERS_CONFIG = [
    {
        "id": "governance_climatic",
        "name": "Gobernanza Riesgo Climatico",
        "category": "governance",
        "description": "Indice UAI de capacidad adaptativa frente al cambio climatico",
        "cost": 1,
        "variable": "UAI_Crisk",
        "imageFile": "01_Governance_UAI_Climatic_Risk.png",
        "colorScale": "positive",
        "isFree": False
    },
    {
        "id": "governance_general",
        "name": "Gobernanza General",
        "category": "governance",
        "description": "Indice UAI general de capacidad institucional",
        "cost": 0,
        "variable": "gobernanza_100",
        "imageFile": "02_Governance_UAI_General.png",
        "colorScale": "positive",
        "isFree": True
    },
    {
        "id": "biodiversity",
        "name": "Riqueza de Especies",
        "category": "biodiversity",
        "description": "Indice de biodiversidad basado en riqueza de especies",
        "cost": 1,
        "variable": "biodiversity",
        "imageFile": "03_Biodiversity_Species_Richness.png",
        "colorScale": "positive",
        "isFree": False
    },
    {
        "id": "natural_habitat",
        "name": "Habitat Natural",
        "category": "biodiversity",
        "description": "Porcentaje de vegetacion natural remanente",
        "cost": 1,
        "variable": "natural_habitat",
        "imageFile": "04_Natural_Habitat_Vegetation.png",
        "colorScale": "positive",
        "isFree": False
    },
    {
        "id": "pollination",
        "name": "Deficit de Polinizacion",
        "category": "biodiversity",
        "description": "Deficit de servicios de polinizacion agricola",
        "cost": 1,
        "variable": "pollination_deficit",
        "imageFile": "05_Pollination_Deficit.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "flooding",
        "name": "Riesgo de Inundacion",
        "category": "climate",
        "description": "Indice de riesgo de inundaciones",
        "cost": 1,
        "variable": "flooding_risk",
        "imageFile": "06_Flooding_Risk.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "fire_risk",
        "name": "Riesgo de Incendio",
        "category": "climate",
        "description": "Indice de riesgo de incendios forestales",
        "cost": 1,
        "variable": "fire_risk_index",
        "imageFile": "07_Fire_Risk_Index.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "hydric_stress",
        "name": "Estres Hidrico",
        "category": "climate",
        "description": "Indice de estres hidrico por sequia",
        "cost": 1,
        "variable": "hydric_stress_r",
        "imageFile": "08_Hydric_Stress_Risk.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "dengue",
        "name": "Incidencia de Dengue",
        "category": "health",
        "description": "Tasa de incidencia de dengue por 100,000 hab",
        "cost": 1,
        "variable": "dengue",
        "imageFile": "09_Zoonotic_Dengue_Incidence.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "diarrhea",
        "name": "Incidencia de Diarrea",
        "category": "health",
        "description": "Tasa de hospitalizacion por enfermedades diarreicas",
        "cost": 1,
        "variable": "incidence_diarr",
        "imageFile": "10_Water_Pollution_Diarrhea.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "cv_mortality",
        "name": "Mortalidad Cardiovascular",
        "category": "health",
        "description": "Tasa de mortalidad por enfermedades cardiovasculares",
        "cost": 1,
        "variable": "death_circ_mean",
        "imageFile": "11_Heat_Fire_CV_Mortality.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "resp_hosp",
        "name": "Hospitalizacion Respiratoria",
        "category": "health",
        "description": "Tasa de hospitalizacion por enfermedades respiratorias",
        "cost": 1,
        "variable": "hosp_resp_mean",
        "imageFile": "12_Heat_Fire_Resp_Hospitalization.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "poverty",
        "name": "Porcentaje de Pobreza",
        "category": "social",
        "description": "Porcentaje de poblacion en situacion de pobreza",
        "cost": 1,
        "variable": "pct_pobreza",
        "imageFile": "13_Poverty_Percentage.png",
        "colorScale": "negative",
        "isFree": False
    },
    {
        "id": "vulnerability",
        "name": "Indice de Vulnerabilidad",
        "category": "social",
        "description": "Indice compuesto de vulnerabilidad socioeconomica",
        "cost": 0,
        "variable": "vulnerabilidad",
        "imageFile": "14_Vulnerability_Index.png",
        "colorScale": "negative",
        "isFree": True
    },
    {
        "id": "rural",
        "name": "Poblacion Rural",
        "category": "social",
        "description": "Porcentaje de poblacion en areas rurales",
        "cost": 1,
        "variable": "pct_rural",
        "imageFile": "15_Rural_Population.png",
        "colorScale": "neutral",
        "isFree": False
    },
    {
        "id": "leishmaniasis",
        "name": "Incidencia de Leishmaniasis",
        "category": "health",
        "description": "Tasa de incidencia de leishmaniasis visceral",
        "cost": 1,
        "variable": "leishmaniose",
        "imageFile": "16_Zoonotic_Leishmaniasis_Incidence.png",
        "colorScale": "negative",
        "isFree": False
    },
]
