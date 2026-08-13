"""Part A diagnostics for the locked Ghosh unsupported-In2O3 model.

This module does not fit or optimize kinetic parameters. It audits the 88
external conditions, resolves the Yang space-velocity wording from the main
article, regenerates locked predictions, stratifies residuals, reports a
predefined adsorption-enthalpy sensitivity, and creates point-level plots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.ghosh_external_validation_batch import load_candidates, predict_rows
from src.ghosh_in2o3_pfr import ReactorCase, simulate_case


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = (
    ROOT
    / "data"
    / "processed"
    / "unsupported_in2o3"
    / "ghosh_yield_validation_candidates.csv"
)
DEFAULT_DESCRIPTORS = (
    ROOT / "data" / "curated" / "unsupported_in2o3" / "catalyst_descriptors.csv"
)
DEFAULT_LOCKED_OUTPUT = (
    ROOT
    / "results"
    / "ghosh_external_validation_all_studies"
    / "methanol_outputs_by_condition.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "results" / "ghosh_part_a_diagnostic_2026-08-12"

RESPONSE_SPECS: dict[str, tuple[str, str, str, str]] = {
    "co2_conversion": (
        "observed_co2_conversion_percent",
        "co2_conversion_percent_pred",
        "co2_conversion_signed_error_pred_minus_obs",
        "CO2 conversion residual (percentage points)",
    ),
    "meoh_selectivity": (
        "observed_meoh_selectivity_percent",
        "meoh_selectivity_percent_pred",
        "meoh_selectivity_signed_error_pred_minus_obs",
        "MeOH selectivity residual (percentage points)",
    ),
    "meoh_yield": (
        "observed_meoh_yield_for_validation_percent",
        "meoh_yield_percent_pred",
        "meoh_yield_signed_error_pred_minus_obs",
        "MeOH yield residual (percentage points)",
    ),
}

RESPONSE_TITLES = {
    "co2_conversion": "CO2 conversion",
    "meoh_selectivity": "MeOH selectivity",
    "meoh_yield": "MeOH yield",
}

NUMERIC_PLOT_SPECS: dict[str, tuple[str, str]] = {
    "temperature": ("temperature_c", "Temperature (deg C)"),
    "pressure": ("pressure_bar_reported", "Reported pressure (bar)"),
    "h2_co2_ratio": ("h2_co2_ratio", "Inlet H2/CO2 ratio"),
    "whsv": ("whsv_ml_gcat_h", "Mass-normalized flow (mL gcat^-1 h^-1)"),
    "inert_fraction": ("inert_mole_fraction_audited", "Inlet inert mole fraction"),
}

CATEGORICAL_PLOT_SPECS: dict[str, tuple[str, str]] = {
    "phase": ("phase_category", "In2O3 phase"),
    "study": ("study_id", "Independent study"),
    "evidence": ("row_evidence_class", "Observation evidence class"),
    "domain": ("domain_category", "Ghosh numeric-domain status"),
    "preparation": ("preparation_family", "Catalyst preparation family"),
}

PHASE_COLORS = {
    "cubic": "#1f77b4",
    "hexagonal": "#d95f02",
    "rhombohedral": "#2ca02c",
    "mixed": "#9467bd",
    "unresolved": "#7f7f7f",
}

EVIDENCE_MARKERS = {
    "directly_reported": "o",
    "calculated_or_derived": "s",
    "graph_digitized": "^",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _clean_text(value: object, default: str = "not_reported") -> str:
    if pd.isna(value) or not str(value).strip():
        return default
    return str(value).strip()


def _preparation_family(value: object) -> str:
    text = _clean_text(value).lower()
    if "commercial" in text:
        return "commercial_air_calcined"
    if "hydrothermal" in text:
        return "hydrothermal_air_calcined"
    if "methanol-based" in text or "inooh" in text:
        return "methanol_route_inooh_calcined"
    if "nanoparticle" in text or "nano material" in text:
        return "nanoparticle_synthesis_calcined"
    if "precipitation" in text:
        return "precipitation_calcined"
    return "other_or_not_reported"


def _response_evidence_class(row: pd.Series, response: str) -> str:
    extraction = _clean_text(row.get("extraction_method"), "").lower()
    if "digitized" in extraction:
        return "graph_digitized"
    if response == "meoh_yield":
        target = _clean_text(row.get("yield_target_method"), "").lower()
        if "calculated" in target:
            return "calculated_or_derived"
    if response == "meoh_selectivity" and "calculated_selectivity" in extraction:
        return "calculated_or_derived"
    return "directly_reported"


def audit_candidates(
    candidates: pd.DataFrame,
    descriptors: pd.DataFrame,
) -> pd.DataFrame:
    """Add audit decisions without changing the controlled candidate table."""

    descriptor_columns = [
        "catalyst_id",
        "material",
        "support_or_dopant",
        "preparation",
        "calcination_c",
        "fresh_crystallite_nm",
        "fresh_bet_m2_g",
        "bed_diluent",
        "notes",
    ]
    selected = descriptors.loc[:, descriptor_columns].rename(
        columns={"notes": "catalyst_descriptor_notes"}
    )
    if selected["catalyst_id"].duplicated().any():
        raise ValueError("catalyst_descriptors.csv must contain unique catalyst_id rows")
    result = candidates.merge(
        selected,
        on="catalyst_id",
        how="left",
        validate="many_to_one",
    )
    if result["preparation"].isna().any():
        missing = sorted(result.loc[result["preparation"].isna(), "catalyst_id"].unique())
        raise ValueError(f"Missing catalyst descriptors for: {missing}")

    result["phase_category"] = (
        result["in2o3_phase"]
        .fillna("unresolved")
        .str.lower()
        .where(
            lambda values: values.isin(
                {"cubic", "hexagonal", "rhombohedral", "mixed"}
            ),
            "unresolved",
        )
    )
    result["preparation_family"] = result["preparation"].map(_preparation_family)
    result["inert_mole_fraction_audited"] = pd.to_numeric(
        result["inert_mole_fraction"], errors="coerce"
    ).fillna(0.0)
    result["inert_status"] = np.where(
        result["inert_mole_fraction_audited"].gt(0), "reported_inert", "no_inert_reported"
    )
    result["domain_category"] = np.where(
        result["ghosh_numeric_domain_status"].eq("inside_Ghosh_numeric_domain"),
        "inside_original_numeric_domain",
        "outside_or_incomplete_domain",
    )

    for response in RESPONSE_SPECS:
        result[f"{response}_evidence_class"] = result.apply(
            _response_evidence_class, axis=1, response=response
        )
    evidence_columns = [f"{response}_evidence_class" for response in RESPONSE_SPECS]
    result["row_evidence_class"] = "directly_reported"
    result.loc[
        result[evidence_columns].eq("calculated_or_derived").any(axis=1),
        "row_evidence_class",
    ] = "calculated_or_derived"
    result.loc[
        result[evidence_columns].eq("graph_digitized").any(axis=1),
        "row_evidence_class",
    ] = "graph_digitized"

    is_yang = result["study_id"].eq("YANG-2020")
    result["yang_space_velocity_resolution"] = "not_applicable"
    result.loc[is_yang, "yang_space_velocity_resolution"] = (
        "verified_mass_normalized_ml_gcat_h_from_main_Fig2_caption"
    )
    result["space_velocity_basis_status_audited"] = result[
        "space_velocity_basis_status"
    ]
    result.loc[is_yang, "space_velocity_basis_status_audited"] = (
        "mass_normalized_flow_verified_in_main_article"
    )
    result["simulation_gate_audited"] = result["simulation_gate"]
    result.loc[is_yang, "simulation_gate_audited"] = (
        "ready_as_lower_certainty_digitized_transfer_test"
    )
    result["scientific_interpretation_status"] = "primary_interpretable"
    result.loc[is_yang, "scientific_interpretation_status"] = (
        "primary_interpretable_lower_certainty_graph_digitized"
    )
    result["absolute_flow_status"] = np.where(
        pd.to_numeric(result["catalyst_mass_g_reported"], errors="coerce").notna(),
        "physical_source_mass_available",
        "normalized_mass_only_absolute_flow_not_physical",
    )
    result["parameter_refit_performed"] = False
    result["audit_version"] = "part_a_2026-08-12"
    return result


def _case_from_row(row: Mapping[str, Any]) -> ReactorCase:
    inert = row.get("inert_mole_fraction")
    inert_fraction = 0.0 if pd.isna(inert) else float(inert)
    inert_species = _clean_text(row.get("inert_species"), "none")
    return ReactorCase(
        run_id=str(row["reactorcase_run_id"]),
        pressure_bar_reported=float(row["pressure_bar_reported"]),
        temperature_c=float(row["temperature_c"]),
        whsv_ml_gcat_h=float(row["whsv_ml_gcat_h"]),
        h2_co2_ratio=float(row["h2_co2_ratio"]),
        catalyst_mass_g=float(row["catalyst_mass_g_for_reactorcase"]),
        inert_mole_fraction=inert_fraction,
        inert_species=inert_species,
    )


def add_locked_predictions(
    candidates: pd.DataFrame,
    audit: pd.DataFrame,
    *,
    integration_steps: int,
) -> pd.DataFrame:
    predictions = predict_rows(candidates, integration_steps=integration_steps)
    audit_columns = [
        "reactorcase_run_id",
        "material",
        "support_or_dopant",
        "preparation",
        "preparation_family",
        "calcination_c",
        "fresh_crystallite_nm",
        "fresh_bet_m2_g",
        "bed_diluent",
        "phase_category",
        "inert_mole_fraction_audited",
        "inert_status",
        "domain_category",
        "row_evidence_class",
        "co2_conversion_evidence_class",
        "meoh_selectivity_evidence_class",
        "meoh_yield_evidence_class",
        "yang_space_velocity_resolution",
        "space_velocity_basis_status_audited",
        "simulation_gate_audited",
        "scientific_interpretation_status",
        "absolute_flow_status",
        "audit_version",
    ]
    result = predictions.merge(
        audit.loc[:, audit_columns],
        on="reactorcase_run_id",
        how="left",
        validate="one_to_one",
    )
    if len(result) != len(candidates):
        raise AssertionError("Locked residual table lost input conditions")

    dx = (
        result["co2_conversion_percent_pred"]
        - result["observed_co2_conversion_percent"]
    )
    ds = (
        result["meoh_selectivity_percent_pred"]
        - result["observed_meoh_selectivity_percent"]
    )
    result["yield_error_conversion_contribution_pp"] = (
        dx * result["observed_meoh_selectivity_percent"] / 100.0
    )
    result["yield_error_selectivity_contribution_pp"] = (
        result["observed_co2_conversion_percent"] * ds / 100.0
    )
    result["yield_error_interaction_contribution_pp"] = dx * ds / 100.0
    result["yield_error_decomposition_sum_pp"] = result[
        [
            "yield_error_conversion_contribution_pp",
            "yield_error_selectivity_contribution_pp",
            "yield_error_interaction_contribution_pp",
        ]
    ].sum(axis=1)
    result["yield_error_vs_calculated_xs_pp"] = (
        result["meoh_yield_percent_pred"]
        - result["observed_meoh_yield_calculated_percent"]
    )
    result["yield_error_cancellation_flag"] = np.where(
        (
            result["yield_error_conversion_contribution_pp"]
            * result["yield_error_selectivity_contribution_pp"]
        ).lt(0),
        "opposing_conversion_and_selectivity_contributions",
        "same_direction_or_zero_contributions",
    )
    return result


def _metric_record(
    group: pd.DataFrame,
    *,
    dimension: str,
    value: str,
    response: str,
) -> dict[str, Any] | None:
    observed_col, predicted_col, residual_col, _ = RESPONSE_SPECS[response]
    subset = group.loc[
        group["solver_converged"].eq(True)
        & group[observed_col].notna()
        & group[predicted_col].notna()
    ].copy()
    if subset.empty:
        return None
    residual = subset[residual_col].to_numpy(float)
    study_mae = (
        subset.assign(_ae=np.abs(residual))
        .groupby("study_id", sort=True)["_ae"]
        .mean()
    )
    return {
        "group_dimension": dimension,
        "group_value": value,
        "response": response,
        "n": int(len(subset)),
        "independent_studies": int(subset["study_id"].nunique()),
        "mae": float(np.mean(np.abs(residual))),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "bias_pred_minus_obs": float(np.mean(residual)),
        "median_absolute_error": float(np.median(np.abs(residual))),
        "study_balanced_mae": float(study_mae.mean()),
        "unit": "percentage_points",
    }


def grouped_metrics(residuals: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    def add(dimension: str, value: str, group: pd.DataFrame) -> None:
        for response in RESPONSE_SPECS:
            record = _metric_record(
                group,
                dimension=dimension,
                value=value,
                response=response,
            )
            if record is not None:
                records.append(record)

    primary = residuals.loc[
        residuals["scientific_interpretation_status"].str.startswith(
            "primary_interpretable"
        )
    ]
    add("analysis_scope", "primary_all_after_yang_resolution", primary)
    add(
        "analysis_scope",
        "primary_non_yang",
        primary.loc[~primary["study_id"].eq("YANG-2020")],
    )
    add(
        "analysis_scope",
        "yang_lower_certainty_digitized",
        primary.loc[primary["study_id"].eq("YANG-2020")],
    )
    for dimension, column in [
        ("numeric_domain", "domain_category"),
        ("phase", "phase_category"),
        ("study", "study_id"),
        ("row_evidence_class", "row_evidence_class"),
        ("extraction_method", "extraction_method"),
        ("preparation_family", "preparation_family"),
        ("inert_status", "inert_status"),
    ]:
        for value, group in primary.groupby(column, dropna=False, sort=True):
            add(dimension, _clean_text(value), group)

    for response in RESPONSE_SPECS:
        evidence_col = f"{response}_evidence_class"
        for value, group in primary.groupby(evidence_col, sort=True):
            record = _metric_record(
                group,
                dimension="response_specific_evidence_class",
                value=str(value),
                response=response,
            )
            if record is not None:
                records.append(record)
    return pd.DataFrame(records)


def residual_trends(residuals: pd.DataFrame) -> pd.DataFrame:
    """Calculate descriptive linear and rank trends; no causal claim is made."""

    primary = residuals.loc[
        residuals["scientific_interpretation_status"].str.startswith(
            "primary_interpretable"
        )
    ]
    records: list[dict[str, Any]] = []
    scopes: list[tuple[str, pd.DataFrame]] = [
        ("primary_all_after_yang_resolution", primary)
    ]
    scopes.extend(
        (f"complete_study:{study_id}", group)
        for study_id, group in primary.groupby("study_id", sort=True)
    )
    for scope, scope_rows in scopes:
        for predictor_name, (predictor_col, _) in NUMERIC_PLOT_SPECS.items():
            for response, (_, _, residual_col, _) in RESPONSE_SPECS.items():
                subset = scope_rows.loc[
                    scope_rows[predictor_col].notna()
                    & scope_rows[residual_col].notna()
                ]
                x = subset[predictor_col].to_numpy(float)
                y = subset[residual_col].to_numpy(float)
                distinct_x = int(pd.Series(x).nunique())
                if len(subset) < 3 or distinct_x < 2:
                    pearson = float("nan")
                    spearman = float("nan")
                    slope = float("nan")
                else:
                    x_centered = x - float(np.mean(x))
                    y_centered = y - float(np.mean(y))
                    x_ss = float(np.sum(x_centered**2))
                    y_ss = float(np.sum(y_centered**2))
                    slope = float(np.sum(x_centered * y_centered) / x_ss)
                    pearson = (
                        float(np.sum(x_centered * y_centered) / math.sqrt(x_ss * y_ss))
                        if y_ss > 0
                        else float("nan")
                    )
                    x_rank = pd.Series(x).rank(method="average").to_numpy(float)
                    y_rank = pd.Series(y).rank(method="average").to_numpy(float)
                    xr = x_rank - float(np.mean(x_rank))
                    yr = y_rank - float(np.mean(y_rank))
                    xr_ss = float(np.sum(xr**2))
                    yr_ss = float(np.sum(yr**2))
                    spearman = (
                        float(np.sum(xr * yr) / math.sqrt(xr_ss * yr_ss))
                        if xr_ss > 0 and yr_ss > 0
                        else float("nan")
                    )
                records.append(
                    {
                        "scope": scope,
                        "predictor": predictor_name,
                        "response": response,
                        "n": int(len(subset)),
                        "independent_studies": int(subset["study_id"].nunique()),
                        "distinct_predictor_values": distinct_x,
                        "pearson_r": pearson,
                        "spearman_rank_rho": spearman,
                        "ols_slope_residual_per_predictor_unit": slope,
                        "interpretation": "descriptive_association_not_causal_evidence",
                    }
                )
    return pd.DataFrame(records)


def adsorption_assignment_sensitivity(
    candidates: pd.DataFrame,
    *,
    integration_steps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Report both sides of the documented Ghosh Table-4/prose ambiguity."""

    records: list[dict[str, Any]] = []
    for row in candidates.to_dict(orient="records"):
        case = _case_from_row(row)
        for scenario, swapped in [
            ("published_table_4_assignment", False),
            ("published_prose_swapped_assignment", True),
        ]:
            prediction = simulate_case(
                case,
                swap_adsorption_enthalpies=swapped,
                integration_steps=integration_steps,
            )
            record: dict[str, Any] = {
                "study_id": row["study_id"],
                "reactorcase_run_id": row["reactorcase_run_id"],
                "scenario": scenario,
                "parameter_refit_performed": False,
            }
            for response, (observed_col, predicted_col, _, _) in RESPONSE_SPECS.items():
                observed = float(row[observed_col])
                predicted = float(prediction[predicted_col])
                record[observed_col] = observed
                record[predicted_col] = predicted
                record[f"{response}_residual"] = predicted - observed
            records.append(record)
    condition = pd.DataFrame(records)

    metric_records: list[dict[str, Any]] = []
    for scenario, scenario_rows in condition.groupby("scenario", sort=True):
        for response in RESPONSE_SPECS:
            residual = scenario_rows[f"{response}_residual"].to_numpy(float)
            study_mae = (
                scenario_rows.assign(_ae=np.abs(residual))
                .groupby("study_id")["_ae"]
                .mean()
            )
            metric_records.append(
                {
                    "scenario": scenario,
                    "response": response,
                    "n": int(len(scenario_rows)),
                    "independent_studies": int(scenario_rows["study_id"].nunique()),
                    "mae": float(np.mean(np.abs(residual))),
                    "rmse": float(np.sqrt(np.mean(residual**2))),
                    "bias_pred_minus_obs": float(np.mean(residual)),
                    "median_absolute_error": float(np.median(np.abs(residual))),
                    "study_balanced_mae": float(study_mae.mean()),
                    "parameter_refit_performed": False,
                }
            )
    return condition, pd.DataFrame(metric_records)


