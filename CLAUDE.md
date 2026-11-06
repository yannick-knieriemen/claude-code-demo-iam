# Toy climate-economy model

Small DICE-style planner model for teaching and demos. A planner chooses savings
and abatement over 5-year periods, 2025 to 2200.

## Files
- `config.py`: all parameters and scenarios (single source of truth)
- `model.py`: equations (`simulate`, `welfare`)
- `solve.py`: optimiser (scipy SLSQP); solves every scenario in `config.SCENARIOS`
- `data/raw/`: calibration targets for 2025. Never edit.
- `results/tables/`, `results/figures/`: generated output only
- `paper/paper.tex`: short paper; `\input`s tables from `results/tables/`
- `tests/`: pytest

## Commands
- Solve: `uv run python solve.py`
- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Paper: `cd paper && latexmk -pdf paper.tex`
- Add packages with `uv add`, never pip

## Rules
- No parameter values outside `config.py`
- Tables: booktabs LaTeX, written by a script, never by hand
- Figures: PDF
- Run the tests before saying a change is done

## Workflow
- Start with `/session-start`, end with `/wrap-up`
- Plan hook: before editing a `.py` file at the repo root, write a plan to
  `notes/plans/<session id>.md` naming every file you will edit (the hook
  tells you the exact path)
- Test hook: after editing code you can't finish until `uv run pytest` ran
- Before committing model changes, ask the `reviewer` agent
