"""
TerraRisk Workshop - Database (SQLite + JSON)
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from core.config import DATABASE_PATH, INITIAL_CREDITS

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                credits INTEGER DEFAULT 10,
                purchased_layers TEXT DEFAULT '[]',
                professional_area TEXT,
                environmental_experience TEXT,
                num_participants INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Migration: add profile columns to existing tables
        try:
            cursor.execute("ALTER TABLE groups ADD COLUMN professional_area TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE groups ADD COLUMN environmental_experience TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE groups ADD COLUMN num_participants INTEGER")
        except sqlite3.OperationalError:
            pass

        # Purchase history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                layer_id TEXT NOT NULL,
                cost INTEGER NOT NULL,
                purchased_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        """)

        # Workshop rankings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                ranking TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                UNIQUE(group_id, phase)
            )
        """)

        # Workshop selected actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS selected_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL UNIQUE,
                actions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        """)

        # ITECS v1 responses table (legacy — 2 test responses preserved)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itecs_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                participant_id TEXT NOT NULL UNIQUE,
                tc1 INTEGER, tc2 INTEGER, tc3 INTEGER, tc4 INTEGER, tc5 INTEGER,
                ra6 INTEGER, ra7 INTEGER, ra8 INTEGER,
                pf9 INTEGER, pf10 INTEGER, pf11 INTEGER, pf12 INTEGER,
                csp13 INTEGER, csp14 INTEGER, csp15 INTEGER, csp16 INTEGER,
                ia17 INTEGER, ia18 INTEGER, ia19 INTEGER, ia20 INTEGER,
                ap21 INTEGER, ap22 INTEGER, ap23 INTEGER, ap24 INTEGER, ap25 INTEGER,
                q26 TEXT, q27 TEXT, q28 TEXT, q29 TEXT, q30 TEXT,
                layers_purchased TEXT, credits_spent INTEGER,
                ranking_changed BOOLEAN, actions_selected TEXT,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        """)

        # ITECS v2 responses table (16 questions, 3 blocos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itecs_responses_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                participant_id TEXT NOT NULL UNIQUE,
                -- Bloco I: Experiência com o TerraRisk (Likert 1-7)
                exp1 INTEGER, exp2 INTEGER, exp3 INTEGER, exp4 INTEGER,
                exp5 INTEGER, exp6 INTEGER, exp7 INTEGER, exp8 INTEGER,
                -- Bloco II: Aplicação prática (texto)
                q9 TEXT, q10 TEXT, q11 TEXT,
                q12 TEXT,  -- JSON: colaboradores
                q13 TEXT,
                -- Bloco III: Próximos passos
                ps14 INTEGER, ps15 INTEGER,
                q16 BOOLEAN,
                -- Metadata automático
                version TEXT DEFAULT '2.0',
                layers_purchased TEXT,
                credits_spent INTEGER,
                ranking_changed BOOLEAN,
                actions_selected TEXT,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        """)

        conn.commit()


def row_to_dict(row) -> dict:
    """Convert SQLite Row to dict"""
    if row is None:
        return None
    d = dict(row)
    if 'purchased_layers' in d:
        d['purchasedLayers'] = json.loads(d.pop('purchased_layers'))
    if 'created_at' in d:
        d['createdAt'] = d.pop('created_at')
    if 'updated_at' in d:
        d['updatedAt'] = d.pop('updated_at')
    if 'professional_area' in d:
        d['professionalArea'] = d.pop('professional_area')
    if 'environmental_experience' in d:
        d['environmentalExperience'] = d.pop('environmental_experience')
    if 'num_participants' in d:
        d['numParticipants'] = d.pop('num_participants')
    return d


# Group operations

def create_group(group_id: str, name: str, professional_area: str = None,
                  environmental_experience: str = None, num_participants: int = None) -> dict:
    """Create a new group with optional profile data"""
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO groups (id, name, credits, purchased_layers,
                                professional_area, environmental_experience, num_participants,
                                created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (group_id, name, INITIAL_CREDITS, '[]',
              professional_area, environmental_experience, num_participants,
              now, now))

        cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
        return row_to_dict(cursor.fetchone())


