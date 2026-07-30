"""H2S evidence engine with explicit no-fit safeguards.

The strict cross-study model gate currently fails. This module therefore
implements only source-specific calculations and bounded interpolation. Every
estimate carries its scientific target and domain so that a decomposition or
COx-conversion proxy cannot be mistaken for methanol-synthesis activity.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

_MPL_CACHE = Path(tempfile.gettempdir()) / "h2s_evidence_engine_matplotlib"
_MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
H2S_DATA = ROOT / "data" / "processed" / "h2s"
CURATED = ROOT / "data" / "curated" / "h2s"
RESULTS = ROOT / "results" / "h2s"

WOOD_RATES = {1.6: 0.011, 3.2: 0.025, 33.0: 0.153}
GAS_CONSTANT_J_MOL_K = 8.314


class DomainError(ValueError):
    """Raised when a source-specific equation is used outside its evidence domain."""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def require_close(value: float, expected: float, label: str, tolerance: float = 1e-9) -> None:
    if not math.isclose(value, expected, rel_tol=0, abs_tol=tolerance):
        raise DomainError(f"{label} must be {expected:g}; received {value:g}.")


def interpolate(points: list[tuple[float, float]], x: float) -> float:
    if x < points[0][0] or x > points[-1][0]:
        raise DomainError(
            f"time_h must be within [{points[0][0]:g}, {points[-1][0]:g}]."
        )
    for x0, y0 in points:
        if math.isclose(x, x0, rel_tol=0, abs_tol=1e-12):
            return y0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            weight = (x - x0) / (x1 - x0)
            return y0 + weight * (y1 - y0)
    raise AssertionError("Interpolation interval not found.")


def prasnikar_endpoint_interpolation(time_h: float, h2s_ppm: float = 8.1) -> float:
    """Interpolate the sole eligible CZA endpoint at its exact conditions.

    This is not a concentration-response equation. It only joins the reported
    normalized endpoints (0 h, 1.0) and (30 h, 0.9).
    """

    require_close(h2s_ppm, 8.1, "h2s_ppm")
    if not 0 <= time_h <= 30:
        raise DomainError("time_h must be within [0, 30] for the CZA endpoint.")
    return 1.0 - (0.1 / 30.0) * time_h


def wood_exponential_retention(h2s_ppm: float, time_h: float) -> float:
    """Calculate retention from one of Wood's exact reported decay rates."""

    if time_h < 0:
        raise DomainError("time_h must be nonnegative.")
    concentration = next(
        (value for value in WOOD_RATES if math.isclose(h2s_ppm, value, abs_tol=1e-9)),
        None,
    )
    if concentration is None:
        raise DomainError(
            "h2s_ppm must be one of Wood's reported C79-1 runs: 1.6, 3.2, or 33."
        )
    return math.exp(-WOOD_RATES[concentration] * time_h)


def he_points() -> list[dict[str, str]]:
    return read_csv(CURATED / "he_2020_si_digitized.csv")


def he_cox_proxy(time_h: float, h2s_ppm: float = 50.0) -> float:
    """Interpolate the matched H2S/clean COx-conversion ratio in He Fig. S1."""

    require_close(h2s_ppm, 50.0, "h2s_ppm")
    points = [
        (float(row["exposure_h"]), float(row["h2s_to_clean_ratio"]))
        for row in he_points()
    ]
    return interpolate(points, time_h)


def ying_time_series() -> list[dict[str, str]]:
    return read_csv(
        ROOT / "data" / "processed" / "sulfur_batch_b_ying_1995_time_series.csv"
    )


def ying_empirical_activity(
    time_h: float, h2s_ppm: float = 211.0, temperature_c: float = 260.0
) -> float:
    """Interpolate Ying Part I Table II within the exact Run 1 domain."""

    require_close(h2s_ppm, 211.0, "h2s_ppm")
    require_close(temperature_c, 260.0, "temperature_c")
    points = [
        (float(row["time_on_stream_h"]), float(row["with_impurity_value"]))
        for row in ying_time_series()
    ]
    return interpolate(points, time_h)


