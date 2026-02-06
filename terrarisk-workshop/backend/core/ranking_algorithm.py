"""
TerraRisk Workshop - Optimal Ranking Algorithm

Computes the "platform optimal ranking" for workshop municipalities
based on composite risk scores across multiple dimensions.
"""

import pandas as pd
from typing import Optional
from pathlib import Path


def normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalization (0-1)"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)


def compute_platform_ranking(csv_path: str, municipality_names: list[str]) -> list[dict]:
    """
    Compute optimal ranking for specified municipalities

    Args:
        csv_path: Path to municipios CSV file
        municipality_names: List of municipality names to rank

    Returns:
        List of dicts with: code, name, position, compositeScore, dimensionScores
    """
    # Load data
    df = pd.read_csv(csv_path)

    # Find name column (flexible mapping)
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

    # Filter to workshop municipalities
    df_workshop = df[df[name_col].isin(municipality_names)].copy()

    if len(df_workshop) == 0:
        raise ValueError(f"No matching municipalities found in CSV")

    # Variable mapping (layer_id -> CSV column name)
    variable_mapping = {
        'fire_risk': 'fire_risk_index',
        'flooding': 'flooding_risks',
        'hydric_stress': 'hydric_stress_risk',
        'dengue': 'incidence_mean_dengue',
        'diarrhea': 'incidence_diarrhea_mean',
        'cv_mortality': 'health_death_circ_mean',
        'resp_hosp': 'health_hosp_resp_mean',
        'leishmaniasis': 'incidence_mean_leishmaniose',
        'poverty': 'pct_pobreza',
        'vulnerability': 'idx_vulnerabilidad',
        'governance_general': 'idx_gobernanza_100',
        'governance_climatic': 'UAI_Crisk',
        'biodiversity': 'idx_biodiv',
        'natural_habitat': 'forest_cover'
    }

    # Risk dimensions (higher = worse)
    risk_dims = [
        'fire_risk', 'flooding', 'hydric_stress', 'dengue', 'diarrhea',
        'cv_mortality', 'resp_hosp', 'leishmaniasis', 'poverty', 'vulnerability'
    ]

    # Protective dimensions (lower = worse)
    protective_dims = [
        'governance_general', 'governance_climatic', 'biodiversity', 'natural_habitat'
    ]

    # Normalize all dimensions
    normalized_scores = {}
    dimension_scores = {}

    for layer_id, col_name in variable_mapping.items():
        if col_name in df_workshop.columns:
            series = df_workshop[col_name].fillna(df_workshop[col_name].median())
            normalized = normalize_series(series)
            normalized_scores[layer_id] = normalized
            dimension_scores[layer_id] = series

    # Compute composite score for each municipality
    results = []

    for idx, row in df_workshop.iterrows():
        code = str(row[code_col])
        name = row[name_col]

        # Risk component (higher normalized = worse)
        risk_values = []
        for dim in risk_dims:
            if dim in normalized_scores:
                risk_values.append(normalized_scores[dim].loc[idx])

        risk_score = sum(risk_values) / len(risk_values) if risk_values else 0

        # Protective component (lower normalized = worse, so we take 1 - normalized)
        protective_values = []
        for dim in protective_dims:
            if dim in normalized_scores:
                protective_values.append(1 - normalized_scores[dim].loc[idx])

        protective_score = sum(protective_values) / len(protective_values) if protective_values else 0

        # Composite score (higher = higher priority)
        composite = risk_score + protective_score

        # Get dimension scores for this municipality
        dim_scores = {}
        for layer_id, series in dimension_scores.items():
            dim_scores[layer_id] = float(series.loc[idx])

        results.append({
            "code": code,
            "name": name,
            "compositeScore": round(composite, 4),
            "riskScore": round(risk_score, 4),
            "protectiveScore": round(protective_score, 4),
            "dimensionScores": dim_scores
        })

    # Sort by composite score descending (highest risk = position 1)
    results.sort(key=lambda x: x["compositeScore"], reverse=True)

    # Add positions
    for i, item in enumerate(results):
        item["position"] = i + 1

    return results


def compute_ranking_difference(user_ranking: list[dict], platform_ranking: list[dict]) -> dict:
    """
    Compare user ranking vs platform ranking

    Args:
        user_ranking: List of {code, position}
        platform_ranking: List of {code, name, position, ...}

    Returns:
        Dict with correlation metrics and position differences
    """
    # Create mappings
    user_positions = {item["code"]: item["position"] for item in user_ranking}
    platform_positions = {item["code"]: item["position"] for item in platform_ranking}

    # Find common codes
    common_codes = set(user_positions.keys()) & set(platform_positions.keys())

    if len(common_codes) == 0:
        return {
            "spearman": None,
            "kendall": None,
            "positionDifferences": []
        }

    # Extract paired rankings
    user_ranks = [user_positions[code] for code in common_codes]
    platform_ranks = [platform_positions[code] for code in common_codes]

    # Compute Spearman's rank correlation
    spearman = compute_spearman(user_ranks, platform_ranks)

    # Compute Kendall's tau
    kendall = compute_kendall(user_ranks, platform_ranks)

    # Position differences
    differences = []
    for code in common_codes:
        name = next((item["name"] for item in platform_ranking if item["code"] == code), "Unknown")
        user_pos = user_positions[code]
        platform_pos = platform_positions[code]
        diff = user_pos - platform_pos

        differences.append({
            "code": code,
            "name": name,
            "userPosition": user_pos,
            "platformPosition": platform_pos,
            "difference": diff
        })

    # Sort by absolute difference descending
    differences.sort(key=lambda x: abs(x["difference"]), reverse=True)

    return {
        "spearman": round(spearman, 3) if spearman is not None else None,
        "kendall": round(kendall, 3) if kendall is not None else None,
        "positionDifferences": differences
    }


def compute_spearman(ranks1: list[int], ranks2: list[int]) -> Optional[float]:
    """
    Compute Spearman's rank correlation coefficient

    Formula: 1 - (6 * sum(d^2)) / (n * (n^2 - 1))
    where d = difference between paired ranks
    """
    if len(ranks1) != len(ranks2) or len(ranks1) == 0:
        return None

    n = len(ranks1)
    d_squared_sum = sum((r1 - r2) ** 2 for r1, r2 in zip(ranks1, ranks2))

    if n == 1:
        return 1.0

    spearman = 1 - (6 * d_squared_sum) / (n * (n ** 2 - 1))
    return spearman


def compute_kendall(ranks1: list[int], ranks2: list[int]) -> Optional[float]:
    """
    Compute Kendall's tau correlation coefficient

    Counts concordant and discordant pairs
    """
    if len(ranks1) != len(ranks2) or len(ranks1) == 0:
        return None

    n = len(ranks1)
    concordant = 0
    discordant = 0

    for i in range(n):
        for j in range(i + 1, n):
            # Check if pair (i, j) is concordant or discordant
            sign1 = (ranks1[j] - ranks1[i]) / abs(ranks1[j] - ranks1[i]) if ranks1[j] != ranks1[i] else 0
            sign2 = (ranks2[j] - ranks2[i]) / abs(ranks2[j] - ranks2[i]) if ranks2[j] != ranks2[i] else 0

            if sign1 * sign2 > 0:
                concordant += 1
            elif sign1 * sign2 < 0:
                discordant += 1

    total_pairs = n * (n - 1) // 2

    if total_pairs == 0:
        return None

    kendall = (concordant - discordant) / total_pairs
    return kendall
