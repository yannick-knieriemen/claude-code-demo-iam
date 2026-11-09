# Toy climate-economy model for Claude Code

A stripped-down DICE-style integrated assessment model, built as the demo repo
for an introduction to [Claude Code](https://claude.com/claude-code). It is **not
for research use**; it exists to show what a well-prepared repo looks like to an
AI coding assistant.

A planner chooses savings and abatement over 5-year periods (2025 to 2200) and
the model solves three scenarios: business as usual, optimal abatement, and
optimal abatement with doubled damages.

## Run it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```
uv sync
uv run python solve.py   # solve all scenarios, write tables to results/
uv run pytest            # run the tests
uv run ruff check .      # lint
```

## Layout

| Path | Purpose |
|---|---|
| `config.py` | All parameters and scenarios (single source of truth) |
| `model.py` | Equations (`simulate`, `welfare`) |
| `solve.py` | Optimiser (SLSQP) over every scenario |
| `data/raw/` | 2025 calibration targets, never edited |
| `results/` | Generated tables and figures only |
| `paper/` | Short LaTeX paper that pulls in the generated tables |
| `tests/` | pytest suite |

## The Claude Code setup

This is the part to copy for your own projects.

| File | What it does |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Project memory: layout, commands, rules (no parameters outside `config.py`, tests before "done") |
| [`.claude/skills/session-start`](.claude/skills/session-start/SKILL.md) | `/session-start`: pull from GitHub, summarise what coauthors changed, run tests |
| [`.claude/skills/wrap-up`](.claude/skills/wrap-up/SKILL.md) | `/wrap-up`: lint, test, commit and push |
| [`.claude/agents/reviewer.md`](.claude/agents/reviewer.md) | Sceptical read-only subagent that reviews model changes before commit |
| [`.claude/hooks/`](.claude/hooks) | Plan hook (write a plan before editing root `.py` files) and test hook (cannot finish until tests ran) |
| [`.claude/settings.json`](.claude/settings.json) | Wires the hooks up |

Hooks are the difference between *asking* Claude to follow a rule and
*enforcing* it: the harness runs them, not the model.

## Try it

```
cd claude-code-demo-iam
claude
> /session-start
> Add a scenario with half the damage coefficient and update the paper table.
```

Watch the plan hook ask for a plan first, and the test hook block "done" until
the tests have run.