def ying_intrinsic_rate_constant(h2s_ppm: float, temperature_c: float) -> float:
    """Return lambda in -da/dt=lambda*a from Ying Part I Eq. 7."""

    if not 105 <= h2s_ppm <= 281:
        raise DomainError("h2s_ppm must be within Ying's fitted range [105, 281].")
    if not 250 <= temperature_c <= 265:
        raise DomainError(
            "temperature_c must be within Ying's fitted range [250, 265]."
        )
    temperature_k = temperature_c + 273.15
    return (
        0.1504
        * 10**5
        * math.exp(-81128 / (GAS_CONSTANT_J_MOL_K * temperature_k))
        * h2s_ppm
    )


def ying_intrinsic_activity(
    time_h: float,
    h2s_ppm: float,
    temperature_c: float,
    initial_activity: float = 1.0,
) -> float:
    """Analytic solution to Ying Part I Eq. 7 within its fitted domain."""

    if time_h < 0:
        raise DomainError("time_h must be nonnegative.")
    if not 0 < initial_activity <= 1:
        raise DomainError("initial_activity must be in (0, 1].")
    rate = ying_intrinsic_rate_constant(h2s_ppm, temperature_c)
    return initial_activity * math.exp(-rate * time_h)


MODEL_FUNCTIONS: dict[str, Callable[..., float]] = {
    "prasnikar_cza_endpoint": prasnikar_endpoint_interpolation,
    "wood_c79_exponential": wood_exponential_retention,
    "he_matched_cox_proxy": he_cox_proxy,
    "ying_empirical_decomposition": ying_empirical_activity,
    "ying_intrinsic_decomposition": ying_intrinsic_activity,
}


def estimate(
    model_id: str,
    h2s_ppm: float,
    time_h: float,
    temperature_c: float | None = None,
) -> dict[str, Any]:
    if model_id not in MODEL_FUNCTIONS:
        raise DomainError(f"Unknown model_id: {model_id}")
    if model_id == "ying_empirical_decomposition":
        value = ying_empirical_activity(
            time_h,
            h2s_ppm,
            260.0 if temperature_c is None else temperature_c,
        )
    elif model_id == "ying_intrinsic_decomposition":
        if temperature_c is None:
            raise DomainError("temperature_c is required for the Ying equation.")
        value = ying_intrinsic_activity(time_h, h2s_ppm, temperature_c)
    else:
        value = MODEL_FUNCTIONS[model_id](time_h=time_h, h2s_ppm=h2s_ppm)

    metadata = scenario_catalog_by_id()[model_id]
    return {
        "model_id": model_id,
        "estimate": value,
        "target": metadata["target"],
        "unit": metadata["unit"],
        "domain": metadata["domain"],
        "primary_synthesis_prediction": metadata["primary_synthesis_prediction"],
        "warning": metadata["warning"],
    }


def scenario_catalog() -> list[dict[str, str]]:
    return [
        {
            "model_id": "prasnikar_cza_endpoint",
            "study_id": "T2-004",
            "target": "normalized methanol-synthesis activity",
            "unit": "dimensionless",
            "domain": "CZA; 8.1 ppm H2S; 240°C; 20 bar; H2:CO2=3; GHSV 40000 h^-1; 0–30 h",
            "method": "linear interpolation between the reported 0 h and 30 h endpoints",
            "primary_synthesis_prediction": "bounded exact-condition interpolation only",
            "uncertainty": "no replicate/error estimate reported; 30 h endpoint is approximate",
            "warning": "Do not vary concentration or extrapolate beyond 30 h.",
        },
        {
            "model_id": "wood_c79_exponential",
            "study_id": "T2-002",
            "target": "methanol-synthesis activity retention from reported decay rate",
            "unit": "dimensionless",
            "domain": "C79-1; exact runs at 1.6, 3.2, or 33 ppm; 230°C; 34.47 bar gauge; GHSV 10000 h^-1",
            "method": "A(t)=exp(-k_obs t), using k_obs=0.011, 0.025, or 0.153 h^-1",
            "primary_synthesis_prediction": "separate historical catalyst/source only",
            "uncertainty": "no row-level uncertainty or raw time series available",
            "warning": "33 ppm was reported as transport-influenced; do not transfer across catalysts.",
        },
        {
            "model_id": "he_matched_cox_proxy",
            "study_id": "T1-004",
            "target": "H2S/clean normalized COx-conversion ratio",
            "unit": "dimensionless",
            "domain": "industrial CZA; 50 ppm; 60 bar; syngas; 50–1000 h with 483/523 K cycling",
            "method": "piecewise-linear interpolation of digitized Fig. S1 ratios",
            "primary_synthesis_prediction": "no",
            "uncertainty": "approximate digitization; near-zero H2S points are resolution-limited",
            "warning": "COx conversion is not methanol output; accelerated temperature cycling applies.",
        },
        {
            "model_id": "ying_empirical_decomposition",
            "study_id": "T3-001",
            "target": "relative methanol-decomposition activity",
            "unit": "dimensionless",
            "domain": "C207; 211 ppm; 260°C; atmospheric; 0–24 h",
            "method": "piecewise-linear interpolation of exact Table II values",
            "primary_synthesis_prediction": "no",
            "uncertainty": "source reports no replicate/error estimate",
            "warning": "Reverse reaction and atmospheric conditions; not methanol synthesis.",
        },
        {
            "model_id": "ying_intrinsic_decomposition",
            "study_id": "T3-001",
            "target": "relative methanol-decomposition activity",
            "unit": "dimensionless",
            "domain": "C207; 105–281 ppm; 250–265°C; atmospheric",
            "method": "analytic solution to source Eq. 7",
            "primary_synthesis_prediction": "no",
            "uncertainty": "source-fitted equation; no external-study validation",
            "warning": "Reverse reaction; fitted to one study and not transferable to synthesis.",
        },
    ]


