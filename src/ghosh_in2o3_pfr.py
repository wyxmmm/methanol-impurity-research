"""Transparent reproduction of the Ghosh et al. (2021) In2O3 model.

The paper reports a single-site LHHW model embedded in an isothermal,
isobaric plug-flow reactor.  This module implements those published rate
expressions and parameters without refitting them.  It is deliberately scoped
to the unsupported In2O3 catalyst used by Ghosh et al.; it is not a kinetic
model for supported In2O3/ZrO2 or for sulfur poisoning.

The original implementation's equilibrium-constant correlations and exact
standard-volume convention were not published.  Here, reaction equilibrium
constants are calculated from the GRI-Mech 3.0 NASA-7 polynomials and inlet
volumetric flow is converted at 273.15 K and 1 atm.  Those choices are exposed
as reproducibility assumptions in every result.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    ROOT
    / "data"
    / "curated"
    / "in2o3_zro2"
    / "ghosh_2021_unsupported_in2o3_kinetics.csv"
)
VALIDATION_DATA_PATH = (
    ROOT
    / "data"
    / "curated"
    / "in2o3_zro2"
    / "ghosh_2021_validation_inputs.csv"
)
R_GAS = 8.31446261815324  # J mol-1 K-1
T_REF_K = 573.15
STANDARD_MOLAR_VOLUME_ML_MOL = 22_414.0
ATM_BAR = 1.01325
METHANOL_MOLAR_MASS_G_MOL = 32.04186

SPECIES = ("CO2", "H2", "CH3OH", "H2O", "CO", "CH4")
INDEX = {name: index for index, name in enumerate(SPECIES)}

# Low-temperature NASA-7 coefficients (200-1000 K).  The model is evaluated
# over 473-673 K, so only this branch is needed.  Coefficients produce h/RT and
# s/R; reaction Kp is dimensionless with the 1-bar standard state.
NASA7_LOW: dict[str, tuple[float, ...]] = {
    "H2": (
        2.34433112,
        7.98052075e-3,
        -1.94781510e-5,
        2.01572094e-8,
        -7.37611761e-12,
        -917.935173,
        0.683010238,
    ),
    "CO2": (
        2.35677352,
        8.98459677e-3,
        -7.12356269e-6,
        2.45919022e-9,
        -1.43699548e-13,
        -48371.9697,
        9.90105222,
    ),
    "H2O": (
        4.19864056,
        -2.03643410e-3,
        6.52040211e-6,
        -5.48797062e-9,
        1.77197817e-12,
        -30293.7267,
        -0.849032208,
    ),
    "CO": (
        3.57953347,
        -6.10353680e-4,
        1.01681433e-6,
        9.07005884e-10,
        -9.04424499e-13,
        -14344.0860,
        3.50840928,
    ),
    "CH4": (
        5.14987613,
        -1.36709788e-2,
        4.91800599e-5,
        -4.84743026e-8,
        1.66693956e-11,
        -10246.6476,
        -4.64130376,
    ),
    "CH3OH": (
        5.71539582,
        -1.52309129e-2,
        6.52441155e-5,
        -7.10806889e-8,
        2.61352698e-11,
        -25642.7656,
        -1.50409823,
    ),
}

STOICHIOMETRY = {
    # CO2 + 3 H2 <=> CH3OH + H2O
    "MeOH": (-1.0, -3.0, 1.0, 1.0, 0.0, 0.0),
    # CO2 + H2 <=> CO + H2O
    "RWGS": (-1.0, -1.0, 0.0, 1.0, 1.0, 0.0),
    # CO2 + 4 H2 <=> CH4 + 2 H2O
    "CH4": (-1.0, -4.0, 0.0, 2.0, 0.0, 1.0),
}


@dataclass(frozen=True)
class KineticParameters:
    """Published single-site parameter set (Tables 3 and 4)."""

    k_meoh_ref: float = 6.9e-4
    ea_meoh_kj_mol: float = 35.7
    k_rwgs_ref: float = 1.8e-3
    ea_rwgs_kj_mol: float = 54.5
    k_ch4_ref: float = 1.1e-4
    ea_ch4_kj_mol: float = 42.5
    k_h2_ref_bar_inv: float = 0.76
    dh_h2_kj_mol: float = -12.5
    k_co2_ref_bar_inv: float = 0.79
    dh_co2_kj_mol: float = -25.9


@dataclass(frozen=True)
class ReactorCase:
    run_id: str
    pressure_bar_reported: float
    temperature_c: float
    whsv_ml_gcat_h: float
    h2_co2_ratio: float
    catalyst_mass_g: float = 1.0
    inert_mole_fraction: float = 0.0
    inert_species: str = "none"


def _nasa_g_rt(species: str, temperature_k: float) -> float:
    a1, a2, a3, a4, a5, a6, a7 = NASA7_LOW[species]
    t = temperature_k
    h_rt = a1 + a2 * t / 2 + a3 * t**2 / 3 + a4 * t**3 / 4 + a5 * t**4 / 5 + a6 / t
    s_r = a1 * math.log(t) + a2 * t + a3 * t**2 / 2 + a4 * t**3 / 3 + a5 * t**4 / 4 + a7
    return h_rt - s_r


def reaction_equilibrium_constants(temperature_k: float) -> dict[str, float]:
    """Return Kp for the three reactions using a dimensionless 1-bar state."""

    if not 200.0 <= temperature_k <= 1000.0:
        raise ValueError("NASA low-temperature coefficients are valid from 200 to 1000 K.")
    result: dict[str, float] = {}
    for reaction, coefficients in STOICHIOMETRY.items():
        delta_g_rt = sum(
            coefficient * _nasa_g_rt(species, temperature_k)
            for species, coefficient in zip(SPECIES, coefficients)
        )
        result[reaction] = math.exp(-delta_g_rt)
    return result


def _temperature_adjusted(value_ref: float, energy_kj_mol: float, temperature_k: float) -> float:
    return value_ref * math.exp(
        energy_kj_mol * 1000.0 / R_GAS * (1.0 / T_REF_K - 1.0 / temperature_k)
    )


def kinetic_values(
    temperature_k: float,
    parameters: KineticParameters = KineticParameters(),
    *,
    swap_adsorption_enthalpies: bool = False,
) -> dict[str, float]:
    """Calculate rate and adsorption constants at ``temperature_k``.

    ``swap_adsorption_enthalpies`` represents a documented source ambiguity:
    Table 4 assigns -12.5 kJ/mol to H2 and -25.9 kJ/mol to CO2, while the prose
    later assigns those two values in the reverse order.
    """

    dh_h2 = parameters.dh_h2_kj_mol
    dh_co2 = parameters.dh_co2_kj_mol
    if swap_adsorption_enthalpies:
        dh_h2, dh_co2 = dh_co2, dh_h2
    return {
        "k_meoh": _temperature_adjusted(parameters.k_meoh_ref, parameters.ea_meoh_kj_mol, temperature_k),
        "k_rwgs": _temperature_adjusted(parameters.k_rwgs_ref, parameters.ea_rwgs_kj_mol, temperature_k),
        "k_ch4": _temperature_adjusted(parameters.k_ch4_ref, parameters.ea_ch4_kj_mol, temperature_k),
        "K_H2": _temperature_adjusted(parameters.k_h2_ref_bar_inv, dh_h2, temperature_k),
        "K_CO2": _temperature_adjusted(parameters.k_co2_ref_bar_inv, dh_co2, temperature_k),
    }


def reaction_rates(
    molar_flows_mol_s: Sequence[float],
    pressure_bar_absolute: float,
    temperature_k: float,
    parameters: KineticParameters = KineticParameters(),
    *,
    swap_adsorption_enthalpies: bool = False,
) -> tuple[float, float, float]:
    """Return MeOH, RWGS, and methanation rates in mol/(kgcat s)."""

    total = sum(molar_flows_mol_s)
    if total <= 0:
        raise ValueError("Total molar flow must remain positive.")
    p = {
        name: max(float(flow) / total * pressure_bar_absolute, 1e-18)
        for name, flow in zip(SPECIES, molar_flows_mol_s)
    }
    values = kinetic_values(
        temperature_k,
        parameters,
        swap_adsorption_enthalpies=swap_adsorption_enthalpies,
    )
    keq = reaction_equilibrium_constants(temperature_k)
    inhibition = (1.0 + values["K_CO2"] * p["CO2"] + math.sqrt(values["K_H2"] * p["H2"])) ** 2

    meoh_driving = (
        p["CO2"] * p["H2"] ** 3
        - p["CH3OH"] * p["H2O"] / keq["MeOH"]
    ) / p["H2"] ** 2
    rwgs_driving = (
        p["CO2"] * p["H2"]
        - p["CO"] * p["H2O"] / keq["RWGS"]
    ) / math.sqrt(p["H2"])
    ch4_driving = 1.0 - (
        p["CH4"] * p["H2O"] ** 2
        / (p["CO2"] * p["H2"] ** 4 * keq["CH4"])
    )
    return (
        values["k_meoh"] * meoh_driving / inhibition,
        values["k_rwgs"] * rwgs_driving / inhibition,
        values["k_ch4"] * math.sqrt(p["CO2"] * p["H2"]) * ch4_driving / inhibition,
    )


def _flow_derivative(
    flows: Sequence[float],
    pressure_bar_absolute: float,
    temperature_k: float,
    parameters: KineticParameters,
    swap_adsorption_enthalpies: bool,
    inert_flow: float = 0.0,
) -> list[float]:
    reactive_total = sum(flows)
    total_with_inert = reactive_total + inert_flow
    if reactive_total <= 0 or total_with_inert <= 0:
        raise ValueError("Total reactor flow must remain positive.")
    # reaction_rates normalizes the six reacting species internally. Scaling
    # pressure by their fraction of the total flow preserves the correct
    # partial pressures while carrying an unreactive inlet species.
    reactive_partial_pressure_sum = (
        pressure_bar_absolute * reactive_total / total_with_inert
    )
    rates = reaction_rates(
        flows,
        reactive_partial_pressure_sum,
        temperature_k,
        parameters,
        swap_adsorption_enthalpies=swap_adsorption_enthalpies,
    )
    return [
        sum(STOICHIOMETRY[reaction][index] * rate for reaction, rate in zip(("MeOH", "RWGS", "CH4"), rates))
        for index in range(len(SPECIES))
    ]


def _rk4_step(
    flows: Sequence[float],
    step_kg: float,
    pressure_bar_absolute: float,
    temperature_k: float,
    parameters: KineticParameters,
    swap_adsorption_enthalpies: bool,
    inert_flow: float = 0.0,
) -> list[float]:
    args = (
        pressure_bar_absolute,
        temperature_k,
        parameters,
        swap_adsorption_enthalpies,
        inert_flow,
    )
    k1 = _flow_derivative(flows, *args)
    y2 = [value + step_kg * slope / 2 for value, slope in zip(flows, k1)]
    k2 = _flow_derivative(y2, *args)
    y3 = [value + step_kg * slope / 2 for value, slope in zip(flows, k2)]
    k3 = _flow_derivative(y3, *args)
    y4 = [value + step_kg * slope for value, slope in zip(flows, k3)]
    k4 = _flow_derivative(y4, *args)
    return [
        value + step_kg * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(flows, k1, k2, k3, k4)
    ]


def simulate_case(
    case: ReactorCase,
    *,
    parameters: KineticParameters = KineticParameters(),
    pressure_interpretation: str = "reported_absolute",
    catalyst_mass_basis: str = "total_composite",
    swap_adsorption_enthalpies: bool = False,
    integration_steps: int = 800,
) -> dict[str, float | str]:
    """Integrate the published PFR balances for one reported condition."""

    if integration_steps < 20:
        raise ValueError("integration_steps must be at least 20.")
    if not 0.0 <= case.inert_mole_fraction < 1.0:
        raise ValueError("inert_mole_fraction must be at least 0 and less than 1.")
    if case.pressure_bar_reported <= 0:
        raise ValueError("pressure_bar_reported must be positive.")
    if case.whsv_ml_gcat_h <= 0 or case.catalyst_mass_g <= 0:
        raise ValueError("WHSV and catalyst mass must be positive.")
    if case.h2_co2_ratio <= 0:
        raise ValueError("H2/CO2 ratio must be positive.")
    if pressure_interpretation == "reported_absolute":
        pressure_bar = case.pressure_bar_reported
    elif pressure_interpretation == "reported_gauge":
        pressure_bar = case.pressure_bar_reported + ATM_BAR
    else:
        raise ValueError("pressure_interpretation must be reported_absolute or reported_gauge.")

    if catalyst_mass_basis == "total_composite":
        integrated_mass_g = case.catalyst_mass_g
    elif catalyst_mass_basis == "active_in2o3":
        # The experimental bed was 2:1 In2O3:silica by mass.
        integrated_mass_g = case.catalyst_mass_g * 2.0 / 3.0
    else:
        raise ValueError("catalyst_mass_basis must be total_composite or active_in2o3.")

    temperature_k = case.temperature_c + 273.15
    inlet_total = (
        case.whsv_ml_gcat_h
        * case.catalyst_mass_g
        / STANDARD_MOLAR_VOLUME_ML_MOL
        / 3600.0
    )
    reactive_inlet = inlet_total * (1.0 - case.inert_mole_fraction)
    co2_in = reactive_inlet / (1.0 + case.h2_co2_ratio)
    h2_in = reactive_inlet - co2_in
    inert_in = inlet_total * case.inert_mole_fraction
    flows: list[float] = [co2_in, h2_in, 0.0, 0.0, 0.0, 0.0]
    step_kg = integrated_mass_g / 1000.0 / integration_steps

    for _ in range(integration_steps):
        candidate = _rk4_step(
            flows,
            step_kg,
            pressure_bar,
            temperature_k,
            parameters,
            swap_adsorption_enthalpies,
            inert_in,
        )
        # Tiny negative values can arise from roundoff; a material negative
        # value indicates an integration failure or a domain excursion.
        if min(candidate) < -1e-10 * inlet_total:
            raise RuntimeError(
                f"PFR integration produced a negative flow for run {case.run_id}; "
                "increase integration_steps or inspect the model domain."
            )
        flows = [max(value, 0.0) for value in candidate]

    co2_consumed = co2_in - flows[INDEX["CO2"]]
    conversion = co2_consumed / co2_in * 100.0
    products = {
        "meoh": flows[INDEX["CH3OH"]],
        "co": flows[INDEX["CO"]],
        "ch4": flows[INDEX["CH4"]],
    }
    denominator = max(co2_consumed, 1e-30)
    total_out = sum(flows) + inert_in
    result: dict[str, float | str] = {
        "run_id": case.run_id,
        "pressure_bar_reported": case.pressure_bar_reported,
        "pressure_bar_absolute_used": pressure_bar,
        "temperature_c": case.temperature_c,
        "whsv_ml_gcat_h": case.whsv_ml_gcat_h,
        "h2_co2_ratio": case.h2_co2_ratio,
        "catalyst_mass_g_used": case.catalyst_mass_g,
        "inert_species": case.inert_species if case.inert_mole_fraction > 0 else "none",
        "inert_inlet_mole_fraction": case.inert_mole_fraction,
        "co2_conversion_percent_pred": conversion,
        "meoh_selectivity_percent_pred": products["meoh"] / denominator * 100.0,
        "meoh_yield_percent_pred": conversion * products["meoh"] / denominator,
        "co_selectivity_percent_pred": products["co"] / denominator * 100.0,
        "ch4_selectivity_percent_pred": products["ch4"] / denominator * 100.0,
        "meoh_outlet_mole_fraction_pred": products["meoh"] / total_out,
        "meoh_outlet_mol_s_pred": products["meoh"],
        "meoh_outlet_g_h_pred": products["meoh"] * METHANOL_MOLAR_MASS_G_MOL * 3600.0,
        "co_outlet_mole_fraction_pred": products["co"] / total_out,
        "ch4_outlet_mole_fraction_pred": products["ch4"] / total_out,
        "co2_outlet_mole_fraction_pred": flows[INDEX["CO2"]] / total_out,
        "inert_outlet_mole_fraction_pred": inert_in / total_out,
        "meoh_productivity_g_gcat_h_pred": (
            products["meoh"] * METHANOL_MOLAR_MASS_G_MOL * 3600.0 / case.catalyst_mass_g
        ),
        "pressure_interpretation": pressure_interpretation,
        "catalyst_mass_basis": catalyst_mass_basis,
        "adsorption_enthalpy_assignment": (
            "prose_swapped" if swap_adsorption_enthalpies else "table_4"
        ),
        "equilibrium_constant_method": "GRI-Mech_3.0_NASA7_low_temperature_1bar_standard_state",
        "standard_flow_method": "273.15_K_1_atm_22414_mL_per_mol",
        "model_scope": "Ghosh_2021_unsupported_In2O3_only",
    }
    return result


@lru_cache(maxsize=1)
def calibration_rows() -> tuple[dict[str, str], ...]:
    with DATA_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 32:
        raise RuntimeError(f"Expected 32 Ghosh Table 2 rows; found {len(rows)}.")
    return rows


def case_from_row(row: Mapping[str, str]) -> ReactorCase:
    return ReactorCase(
        run_id=row["run_id"],
        pressure_bar_reported=float(row["pressure_bar"]),
        temperature_c=float(row["temperature_c"]),
        whsv_ml_gcat_h=float(row["whsv_ml_gcat_h"]),
        h2_co2_ratio=float(row["h2_co2_ratio"]),
    )


def reproduce_calibration_grid(**simulation_options: object) -> list[dict[str, float | str]]:
    """Run every Table 2 condition and attach the reported targets."""

    output: list[dict[str, float | str]] = []
    for row in calibration_rows():
        predicted = simulate_case(case_from_row(row), **simulation_options)
        predicted.update(
            {
                "co2_conversion_percent_exp": float(row["co2_conversion_percent"]),
                "meoh_selectivity_percent_exp": float(row["meoh_selectivity_percent"]),
                "co_selectivity_percent_exp": float(row["co_selectivity_percent"]),
                "ch4_selectivity_percent_exp": float(row["ch4_selectivity_percent"]),
                "fit_series": row["fit_series"],
            }
        )
        output.append(predicted)
    return output


def error_metrics(rows: Iterable[Mapping[str, float | str]]) -> dict[str, float]:
    """Calculate transparent errors in reported percentage-point units."""

    records = list(rows)
    metrics: dict[str, float] = {"n": float(len(records))}
    for response in ("co2_conversion", "meoh_selectivity", "co_selectivity", "ch4_selectivity"):
        residuals = [
            float(row[f"{response}_percent_pred"]) - float(row[f"{response}_percent_exp"])
            for row in records
        ]
        metrics[f"{response}_mae_percentage_points"] = sum(abs(value) for value in residuals) / len(residuals)
        metrics[f"{response}_rmse_percentage_points"] = math.sqrt(
            sum(value * value for value in residuals) / len(residuals)
        )
        metrics[f"{response}_bias_percentage_points"] = sum(residuals) / len(residuals)
    return metrics


@lru_cache(maxsize=1)
def validation_cases() -> tuple[ReactorCase, ...]:
    with VALIDATION_DATA_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 6:
        raise RuntimeError(f"Expected six Ghosh SI Table S3 conditions; found {len(rows)}.")
    return tuple(case_from_row(row) for row in rows)


def predict_validation_grid(**simulation_options: object) -> list[dict[str, float | str]]:
    """Predict SI Table S3 inputs; the source does not tabulate their outputs."""

    return [simulate_case(case, **simulation_options) for case in validation_cases()]
