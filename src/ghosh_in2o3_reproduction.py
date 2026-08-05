"""Build reproducible evidence outputs for the Ghosh In2O3 PFR model."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.ghosh_in2o3_pfr import (
    ROOT,
    ReactorCase,
    error_metrics,
    predict_validation_grid,
    reproduce_calibration_grid,
    simulate_case,
)


DEFAULT_OUTPUT_DIR = ROOT / "results" / "unsupported_in2o3" / "ghosh_pfr"


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    records = list(rows)
    if not records:
        raise ValueError(f"Cannot write an empty table to {path}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    integration_steps: int = 800,
) -> dict[str, Any]:
    """Generate calibration, sensitivity, and validation-input artifacts."""

    primary = reproduce_calibration_grid(integration_steps=integration_steps)
    metrics = error_metrics(primary)
    metrics.update(
        {
            "dataset": "Ghosh_2021_Table_2",
            "catalyst": "unsupported_In2O3_in_2_to_1_In2O3_silica_composite_bed",
            "parameter_refit_performed": False,
            "primary_pressure_interpretation": "reported_absolute",
            "primary_catalyst_mass_basis": "total_composite",
            "primary_adsorption_enthalpy_assignment": "Table_4",
            "thermochemistry_reproduction": "independent_NASA7_implementation_not_authors_unpublished_correlations",
        }
    )
    _write_csv(output_dir / "calibration_predictions.csv", primary)
    _write_json(output_dir / "calibration_metrics.json", metrics)

    variants = (
        ("primary", {}),
        ("reported_pressure_as_gauge", {"pressure_interpretation": "reported_gauge"}),
        ("active_in2o3_mass_only", {"catalyst_mass_basis": "active_in2o3"}),
        ("prose_adsorption_enthalpy_assignment", {"swap_adsorption_enthalpies": True}),
    )
    sensitivity: list[dict[str, Any]] = []
    for label, options in variants:
        rows = reproduce_calibration_grid(
            integration_steps=max(400, integration_steps // 2),
            **options,
        )
        sensitivity.append({"variant": label, **error_metrics(rows)})
    _write_csv(output_dir / "source_ambiguity_sensitivity.csv", sensitivity)

    validation = predict_validation_grid(integration_steps=integration_steps)
    for row in validation:
        row["experimental_output_availability"] = (
            "not_tabulated; shown_only_as_unlabeled_square_in_Figure_12_parity_plot"
        )
        row["quantitative_heldout_error_status"] = "not_identifiable_from_supplied_source"
    _write_csv(output_dir / "validation_input_predictions.csv", validation)

    standard = ReactorCase("standard_convergence", 40.0, 300.0, 9000.0, 3.0)
    convergence = [
        simulate_case(standard, integration_steps=steps)
        for steps in (100, 200, 400, 800, 1600)
    ]
    _write_csv(output_dir / "integration_convergence.csv", convergence)

    decision = {
        "published_model_implemented": True,
        "published_parameters_refit": False,
        "calibration_condition_count": len(primary),
        "calibration_reproduction_quality": {
            "co2_conversion_mae_percentage_points": metrics[
                "co2_conversion_mae_percentage_points"
            ],
            "meoh_selectivity_mae_percentage_points": metrics[
                "meoh_selectivity_mae_percentage_points"
            ],
            "co_selectivity_mae_percentage_points": metrics[
                "co_selectivity_mae_percentage_points"
            ],
            "ch4_selectivity_mae_percentage_points": metrics[
                "ch4_selectivity_mae_percentage_points"
            ],
        },
        "heldout_validation_input_count": len(validation),
        "heldout_quantitative_validation_possible": False,
        "heldout_blocker": (
            "SI Table S3 tabulates the six input conditions but not measured outputs; "
            "Figure 12 shows anonymous parity points that cannot be mapped back to runs 6a-6f."
        ),
        "supported_in2o3_zro2_transfer_allowed": False,
        "supported_transfer_reason": (
            "Support identity, In loading/dispersion, preparation, rate normalization, "
            "and intrinsic selectivity differ across Martin, Wesner, Jiang, and Tsoukalou."
        ),
        "appropriate_use": (
            "transparent reproduction and bounded simulation of the unsupported Ghosh catalyst"
        ),
        "inappropriate_uses": [
            "claiming validation for supported In2O3/ZrO2",
            "predicting sulfur poisoning",
            "extrapolating outside the reported 200-400 C, 20-40 bar, H2/CO2 2-6, WHSV 6000-16000 domain",
        ],
    }
    _write_json(output_dir / "model_reproduction_decision.json", decision)
    return decision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--integration-steps", type=int, default=800)
    args = parser.parse_args()
    decision = build_outputs(args.output_dir, integration_steps=args.integration_steps)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