def _style_axis(ax: plt.Axes, ylabel: str) -> None:
    ax.axhline(0.0, color="#333333", linewidth=0.9, linestyle="--", zorder=1)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def _scatter_points(ax: plt.Axes, data: pd.DataFrame, x: np.ndarray, y_col: str) -> None:
    for (phase, evidence), group in data.groupby(
        ["phase_category", "row_evidence_class"], sort=True
    ):
        positions = data.index.get_indexer(group.index)
        ax.scatter(
            x[positions],
            group[y_col],
            s=34,
            marker=EVIDENCE_MARKERS.get(str(evidence), "o"),
            facecolor=PHASE_COLORS.get(str(phase), "#7f7f7f"),
            edgecolor=[
                "#111111" if study_id == "YANG-2020" else "white"
                for study_id in group["study_id"]
            ],
            linewidth=0.55,
            alpha=0.82,
            label=f"{phase}; {evidence}",
            zorder=2,
        )


def plot_numeric(residuals: pd.DataFrame, column: str, xlabel: str, path: Path) -> None:
    data = residuals.reset_index(drop=True).copy()
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 10.2), sharex=True)
    x = data[column].to_numpy(float)
    for ax, (response, (_, _, residual_col, ylabel)) in zip(axes, RESPONSE_SPECS.items()):
        _scatter_points(ax, data, x, residual_col)
        _style_axis(ax, "Residual (percentage points)")
        ax.set_title(RESPONSE_TITLES[response], loc="left", fontsize=10)
    if column == "whsv_ml_gcat_h":
        axes[-1].set_xscale("log")
        xlabel = f"{xlabel} - logarithmic scale"
    axes[-1].set_xlabel(xlabel)
    handles, labels = axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(
        unique.values(),
        unique.keys(),
        loc="lower center",
        ncol=3,
        fontsize=7,
        frameon=False,
    )
    fig.suptitle(
        "Locked Ghosh residuals (prediction - observation)\n"
        "Black-edged points: Yang 2020 lower-certainty digitization",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    fig.savefig(path, format="svg", bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_categorical(
    residuals: pd.DataFrame,
    column: str,
    xlabel: str,
    path: Path,
) -> None:
    data = residuals.reset_index(drop=True).copy()
    categories = sorted(data[column].fillna("not_reported").astype(str).unique())
    positions = {value: index for index, value in enumerate(categories)}
    base_x = data[column].fillna("not_reported").astype(str).map(positions).to_numpy(float)
    jitter = ((np.arange(len(data)) % 9) - 4) * 0.025
    x = base_x + jitter
    width = max(8.2, 0.85 * len(categories) + 4.5)
    fig, axes = plt.subplots(3, 1, figsize=(width, 10.2), sharex=True)
    for ax, (response, (_, _, residual_col, ylabel)) in zip(axes, RESPONSE_SPECS.items()):
        _scatter_points(ax, data, x, residual_col)
        _style_axis(ax, "Residual (percentage points)")
        ax.set_title(RESPONSE_TITLES[response], loc="left", fontsize=10)
    axes[-1].set_xticks(range(len(categories)))
    axes[-1].set_xticklabels(categories, rotation=30, ha="right")
    axes[-1].set_xlabel(xlabel)
    handles, labels = axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(
        unique.values(),
        unique.keys(),
        loc="lower center",
        ncol=3,
        fontsize=7,
        frameon=False,
    )
    fig.suptitle(
        "Locked Ghosh residuals (prediction - observation)\n"
        "Individual points shown; horizontal displacement is display-only",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0.11, 1, 0.95))
    fig.savefig(path, format="svg", bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=180, bbox_inches="tight")
    plt.close(fig)


def create_plots(residuals: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    plot_dir = output_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, str]] = []
    for name, (column, label) in NUMERIC_PLOT_SPECS.items():
        path = plot_dir / f"residuals_vs_{name}.svg"
        plot_numeric(residuals, column, label, path)
        records.append(
            {
                "plot": name,
                "type": "numeric",
                "path": str(path.relative_to(output_dir)),
                "preview_path": str(path.with_suffix(".png").relative_to(output_dir)),
            }
        )
    for name, (column, label) in CATEGORICAL_PLOT_SPECS.items():
        path = plot_dir / f"residuals_by_{name}.svg"
        plot_categorical(residuals, column, label, path)
        records.append(
            {
                "plot": name,
                "type": "categorical",
                "path": str(path.relative_to(output_dir)),
                "preview_path": str(path.with_suffix(".png").relative_to(output_dir)),
            }
        )
    return pd.DataFrame(records)


