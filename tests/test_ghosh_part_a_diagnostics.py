import json

import pandas as pd
import pytest

from src.ghosh_external_validation_batch import load_candidates
from src.ghosh_part_a_diagnostics import (
    DEFAULT_CANDIDATES,
    DEFAULT_DESCRIPTORS,
    audit_candidates,
    build_outputs,
    grouped_metrics,
)


def test_yang_main_article_resolution_releases_rows_with_lower_certainty():
    candidates = load_candidates(DEFAULT_CANDIDATES)
    descriptors = pd.read_csv(DEFAULT_DESCRIPTORS)
    audit = audit_candidates(candidates, descriptors)
    yang = audit.loc[audit["study_id"].eq("YANG-2020")]
    assert len(yang) == 26
    assert yang["space_velocity_basis_status_audited"].eq(
        "mass_normalized_flow_verified_in_main_article"
    ).all()
    assert yang["scientific_interpretation_status"].eq(
        "primary_interpretable_lower_certainty_graph_digitized"
    ).all()
    assert yang["row_evidence_class"].eq("graph_digitized").all()
    assert yang["absolute_flow_status"].eq(
        "normalized_mass_only_absolute_flow_not_physical"
    ).all()


def test_grouped_metrics_are_study_balanced_and_response_separated():
    sample = pd.DataFrame(
        {
            "study_id": ["A", "A", "B"],
            "solver_converged": [True, True, True],
            "scientific_interpretation_status": ["primary_interpretable"] * 3,
            "co2_conversion_percent_pred": [2.0, 4.0, 12.0],
            "observed_co2_conversion_percent": [1.0, 1.0, 2.0],
            "co2_conversion_signed_error_pred_minus_obs": [1.0, 3.0, 10.0],
            "meoh_selectivity_percent_pred": [2.0, 4.0, 12.0],
            "observed_meoh_selectivity_percent": [1.0, 1.0, 2.0],
            "meoh_selectivity_signed_error_pred_minus_obs": [1.0, 3.0, 10.0],
            "meoh_yield_percent_pred": [2.0, 4.0, 12.0],
            "observed_meoh_yield_for_validation_percent": [1.0, 1.0, 2.0],
            "meoh_yield_signed_error_pred_minus_obs": [1.0, 3.0, 10.0],
            "domain_category": ["inside_original_numeric_domain"] * 3,
            "phase_category": ["cubic"] * 3,
            "row_evidence_class": ["directly_reported"] * 3,
            "extraction_method": ["reported_table"] * 3,
            "preparation_family": ["precipitation_calcined"] * 3,
            "inert_status": ["no_inert_reported"] * 3,
            "co2_conversion_evidence_class": ["directly_reported"] * 3,
            "meoh_selectivity_evidence_class": ["directly_reported"] * 3,
            "meoh_yield_evidence_class": ["directly_reported"] * 3,
        }
    )
    metrics = grouped_metrics(sample)
    row = metrics.loc[
        metrics["group_dimension"].eq("analysis_scope")
        & metrics["group_value"].eq("primary_all_after_yang_resolution")
        & metrics["response"].eq("co2_conversion")
    ].iloc[0]
    assert row["mae"] == pytest.approx((1 + 3 + 10) / 3)
    assert row["study_balanced_mae"] == pytest.approx((2 + 10) / 2)


def test_part_a_build_is_additive_and_preserves_yield_decomposition(tmp_path):
    decision = build_outputs(
        DEFAULT_CANDIDATES,
        DEFAULT_DESCRIPTORS,
        tmp_path,
        integration_steps=30,
    )
    residuals = pd.read_csv(tmp_path / "locked_residuals_by_condition.csv")
    audit = pd.read_csv(tmp_path / "input_provenance_audit.csv")
    integrity = json.loads((tmp_path / "data_integrity_manifest.json").read_text())

    assert len(audit) == len(residuals) == 88
    assert residuals["reactorcase_run_id"].is_unique
    assert residuals["solver_converged"].all()
    assert residuals["parameter_refit_performed"].eq(False).all()
    assert decision["scientifically_interpretable_rows"] == 88
    assert decision["held_rows_after_yang_source_review"] == 0
    assert integrity["source_hashes_unchanged"] is True
    assert integrity["input_ids_equal_audit_ids"] is True
    assert integrity["input_ids_equal_residual_ids"] is True
    assert residuals["yield_error_decomposition_sum_pp"].to_numpy() == pytest.approx(
        residuals["yield_error_vs_calculated_xs_pp"].to_numpy(), abs=1e-10
    )
    assert len(list((tmp_path / "plots").glob("*.svg"))) == 10
    assert (tmp_path / "grouped_diagnostic_metrics.csv").exists()
    assert (tmp_path / "residual_trend_summary.csv").exists()
    assert (tmp_path / "adsorption_assignment_sensitivity_metrics.csv").exists()
