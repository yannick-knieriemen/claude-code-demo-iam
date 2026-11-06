"""PreToolUse hook (Edit|Write): no edit to model or script code without a plan.

The plan is a file, not a chat message, so the hook can check it: it must exist
for this session and name the file being edited. Exit code 2 blocks the edit
and shows the message to Claude.
"""

import json
import sys
import time

from hook_state import ROOT, guarded, load, plan_path, save, session_id


def main() -> int:
    """Return 2 to block the edit, 0 to allow it."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0

    rel = guarded(payload.get("tool_input", {}).get("file_path", ""))
    if rel is None:
        return 0

    sid = session_id(payload)
    plan = plan_path(sid)
    if not plan.exists() or rel not in plan.read_text():
        reason = (
            "No plan for this session yet."
            if not plan.exists()
            else (f"The plan does not mention {rel}.")
        )
        sys.stderr.write(
            f"BLOCKED by the plan hook: {reason}\n"
            f"Before editing {rel}, write a short plan to "
            f"{plan.relative_to(ROOT).as_posix()}:\n"
            "  - what you will change and why\n"
            "  - every file you will edit, by path\n"
            "  - how you will check the result\n"
            "Then retry the edit.\n"
        )
        return 2

    state = load(sid)
    state["edits"][rel] = time.time()
    save(sid, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
