import pytest

from src.ghosh_in2o3_pfr import (
    ReactorCase,
    error_metrics,
    predict_validation_grid,
    reaction_equilibrium_constants,
    reproduce_calibration_grid,
    simulate_case,
)


def test_equilibrium_constants_are_physical_at_reference_temperature():
    constants = reaction_equilibrium_constants(573.15)
    assert constants["MeOH"] == pytest.approx(6.8718628e-6, rel=1e-6)
    assert constants["RWGS"] == pytest.approx(0.024521985, rel=1e-6)
    assert constants["CH4"] > 1e5


def test_standard_case_reproduces_reported_shape_without_refitting():
    result = simulate_case(
        ReactorCase("1c", 40.0, 300.0, 9000.0, 3.0),
        integration_steps=300,
    )
    assert result["co2_conversion_percent_pred"] == pytest.approx(5.69, abs=0.08)
    assert result["meoh_selectivity_percent_pred"] == pytest.approx(66.3, abs=0.5)
    assert result["co_selectivity_percent_pred"] == pytest.approx(33.1, abs=0.5)
    assert result["ch4_selectivity_percent_pred"] == pytest.approx(0.65, abs=0.08)
    assert (
        result["meoh_selectivity_percent_pred"]
        + result["co_selectivity_percent_pred"]
        + result["ch4_selectivity_percent_pred"]
    ) == pytest.approx(100.0, abs=1e-8)


def test_full_table2_reproduction_has_bounded_error():
    rows = reproduce_calibration_grid(integration_steps=200)
    assert len(rows) == 32
    metrics = error_metrics(rows)
    assert metrics["co2_conversion_mae_percentage_points"] < 1.0
    assert metrics["meoh_selectivity_mae_percentage_points"] < 4.5
    assert metrics["co_selectivity_mae_percentage_points"] < 4.5
    assert metrics["ch4_selectivity_mae_percentage_points"] < 0.4


def test_source_ambiguities_are_exposed_not_silently_resolved():
    # Use a non-reference temperature so the adsorption-enthalpy assignment
    # affects the van't Hoff correction.
    case = ReactorCase("ambiguity", 40.0, 350.0, 9000.0, 3.0)
    primary = simulate_case(case, integration_steps=200)
    gauge = simulate_case(
        case,
        pressure_interpretation="reported_gauge",
        integration_steps=200,
    )
    active_mass = simulate_case(
        case,
        catalyst_mass_basis="active_in2o3",
        integration_steps=200,
    )
    swapped = simulate_case(
        case,
        swap_adsorption_enthalpies=True,
        integration_steps=200,
    )
    assert gauge["pressure_bar_absolute_used"] == pytest.approx(41.01325)
    assert active_mass["co2_conversion_percent_pred"] < primary["co2_conversion_percent_pred"]
    assert swapped["adsorption_enthalpy_assignment"] == "prose_swapped"
    assert swapped["meoh_selectivity_percent_pred"] != pytest.approx(
        primary["meoh_selectivity_percent_pred"], abs=0.01
    )


def test_validation_grid_preserves_all_six_si_conditions():
    rows = predict_validation_grid(integration_steps=150)
    assert [row["run_id"] for row in rows] == ["6a", "6b", "6c", "6d", "6e", "6f"]
    assert all(row["model_scope"] == "Ghosh_2021_unsupported_In2O3_only" for row in rows)
