"""
TerraRisk Workshop - Municipalities API
"""

import os
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from core.config import DATA_DIR

router = APIRouter()

# Load municipality data on startup
_municipalities_df = None
_municipalities_list = None


def get_municipalities_df():
    """Lazy load municipalities dataframe"""
    global _municipalities_df

    if _municipalities_df is None:
        csv_path = DATA_DIR / "municipios.csv"
        if not csv_path.exists():
            # Try alternative paths
            alt_paths = [
                DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v8.csv",
                DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v7.csv",
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    csv_path = alt_path
                    break

        if csv_path.exists():
            _municipalities_df = pd.read_csv(csv_path)
            # Ensure code is string
            if 'cod_ibge' in _municipalities_df.columns:
                _municipalities_df['cod_ibge'] = _municipalities_df['cod_ibge'].astype(str)
        else:
            _municipalities_df = pd.DataFrame()

    return _municipalities_df


def get_municipalities_list():
    """Get simplified list of municipalities"""
    global _municipalities_list

    if _municipalities_list is None:
        df = get_municipalities_df()

        if df.empty:
            _municipalities_list = []
        else:
            # Find code and name columns
            code_col = next((c for c in ['cod_ibge', 'CD_MUN', 'codigo'] if c in df.columns), None)
            name_col = next((c for c in ['Municipio', 'nome', 'NM_MUN', 'municipio', 'name'] if c in df.columns), None)
            region_col = next((c for c in ['nome_mesorregiao', 'regiao', 'REGIAO', 'region'] if c in df.columns), None)

            _municipalities_list = []
            for _, row in df.iterrows():
                item = {
                    "code": str(row[code_col]) if code_col else "",
                    "name": row[name_col] if name_col else "Unknown",
                }
                if region_col and region_col in df.columns:
                    item["region"] = row[region_col]
                _municipalities_list.append(item)

    return _municipalities_list


@router.get("")
async def get_all_municipalities():
    """Get list of all municipalities (minimal data)"""
    return get_municipalities_list()


@router.get("/search")
async def search_municipalities(q: str = Query(..., min_length=2)):
    """Search municipalities by name"""
    municipalities = get_municipalities_list()
    query = q.lower()

    results = [
        m for m in municipalities
        if query in m["name"].lower()
    ]

    return results[:20]  # Limit results


@router.get("/choropleth/{variable}")
async def get_choropleth_data(variable: str):
    """Get values for a variable across all municipalities for choropleth mapping"""
    df = get_municipalities_df()

    if df.empty:
        raise HTTPException(status_code=404, detail="Datos no disponibles")

    # Find code column
    code_col = next((c for c in ['cod_ibge', 'CD_MUN', 'codigo'] if c in df.columns), None)

    if not code_col:
        raise HTTPException(status_code=500, detail="Formato de datos incorrecto")

    # Variable name mapping (frontend names to CSV column names)
    variable_mapping = {
        'UAI_Crisk': 'UAI_Crisk',
        'gobernanza_100': 'idx_gobernanza_100',
        'biodiversity': 'idx_biodiv',
        'forest_cover': 'forest_cover',
        'natural_habitat': 'forest_cover',  # Using forest_cover as proxy
        'pollination_deficit': 'pol_deficit',
        'fire_risk_index': 'fire_risk_index',
        'flooding_risk': 'flooding_risks',
        'hydric_stress_r': 'hydric_stress_risk',
        'dengue': 'incidence_mean_dengue',
        'leishmaniose': 'incidence_mean_leishmaniose',
        'incidence_diarr': 'incidence_diarrhea_mean',
        'death_circ_mean': 'health_death_circ_mean',
        'hosp_resp_mean': 'health_hosp_resp_mean',
        'vulnerabilidad': 'idx_vulnerabilidad',
        'pct_pobreza': 'pct_pobreza',
        'pct_rural': 'pct_rural',
        'pct_preta': 'pct_preta',
    }

    col_name = variable_mapping.get(variable, variable)

    if col_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Variable '{variable}' no encontrada")

    # Get values
    values = {}
    valid_values = []

    for _, row in df.iterrows():
        code = str(row[code_col])
        val = row[col_name]
        if pd.notna(val):
            values[code] = float(val)
            valid_values.append(float(val))
        else:
            values[code] = None

    # Calculate terciles
    if valid_values:
        valid_values.sort()
        n = len(valid_values)
        t1 = valid_values[int(n * 0.33)]
        t2 = valid_values[int(n * 0.66)]
    else:
        t1, t2 = 0, 0

    return {
        "variable": variable,
        "values": values,
        "terciles": [t1, t2],
        "min": min(valid_values) if valid_values else 0,
        "max": max(valid_values) if valid_values else 0
    }


@router.get("/{code}")
async def get_municipality_by_code(code: str):
    """Get full municipality data by code"""
    df = get_municipalities_df()

    if df.empty:
        raise HTTPException(status_code=404, detail="Datos no disponibles")

    # Find code column
    code_col = next((c for c in ['cod_ibge', 'CD_MUN', 'codigo'] if c in df.columns), None)
    name_col = next((c for c in ['Municipio', 'nome', 'NM_MUN', 'municipio', 'name'] if c in df.columns), None)

    if not code_col:
        raise HTTPException(status_code=500, detail="Formato de datos incorrecto")

    # Find municipality
    row = df[df[code_col].astype(str) == str(code)]

    if row.empty:
        raise HTTPException(status_code=404, detail="Municipio no encontrado")

    row = row.iloc[0]

    # Convert to dict, handling NaN values
    data = {}
    for col in df.columns:
        val = row[col]
        if pd.isna(val):
            data[col] = None
        elif isinstance(val, (int, float)):
            data[col] = float(val) if isinstance(val, float) else int(val)
        else:
            data[col] = str(val)

    return {
        "code": str(row[code_col]),
        "name": row[name_col] if name_col else "Unknown",
        "data": data
    }
