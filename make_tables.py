"""Write the scenario summary table to results/tables/scenarios.tex.

Run with ``uv run python make_tables.py``.
"""

import logging

import numpy as np

from config import SCENARIOS, TABLES_DIR
from solve import solve

logger = logging.getLogger(__name__)

ABATEMENT_YEAR = 2050
LOSS_YEAR = 2100


def scenario_row(name: str, path: dict[str, np.ndarray]) -> str:
    """Format one table row: peak warming, abatement in 2050, loss in 2100.

    Parameters
    ----------
    name : str
        Scenario label.
    path : dict[str, np.ndarray]
        Solved path from ``solve.solve``.

    Returns
    -------
    str
        LaTeX table row.
    """
    peak = path["temperature"].max()
    i_abate = int(np.flatnonzero(path["year"] == ABATEMENT_YEAR)[0])
    i_loss = int(np.flatnonzero(path["year"] == LOSS_YEAR)[0])
    loss = path["damages"][i_loss] + path["abatement_cost"][i_loss]
    label = "BAU" if name == "bau" else name.replace("-", " ").capitalize()
    return (
        f"{label} & {peak:.2f} & {100 * path['abatement'][i_abate]:.1f} "
        f"& {100 * loss:.2f} \\\\"
    )


def main() -> None:
    """Solve all scenarios and write the booktabs table."""
    rows = [scenario_row(s.name, solve(s)) for s in SCENARIOS]
    lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Scenario & Peak warming ($^\circ$C) & Abatement 2050 (\%) "
        r"& Consumption loss 2100 (\% of gross output) \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out = TABLES_DIR / "scenarios.tex"
    out.write_text("\n".join(lines) + "\n")
    logger.info("wrote %s", out)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
