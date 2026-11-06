---
name: session-start
description: Start-of-session routine. Pulls from GitHub, briefs on what coauthors changed, runs the tests and reports where things stand.
disable-model-invocation: true
---

# Session start

Run these steps in order. Keep the report short: one bullet block per step.

1. **Sync with GitHub**
   Run `git fetch origin`, then `git status -sb`.
   - Behind, nothing local ahead: `git pull`.
   - Diverged (ahead and behind): stop and report it; merging needs the user.
   Report: pulled N commits / already up to date / diverged.

2. **What coauthors changed**
   For each new commit from someone else: author, date, message, and what the
   change does, read from the diff. Describe behaviour, not files ("changed how
   depreciation is set", not "edited config.py"). Lead with anything that can
   move results: model code, parameters, data. Describe only; reviewing is the
   `reviewer` agent's job at the end of the session.

3. **Tests**
   Run `uv run pytest -q`. Report the pass count and any failures.

4. **Ready**
   One line: clean and ready, or what needs attention first.
