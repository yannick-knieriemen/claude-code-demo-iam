"""Solve the planner problem for every scenario in config.SCENARIOS.

Run with ``uv run python solve.py``.
"""

import logging

import numpy as np
from scipy.optimize import minimize
from threadpoolctl import threadpool_limits

from config import SCENARIOS, Scenario
from model import simulate, welfare

logger = logging.getLogger(__name__)


def solve(scenario: Scenario) -> dict[str, np.ndarray]:
    """Find the welfare-maximising abatement path (or none, for BAU).

    The model runs to the end of the horizon; the result is cut at
    ``params.report_until``.

    Parameters
    ----------
    scenario : Scenario
        Parameters and whether abatement is a choice.

    Returns
    -------
    dict[str, np.ndarray]
        The simulated path up to ``report_until`` (see ``model.simulate``).

    Raises
    ------
    RuntimeError
        If the optimiser does not converge.
    """
    p = scenario.params
    abatement = np.zeros(p.n_periods)

    if scenario.optimise_abatement:
        # The optimiser's small matrix steps are slower on many threads.
        with threadpool_limits(limits=1):
            result = minimize(
                lambda mu: -welfare(p, simulate(p, mu)),
                np.linspace(0.1, 1.0, p.n_periods),
                method="SLSQP",
                bounds=[(0.0, 1.0)] * p.n_periods,
                options={"maxiter": 2000, "ftol": 1e-10},
            )
        if not result.success:
            raise RuntimeError(f"{scenario.name}: optimiser failed: {result.message}")
        abatement = result.x

    path = simulate(p, abatement)
    keep = path["year"] <= p.report_until
    return {name: values[keep] for name, values in path.items()}


def main() -> dict[str, dict[str, np.ndarray]]:
    """Solve all scenarios and log a short summary."""
    paths = {}
    for scenario in SCENARIOS:
        path = solve(scenario)
        peak = int(np.argmax(path["temperature"]))
        logger.info(
            "%-8s peak warming %.2f degC in %d",
            scenario.name,
            path["temperature"][peak],
            path["year"][peak],
        )
        paths[scenario.name] = path
    return paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
