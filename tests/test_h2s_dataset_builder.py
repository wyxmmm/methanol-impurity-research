import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
H2S_DIR = ROOT / "data" / "processed" / "h2s"


def read_csv(name: str):
    with (H2S_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_core_dataset_has_only_the_eligible_prasnikar_record():
    rows = read_csv("h2s_core_model_ready.csv")
    assert len(rows) == 1
    row = rows[0]
    assert row["experimental_unit_id"] == "T2-004-CUZNAL-ACT"
    assert row["stratum"] == "core_continuous_cuznal"
    assert float(row["activity_retention_fraction"]) == 0.9


def test_schuhle_h2s_correction_is_explicit_and_legacy_error_is_absent():
    rows = read_csv("h2s_all_curated_observations.csv")
    corrected = next(
        row
        for row in rows
        if row["experimental_unit_id"] == "T1-001-CU-H2S-4H-CORRECTED"
    )
    assert float(corrected["h2s_concentration_ppm"]) == 400
    assert float(corrected["clean_or_initial_value"]) == 0.54
    assert float(corrected["h2s_value"]) == 0.45
    assert abs(float(corrected["activity_retention_fraction"]) - 5 / 6) < 1e-9
    assert not any(
        row["experimental_unit_id"].startswith("T1-001-CU-H2S-18H")
        for row in rows
    )


def test_henriksson_second_stage_uses_the_preceding_recovery_baseline():
    rows = read_csv("h2s_supporting_evidence.csv")
    stage2 = next(
        row
        for row in rows
        if row["experimental_unit_id"] == "T1-002-PFR-CU-STAGE2-YIELD"
    )
    assert float(stage2["clean_or_initial_value"]) == 5.4
    assert float(stage2["h2s_value"]) == 3.7
    assert "follows 33.2 ppm" in stage2["cumulative_exposure"]


def test_kinetic_equations_remain_in_separate_comparable_groups():
    rows = read_csv("h2s_kinetic_evidence.csv")
    assert len(rows) == 38
    groups = {row["comparable_group"] for row in rows}
    assert groups == {
        "wood_observed_decay_rate",
        "wood_poisoning_constant",
        "prasnikar_intrinsic_coefficient",
        "ying1995_decomposition_derivative",
        "ying1995_decomposition_intrinsic_model",
    }


def test_gap_matrix_and_summary_fail_the_global_fit_gate_transparently():
    gaps = {row["gap_id"]: row for row in read_csv("h2s_evidence_gap_matrix.csv")}
    assert gaps["G01"]["current_evidence"] == "1"
    assert gaps["G01"]["required_evidence"] == "4"
    assert gaps["G01"]["status"] == "open"
    assert gaps["G05"]["status"] == "closed"
    assert gaps["G11"]["status"] == "closed"

    summary = json.loads(
        (H2S_DIR / "h2s_dataset_summary.json").read_text(encoding="utf-8")
    )
    assert summary["core_model_ready"] == 1
    assert summary["global_fit_gate_passed"] is False


def test_new_research_is_supporting_only_and_does_not_inflate_core():
    all_rows = read_csv("h2s_all_curated_observations.csv")
    assert sum(row["study_id"] == "T3-001" for row in all_rows) == 7
    assert sum(row["study_id"] == "T3-002" for row in all_rows) == 28
    assert sum(
        row["eligibility_status"] == "matched_cox_proxy_only"
        for row in all_rows
    ) == 8
    assert all(
        row["stratum"] == "mechanism_only"
        for row in all_rows
        if row["study_id"] in {"T3-001", "T3-002"}
    )
