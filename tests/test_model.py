import numpy as np
import pytest

from config import BASE, SCENARIOS
from model import simulate
from solve import solve


@pytest.fixture(scope="module")
def paths() -> dict[str, dict[str, np.ndarray]]:
    return {s.name: solve(s) for s in SCENARIOS}


def test_starts_at_observed_warming() -> None:
    path = simulate(BASE, np.zeros(BASE.n_periods))
    assert path["temperature"][0] == pytest.approx(BASE.temperature0)


def test_bau_warming_rises(paths: dict[str, dict[str, np.ndarray]]) -> None:
    assert np.all(np.diff(paths["bau"]["temperature"]) > 0)


def test_bau_has_no_abatement(paths: dict[str, dict[str, np.ndarray]]) -> None:
    assert np.all(paths["bau"]["abatement"] == 0)


@pytest.mark.parametrize("name", [s.name for s in SCENARIOS])
def test_abatement_between_zero_and_one(
    paths: dict[str, dict[str, np.ndarray]], name: str
) -> None:
    abatement = paths[name]["abatement"]
    assert np.all((abatement >= -1e-9) & (abatement <= 1 + 1e-9))


def test_optimal_peak_below_bau(paths: dict[str, dict[str, np.ndarray]]) -> None:
    assert paths["optimal"]["temperature"].max() < paths["bau"]["temperature"].max()
