"""
TerraRisk Workshop - PEARC Actions Catalog
"""

# 15 PEARC Priority Actions with linkages to risk dimensions
PEARC_ACTIONS = [
    {
        "id": "reforestation",
        "category": "biodiversity",
        "links": {
            "natural_habitat": 3,
            "biodiversity": 3,
            "pollination": 3,
            "fire_risk": 2,
            "flooding": 2,
            "resp_hosp": 2,
            "hydric_stress": 1
        }
    },
    {
        "id": "urban_drainage",
        "category": "climate",
        "links": {
            "flooding": 3,
            "diarrhea": 2,
            "cv_mortality": 1
        }
    },
    {
        "id": "vector_surveillance",
        "category": "health",
        "links": {
            "dengue": 3,
            "leishmaniasis": 3
        }
    },
    {
        "id": "water_management",
        "category": "climate",
        "links": {
            "hydric_stress": 3,
            "diarrhea": 2,
            "flooding": 1
        }
    },
    {
        "id": "protected_areas",
        "category": "biodiversity",
        "links": {
            "biodiversity": 3,
            "natural_habitat": 3,
            "pollination": 2,
            "fire_risk": 1
        }
    },
    {
        "id": "climate_agriculture",
        "category": "climate",
        "links": {
            "fire_risk": 2,
            "pollination": 2,
            "hydric_stress": 2,
            "poverty": 1
        }
    },
    {
        "id": "community_health",
        "category": "health",
        "links": {
            "cv_mortality": 3,
            "resp_hosp": 3,
            "diarrhea": 2,
            "dengue": 1
        }
    },
    {
        "id": "green_infrastructure",
        "category": "climate",
        "links": {
            "cv_mortality": 2,
            "resp_hosp": 2,
            "flooding": 2,
            "biodiversity": 1
        }
    },
    {
        "id": "environmental_monitoring",
        "category": "governance",
        "links": {
            "fire_risk": 2,
            "flooding": 2,
            "hydric_stress": 2
        }
    },
    {
        "id": "land_use_zoning",
        "category": "governance",
        "links": {
            "natural_habitat": 3,
            "fire_risk": 2,
            "flooding": 2,
            "biodiversity": 1
        }
    },
    {
        "id": "social_protection",
        "category": "social",
        "links": {
            "poverty": 3,
            "vulnerability": 3,
            "cv_mortality": 1,
            "diarrhea": 1
        }
    },
    {
        "id": "emergency_response",
        "category": "climate",
        "links": {
            "flooding": 3,
            "fire_risk": 3,
            "cv_mortality": 2
        }
    },
    {
        "id": "biodiversity_corridors",
        "category": "biodiversity",
        "links": {
            "biodiversity": 3,
            "natural_habitat": 2,
            "pollination": 2,
            "leishmaniasis": 1
        }
    },
    {
        "id": "pollution_control",
        "category": "health",
        "links": {
            "resp_hosp": 3,
            "cv_mortality": 2,
            "diarrhea": 2
        }
    },
    {
        "id": "climate_education",
        "category": "governance",
        "links": {
            "governance_general": 2,
            "governance_climatic": 2,
            "vulnerability": 1
        }
    }
]

# 10 Workshop Municipalities (pre-selected)
WORKSHOP_MUNICIPALITIES = [
    {"name": "Iporanga", "quadrant": "Q3"},
    {"name": "Campinas", "quadrant": "Q1"},
    {"name": "Santos", "quadrant": "Q1"},
    {"name": "São Joaquim da Barra", "quadrant": "Q3"},
    {"name": "Miracatu", "quadrant": "Q3"},
    {"name": "Eldorado", "quadrant": "Q4"},
    {"name": "Francisco Morato", "quadrant": "Q4"},
    {"name": "São Paulo", "quadrant": "Q1"},
    {"name": "Arujá", "quadrant": "Q2"},
    {"name": "Cerquilho", "quadrant": "Q2"}
]


def get_actions_list() -> list[dict]:
    """
    Get list of PEARC actions with computed statistics

    Returns:
        List of actions with totalLinks, avgEvidence, totalEvidence
    """
    actions = []

    for action in PEARC_ACTIONS:
        links = action["links"]
        total_links = len(links)
        total_evidence = sum(links.values())
        avg_evidence = total_evidence / total_links if total_links > 0 else 0

        actions.append({
            "id": action["id"],
            "category": action["category"],
            "links": links,
            "totalLinks": total_links,
            "avgEvidence": round(avg_evidence, 2),
            "totalEvidence": total_evidence
        })

    return actions


def get_actions_for_risks(high_risk_layers: list[str]) -> list[dict]:
    """
    Get actions sorted by relevance to specified high-risk layers

    Args:
        high_risk_layers: List of layer IDs with high risk

    Returns:
        List of actions sorted by relevance score (descending)
    """
    actions_with_score = []

    for action in PEARC_ACTIONS:
        # Calculate relevance score
        relevance_score = 0
        matching_risks = []

        for layer_id in high_risk_layers:
            if layer_id in action["links"]:
                evidence = action["links"][layer_id]
                relevance_score += evidence
                matching_risks.append({
                    "layerId": layer_id,
                    "evidence": evidence
                })

        if relevance_score > 0:
            actions_with_score.append({
                "id": action["id"],
                "category": action["category"],
                "relevanceScore": relevance_score,
                "matchingRisks": matching_risks,
                "matchingCount": len(matching_risks)
            })

    # Sort by relevance score descending
    actions_with_score.sort(key=lambda x: x["relevanceScore"], reverse=True)

    return actions_with_score
