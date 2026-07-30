import csv
import json
import math
from pathlib import Path

import pytest

from src.h2s_evidence_engine import (
    DomainError,
    build_outputs,
    he_cox_proxy,
    prasnikar_endpoint_interpolation,
    wood_exponential_retention,
    ying_empirical_activity,
    ying_intrinsic_activity,
    ying_intrinsic_rate_constant,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "h2s"


def test_prasnikar_interpolation_is_bounded_to_the_single_core_endpoint():
    assert prasnikar_endpoint_interpolation(0) == 1
    assert prasnikar_endpoint_interpolation(30) == pytest.approx(0.9)
    with pytest.raises(DomainError):
        prasnikar_endpoint_interpolation(31)
    with pytest.raises(DomainError):
        prasnikar_endpoint_interpolation(10, h2s_ppm=10)


def test_wood_uses_only_exact_reported_concentration_runs():
    assert wood_exponential_retention(1.6, 10) == pytest.approx(
        math.exp(-0.011 * 10)
    )
    assert wood_exponential_retention(33, 10) == pytest.approx(
        math.exp(-0.153 * 10)
    )
    with pytest.raises(DomainError):
        wood_exponential_retention(5, 10)


def test_he_and_ying_empirical_models_reproduce_source_points():
    assert he_cox_proxy(100) == pytest.approx(0.371)
    assert ying_empirical_activity(24) == pytest.approx(0.468)
    with pytest.raises(DomainError):
        he_cox_proxy(25)
    with pytest.raises(DomainError):
        ying_empirical_activity(24, h2s_ppm=200)


def test_ying_equation_uses_the_verified_10_to_the_5_preexponential():
    rate = ying_intrinsic_rate_constant(211, 260)
    assert rate == pytest.approx(0.03571401606259337)
    assert ying_intrinsic_activity(24, 211, 260) == pytest.approx(
        math.exp(-rate * 24)
    )
    with pytest.raises(DomainError):
        ying_intrinsic_activity(10, 50, 260)


def test_outputs_make_the_universal_holdout_non_estimable():
    decision = build_outputs()
    assert decision["global_fit_gate_passed"] is False
    assert decision["whole_study_validation_status"] == "not_estimable"

    with (RESULTS / "held_out_study_validation.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        holdout = list(csv.DictReader(handle))
    assert holdout == [
        {
            "model_id": "universal_core_h2s_model",
            "held_out_study": "T2-004",
            "training_studies": "0",
            "test_studies": "1",
            "status": "not_estimable",
            "prediction": "",
            "observed_retention": "0.9",
            "reason": "The only eligible core study was held out, leaving no training evidence.",
        }
    ]

    saved = json.loads((RESULTS / "model_decision.json").read_text(encoding="utf-8"))
    assert saved["decision"] == "do not fit universal model"
    assert (RESULTS / "h2s_source_specific_scenarios.svg").exists()
    assert (RESULTS / "h2s_source_specific_scenarios.png").exists()
