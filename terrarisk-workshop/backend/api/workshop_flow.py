"""
TerraRisk Workshop - Workshop Flow API
Multi-step workshop dynamic for municipality ranking and PEARC actions
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd

from core.config import DATA_DIR
from core.pearc_actions import (
    get_actions_list,
    get_actions_for_risks,
    WORKSHOP_MUNICIPALITIES
)
from core.ranking_algorithm import compute_platform_ranking, compute_ranking_difference
from core.database import (
    save_ranking,
    get_rankings,
    save_selected_actions,
    get_selected_actions,
    get_group
)

router = APIRouter()


# Request models
class RankingRequest(BaseModel):
    groupId: str
    phase: str  # 'initial' or 'revised'
    ranking: list[dict]  # [{code, position}]


class ActionsRequest(BaseModel):
    groupId: str
    selectedActions: list[str]  # List of action IDs


# Cached data
_workshop_data = None
_platform_ranking = None
_full_data = None


def _load_csv():
    """Find and load the municipality CSV"""
    csv_path = DATA_DIR / "municipios.csv"
    if not csv_path.exists():
        alt_paths = [
            DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v8.csv",
            DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v7.csv",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                csv_path = alt_path
                break

    if not csv_path.exists():
        raise FileNotFoundError("Municipality data CSV not found")

    df = pd.read_csv(csv_path)

    name_col = next(
        (c for c in ['Municipio', 'nome', 'NM_MUN', 'municipio', 'name'] if c in df.columns),
        None
    )
    code_col = next(
        (c for c in ['cod_ibge', 'CD_MUN', 'codigo'] if c in df.columns),
        None
    )

    if not name_col or not code_col:
        raise ValueError("Could not find name or code column in CSV")

    return df, name_col, code_col, str(csv_path)


# Variable mapping (shared)
VARIABLE_MAPPING = {
    'governance_general': 'idx_gobernanza_100',
    'governance_climatic': 'UAI_Crisk',
    'biodiversity': 'idx_biodiv',
    'natural_habitat': 'forest_cover',
    'pollination': 'pol_deficit',
    'fire_risk': 'fire_risk_index',
    'flooding': 'flooding_risks',
    'hydric_stress': 'hydric_stress_risk',
    'dengue': 'incidence_mean_dengue',
    'diarrhea': 'incidence_diarrhea_mean',
    'cv_mortality': 'health_death_circ_mean',
    'resp_hosp': 'health_hosp_resp_mean',
    'leishmaniasis': 'incidence_mean_leishmaniose',
    'poverty': 'pct_pobreza',
    'vulnerability': 'idx_vulnerabilidad'
}

# Category to layer mapping
CATEGORY_LAYERS = {
    "governance": ["governance_general", "governance_climatic"],
    "biodiversity": ["biodiversity", "natural_habitat", "pollination"],
    "climate": ["fire_risk", "flooding", "hydric_stress"],
    "health": ["dengue", "diarrhea", "cv_mortality", "resp_hosp", "leishmaniasis"],
    "social": ["poverty", "vulnerability"]
}

# Risk layers (higher = worse) vs protective (higher = better)
PROTECTIVE_LAYERS = {"governance_general", "governance_climatic", "biodiversity", "natural_habitat"}


def get_workshop_data():
    """Load workshop municipality data"""
    global _workshop_data

    if _workshop_data is None:
        df, name_col, code_col, csv_path = _load_csv()

        workshop_names = [m["name"] for m in WORKSHOP_MUNICIPALITIES]
        df_workshop = df[df[name_col].isin(workshop_names)].copy()

        _workshop_data = {
            "df": df_workshop,
            "name_col": name_col,
            "code_col": code_col,
            "variable_mapping": VARIABLE_MAPPING,
            "csv_path": csv_path
        }

    return _workshop_data


def get_full_data():
    """Load ALL municipality data with min-max normalization stats"""
    global _full_data

    if _full_data is None:
        df, name_col, code_col, csv_path = _load_csv()

        # Pre-compute min/max for each variable across all 645 municipalities
        min_max = {}
        for layer_id, col_name in VARIABLE_MAPPING.items():
            if col_name in df.columns:
                col = pd.to_numeric(df[col_name], errors='coerce')
                min_max[layer_id] = {
                    "min": float(col.min()) if not col.isna().all() else 0,
                    "max": float(col.max()) if not col.isna().all() else 1,
                }

        _full_data = {
            "df": df,
            "name_col": name_col,
            "code_col": code_col,
            "min_max": min_max,
            "csv_path": csv_path,
        }

    return _full_data


def get_platform_ranking():
    """Get cached platform ranking"""
    global _platform_ranking

    if _platform_ranking is None:
        data = get_workshop_data()
        workshop_names = [m["name"] for m in WORKSHOP_MUNICIPALITIES]
        _platform_ranking = compute_platform_ranking(data["csv_path"], workshop_names)

    return _platform_ranking


@router.get("/municipalities")
async def get_workshop_municipalities():
    """
    Get the 10 workshop municipalities with their risk summaries

    Returns:
        List of municipalities with code, name, quadrant, and risk summary
    """
    try:
        data = get_workshop_data()
        df = data["df"]
        name_col = data["name_col"]
        code_col = data["code_col"]
        var_mapping = data["variable_mapping"]

        results = []

        for workshop_muni in WORKSHOP_MUNICIPALITIES:
            name = workshop_muni["name"]
            quadrant = workshop_muni["quadrant"]

            # Find in dataframe
            row = df[df[name_col] == name]
            if row.empty:
                continue

            row = row.iloc[0]
            code = str(row[code_col])

            # Build risk summary by category (average normalized score per category)
            risk_summary = {}

            # Category mapping
            category_map = {
                "governance": ["governance_general", "governance_climatic"],
                "biodiversity": ["biodiversity", "natural_habitat", "pollination"],
                "climate": ["fire_risk", "flooding", "hydric_stress"],
                "health": ["dengue", "diarrhea", "cv_mortality", "resp_hosp", "leishmaniasis"],
                "social": ["poverty", "vulnerability"]
            }

            for category, layers_list in category_map.items():
                values = []
                for layer_id in layers_list:
                    col_name = var_mapping.get(layer_id)
                    if col_name and col_name in df.columns:
                        val = row[col_name]
                        if pd.notna(val):
                            values.append(float(val))
                # Compute category average (or 0 if no data)
                risk_summary[category] = round(sum(values) / len(values), 3) if values else 0

            # Description based on quadrant
            descriptions = {
                "Q1": "Alta gobernanza, alta biodiversidad",
                "Q2": "Alta gobernanza, baja biodiversidad",
                "Q3": "Baja gobernanza, alta biodiversidad",
                "Q4": "Baja gobernanza, baja biodiversidad"
            }

            results.append({
                "code": code,
                "name": name,
                "quadrant": quadrant,
                "description": descriptions.get(quadrant, ""),
                "riskSummary": risk_summary
            })

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workshop municipalities: {str(e)}")


@router.get("/actions")
async def get_pearc_actions():
    """
    Get all PEARC actions with computed statistics

    Returns:
        List of actions with totalLinks, avgEvidence, totalEvidence
    """
    return get_actions_list()


@router.post("/ranking")
async def save_municipality_ranking(request: RankingRequest):
    """
    Save a group's municipality ranking

    Body:
        - groupId: Group identifier
        - phase: 'initial' or 'revised'
        - ranking: List of {code, position}
    """
    # Validate group exists
    group = get_group(request.groupId)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Validate phase
    if request.phase not in ["initial", "revised"]:
        raise HTTPException(status_code=400, detail="Phase must be 'initial' or 'revised'")

    # Validate ranking data
    if not request.ranking or len(request.ranking) == 0:
        raise HTTPException(status_code=400, detail="Ranking data is required")

    # Save ranking
    try:
        save_ranking(request.groupId, request.phase, request.ranking)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving ranking: {str(e)}")


@router.get("/rankings/{group_id}")
async def get_group_rankings(group_id: str):
    """
    Get all rankings for a group

    Returns:
        - initial: Initial ranking or null
        - revised: Revised ranking or null
        - platform: Platform optimal ranking
    """
    # Validate group exists
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        user_rankings = get_rankings(group_id)
        platform_ranking = get_platform_ranking()

        return {
            "initial": user_rankings.get("initial"),
            "revised": user_rankings.get("revised"),
            "platform": platform_ranking
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading rankings: {str(e)}")


@router.post("/actions/save")
async def save_group_actions(request: ActionsRequest):
    """
    Save selected actions for a group

    Body:
        - groupId: Group identifier
        - selectedActions: List of action IDs
    """
    # Validate group exists
    group = get_group(request.groupId)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        save_selected_actions(request.groupId, request.selectedActions)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving actions: {str(e)}")


@router.get("/comparison/{group_id}")
async def get_workshop_comparison(group_id: str):
    """
    Full comparison: user ranking vs platform, user actions vs suggested

    Returns:
        - userRanking: User's ranking (initial or revised)
        - platformRanking: Platform optimal ranking
        - rankingCorrelation: {spearman, kendall}
        - positionDifferences: List of position differences
        - userActions: User's selected actions
        - suggestedActions: Actions suggested based on user's high-risk layers
        - actionOverlap: Percentage of overlap (0-100)
    """
    # Validate group exists
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        # Get rankings
        user_rankings = get_rankings(group_id)
        platform_ranking = get_platform_ranking()

        # Use revised if available, otherwise initial
        user_ranking = user_rankings.get("revised") or user_rankings.get("initial")

        if not user_ranking:
            raise HTTPException(status_code=404, detail="No ranking found for this group")

        # Compute ranking comparison
        comparison = compute_ranking_difference(user_ranking, platform_ranking)

        # Get user actions
        user_actions = get_selected_actions(group_id)

        # Determine high-risk layers from user's purchased layers
        # For now, we'll suggest based on common high-risk layers
        # TODO: Could be improved by analyzing which layers the group purchased
        high_risk_layers = [
            "fire_risk", "flooding", "dengue", "diarrhea", "cv_mortality",
            "poverty", "vulnerability"
        ]

        suggested_actions = get_actions_for_risks(high_risk_layers)

        # Calculate action overlap
        if len(user_actions) == 0:
            action_overlap = 0
        else:
            suggested_ids = [action["id"] for action in suggested_actions[:10]]  # Top 10
            overlap_count = len(set(user_actions) & set(suggested_ids))
            action_overlap = (overlap_count / len(user_actions)) * 100

        return {
            "userRanking": user_ranking,
            "platformRanking": platform_ranking,
            "rankingCorrelation": {
                "spearman": comparison["spearman"],
                "kendall": comparison["kendall"]
            },
            "positionDifferences": comparison["positionDifferences"],
            "userActions": user_actions,
            "suggestedActions": suggested_actions[:10],  # Top 10
            "actionOverlap": round(action_overlap, 1)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comparison: {str(e)}")


@router.get("/radar")
async def get_radar_profiles(codes: str):
    """
    Get radar chart profiles for one or more municipalities.
    Each category score is min-max normalized to 0-100 across all 645 municipalities.

    For risk categories (climate, health, social): higher score = higher risk.
    For protective categories (governance, biodiversity): higher score = better.

    Query params:
        codes: Comma-separated municipality codes (e.g. "3520509,3548500")

    Returns:
        List of {code, name, scores: {governance, biodiversity, climate, health, social}}
    """
    if not codes or not codes.strip():
        raise HTTPException(status_code=400, detail="codes parameter is required")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]

    try:
        data = get_full_data()
        df = data["df"]
        code_col = data["code_col"]
        name_col = data["name_col"]
        min_max = data["min_max"]

        results = []

        for code in code_list:
            # Match by code (try int and string)
            row = df[df[code_col].astype(str).str.strip() == code]
            if row.empty:
                continue

            row = row.iloc[0]
            scores = {}

            for category, layers_list in CATEGORY_LAYERS.items():
                normalized_values = []

                for layer_id in layers_list:
                    col_name = VARIABLE_MAPPING.get(layer_id)
                    if not col_name or col_name not in df.columns:
                        continue

                    val = row[col_name]
                    if pd.isna(val):
                        continue

                    val = float(val)
                    mm = min_max.get(layer_id)
                    if not mm:
                        continue

                    # Min-max normalize to 0-100
                    range_val = mm["max"] - mm["min"]
                    if range_val > 0:
                        norm = ((val - mm["min"]) / range_val) * 100
                    else:
                        norm = 50

                    # For protective layers, invert so higher = better protection
                    if layer_id in PROTECTIVE_LAYERS:
                        norm = norm  # Keep as-is: higher governance = higher score = good
                    else:
                        # Risk layers: higher raw = more risk, we keep as-is
                        norm = norm

                    normalized_values.append(norm)

                scores[category] = round(
                    sum(normalized_values) / len(normalized_values), 1
                ) if normalized_values else 0

            results.append({
                "code": code,
                "name": str(row[name_col]),
                "scores": scores
            })

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing radar: {str(e)}")
