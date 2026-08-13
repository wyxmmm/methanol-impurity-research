import pandas as pd
import pytest

from src.ghosh_external_validation_batch import (
    DEFAULT_INPUT,
    build_outputs,
    load_candidates,
    predict_rows,
)


def test_candidate_table_contains_all_external_yield_rows():
    data = load_candidates(DEFAULT_INPUT)
    assert len(data) == 88
    assert data["study_id"].nunique() == 6
    assert data["reactorcase_run_id"].is_unique


def test_batch_prediction_preserves_yield_identity_and_inert_feed():
    data = load_candidates(DEFAULT_INPUT)
    sample = pd.concat(
        [
            data.loc[data["inert_mole_fraction"].notna()].head(1),
            data.loc[data["inert_mole_fraction"].isna()].head(1),
        ],
        ignore_index=True,
    )
    result = predict_rows(sample, integration_steps=40)
    assert result["solver_converged"].all()
    expected_yield = (
        result["co2_conversion_percent_pred"]
        * result["meoh_selectivity_percent_pred"]
        / 100.0
    )
    assert result["meoh_yield_percent_pred"].to_numpy() == pytest.approx(
        expected_yield.to_numpy(), abs=1e-12
    )
    inert_row = result.loc[result["inert_mole_fraction"].notna()].iloc[0]
    assert inert_row["inert_inlet_mole_fraction"] == pytest.approx(
        inert_row["inert_mole_fraction"]
    )
    assert not result["parameter_refit_performed"].any()


def test_build_writes_one_output_for_every_input(tmp_path):
    decision = build_outputs(DEFAULT_INPUT, tmp_path, integration_steps=30)
    output = pd.read_csv(tmp_path / "methanol_output_table.csv")
    assert len(output) == 88
    assert output["solver_converged"].all()
    assert decision["parameter_refit_performed"] is False
    assert decision["external_conditions_predicted"] == 88
    assert (tmp_path / "validation_metrics.csv").exists()
    assert (tmp_path / "validation_summary.md").exists()
