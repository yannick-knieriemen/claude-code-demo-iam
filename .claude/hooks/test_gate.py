"""Test hook: Claude can't finish after editing code until the tests have run.

``record`` (PostToolUse, Bash): notes the time of every pytest run.
``check`` (Stop): if a guarded file was edited after the last pytest run, exit
code 2 keeps Claude working and tells it to run the tests. It fires once per
turn, so a test run that is impossible here can't trap the session.
"""

import json
import sys
import time

from hook_state import load, save, session_id


def record(payload: dict) -> int:
    """Remember when pytest ran."""
    if "pytest" in payload.get("tool_input", {}).get("command", ""):
        sid = session_id(payload)
        state = load(sid)
        state["last_test"] = time.time()
        save(sid, state)
    return 0


def check(payload: dict) -> int:
    """Return 2 if guarded files changed after the last test run."""
    if payload.get("stop_hook_active"):
        return 0
    state = load(session_id(payload))
    last_test = state.get("last_test", 0.0)
    untested = sorted(f for f, t in state["edits"].items() if t > last_test)
    if not untested:
        return 0
    sys.stderr.write(
        "BLOCKED by the test hook: you edited "
        + ", ".join(untested)
        + " but the tests have not run since.\n"
        "Run `uv run pytest` and report the result before you finish.\n"
    )
    return 2


def main() -> int:
    """Dispatch on the first argument: record or check."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    return {"record": record, "check": check}[sys.argv[1]](payload)


if __name__ == "__main__":
    sys.exit(main())
