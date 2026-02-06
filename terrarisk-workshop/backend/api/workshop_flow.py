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
    WORKSHOP_MUNICIPALITIES,
    PEARC_ACTIONS
)
from core.ranking_algorithm import compute_platform_ranking, compute_ranking_difference, compute_spearman, compute_kendall
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


@router.get("/perspective-change/{group_id}")
async def get_perspective_change(group_id: str):
    """
    Compute perspective change metrics between initial and revised rankings.

    Measures how much a group's decisions changed after exploring data,
    and whether they converged toward the platform optimal ranking.

    Path params:
        group_id: Group identifier

    Returns:
        - totalPositionChanges, averagePositionShift, maxPositionShift
        - municipalityChanges: detailed per-municipality changes
        - convergenceWithPlatform: improvement toward optimal
        - dataLayersUsed: how many layers informed the decision
    """
    # Validate group exists
    group = get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        # Get both rankings
        rankings = get_rankings(group_id)
        initial = rankings.get("initial")
        revised = rankings.get("revised")

        if not initial:
            raise HTTPException(status_code=404, detail="No initial ranking found")

        # If no revised ranking, use initial (no change)
        if not revised:
            revised = initial

        # Get platform optimal ranking
        platform_ranking = get_platform_ranking()

        # Build position mappings
        initial_pos = {item["code"]: item["position"] for item in initial}
        revised_pos = {item["code"]: item["position"] for item in revised}
        platform_pos = {item["code"]: item["position"] for item in platform_ranking}

        # Get municipality names from platform ranking
        code_to_name = {item["code"]: item["name"] for item in platform_ranking}

        # Compute per-municipality changes
        changes = []
        promotions = 0
        demotions = 0

        for code in initial_pos:
            init_p = initial_pos[code]
            rev_p = revised_pos.get(code, init_p)
            change = init_p - rev_p  # Positive = promoted (moved to higher priority)

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
                "initialPosition": init_p,
                "revisedPosition": rev_p,
                "positionChange": change,
                "changeType": change_type
            })

        # Aggregate metrics
        position_shifts = [abs(c["positionChange"]) for c in changes]
        total_changes = sum(1 for s in position_shifts if s > 0)
        avg_shift = sum(position_shifts) / len(position_shifts) if position_shifts else 0
        max_shift = max(position_shifts) if position_shifts else 0

        # Top 3 / bottom 3 changes
        top_three_changed = any(
            c["positionChange"] != 0 for c in changes if c["initialPosition"] <= 3
        )
        bottom_three_changed = any(
            c["positionChange"] != 0 for c in changes if c["initialPosition"] >= 8
        )

        # Correlation: initial vs revised
        common_codes = sorted(initial_pos.keys())
        initial_ranks = [initial_pos[c] for c in common_codes]
        revised_ranks = [revised_pos.get(c, initial_pos[c]) for c in common_codes]

        initial_vs_revised = {
            "spearman": round(compute_spearman(initial_ranks, revised_ranks), 3),
            "kendall": round(compute_kendall(initial_ranks, revised_ranks), 3),
        }

        # Convergence with platform
        platform_ranks = [platform_pos.get(c, 5) for c in common_codes]

        initial_plat_corr = compute_spearman(initial_ranks, platform_ranks) or 0
        revised_plat_corr = compute_spearman(revised_ranks, platform_ranks) or 0
        improvement = (revised_plat_corr - initial_plat_corr) * 100

        # Data usage
        purchased_layers = group.get("purchasedLayers", [])
        initial_credits = 10  # from config
        credits_spent = initial_credits - group.get("credits", initial_credits)

        # Sort changes: biggest shifts first
        changes.sort(key=lambda x: abs(x["positionChange"]), reverse=True)

        return {
            "totalPositionChanges": total_changes,
            "averagePositionShift": round(avg_shift, 2),
            "maxPositionShift": max_shift,
            "unchangedCount": len(changes) - total_changes,
            "promotions": promotions,
            "demotions": demotions,
            "topThreeChanges": top_three_changed,
            "bottomThreeChanges": bottom_three_changed,
            "initialVsRevisedCorrelation": initial_vs_revised,
            "municipalityChanges": changes,
            "convergenceWithPlatform": {
                "initialSpearman": round(initial_plat_corr, 3),
                "revisedSpearman": round(revised_plat_corr, 3),
                "improvement": round(improvement, 1)
            },
            "dataLayersUsed": len(purchased_layers),
            "layersUsed": purchased_layers,
            "creditsSpent": max(0, credits_spent)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing perspective change: {str(e)}")
