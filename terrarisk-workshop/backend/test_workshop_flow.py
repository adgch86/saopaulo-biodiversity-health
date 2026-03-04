"""
Quick integration test for Workshop Flow API
Run: python test_workshop_flow.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pearc_actions import get_actions_list, get_actions_for_risks, WORKSHOP_MUNICIPALITIES
from core.ranking_algorithm import compute_platform_ranking, compute_ranking_difference
from core.database import (
    init_db,
    create_group,
    save_ranking,
    get_rankings,
    save_selected_actions,
    get_selected_actions
)
from core.config import DATA_DIR


def test_pearc_actions():
    """Test PEARC actions functions"""
    print("Testing PEARC Actions...")

    # Get all actions
    actions = get_actions_list()
    assert len(actions) == 15, f"Expected 15 actions, got {len(actions)}"
    assert "id" in actions[0], "Missing 'id' field"
    assert "totalLinks" in actions[0], "Missing 'totalLinks' field"
    print(f"[OK] {len(actions)} PEARC actions loaded")

    # Get suggested actions
    high_risk = ["fire_risk", "flooding", "dengue"]
    suggested = get_actions_for_risks(high_risk)
    assert len(suggested) > 0, "No actions suggested"
    assert suggested[0]["relevanceScore"] >= suggested[-1]["relevanceScore"], "Actions not sorted by relevance"
    print(f"[OK] {len(suggested)} actions suggested for {high_risk}")

    # Check workshop municipalities
    assert len(WORKSHOP_MUNICIPALITIES) == 10, f"Expected 10 workshop municipalities, got {len(WORKSHOP_MUNICIPALITIES)}"
    print(f"[OK] {len(WORKSHOP_MUNICIPALITIES)} workshop municipalities defined")


def test_ranking_algorithm():
    """Test ranking algorithm"""
    print("\nTesting Ranking Algorithm...")

    # Find CSV
    csv_path = DATA_DIR / "municipios.csv"
    if not csv_path.exists():
        csv_path = DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v8.csv"
        if not csv_path.exists():
            csv_path = DATA_DIR.parent.parent / "outputs" / "municipios_integrado_v7.csv"

    if not csv_path.exists():
        print("[SKIP] CSV not found, skipping ranking algorithm test")
        return

    # Compute platform ranking
    workshop_names = [m["name"] for m in WORKSHOP_MUNICIPALITIES]
    ranking = compute_platform_ranking(str(csv_path), workshop_names)

    assert len(ranking) <= 10, f"Expected max 10 municipalities, got {len(ranking)}"
    assert "position" in ranking[0], "Missing 'position' field"
    assert "compositeScore" in ranking[0], "Missing 'compositeScore' field"
    print(f"[OK] Platform ranking computed for {len(ranking)} municipalities")
    print(f"  Top priority: {ranking[0]['name']} (score: {ranking[0]['compositeScore']})")

    # Test correlation
    user_ranking = [{"code": r["code"], "position": len(ranking) - i} for i, r in enumerate(ranking)]
    comparison = compute_ranking_difference(user_ranking, ranking)

    assert "spearman" in comparison, "Missing Spearman correlation"
    assert "kendall" in comparison, "Missing Kendall correlation"
    assert comparison["spearman"] is not None, "Spearman correlation is None"
    print(f"[OK] Ranking comparison computed (Spearman: {comparison['spearman']}, Kendall: {comparison['kendall']})")


def test_database():
    """Test database workshop functions"""
    print("\nTesting Database Functions...")

    # Initialize database
    init_db()
    print("[OK] Database initialized")

    # Create test group
    test_group_id = "test-workshop-flow"
    group = create_group(test_group_id, "Test Workshop Flow")
    assert group["id"] == test_group_id, "Group ID mismatch"
    print(f"[OK] Created test group: {test_group_id}")

    # Save initial ranking
    ranking_data = [
        {"code": "001", "position": 1},
        {"code": "002", "position": 2},
    ]
    save_ranking(test_group_id, "initial", ranking_data)
    print("[OK] Saved initial ranking")

    # Get rankings
    rankings = get_rankings(test_group_id)
    assert rankings["initial"] is not None, "Initial ranking not saved"
    assert len(rankings["initial"]) == 2, f"Expected 2 rankings, got {len(rankings['initial'])}"
    assert rankings["revised"] is None, "Revised ranking should be None"
    print(f"[OK] Retrieved rankings (initial: {len(rankings['initial'])}, revised: None)")

    # Save revised ranking
    revised_data = [
        {"code": "002", "position": 1},
        {"code": "001", "position": 2},
    ]
    save_ranking(test_group_id, "revised", revised_data)
    rankings = get_rankings(test_group_id)
    assert rankings["revised"] is not None, "Revised ranking not saved"
    print("[OK] Saved and retrieved revised ranking")

    # Save actions
    actions = ["reforestation", "urban_drainage"]
    save_selected_actions(test_group_id, actions)
    print("[OK] Saved selected actions")

    # Get actions
    retrieved = get_selected_actions(test_group_id)
    assert len(retrieved) == 2, f"Expected 2 actions, got {len(retrieved)}"
    assert retrieved == actions, "Actions mismatch"
    print(f"[OK] Retrieved selected actions: {retrieved}")

    # Update actions (upsert test)
    new_actions = ["reforestation", "vector_surveillance", "emergency_response"]
    save_selected_actions(test_group_id, new_actions)
    retrieved = get_selected_actions(test_group_id)
    assert len(retrieved) == 3, f"Expected 3 actions after update, got {len(retrieved)}"
    print("[OK] Actions upsert works correctly")


def test_api_router():
    """Test API router loads"""
    print("\nTesting API Router...")

    from main import app

    # Check workshop routes
    workshop_routes = [
        route.path for route in app.routes
        if hasattr(route, "tags") and "workshop" in (route.tags or [])
    ]

    expected_routes = [
        "/api/workshop/municipalities",
        "/api/workshop/actions",
        "/api/workshop/ranking",
        "/api/workshop/rankings/{group_id}",
        "/api/workshop/actions/save",
        "/api/workshop/comparison/{group_id}"
    ]

    for expected in expected_routes:
        assert expected in workshop_routes, f"Missing route: {expected}"

    print(f"[OK] All {len(expected_routes)} workshop endpoints registered")
    for route in workshop_routes:
        print(f"  - {route}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("TerraRisk Workshop Flow - Integration Test")
    print("=" * 60)

    try:
        test_pearc_actions()
        test_ranking_algorithm()
        test_database()
        test_api_router()

        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
