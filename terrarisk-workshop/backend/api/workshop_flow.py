"""
TerraRisk Workshop - Workshop Flow API
Multi-step workshop dynamic for municipality ranking and PEARC actions
"""

import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import pandas as pd

from core.config import DATA_DIR

# Categorical columns that need numeric encoding
CATEGORICAL_ENCODINGS = {
    'classe_pri': {'Baixa': 1, 'Média': 2, 'Alta': 3, 'Muito alta': 4},
}


def _to_numeric(val, col_name: str):
    """Convert a value to float, handling categorical encodings."""
    if col_name in CATEGORICAL_ENCODINGS:
        return CATEGORICAL_ENCODINGS[col_name].get(val)
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
from core.pearc_actions import (
    get_actions_list,
    get_actions_for_risks,
    WORKSHOP_MUNICIPALITIES,
    PEARC_ACTIONS
)
from core.ranking_algorithm import compute_platform_ranking, compute_ranking_difference, compute_spearman, compute_kendall
from core.database import (
    save_ranking,
    get_rankings,
    save_selected_actions,
    get_selected_actions,
    get_group,
    list_groups
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


# Variable mapping: layer_id -> CSV column name
VARIABLE_MAPPING = {
    # Governance (2 credits)
    'governance_general': 'idx_gobernanza_100',
    'governance_climatic': 'UAI_Crisk',
    # Biodiversity
    'forest_cover': 'forest_cover',                     # 1 credit
    'biodiversity': 'mean_species_richness',            # 2 credits
    'pollination': 'pol_deficit',                       # 2 credits
    'composite_biodiversity': 'idx_biodiv',             # 4 credits
    # Climate
    'flooding': 'flooding_risks',                       # 1 credit
    'fire_risk': 'fire_risk_index',                     # 3 credits
    'hydric_stress': 'hydric_stress_risk',              # 3 credits
    'composite_climate': 'idx_clima',                   # 4 credits
    # Health (3 credits)
    'dengue': 'incidence_mean_dengue',
    'diarrhea': 'incidence_diarrhea_mean',
    'cv_mortality': 'health_death_circ_mean',
    'resp_hosp': 'health_hosp_resp_mean',
    'composite_health': 'idx_carga_enfermedad',         # 4 credits
    # Social
    'population': 'population',                         # 1 credit
    'rural': 'pct_rural',                               # 1 credit
    'urban': 'pct_urbana',                              # 1 credit
    'poverty': 'pct_pobreza',                           # 2 credits
    'vulnerability': 'idx_vulnerabilidad',              # 2 credits
    # Coringa (5 credits)
    'coringa_esgoto': 'esgoto_tratado',
    'coringa_restauracao': 'classe_pri',
    'coringa_mulheres': 'per_mulh_1',
}

# Category to layer mapping
CATEGORY_LAYERS = {
    "governance": ["governance_general", "governance_climatic"],
    "biodiversity": ["forest_cover", "biodiversity", "pollination", "composite_biodiversity"],
    "climate": ["flooding", "fire_risk", "hydric_stress", "composite_climate"],
    "health": ["dengue", "diarrhea", "cv_mortality", "resp_hosp", "composite_health"],
    "social": ["population", "rural", "urban", "poverty", "vulnerability"],
    "coringa": ["coringa_esgoto", "coringa_restauracao", "coringa_mulheres"],
}

# Risk layers (higher = worse) vs protective (higher = better)
PROTECTIVE_LAYERS = {"governance_general", "governance_climatic", "biodiversity", "forest_cover"}


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
                if col_name in CATEGORICAL_ENCODINGS:
                    vals = list(CATEGORICAL_ENCODINGS[col_name].values())
                    min_max[layer_id] = {"min": min(vals), "max": max(vals)}
                else:
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

            category_map = CATEGORY_LAYERS

            for category, layers_list in category_map.items():
                values = []
                for layer_id in layers_list:
                    col_name = var_mapping.get(layer_id)
                    if col_name and col_name in df.columns:
                        val = row[col_name]
                        if pd.notna(val):
                            numeric_val = _to_numeric(val, col_name)
                            if numeric_val is not None:
                                values.append(numeric_val)
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
    if request.phase not in ["initial", "revised", "exchange"]:
        raise HTTPException(status_code=400, detail="Phase must be 'initial', 'revised', or 'exchange'")

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
            "exchange": user_rankings.get("exchange"),
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

        # Use most recent ranking: exchange > revised > initial
        user_ranking = user_rankings.get("exchange") or user_rankings.get("revised") or user_rankings.get("initial")

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
async def get_radar_profiles(codes: str, group_id: str = Query(..., description="Group ID for access verification")):
    """
    Get radar chart profiles for workshop municipalities only.
    Each category score is min-max normalized to 0-100.
    Restricted to the 10 workshop municipalities.

    Query params:
        codes: Comma-separated municipality codes
        group_id: Group ID for access verification
    """
    # Verify group exists
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=403, detail="Grupo no válido")

    if not codes or not codes.strip():
        raise HTTPException(status_code=400, detail="codes parameter is required")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]

    # Restrict to workshop municipality codes only
    workshop_names = {m["name"] for m in WORKSHOP_MUNICIPALITIES}
    data = get_workshop_data()
    df = data["df"]
    name_col = data["name_col"]
    code_col = data["code_col"]
    allowed_codes = set()
    for wm_name in workshop_names:
        row = df[df[name_col] == wm_name]
        if not row.empty:
            allowed_codes.add(str(row.iloc[0][code_col]))

    code_list = [c for c in code_list if c in allowed_codes]
    if not code_list:
        raise HTTPException(status_code=403, detail="Solo se permite acceso a municipios del workshop")

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

                    val = _to_numeric(val, col_name)
                    if val is None:
                        continue
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