def build_outputs(
    candidates_path: Path = DEFAULT_CANDIDATES,
    descriptors_path: Path = DEFAULT_DESCRIPTORS,
    locked_output_path: Path = DEFAULT_LOCKED_OUTPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    integration_steps: int = 800,
) -> dict[str, Any]:
    source_hashes_before = {
        str(candidates_path.relative_to(ROOT)): sha256(candidates_path),
        str(descriptors_path.relative_to(ROOT)): sha256(descriptors_path),
        str(locked_output_path.relative_to(ROOT)): sha256(locked_output_path),
    }
    candidates = load_candidates(candidates_path)
    descriptors = pd.read_csv(descriptors_path)
    audit = audit_candidates(candidates, descriptors)
    residuals = add_locked_predictions(
        candidates,
        audit,
        integration_steps=integration_steps,
    )
    metrics = grouped_metrics(residuals)
    trends = residual_trends(residuals)
    sensitivity_rows, sensitivity_metrics = adsorption_assignment_sensitivity(
        candidates,
        integration_steps=integration_steps,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    audit.to_csv(output_dir / "input_provenance_audit.csv", index=False)
    residuals.to_csv(output_dir / "locked_residuals_by_condition.csv", index=False)
    metrics.to_csv(output_dir / "grouped_diagnostic_metrics.csv", index=False)
    trends.to_csv(output_dir / "residual_trend_summary.csv", index=False)
    sensitivity_rows.to_csv(
        output_dir / "adsorption_assignment_sensitivity_by_condition.csv", index=False
    )
    sensitivity_metrics.to_csv(
        output_dir / "adsorption_assignment_sensitivity_metrics.csv", index=False
    )
    plot_manifest = create_plots(residuals, output_dir)
    plot_manifest.to_csv(output_dir / "diagnostic_plot_manifest.csv", index=False)

    source_hashes_after = {
        str(candidates_path.relative_to(ROOT)): sha256(candidates_path),
        str(descriptors_path.relative_to(ROOT)): sha256(descriptors_path),
        str(locked_output_path.relative_to(ROOT)): sha256(locked_output_path),
    }
    input_ids = set(candidates["reactorcase_run_id"].astype(str))
    audit_ids = set(audit["reactorcase_run_id"].astype(str))
    residual_ids = set(residuals["reactorcase_run_id"].astype(str))
    integrity = {
        "audit_version": "part_a_2026-08-12",
        "source_hashes_before": source_hashes_before,
        "source_hashes_after": source_hashes_after,
        "source_hashes_unchanged": source_hashes_before == source_hashes_after,
        "input_rows": int(len(candidates)),
        "audit_rows": int(len(audit)),
        "residual_rows": int(len(residuals)),
        "input_ids_equal_audit_ids": input_ids == audit_ids,
        "input_ids_equal_residual_ids": input_ids == residual_ids,
        "duplicate_input_ids": int(candidates["reactorcase_run_id"].duplicated().sum()),
        "duplicate_audit_ids": int(audit["reactorcase_run_id"].duplicated().sum()),
        "duplicate_residual_ids": int(residuals["reactorcase_run_id"].duplicated().sum()),
        "parameter_refit_performed": False,
    }
    (output_dir / "data_integrity_manifest.json").write_text(
        json.dumps(integrity, indent=2) + "\n", encoding="utf-8"
    )

    summary = metrics.loc[
        metrics["group_dimension"].eq("analysis_scope")
        & metrics["group_value"].eq("primary_all_after_yang_resolution")
    ].set_index("response")
    decision = {
        "audit_version": "part_a_2026-08-12",
        "model": "Ghosh_2021_published_single_site_locked",
        "parameter_refit_performed": False,
        "computationally_successful_rows": int(residuals["solver_converged"].sum()),
        "scientifically_interpretable_rows": int(
            residuals["scientific_interpretation_status"].str.startswith(
                "primary_interpretable"
            ).sum()
        ),
        "lower_certainty_yang_rows": int(residuals["study_id"].eq("YANG-2020").sum()),
        "held_rows_after_yang_source_review": 0,
        "independent_external_studies": int(residuals["study_id"].nunique()),
        "inside_original_numeric_domain_rows": int(
            residuals["domain_category"].eq("inside_original_numeric_domain").sum()
        ),
        "primary_metrics": {
            response: {
                "mae_percentage_points": float(summary.loc[response, "mae"]),
                "rmse_percentage_points": float(summary.loc[response, "rmse"]),
                "bias_percentage_points": float(
                    summary.loc[response, "bias_pred_minus_obs"]
                ),
                "study_balanced_mae_percentage_points": float(
                    summary.loc[response, "study_balanced_mae"]
                ),
            }
            for response in RESPONSE_SPECS
        },
        "yang_resolution": (
            "main Figure 2 explicitly reports GHSV in mL g^-1 h^-1; rows released "
            "as lower-certainty graph-digitized transfer tests"
        ),
        "scientific_boundary": (
            "clean unsupported-In2O3 diagnostic only; not an In2O3/ZrO2 or H2S model"
        ),
        "software_success_is_not_experimental_validation": True,
        "integrity_checks_passed": bool(
            integrity["source_hashes_unchanged"]
            and integrity["input_ids_equal_audit_ids"]
            and integrity["input_ids_equal_residual_ids"]
        ),
    }
    (output_dir / "diagnostic_decision.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--descriptors", type=Path, default=DEFAULT_DESCRIPTORS)
    parser.add_argument("--locked-output", type=Path, default=DEFAULT_LOCKED_OUTPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--integration-steps", type=int, default=800)
    args = parser.parse_args()
    print(
        json.dumps(
            build_outputs(
                args.candidates,
                args.descriptors,
                args.locked_output,
                args.output_dir,
                integration_steps=args.integration_steps,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