def scenario_catalog_by_id() -> dict[str, dict[str, str]]:
    return {row["model_id"]: row for row in scenario_catalog()}


def he_digitization_bounds(clean: float, h2s: float, delta: float = 0.01) -> tuple[float, float]:
    """Conservative figure-resolution sensitivity, not a confidence interval."""

    lower = max(0.0, h2s - delta) / (clean + delta)
    denominator = clean - delta
    upper = 1.0 if denominator <= 0 else min(1.0, (h2s + delta) / denominator)
    return lower, upper


def build_predictions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(
        model_id: str,
        study_id: str,
        target: str,
        ppm: float,
        temp: float,
        pressure: float | str,
        time_h: float,
        value: float,
        lower: float | str = "",
        upper: float | str = "",
        uncertainty: str = "",
    ) -> None:
        rows.append(
            {
                "model_id": model_id,
                "study_id": study_id,
                "target": target,
                "h2s_ppm": ppm,
                "temperature_c": temp,
                "pressure_bar": pressure,
                "time_h": time_h,
                "estimate": value,
                "lower_sensitivity": lower,
                "upper_sensitivity": upper,
                "uncertainty_status": uncertainty,
                "primary_model_eligible": model_id == "prasnikar_cza_endpoint",
            }
        )

    for time_h in [0, 5, 10, 20, 30]:
        add(
            "prasnikar_cza_endpoint",
            "T2-004",
            "normalized methanol-synthesis activity",
            8.1,
            240,
            20,
            time_h,
            prasnikar_endpoint_interpolation(time_h),
            uncertainty="not reported; interpolation is conditional on exact source conditions",
        )

    for ppm in WOOD_RATES:
        for time_h in [0, 1, 5, 10, 24]:
            add(
                "wood_c79_exponential",
                "T2-002",
                "methanol-synthesis activity retention",
                ppm,
                230,
                "34.47 gauge",
                time_h,
                wood_exponential_retention(ppm, time_h),
                uncertainty="not reported; source-specific coefficient projection",
            )

    for source in he_points():
        clean = float(source["clean_normalized_cox_conversion"])
        h2s = float(source["h2s_normalized_cox_conversion"])
        lower, upper = he_digitization_bounds(clean, h2s)
        add(
            "he_matched_cox_proxy",
            "T1-004",
            "H2S/clean normalized COx-conversion ratio",
            50,
            210,
            60,
            float(source["exposure_h"]),
            float(source["h2s_to_clean_ratio"]),
            lower,
            upper,
            "±0.01 absolute trace-read sensitivity; not a confidence interval",
        )

    for source in ying_time_series():
        time_h = float(source["time_on_stream_h"])
        add(
            "ying_empirical_decomposition",
            "T3-001",
            "relative methanol-decomposition activity",
            211,
            260,
            1.02,
            time_h,
            float(source["with_impurity_value"]),
            uncertainty="exact table value; no replicate/error estimate",
        )
        add(
            "ying_intrinsic_decomposition",
            "T3-001",
            "relative methanol-decomposition activity",
            211,
            260,
            1.02,
            time_h,
            ying_intrinsic_activity(time_h, 211, 260),
            uncertainty="source-fitted Eq. 7; no external validation",
        )
    return rows