@router.get("/vulnerability-comparison/{group_id}")
async def get_vulnerability_comparison(group_id: str):
    """
    Compare high vs low vulnerability municipalities among the 10 workshop municipalities.

    Splits municipalities by median vulnerability into two groups and compares:
    - Average dimension values (normalized 0-100)
    - Action impact analysis (which actions benefit each group most)

    Path params:
        group_id: Group identifier (for multi-group workshop support)

    Returns:
        - highVulnerability: {municipalities, averages, count}
        - lowVulnerability: {municipalities, averages, count}
        - actionImpact: List of actions with benefit scores per group
    """
    # Validate group exists
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        # Load workshop data (10 municipalities only)
        data = get_workshop_data()
        df = data["df"]
        name_col = data["name_col"]
        code_col = data["code_col"]

        # Load full data for normalization stats
        full_data = get_full_data()
        min_max = full_data["min_max"]

        # Check if vulnerability column exists
        vuln_col = VARIABLE_MAPPING.get('vulnerability')
        if not vuln_col or vuln_col not in df.columns:
            raise HTTPException(status_code=500, detail="Vulnerability column not found in data")

        # Convert vulnerability column to numeric
        df[vuln_col] = pd.to_numeric(df[vuln_col], errors='coerce')

        # Remove rows with NaN vulnerability
        df_valid = df.dropna(subset=[vuln_col])

        if len(df_valid) == 0:
            raise HTTPException(status_code=500, detail="No valid vulnerability data found")

        # Calculate median vulnerability
        median_vuln = df_valid[vuln_col].median()

        # Split into high and low vulnerability groups
        high_vuln_df = df_valid[df_valid[vuln_col] > median_vuln]
        low_vuln_df = df_valid[df_valid[vuln_col] <= median_vuln]

        # Helper function to normalize a value to 0-100 scale
        def normalize_value(val, layer_id):
            """Normalize value using global min-max from all 645 municipalities"""
            if pd.isna(val):
                return None

            mm = min_max.get(layer_id)
            if not mm:
                return None

            range_val = mm["max"] - mm["min"]
            if range_val > 0:
                norm = ((float(val) - mm["min"]) / range_val) * 100
            else:
                norm = 50

            return round(norm, 2)

        # Helper function to build municipality list with vulnerability scores
        def build_municipality_list(group_df):
            """Build list of municipalities with code, name, and vulnerability score"""
            municipalities = []

            for _, row in group_df.iterrows():
                code = str(row[code_col])
                name = str(row[name_col])
                vuln_raw = float(row[vuln_col])
                vuln_normalized = normalize_value(vuln_raw, 'vulnerability')

                municipalities.append({
                    "code": code,
                    "name": name,
                    "vulnerability": vuln_normalized if vuln_normalized is not None else vuln_raw
                })

            return municipalities

        # Helper function to calculate average normalized values for all dimensions
        def calculate_averages(group_df):
            """Calculate average normalized values for all dimensions in VARIABLE_MAPPING"""
            averages = {}

            for layer_id, col_name in VARIABLE_MAPPING.items():
                if col_name not in group_df.columns:
                    continue

                # Convert to numeric
                col_numeric = pd.to_numeric(group_df[col_name], errors='coerce')

                # Normalize each value
                normalized_values = []
                for val in col_numeric:
                    norm = normalize_value(val, layer_id)
                    if norm is not None:
                        normalized_values.append(norm)

                # Calculate average
                if normalized_values:
                    averages[layer_id] = round(sum(normalized_values) / len(normalized_values), 2)
                else:
                    averages[layer_id] = 0

            return averages

        # Build response for each group
        high_vuln_data = {
            "municipalities": build_municipality_list(high_vuln_df),
            "averages": calculate_averages(high_vuln_df),
            "count": len(high_vuln_df)
        }

        low_vuln_data = {
            "municipalities": build_municipality_list(low_vuln_df),
            "averages": calculate_averages(low_vuln_df),
            "count": len(low_vuln_df)
        }

        # Calculate action impact analysis
        # For each action, compute how much it benefits each group based on their risk profiles
        action_impacts = []

        for action in PEARC_ACTIONS:
            action_id = action["id"]
            links = action["links"]

            # Calculate benefit score for each group
            # Benefit = sum of (link_strength × normalized_risk_level)
            # Higher risk × stronger link = higher benefit

            high_vuln_benefit = 0
            low_vuln_benefit = 0

            for layer_id, link_strength in links.items():
                # Get average risk level for this dimension in each group
                high_risk = high_vuln_data["averages"].get(layer_id, 0)
                low_risk = low_vuln_data["averages"].get(layer_id, 0)

                # For protective layers (governance, biodiversity), benefit is higher when score is LOW
                # For risk layers, benefit is higher when score is HIGH
                if layer_id in PROTECTIVE_LAYERS:
                    # Lower governance = needs more improvement = higher benefit
                    high_vuln_benefit += link_strength * (100 - high_risk) / 100
                    low_vuln_benefit += link_strength * (100 - low_risk) / 100
                else:
                    # Higher risk = needs more mitigation = higher benefit
                    high_vuln_benefit += link_strength * (high_risk / 100)
                    low_vuln_benefit += link_strength * (low_risk / 100)

            # Normalize benefits to 0-1 scale (divide by max possible benefit)
            max_possible = sum(links.values())
            if max_possible > 0:
                high_vuln_benefit = high_vuln_benefit / max_possible
                low_vuln_benefit = low_vuln_benefit / max_possible

            # Calculate disparity
            disparity = abs(high_vuln_benefit - low_vuln_benefit)

            # Get action name (convert ID to readable name)
            action_name = action_id.replace("_", " ").title()

            action_impacts.append({
                "actionId": action_id,
                "actionName": action_name,
                "category": action["category"],
                "highVulnBenefit": round(high_vuln_benefit, 3),
                "lowVulnBenefit": round(low_vuln_benefit, 3),
                "disparity": round(disparity, 3)
            })

        # Sort by disparity (descending) to show actions with biggest differences first
        action_impacts.sort(key=lambda x: x["disparity"], reverse=True)

        return {
            "highVulnerability": high_vuln_data,
            "lowVulnerability": low_vuln_data,
            "actionImpact": action_impacts,
            "medianVulnerability": round(float(median_vuln), 3)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing vulnerability comparison: {str(e)}")


def _compute_moment(before_ranking, after_ranking, platform_pos, code_to_name):
    """Compute perspective change metrics between two rankings."""
    before_pos = {item["code"]: item["position"] for item in before_ranking}
    after_pos = {item["code"]: item["position"] for item in after_ranking}

    changes = []
    promotions = 0
    demotions = 0

    for code in before_pos:
        b_p = before_pos[code]
        a_p = after_pos.get(code, b_p)
        change = b_p - a_p  # Positive = promoted

        change_type = "unchanged"
        if change > 0:
            change_type = "promoted"
            promotions += 1
        elif change < 0:
            change_type = "demoted"
            demotions += 1

        changes.append({
            "code": code,
            "name": code_to_name.get(code, code),
            "initialPosition": b_p,
            "revisedPosition": a_p,
            "positionChange": change,
            "changeType": change_type,
        })

    position_shifts = [abs(c["positionChange"]) for c in changes]
    total_changes = sum(1 for s in position_shifts if s > 0)
    avg_shift = sum(position_shifts) / len(position_shifts) if position_shifts else 0
    max_shift = max(position_shifts) if position_shifts else 0

    common_codes = sorted(before_pos.keys())
    before_ranks = [before_pos[c] for c in common_codes]
    after_ranks = [after_pos.get(c, before_pos[c]) for c in common_codes]
    platform_ranks = [platform_pos.get(c, 5) for c in common_codes]

    before_plat_corr = compute_spearman(before_ranks, platform_ranks) or 0
    after_plat_corr = compute_spearman(after_ranks, platform_ranks) or 0
    improvement = (after_plat_corr - before_plat_corr) * 100

    changes.sort(key=lambda x: abs(x["positionChange"]), reverse=True)

    return {
        "totalPositionChanges": total_changes,
        "averagePositionShift": round(avg_shift, 2),
        "maxPositionShift": max_shift,
        "unchangedCount": len(changes) - total_changes,
        "promotions": promotions,
        "demotions": demotions,
        "municipalityChanges": changes,
        "convergenceWithPlatform": {
            "initialSpearman": round(before_plat_corr, 3),
            "revisedSpearman": round(after_plat_corr, 3),
            "improvement": round(improvement, 1),
        },
    }


@router.get("/perspective-change/{group_id}")
async def get_perspective_change(group_id: str):
    """
    Compute perspective change metrics across ranking phases.

    Returns two moments:
      - moment1 (Pós-Dados): initial → revised ranking
      - moment2 (Pós-Intercâmbio): revised → exchange ranking (if available)

    Path params:
        group_id: Group identifier
    """
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        rankings = get_rankings(group_id)
        initial = rankings.get("initial")
        revised = rankings.get("revised")
        exchange = rankings.get("exchange")

        if not initial:
            raise HTTPException(status_code=404, detail="No initial ranking found")

        if not revised:
            revised = initial

        platform_ranking = get_platform_ranking()
        platform_pos = {item["code"]: item["position"] for item in platform_ranking}
        code_to_name = {item["code"]: item["name"] for item in platform_ranking}

        # Moment 1: initial → revised (effect of data exploration)
        moment1 = _compute_moment(initial, revised, platform_pos, code_to_name)

        # Moment 2: revised → exchange (effect of group discussion)
        moment2 = None
        if exchange:
            moment2 = _compute_moment(revised, exchange, platform_pos, code_to_name)

        # Data usage
        purchased_layers = group.get("purchasedLayers", [])
        initial_credits = 10  # from config
        credits_spent = initial_credits - group.get("credits", initial_credits)

        return {
            "moment1": moment1,
            "moment2": moment2,
            "dataLayersUsed": len(purchased_layers),
            "creditsSpent": max(0, credits_spent),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing perspective change: {str(e)}")


@router.get("/group-comparison")
async def get_group_comparison():
    """
    Compare all groups in the workshop: purchased layers, rankings, average values.

    Returns:
        - groups: List of group data with layers, rankings, and average values
        - totalGroups: Number of groups
    """
    try:
        data = get_workshop_data()
        df = data["df"]
        name_col = data["name_col"]
        code_col = data["code_col"]

        all_groups = list_groups()
        initial_credits = 10  # from workshop config

        results = []

        for grp in all_groups:
            group_id = grp["id"]
            purchased = grp.get("purchasedLayers", [])

            # Count layers by category
            layers_by_category = {}
            for cat, layer_list in CATEGORY_LAYERS.items():
                layers_by_category[cat] = sum(1 for lid in purchased if lid in layer_list)

            # Get rankings if they exist
            rankings = get_rankings(group_id)
            initial_ranking = rankings.get("initial")
            revised_ranking = rankings.get("revised")

            def _enrich_ranking(ranking_data):
                """Add municipality names to ranking entries"""
                if not ranking_data:
                    return None
                enriched = []
                for entry in ranking_data:
                    row = df[df[code_col].astype(str).str.strip() == str(entry["code"])]
                    name = str(row.iloc[0][name_col]) if not row.empty else entry["code"]
                    enriched.append({
                        "code": entry["code"],
                        "position": entry["position"],
                        "name": name,
                    })
                return enriched

            ranking_with_names = _enrich_ranking(initial_ranking)
            revised_with_names = _enrich_ranking(revised_ranking)
            exchange_ranking = rankings.get("exchange")
            exchange_with_names = _enrich_ranking(exchange_ranking)

            # Calculate average values for purchased layers across workshop municipalities
            average_values = {}
            for layer_id in purchased:
                col_name = VARIABLE_MAPPING.get(layer_id)
                if not col_name or col_name not in df.columns:
                    continue

                col = pd.to_numeric(df[col_name], errors="coerce")
                valid = col.dropna()
                if len(valid) > 0:
                    average_values[layer_id] = round(float(valid.mean()), 2)

            credits_spent = initial_credits - grp.get("credits", initial_credits)

            results.append({
                "id": group_id,
                "name": grp.get("name", group_id),
                "credits": grp.get("credits", 0),
                "creditsSpent": max(0, credits_spent),
                "purchasedLayers": purchased,
                "layersByCategory": layers_by_category,
                "ranking": ranking_with_names,
                "revisedRanking": revised_with_names,
                "exchangeRanking": exchange_with_names,
                "averageValues": average_values,
            })

        return {
            "groups": results,
            "totalGroups": len(results),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing group comparison: {str(e)}")