def get_group(group_id: str) -> Optional[dict]:
    """Get a group by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
        return row_to_dict(cursor.fetchone())


def list_groups() -> list[dict]:
    """List all groups"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM groups ORDER BY created_at DESC")
        return [row_to_dict(row) for row in cursor.fetchall()]


def update_group_credits(group_id: str, new_credits: int, new_purchased: list[str]) -> Optional[dict]:
    """Update group credits and purchased layers"""
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE groups
            SET credits = ?, purchased_layers = ?, updated_at = ?
            WHERE id = ?
        """, (new_credits, json.dumps(new_purchased), now, group_id))

        cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
        return row_to_dict(cursor.fetchone())


def reset_group_credits(group_id: str) -> Optional[dict]:
    """Reset group credits to initial value"""
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE groups
            SET credits = ?, updated_at = ?
            WHERE id = ?
        """, (INITIAL_CREDITS, now, group_id))

        cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
        return row_to_dict(cursor.fetchone())


def delete_group(group_id: str) -> bool:
    """Delete a group"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM purchases WHERE group_id = ?", (group_id,))
        cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        return cursor.rowcount > 0


# Purchase operations

def record_purchase(group_id: str, layer_id: str, cost: int):
    """Record a layer purchase"""
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (group_id, layer_id, cost, purchased_at)
            VALUES (?, ?, ?, ?)
        """, (group_id, layer_id, cost, now))


def get_purchase_stats() -> dict:
    """Get purchase statistics"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total purchases
        cursor.execute("SELECT COUNT(*) as total FROM purchases")
        total_purchases = cursor.fetchone()['total']

        # Total credits spent
        cursor.execute("SELECT COALESCE(SUM(cost), 0) as total FROM purchases")
        credits_spent = cursor.fetchone()['total']

        # Popular layers
        cursor.execute("""
            SELECT layer_id, COUNT(*) as count
            FROM purchases
            GROUP BY layer_id
            ORDER BY count DESC
        """)
        popular_layers = [{"layerId": row['layer_id'], "count": row['count']} for row in cursor.fetchall()]

        # Group stats
        cursor.execute("""
            SELECT g.id, g.name, g.credits, g.purchased_layers, g.updated_at,
                   g.professional_area, g.environmental_experience, g.num_participants
            FROM groups g
            ORDER BY g.updated_at DESC
        """)
        group_stats = []
        for row in cursor.fetchall():
            purchased = json.loads(row['purchased_layers'])
            group_stats.append({
                "id": row['id'],
                "name": row['name'],
                "credits": row['credits'],
                "purchasedCount": len(purchased),
                "lastActivity": row['updated_at'],
                "professionalArea": row['professional_area'],
                "environmentalExperience": row['environmental_experience'],
                "numParticipants": row['num_participants'],
            })

        return {
            "totalGroups": len(group_stats),
            "totalPurchases": total_purchases,
            "creditsSpent": credits_spent,
            "popularLayers": popular_layers,
            "groupStats": group_stats
        }


# Workshop ranking operations

def save_ranking(group_id: str, phase: str, ranking_data: list[dict]):
    """
    Save or update a group's ranking

    Args:
        group_id: Group ID
        phase: 'initial' or 'revised'
        ranking_data: List of {code, position}
    """
    now = datetime.utcnow().isoformat()
    ranking_json = json.dumps(ranking_data)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rankings (group_id, phase, ranking, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(group_id, phase)
            DO UPDATE SET ranking = ?, created_at = ?
        """, (group_id, phase, ranking_json, now, ranking_json, now))


