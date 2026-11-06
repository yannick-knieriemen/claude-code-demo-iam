"""All model parameters and scenarios (single source of truth).

Rates are annual unless the name says otherwise; the model runs in 5-year periods.
The model is solved to 2300 so that the end of the horizon does not distort
results; output is reported up to 2200.
Initial conditions for 2025 come from ``data/raw/calibration_2025.csv``.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
RAW_DATA = ROOT / "data" / "raw" / "calibration_2025.csv"
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"


def load_calibration(path: Path = RAW_DATA) -> dict[str, float]:
    """Read the 2025 calibration targets.

    Parameters
    ----------
    path : Path
        CSV file with columns ``variable`` and ``value``.

    Returns
    -------
    dict[str, float]
        Calibration value by variable name.
    """
    with path.open(newline="") as f:
        return {row["variable"]: float(row["value"]) for row in csv.DictReader(f)}


_CAL = load_calibration()


@dataclass(frozen=True)
class Params:
    """Parameters of the toy climate-economy model."""

    # Time
    start_year: int = 2025
    period_years: int = 5
    n_periods: int = 56  # 2025 to 2300
    report_until: int = 2200

    # Initial conditions (2025)
    population0: float = _CAL["population"]  # billion people
    output0: float = _CAL["gross_output"]  # trillion USD
    capital0: float = _CAL["capital"]  # trillion USD
    emissions0: float = _CAL["emissions"]  # GtCO2 per year
    carbon0: float = _CAL["carbon_stock"]  # GtC
    temperature0: float = _CAL["temperature"]  # degC above 1850-1900

    # Population
    population_max: float = 10.5  # billion, long-run level
    population_adjust: float = 0.134  # share of the gap closed per period

    # Production
    capital_share: float = 0.3
    savings_rate: float = 0.24  # close to the optimum when savings are a choice
    depreciation: float = 0.1  # annual
    tfp_growth0: float = 0.076  # per period, falls over time
    tfp_growth_decline: float = 0.005  # annual

    # Emissions intensity
    intensity_growth0: float = -0.0152  # annual
    intensity_growth_decline: float = -0.001  # annual

    # Carbon cycle (one box)
    carbon_preindustrial: float = 588.0  # GtC
    carbon_retained: float = 0.6  # share of emissions not absorbed quickly
    carbon_decay: float = 0.005  # annual decay of the excess stock
    gtc_per_gtco2: float = 1 / 3.664

    # Damages and abatement cost (shares of gross output)
    damage_coef: float = 0.00236  # damages = damage_coef * T^2
    backstop_price0: float = 550.0  # USD per tCO2
    backstop_decline: float = 0.025  # per period
    abatement_exponent: float = 2.6

    # Preferences
    time_preference: float = 0.015  # annual
    risk_aversion: float = 1.45


@dataclass(frozen=True)
class Scenario:
    """A named model run.

    Attributes
    ----------
    name : str
        Short label used in output files.
    params : Params
        Parameters for this run.
    optimise_abatement : bool
        If False, abatement is fixed at zero (business as usual).
    """

    name: str
    params: Params
    optimise_abatement: bool


BASE = Params()

SCENARIOS: list[Scenario] = [
    Scenario("bau", BASE, optimise_abatement=False),
    Scenario("optimal", BASE, optimise_abatement=True),
]
