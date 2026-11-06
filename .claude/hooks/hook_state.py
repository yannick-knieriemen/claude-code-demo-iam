"""Shared helpers for the plan and test hooks.

Guarded files are the Python files at the repo root: model, solver, config and
scripts. Tests and everything else are not guarded.
"""

import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
STATE_DIR = ROOT / ".claude" / "state"
PLANS_DIR = ROOT / "notes" / "plans"


def session_id(payload: dict) -> str:
    """Session id from the hook payload, safe to use in a file name."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(payload.get("session_id", "unknown")))


def guarded(file_path: str) -> str | None:
    """Repo-relative path if ``file_path`` is guarded, else None."""
    try:
        rel = Path(file_path).resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    if rel.suffix == ".py" and len(rel.parts) == 1:
        return rel.as_posix()
    return None


def plan_path(sid: str) -> Path:
    """Where the plan for this session must be written."""
    return PLANS_DIR / f"{sid}.md"


def load(sid: str) -> dict:
    """Hook state for this session (edits and test runs)."""
    path = STATE_DIR / f"{sid}.json"
    return json.loads(path.read_text()) if path.exists() else {"edits": {}}


def save(sid: str, state: dict) -> None:
    """Write the hook state for this session."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / f"{sid}.json").write_text(json.dumps(state, indent=2))
