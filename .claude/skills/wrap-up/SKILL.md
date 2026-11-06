---
name: wrap-up
description: End-of-session routine. Lints, runs the tests, commits the session's work with a clear message and pushes to GitHub.
disable-model-invocation: true
---

# Wrap-up

Run these steps in order and report each in one line.

1. **Lint**: `uv run ruff check .` and `uv run ruff format .`. Fix any error.
2. **Tests**: `uv run pytest -q`. They must pass before going on.
3. **Results up to date**: if model code or parameters changed this session,
   rerun the scripts that write `results/` so tables match the code.
4. **Commit**: stage changed files by name (never `git add -A`; never plan
   files or `.claude/state/`). Message: one summary line, then what changed
   and whether results moved. Show the message before committing.
5. **Push**: `git push`. Report the commit hash.