def get_rankings(group_id: str) -> dict:
    """
    Get all rankings for a group

    Returns:
        Dict with {initial: [...], revised: [...] or None}
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT phase, ranking FROM rankings WHERE group_id = ?
        """, (group_id,))

        results = {"initial": None, "revised": None, "exchange": None}
        for row in cursor.fetchall():
            phase = row['phase']
            ranking = json.loads(row['ranking'])
            results[phase] = ranking

        return results


def save_selected_actions(group_id: str, action_ids: list[str]):
    """
    Save selected actions for a group

    Args:
        group_id: Group ID
        action_ids: List of action IDs
    """
    now = datetime.utcnow().isoformat()
    actions_json = json.dumps(action_ids)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO selected_actions (group_id, actions, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(group_id)
            DO UPDATE SET actions = ?, created_at = ?
        """, (group_id, actions_json, now, actions_json, now))


def get_selected_actions(group_id: str) -> list[str]:
    """
    Get selected actions for a group

    Returns:
        List of action IDs
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT actions FROM selected_actions WHERE group_id = ?
        """, (group_id,))

        row = cursor.fetchone()
        if row:
            return json.loads(row['actions'])
        return []


# ITECS v2 operations

def save_itecs_response(group_id: str, participant_id: str, responses: dict, meta: dict):
    """Save an individual ITECS v2 response."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itecs_responses_v2 (
                group_id, participant_id,
                exp1, exp2, exp3, exp4, exp5, exp6, exp7, exp8,
                q9, q10, q11, q12, q13,
                ps14, ps15, q16,
                version,
                layers_purchased, credits_spent, ranking_changed, actions_selected,
                submitted_at
            ) VALUES (
                ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?,
                ?, ?, ?, ?,
                ?
            )
            ON CONFLICT(participant_id) DO UPDATE SET
                exp1=excluded.exp1, exp2=excluded.exp2, exp3=excluded.exp3, exp4=excluded.exp4,
                exp5=excluded.exp5, exp6=excluded.exp6, exp7=excluded.exp7, exp8=excluded.exp8,
                q9=excluded.q9, q10=excluded.q10, q11=excluded.q11, q12=excluded.q12, q13=excluded.q13,
                ps14=excluded.ps14, ps15=excluded.ps15, q16=excluded.q16,
                submitted_at=excluded.submitted_at
        """, (
            group_id, participant_id,
            responses.get('exp1'), responses.get('exp2'), responses.get('exp3'), responses.get('exp4'),
            responses.get('exp5'), responses.get('exp6'), responses.get('exp7'), responses.get('exp8'),
            responses.get('q9', ''), responses.get('q10', ''), responses.get('q11', ''),
            json.dumps(responses.get('q12', [])),
            responses.get('q13', ''),
            responses.get('ps14'), responses.get('ps15'),
            responses.get('q16', False),
            meta.get('version', '2.0'),
            json.dumps(meta.get('layersPurchased', [])),
            meta.get('creditsSpent', 0),
            meta.get('rankingChanged', False),
            json.dumps(meta.get('actionsSelected', [])),
            now,
        ))


def get_itecs_results() -> list[dict]:
    """Get all ITECS v2 responses with group names for admin."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, g.name as group_name
            FROM itecs_responses_v2 r
            LEFT JOIN groups g ON r.group_id = g.id
            ORDER BY r.submitted_at DESC
        """)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            d = dict(row)
            for field in ('q12', 'layers_purchased', 'actions_selected'):
                if d.get(field):
                    try:
                        d[field] = json.loads(d[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            results.append(d)
        return results


def get_itecs_v1_results() -> list[dict]:
    """Get legacy ITECS v1 responses with group names."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, g.name as group_name
            FROM itecs_responses r
            LEFT JOIN groups g ON r.group_id = g.id
            ORDER BY r.submitted_at DESC
        """)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            d = dict(row)
            for field in ('q28', 'layers_purchased', 'actions_selected'):
                if d.get(field):
                    try:
                        d[field] = json.loads(d[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            results.append(d)
        return results
