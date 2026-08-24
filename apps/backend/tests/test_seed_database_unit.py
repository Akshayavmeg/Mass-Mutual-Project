"""Unit tests for scripts/seed_database.py's pure logic -- deterministic
UUID derivation (what makes repeated seeding idempotent/safely-repeatable,
this milestone's explicit requirement) and the fail-safe "no reachable
database" exit path, both fully testable without a live PostgreSQL
connection.
"""

from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_SCRIPT_PATH = REPO_ROOT / "scripts" / "seed_database.py"


def _load_seed_module():
    spec = importlib.util.spec_from_file_location("seed_database", SEED_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_seed = _load_seed_module()


def test_deterministic_uuid_is_stable_across_calls():
    a = _seed.deterministic_uuid("customer", "CUST-0001")
    b = _seed.deterministic_uuid("customer", "CUST-0001")
    assert a == b
    assert isinstance(a, uuid.UUID)


def test_deterministic_uuid_differs_for_different_natural_keys():
    a = _seed.deterministic_uuid("account", "9000010001")
    b = _seed.deterministic_uuid("account", "9000010002")
    assert a != b


def test_deterministic_uuid_differs_across_entity_types_for_the_same_key():
    """A customer_id and an unrelated account_number that happened to
    share a literal string must not collide."""
    a = _seed.deterministic_uuid("customer", "0001")
    b = _seed.deterministic_uuid("account", "0001")
    assert a != b


def test_seed_main_reports_and_exits_when_no_database_reachable(capsys):
    exit_code = _seed.main()
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No reachable PostgreSQL" in captured.err
    assert "NOT" in captured.err  # "was NOT performed"