def build_reproduction() -> tuple[list[dict[str, Any]], dict[str, float]]:
    rows: list[dict[str, Any]] = []
    squared: list[float] = []
    absolute: list[float] = []
    for source in ying_time_series():
        time_h = float(source["time_on_stream_h"])
        observed = float(source["with_impurity_value"])
        predicted = ying_intrinsic_activity(time_h, 211, 260)
        residual = predicted - observed
        rows.append(
            {
                "model_id": "ying_intrinsic_decomposition",
                "study_id": "T3-001",
                "evaluation_type": "within-source reproduction; not validation",
                "time_h": time_h,
                "observed": observed,
                "predicted": predicted,
                "residual": residual,
            }
        )
        squared.append(residual**2)
        absolute.append(abs(residual))
    metrics = {
        "n": float(len(rows)),
        "mae": sum(absolute) / len(absolute),
        "rmse": math.sqrt(sum(squared) / len(squared)),
    }
    return rows, metrics


def build_gate_and_decision() -> tuple[list[dict[str, str]], dict[str, Any]]:
    gaps = read_csv(H2S_DATA / "h2s_evidence_gap_matrix.csv")
    gate_ids = ["G01", "G02", "G03", "G04", "G05"]
    gate_rows = [row for row in gaps if row["gap_id"] in gate_ids]
    passed = all(row["status"] == "closed" for row in gate_rows)
    decision = {
        "global_fit_gate_passed": passed,
        "decision": (
            "fit universal model" if passed else "do not fit universal model"
        ),
        "implemented_fallback": (
            "source-specific equations, bounded interpolation, domain checks, "
            "digitization sensitivity, and explicit non-estimable study holdout"
        ),
        "primary_core_studies": 1,
        "primary_core_experimental_units": 1,
        "primary_core_h2s_concentrations": 1,
        "whole_study_validation_status": "not_estimable",
        "reason": (
            "Holding out the sole core study leaves zero training studies. "
            "No honest cross-study predictive error can be calculated."
        ),
    }
    return gate_rows, decision


def build_holdout_audit() -> list[dict[str, Any]]:
    return [
        {
            "model_id": "universal_core_h2s_model",
            "held_out_study": "T2-004",
            "training_studies": 0,
            "test_studies": 1,
            "status": "not_estimable",
            "prediction": "",
            "observed_retention": 0.9,
            "reason": "The only eligible core study was held out, leaving no training evidence.",
        }
    ]


def render_plot(predictions: list[dict[str, Any]], output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)

    p = [r for r in predictions if r["model_id"] == "prasnikar_cza_endpoint"]
    axes[0, 0].plot(
        [r["time_h"] for r in p],
        [r["estimate"] for r in p],
        marker="o",
        color="#2B6CB0",
    )
    axes[0, 0].set_title("Prašnikar CZA: exact-condition interpolation")
    axes[0, 0].set_ylabel("Normalized MeOH activity")

    for ppm, color in [(1.6, "#2F855A"), (3.2, "#D69E2E"), (33.0, "#C53030")]:
        group = [
            r
            for r in predictions
            if r["model_id"] == "wood_c79_exponential"
            and float(r["h2s_ppm"]) == ppm
        ]
        axes[0, 1].plot(
            [r["time_h"] for r in group],
            [r["estimate"] for r in group],
            marker="o",
            label=f"{ppm:g} ppm",
            color=color,
        )
    axes[0, 1].set_title("Wood C79-1: reported exponential rates")
    axes[0, 1].set_ylabel("Activity retention")
    axes[0, 1].legend(frameon=False)

    h = [r for r in predictions if r["model_id"] == "he_matched_cox_proxy"]
    axes[1, 0].plot(
        [r["time_h"] for r in h],
        [r["estimate"] for r in h],
        marker="o",
        color="#805AD5",
    )
    axes[1, 0].fill_between(
        [r["time_h"] for r in h],
        [r["lower_sensitivity"] for r in h],
        [r["upper_sensitivity"] for r in h],
        alpha=0.18,
        color="#805AD5",
    )
    axes[1, 0].set_title("He SI: matched COx proxy (not MeOH output)")
    axes[1, 0].set_ylabel("H₂S / clean COx ratio")

    ye = [r for r in predictions if r["model_id"] == "ying_empirical_decomposition"]
    ym = [
        r
        for r in predictions
        if r["model_id"] == "ying_intrinsic_decomposition"
    ]
    axes[1, 1].plot(
        [r["time_h"] for r in ye],
        [r["estimate"] for r in ye],
        "o",
        label="Table II",
        color="#2D3748",
    )
    axes[1, 1].plot(
        [r["time_h"] for r in ym],
        [r["estimate"] for r in ym],
        "-",
        label="Eq. 7",
        color="#C05621",
    )
    axes[1, 1].set_title("Ying: methanol decomposition (not synthesis)")
    axes[1, 1].set_ylabel("Relative activity")
    axes[1, 1].legend(frameon=False)

    for axis in axes.flat:
        axis.set_xlabel("Exposure time (h)")
        axis.set_ylim(bottom=0)
        axis.grid(alpha=0.25)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="svg")
    fig.savefig(output.with_suffix(".png"), dpi=180)
    plt.close(fig)


