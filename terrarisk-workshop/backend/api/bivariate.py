"""
TerraRisk Workshop - Bivariate Maps API
Generates bivariate data for frontend map coloring
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import LAYERS_CONFIG, DATA_DIR

router = APIRouter()


class BivariateRequest(BaseModel):
    layer1Id: str
    layer2Id: str


# Variable mapping: layer_id -> CSV column
BIVARIATE_VARIABLE_MAP = {
    'governance_general': 'idx_gobernanza_100',
    'governance_climatic': 'UAI_Crisk',
    'forest_cover': 'forest_cover',
    'biodiversity': 'mean_species_richness',
    'pollination': 'pol_deficit',
    'composite_biodiversity': 'idx_biodiv',
    'flooding': 'flooding_risks',
    'fire_risk': 'fire_risk_index',
    'hydric_stress': 'hydric_stress_risk',
    'composite_climate': 'idx_clima',
    'dengue': 'incidence_mean_dengue',
    'diarrhea': 'incidence_diarrhea_mean',
    'cv_mortality': 'health_death_circ_mean',
    'resp_hosp': 'health_hosp_resp_mean',
    'composite_health': 'idx_carga_enfermedad',
    'population': 'population',
    'rural': 'pct_rural',
    'urban': 'pct_urbana',
    'poverty': 'pct_pobreza',
    'vulnerability': 'idx_vulnerabilidad',
}

_cached_df = None


def _load_data():
    global _cached_df
    if _cached_df is None:
        csv_path = DATA_DIR / "municipios.csv"
        if not csv_path.exists():
            raise FileNotFoundError("Municipality data not found")
        _cached_df = pd.read_csv(csv_path)
    return _cached_df


def _compute_terciles(series: pd.Series) -> tuple[float, float]:
    """Compute tercile breakpoints (33rd and 67th percentiles)"""
    valid = series.dropna()
    if len(valid) == 0:
        return (0.0, 0.0)
    t1 = float(valid.quantile(0.33))
    t2 = float(valid.quantile(0.67))
    return (t1, t2)


@router.post("")
async def generate_bivariate(request: BivariateRequest):
    """
    Compute bivariate map data for two layers.
    Returns per-municipality values and tercile breakpoints for both variables.
    The frontend colors the map using a 3x3 bivariate color matrix.
    """
    # Validate layers exist
    layer1 = next((l for l in LAYERS_CONFIG if l["id"] == request.layer1Id), None)
    layer2 = next((l for l in LAYERS_CONFIG if l["id"] == request.layer2Id), None)

    if not layer1 or not layer2:
        raise HTTPException(status_code=404, detail="Layer not found")

    if request.layer1Id == request.layer2Id:
        raise HTTPException(status_code=400, detail="Select two different layers")

    # Get CSV column names
    col1 = BIVARIATE_VARIABLE_MAP.get(request.layer1Id)
    col2 = BIVARIATE_VARIABLE_MAP.get(request.layer2Id)

    if not col1 or not col2:
        raise HTTPException(status_code=400, detail="Variable mapping not found")

    try:
        df = _load_data()

        # Find code column
        code_col = next(
            (c for c in ['cod_ibge', 'CD_MUN', 'codigo'] if c in df.columns),
            None
        )
        if not code_col:
            raise HTTPException(status_code=500, detail="Code column not found")

        if col1 not in df.columns or col2 not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Column not found: {col1 if col1 not in df.columns else col2}"
            )

        # Convert to numeric
        s1 = pd.to_numeric(df[col1], errors='coerce')
        s2 = pd.to_numeric(df[col2], errors='coerce')

        # Compute terciles across ALL municipalities (for proper classification)
        terciles1 = _compute_terciles(s1)
        terciles2 = _compute_terciles(s2)

        # Build per-municipality values
        values = {}
        for _, row in df.iterrows():
            code = str(row[code_col])
            v1 = None if pd.isna(row[col1]) else float(s1.loc[row.name])
            v2 = None if pd.isna(row[col2]) else float(s2.loc[row.name])
            values[code] = [v1, v2]

        return {
            "variable1": col1,
            "variable2": col2,
            "layer1Name": layer1["name"],
            "layer2Name": layer2["name"],
            "terciles1": list(terciles1),
            "terciles2": list(terciles2),
            "values": values,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error computing bivariate: {str(e)}"
        )


@router.get("/available")
async def get_available_bivariates():
    """All combinations are now generated dynamically"""
    return {"message": "All bivariate combinations available dynamically"}
