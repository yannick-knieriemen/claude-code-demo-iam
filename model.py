"""Equations of the toy climate-economy model (DICE-style, 5-year periods)."""

import math
from functools import cache

import numpy as np

from config import Params


def years(p: Params) -> np.ndarray:
    """Calendar year at the start of each period."""
    return p.start_year + p.period_years * np.arange(p.n_periods)


@cache
def exogenous_paths(p: Params) -> dict[str, np.ndarray]:
    """Population, productivity, emissions intensity and abatement cost paths.

    Parameters
    ----------
    p : Params
        Model parameters.

    Returns
    -------
    dict[str, np.ndarray]
        Arrays of length ``p.n_periods``: ``population`` (billion), ``tfp``,
        ``intensity`` (GtCO2 per trillion USD) and ``abatement_cost_coef``
        (share of output at full abatement).
    """
    n, dt = p.n_periods, p.period_years
    t = np.arange(n)

    population = np.empty(n)
    population[0] = p.population0
    for i in range(n - 1):
        gap_ratio = p.population_max / population[i]
        population[i + 1] = population[i] * gap_ratio**p.population_adjust

    tfp_growth = p.tfp_growth0 * np.exp(-p.tfp_growth_decline * dt * t)
    tfp = np.empty(n)
    tfp[0] = p.output0 / (
        p.capital0**p.capital_share * p.population0 ** (1 - p.capital_share)
    )
    for i in range(n - 1):
        tfp[i + 1] = tfp[i] / (1 - tfp_growth[i])

    intensity_growth = p.intensity_growth0 * (1 + p.intensity_growth_decline) ** (
        dt * t
    )
    intensity = np.empty(n)
    intensity[0] = p.emissions0 / p.output0
    for i in range(n - 1):
        intensity[i + 1] = intensity[i] * np.exp(intensity_growth[i] * dt)

    backstop_price = p.backstop_price0 * (1 - p.backstop_decline) ** t
    abatement_cost_coef = backstop_price * intensity / 1000 / p.abatement_exponent

    return {
        "population": population,
        "tfp": tfp,
        "intensity": intensity,
        "abatement_cost_coef": abatement_cost_coef,
    }


def warming_per_doubling(p: Params) -> float:
    """Warming per doubling of the carbon stock, calibrated to 2025 warming."""
    return p.temperature0 / np.log2(p.carbon0 / p.carbon_preindustrial)


def damage_share(temperature: float | np.ndarray, p: Params) -> float | np.ndarray:
    """Climate damages as a share of gross output (quadratic in warming)."""
    return p.damage_coef * temperature**2


def simulate(p: Params, abatement: np.ndarray) -> dict[str, np.ndarray]:
    """Run the model forward for a given abatement path.

    Parameters
    ----------
    p : Params
        Model parameters.
    abatement : np.ndarray
        Abatement rate (share of emissions avoided) per period, in [0, 1].

    Returns
    -------
    dict[str, np.ndarray]
        Model variables per period, including ``temperature`` (degC),
        ``consumption_pc`` (thousand USD per person), ``emissions`` (GtCO2 per
        year), ``carbon`` (GtC), ``capital`` and ``output_net`` (trillion USD).
    """
    n, dt = p.n_periods, p.period_years
    ex = exogenous_paths(p)
    sensitivity = warming_per_doubling(p)
    carbon_persistence = (1 - p.carbon_decay) ** dt
    carbon_per_emission = p.carbon_retained * dt * p.gtc_per_gtco2

    labour_term = ex["population"] ** (1 - p.capital_share)
    abatement_cost = ex["abatement_cost_coef"] * abatement**p.abatement_exponent

    # The loop only moves the two stocks forward; plain floats keep it fast.
    tfp, intensity = ex["tfp"].tolist(), ex["intensity"].tolist()
    labour, cost = labour_term.tolist(), abatement_cost.tolist()
    mu = list(abatement)
    capital, carbon = np.empty(n), np.empty(n)
    k, m = p.capital0, p.carbon0
    for i in range(n):
        capital[i], carbon[i] = k, m
        temp = sensitivity * math.log2(m / p.carbon_preindustrial)
        y = tfp[i] * k**p.capital_share * labour[i]
        y_net = y * (1 - damage_share(temp, p) - cost[i])
        e = intensity[i] * (1 - mu[i]) * y
        k = (1 - p.depreciation_per_period) * k + dt * p.savings_rate * y_net
        m = (
            p.carbon_preindustrial
            + carbon_persistence * (m - p.carbon_preindustrial)
            + carbon_per_emission * e
        )

    temperature = sensitivity * np.log2(carbon / p.carbon_preindustrial)
    damages = damage_share(temperature, p)
    output_gross = ex["tfp"] * capital**p.capital_share * labour_term
    output_net = output_gross * (1 - damages - abatement_cost)
    emissions = ex["intensity"] * (1 - abatement) * output_gross
    consumption = (1 - p.savings_rate) * output_net

    return {
        "year": years(p),
        "population": ex["population"],
        "capital": capital,
        "output_gross": output_gross,
        "output_net": output_net,
        "damages": damages,
        "abatement_cost": abatement_cost,
        "consumption_pc": consumption / ex["population"],
        "emissions": emissions,
        "carbon": carbon,
        "temperature": temperature,
        "abatement": np.asarray(abatement, dtype=float),
    }


def welfare(p: Params, path: dict[str, np.ndarray]) -> float:
    """Discounted sum of population-weighted CRRA utility, per discounted person.

    Dividing by the discounted population keeps the value near one, which helps
    the optimiser.
    """
    t = np.arange(p.n_periods)
    discount = (1 + p.time_preference) ** (-p.period_years * t)
    c = path["consumption_pc"]
    utility = (c ** (1 - p.risk_aversion) - 1) / (1 - p.risk_aversion)
    weights = discount * path["population"]
    return float(np.sum(weights * utility) / np.sum(weights))