def build_outputs() -> dict[str, Any]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    predictions = build_predictions()
    reproduction, reproduction_metrics = build_reproduction()
    gate_rows, decision = build_gate_and_decision()
    holdout = build_holdout_audit()
    catalog = scenario_catalog()

    prediction_fields = [
        "model_id",
        "study_id",
        "target",
        "h2s_ppm",
        "temperature_c",
        "pressure_bar",
        "time_h",
        "estimate",
        "lower_sensitivity",
        "upper_sensitivity",
        "uncertainty_status",
        "primary_model_eligible",
    ]
    reproduction_fields = [
        "model_id",
        "study_id",
        "evaluation_type",
        "time_h",
        "observed",
        "predicted",
        "residual",
    ]
    holdout_fields = [
        "model_id",
        "held_out_study",
        "training_studies",
        "test_studies",
        "status",
        "prediction",
        "observed_retention",
        "reason",
    ]
    gate_fields = [
        "gap_id",
        "model_requirement",
        "current_evidence",
        "required_evidence",
        "numeric_gap",
        "status",
        "priority",
        "research_target",
        "unlock_condition",
    ]
    catalog_fields = [
        "model_id",
        "study_id",
        "target",
        "unit",
        "domain",
        "method",
        "primary_synthesis_prediction",
        "uncertainty",
        "warning",
    ]

    write_csv(RESULTS / "scenario_predictions.csv", predictions, prediction_fields)
    write_csv(RESULTS / "source_model_reproduction.csv", reproduction, reproduction_fields)
    write_csv(RESULTS / "held_out_study_validation.csv", holdout, holdout_fields)
    write_csv(RESULTS / "evidence_gate.csv", gate_rows, gate_fields)
    write_csv(RESULTS / "scenario_catalog.csv", catalog, catalog_fields)
    render_plot(predictions, RESULTS / "h2s_source_specific_scenarios.svg")

    decision["ying_eq7_within_source_reproduction"] = reproduction_metrics
    decision["generated_files"] = [
        "results/h2s/model_decision.json",
        "results/h2s/evidence_gate.csv",
        "results/h2s/scenario_catalog.csv",
        "results/h2s/scenario_predictions.csv",
        "results/h2s/source_model_reproduction.csv",
        "results/h2s/held_out_study_validation.csv",
        "results/h2s/h2s_source_specific_scenarios.svg",
        "results/h2s/h2s_source_specific_scenarios.png",
    ]
    (RESULTS / "model_decision.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    return decision


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=sorted(MODEL_FUNCTIONS),
        help="Return one source-specific estimate instead of rebuilding outputs.",
    )
    parser.add_argument("--h2s-ppm", type=float)
    parser.add_argument("--time-h", type=float)
    parser.add_argument("--temperature-c", type=float)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.model:
        if args.h2s_ppm is None or args.time_h is None:
            raise SystemExit("--h2s-ppm and --time-h are required with --model.")
        print(
            json.dumps(
                estimate(
                    args.model,
                    h2s_ppm=args.h2s_ppm,
                    time_h=args.time_h,
                    temperature_c=args.temperature_c,
                ),
                indent=2,
            )
        )
        return
    print(json.dumps(build_outputs(), indent=2))


if __name__ == "__main__":
    main()
