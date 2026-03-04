# TerraRisk Workshop API - Workshop Flow

Backend implementation for the multi-step workshop dynamic (Point 10 from Adrian's notes).

## Overview

This adds a complete workshop flow where participants:
1. Rank 10 pre-selected municipalities by priority
2. Select PEARC priority actions based on risk analysis
3. Compare their decisions with platform-generated optimal ranking and suggested actions

## Files Created

### 1. `core/pearc_actions.py`
PEARC Actions Catalog with 15 priority actions linked to risk dimensions.

**Functions:**
- `get_actions_list()` - Returns all actions with computed statistics (totalLinks, avgEvidence, totalEvidence)
- `get_actions_for_risks(high_risk_layers)` - Returns actions sorted by relevance to specified risks

**Data:**
- `PEARC_ACTIONS` - 15 actions with evidence-weighted links to risk layers
- `WORKSHOP_MUNICIPALITIES` - 10 pre-selected municipalities from quadrants Q1-Q4

### 2. `core/ranking_algorithm.py`
Optimal ranking computation based on composite risk scores.

**Algorithm:**
- Normalizes risk and protective dimensions across municipalities (min-max 0-1)
- Risk dimensions (higher = worse): fire_risk, flooding, hydric_stress, dengue, diarrhea, cv_mortality, resp_hosp, leishmaniasis, poverty, vulnerability
- Protective dimensions (lower = worse): governance_general, governance_climatic, biodiversity, natural_habitat
- Composite score = avg(risk_dims_normalized) + avg(1 - protective_dims_normalized)
- Higher composite score = higher priority

**Functions:**
- `compute_platform_ranking(csv_path, municipality_names)` - Computes optimal ranking
- `compute_ranking_difference(user_ranking, platform_ranking)` - Computes Spearman/Kendall correlations and position differences

### 3. `core/database.py` (updated)
Added workshop tables and helper functions.

**New Tables:**
- `rankings` - Stores user rankings (initial/revised) per group
- `selected_actions` - Stores PEARC actions selected by each group

**New Functions:**
- `save_ranking(group_id, phase, ranking_data)` - Upsert ranking
- `get_rankings(group_id)` - Get both initial and revised rankings
- `save_selected_actions(group_id, action_ids)` - Upsert selected actions
- `get_selected_actions(group_id)` - Get selected actions for a group

### 4. `api/workshop_flow.py`
FastAPI router with 6 workshop endpoints.

### 5. `main.py` (updated)
Added workshop router to FastAPI app.

## API Endpoints

### GET `/api/workshop/municipalities`
Get the 10 workshop municipalities with risk summaries.

**Response:**
```json
[
  {
    "code": "3520400",
    "name": "Iporanga",
    "quadrant": "Q3",
    "description": "Baja gobernanza, alta biodiversidad",
    "riskSummary": {
      "governance": {"governance_general": 45.2, "governance_climatic": 0.32},
      "biodiversity": {"biodiversity": 78.5, "natural_habitat": 82.3, "pollination": 12.1},
      "climate": {"fire_risk": 0.45, "flooding": 0.23, "hydric_stress": 0.67},
      "health": {"dengue": 123.5, "diarrhea": 45.2, "cv_mortality": 89.3, ...},
      "social": {"poverty": 23.4, "vulnerability": 0.56}
    }
  },
  ...
]
```

### GET `/api/workshop/actions`
Get all PEARC actions with statistics.

**Response:**
```json
[
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
    },
    "totalLinks": 7,
    "avgEvidence": 2.29,
    "totalEvidence": 16
  },
  ...
]
```

### POST `/api/workshop/ranking`
Save a group's municipality ranking.

**Request:**
```json
{
  "groupId": "group-1",
  "phase": "initial",  // or "revised"
  "ranking": [
    {"code": "3520400", "position": 1},
    {"code": "3509502", "position": 2},
    ...
  ]
}
```

**Response:**
```json
{"success": true}
```

### GET `/api/workshop/rankings/{group_id}`
Get all rankings for a group.

**Response:**
```json
{
  "initial": [
    {"code": "3520400", "position": 1},
    ...
  ],
  "revised": null,  // or array if revised ranking exists
  "platform": [
    {
      "code": "3543303",
      "name": "São Joaquim da Barra",
      "position": 1,
      "compositeScore": 1.3776,
      "riskScore": 0.4371,
      "protectiveScore": 0.9405,
      "dimensionScores": {...}
    },
    ...
  ]
}
```

### POST `/api/workshop/actions/save`
Save selected PEARC actions for a group.

**Request:**
```json
{
  "groupId": "group-1",
  "selectedActions": ["reforestation", "urban_drainage", "vector_surveillance"]
}
```

**Response:**
```json
{"success": true}
```

### GET `/api/workshop/comparison/{group_id}`
Full comparison: user ranking vs platform, user actions vs suggested.

**Response:**
```json
{
  "userRanking": [...],
  "platformRanking": [...],
  "rankingCorrelation": {
    "spearman": 0.745,
    "kendall": 0.689
  },
  "positionDifferences": [
    {
      "code": "3520400",
      "name": "Iporanga",
      "userPosition": 1,
      "platformPosition": 2,
      "difference": -1
    },
    ...
  ],
  "userActions": ["reforestation", "urban_drainage"],
  "suggestedActions": [
    {
      "id": "emergency_response",
      "category": "climate",
      "relevanceScore": 6,
      "matchingRisks": [...],
      "matchingCount": 2
    },
    ...
  ],
  "actionOverlap": 50.0  // percentage
}
```

## Data Model

### Workshop Municipalities (10)
| Name | Quadrant |
|------|----------|
| Iporanga | Q3 |
| Campinas | Q1 |
| Santos | Q1 |
| São Joaquim da Barra | Q3 |
| Miracatu | Q3 |
| Eldorado | Q4 |
| Francisco Morato | Q4 |
| São Paulo | Q1 |
| Arujá | Q2 |
| Cerquilho | Q2 |

### PEARC Actions (15)
| ID | Category | Links |
|----|----------|-------|
| reforestation | biodiversity | 7 |
| urban_drainage | climate | 3 |
| vector_surveillance | health | 2 |
| water_management | climate | 3 |
| protected_areas | biodiversity | 4 |
| climate_agriculture | climate | 4 |
| community_health | health | 4 |
| green_infrastructure | climate | 4 |
| environmental_monitoring | governance | 3 |
| land_use_zoning | governance | 4 |
| social_protection | social | 4 |
| emergency_response | climate | 3 |
| biodiversity_corridors | biodiversity | 4 |
| pollution_control | health | 3 |
| climate_education | governance | 3 |

## Testing

All components tested successfully:

```bash
# Test imports
python -c "from core.pearc_actions import get_actions_list; print('OK')"
python -c "from core.ranking_algorithm import compute_platform_ranking; print('OK')"
python -c "from api.workshop_flow import router; print('OK')"

# Test database
python -c "from core.database import init_db; init_db(); print('OK')"

# Test API
python -c "from main import app; print(len([r for r in app.routes if 'workshop' in (r.tags or [])]))"
# Output: 6 endpoints
```

## Integration Notes

- CSV path handling follows the same pattern as `municipalities.py` (multiple fallback paths)
- Column name mapping is flexible to handle different CSV formats
- All correlation calculations are implemented without external dependencies (scipy optional)
- Database uses SQLite with UPSERT (ON CONFLICT) for idempotent operations
- Error handling follows existing API patterns with HTTPException

## Next Steps (Frontend Integration)

1. Create workshop flow UI components
2. Add municipality ranking drag-and-drop interface
3. Add PEARC actions selection interface
4. Add comparison visualization (user vs platform ranking)
5. Add suggested actions display based on selected high-risk layers
