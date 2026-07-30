"""Build the H2S-only evidence datasets without mutating legacy artifacts.

The builder reads the prior local extraction files, applies the Phase-1
reconciliation decisions, and writes a new H2S-specific evidence layer.
It intentionally leaves data/main_data.tsv and data/pilot/sulfur_stage2_verified.csv
unchanged for provenance.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
MAIN_DATA = ROOT / "data" / "main_data.tsv"
STAGE2_DATA = ROOT / "data" / "pilot" / "sulfur_stage2_verified.csv"
SPEC_PATH = ROOT / "config" / "h2s_model_spec.json"
OUTPUT_DIR = ROOT / "data" / "processed" / "h2s"
CURATED_DIR = ROOT / "data" / "curated" / "h2s"
HE_2020_SI = CURATED_DIR / "he_2020_si_digitized.csv"
YING_1992_EFFECTIVENESS = CURATED_DIR / "ying_1992_effectiveness_tables.csv"
YING_1995_TIME_SERIES = (
    ROOT / "data" / "processed" / "sulfur_batch_b_ying_1995_time_series.csv"
)
YING_1995_RATES = (
    ROOT / "data" / "processed" / "sulfur_batch_b_ying_1995_deactivation_rates.csv"
)

OBSERVATION_FIELDS = [
    "study_id",
    "experimental_unit_id",
    "authors_year",
    "source_doi",
    "catalyst_family",
    "catalyst_label",
    "stratum",
    "evidence_tier",
    "eligibility_status",
    "exposure_mode",
    "h2s_concentration_ppm",
    "h2s_concentration_lower_ppm",
    "h2s_concentration_upper_ppm",
    "exposure_h",
    "cumulative_exposure",
    "temperature_c",
    "pressure_bar",
    "feed_basis",
    "feed_h2_fraction",
    "feed_co_fraction",
    "feed_co2_fraction",
    "h2_to_co2_ratio",
    "ghsv_h_minus_1",
    "methanol_metric",
    "clean_or_initial_value",
    "h2s_value",
    "reported_unit",
    "activity_retention_fraction",
    "retention_lower_bound",
    "retention_upper_bound",
    "recovery_value",
    "measurement_status",
    "censoring",
    "duplicate_cluster_id",
    "study_group_id",
    "source_location",
    "key_limitations",
    "notes",
]

KINETIC_FIELDS = [
    "study_id",
    "experimental_unit_id",
    "catalyst_family",
    "catalyst_label",
    "h2s_concentration_ppm",
    "h2s_concentration_lower_ppm",
    "h2s_concentration_upper_ppm",
    "temperature_c",
    "pressure_bar",
    "ghsv_h_minus_1",
    "kinetic_metric",
    "reported_value",
    "reported_unit",
    "equation_context",
    "evidence_tier",
    "comparable_group",
    "duplicate_cluster_id",
    "source_location",
    "notes",
]

EXCLUDED_FIELDS = [
    "study_id",
    "record_id",
    "source_or_file",
    "reason_code",
    "reason",
    "destination",
    "reconsideration_trigger",
]

GAP_FIELDS = [
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


def read_rows(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_rows(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean(row.get(field, "")) for field in fields})


def clean(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.10g}"
    return value


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"not reported", "not applicable", "na", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def ratio(numerator: Any, denominator: Any) -> float | None:
    n = as_float(numerator)
    d = as_float(denominator)
    if n is None or d in (None, 0):
        return None
    return n / d


def base_observation(**values: Any) -> dict[str, Any]:
    row = {field: "" for field in OBSERVATION_FIELDS}
    row.update(values)
    return row


def index_by(rows: Iterable[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows if row.get(key)}


def build_observations(
    main_by_id: dict[str, dict[str, str]], stage2_by_id: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # Primary core record: exact continuous-cofeed commercial Cu/ZnO/Al2O3.
    rows.append(
        base_observation(
            study_id="T2-004",
            experimental_unit_id="T2-004-CUZNAL-ACT",
            authors_year="Prašnikar and Likozar 2022",
            source_doi="10.1039/D1RE00486G",
            catalyst_family="Cu/ZnO/Al2O3",
            catalyst_label="Commercial Cu/ZnO/Al2O3 HiFuel W230",
            stratum="core_continuous_cuznal",
            evidence_tier="A",
            eligibility_status="core_model_ready",
            exposure_mode="continuous_cofeed",
            h2s_concentration_ppm=8.1,
            h2s_concentration_lower_ppm=8.1,
            h2s_concentration_upper_ppm=8.1,
            exposure_h=30,
            cumulative_exposure="no",
            temperature_c=240,
            pressure_bar=20,
            feed_basis="CO2 hydrogenation",
            feed_h2_fraction=0.75,
            feed_co_fraction=0,
            feed_co2_fraction=0.25,
            h2_to_co2_ratio=3,
            ghsv_h_minus_1=40000,
            methanol_metric="normalized methanol activity",
            clean_or_initial_value=1,
            h2s_value=0.9,
            reported_unit="dimensionless",
            activity_retention_fraction=0.9,
            measurement_status="reported",
            censoring="none",
            duplicate_cluster_id="DUP-T2-004-CUZNAL-H2S",
            study_group_id="STUDY-T2-004",
            source_location="Open RSC article, H2S results text/Fig. 8; Sheet row T2-004-CUZNAL-ACT",
            key_limitations="One catalyst, concentration, and exposure duration; no reported replicate uncertainty.",
            notes="Methanol selectivity was reported unchanged. The coefficient from the same run is stored in the kinetic table, not as an independent observation.",
        )
    )

    # Exact ex-situ commercial-CZA damage record corrected from the primary paper.
    rows.append(
        base_observation(
            study_id="T1-001",
            experimental_unit_id="T1-001-CU-H2S-4H-CORRECTED",
            authors_year="Schühle et al. 2020",
            source_doi="10.1039/D0CY00946F",
            catalyst_family="Cu/ZnO/Al2O3",
            catalyst_label="Commercial Cu/ZnO/Al2O3 (63.5% CuO/24.7% ZnO/10.1% Al2O3/1.3% MgO)",
            stratum="ex_situ_damage",
            evidence_tier="A",
            eligibility_status="separate_protocol_model_ready",
            exposure_mode="ex_situ_prepoisoning",
            h2s_concentration_ppm=400,
            h2s_concentration_lower_ppm=400,
            h2s_concentration_upper_ppm=400,
            exposure_h=4,
            cumulative_exposure="no",
            temperature_c=250,
            pressure_bar=53.8,
            feed_basis="clean CO2/H2 methanol test after H2S/He pretreatment",
            feed_h2_fraction=0.75,
            feed_co_fraction=0,
            feed_co2_fraction=0.25,
            h2_to_co2_ratio=3,
            ghsv_h_minus_1=1952,
            methanol_metric="methanol productivity",
            clean_or_initial_value=0.54,
            h2s_value=0.45,
            reported_unit="g MeOH g(Cu)^-1 h^-1",
            activity_retention_fraction=0.45 / 0.54,
            measurement_status="reported",
            censoring="none",
            duplicate_cluster_id="DUP-T1-001-CU-H2S-4H",
            study_group_id="STUDY-T1-001",
            source_location="Main article pp. 2 and 8; canonical Sheet T1-001-CU-H2S-4H",
            key_limitations="Post-exposure retained damage, not direct cofeed response.",
            notes="Corrects the legacy Stage-2 rows that confused 610 N mL/min helium flow with H2S ppm and reused SO2 productivity values.",
        )
    )

    # Heracleous: combine normalized conversion and selectivity into yield retention.
    conversion_retention = 0.898
    selectivity_retention = 0.909
    rows.append(
        base_observation(
            study_id="T1-003",
            experimental_unit_id="T1-003-S-MEOH-YIELD-DERIVED",
            authors_year="Heracleous et al. 2022",
            source_doi="10.1016/j.cej.2022.136571",
            catalyst_family="Cu/ZnO/Al2O3",
            catalyst_label="Commercial CuO/ZnO/Al2O3 (Clariant)",
            stratum="ex_situ_damage",
            evidence_tier="B",
            eligibility_status="separate_protocol_supporting",
            exposure_mode="ex_situ_prepoisoning",
            h2s_concentration_ppm=400,
            h2s_concentration_lower_ppm=400,
            h2s_concentration_upper_ppm=400,
            exposure_h=5,
            cumulative_exposure="no",
            temperature_c=250,
            pressure_bar=70,
            feed_basis="clean CO2/H2 test after H2S pretreatment",
            h2_to_co2_ratio=3,
            ghsv_h_minus_1=6500,
            methanol_metric="derived normalized methanol-yield retention",
            clean_or_initial_value=1,
            h2s_value=conversion_retention * selectivity_retention,
            reported_unit="dimensionless",
            activity_retention_fraction=conversion_retention * selectivity_retention,
            measurement_status="calculated from two figure-derived normalized metrics",
            censoring="none",
            duplicate_cluster_id="DUP-T1-003-H2S",
            study_group_id="STUDY-T1-003",
            source_location="PDF p. 3 Table 1; PDF p. 7 Figs. 4-5; local rows T1-003-S-CV and T1-003-S-MS",
            key_limitations="Derived from normalized conversion and selectivity rather than a directly reported methanol-yield value.",
            notes="0.898 x 0.909 = 0.816182. The two source rows are one physical experiment.",
        )
    )

    # Henriksson staged CuO/ZnO results. Stage 2 uses the immediately preceding
    # recovery as its baseline and is explicitly marked cumulative/confounded.
    rows.extend(
        [
            base_observation(
                study_id="T1-002",
                experimental_unit_id="T1-002-PFR-CU-STAGE1-YIELD",
                authors_year="Henriksson 2016",
                catalyst_family="CuO/ZnO",
                catalyst_label="Commercial BASF CuO/ZnO",
                stratum="continuous_other_cu",
                evidence_tier="C",
                eligibility_status="supporting_only_flow_confounded",
                exposure_mode="continuous_cofeed",
                h2s_concentration_ppm=33.2,
                h2s_concentration_lower_ppm=33.2,
                h2s_concentration_upper_ppm=33.2,
                exposure_h=72,
                cumulative_exposure="no",
                temperature_c=230,
                pressure_bar=30,
                feed_basis="CO2/H2/N2; reactant flow diluted during poisoning",
                feed_h2_fraction=0.713,
                feed_co_fraction=0,
                feed_co2_fraction=0.237,
                h2_to_co2_ratio=3.0084,
                methanol_metric="methanol yield",
                clean_or_initial_value=7.9,
                h2s_value=4.7,
                reported_unit="percent",
                activity_retention_fraction=4.7 / 7.9,
                recovery_value=5.4,
                measurement_status="reported",
                censoring="none",
                duplicate_cluster_id="DUP-T1-002-CU-PFR-SEQUENCE",
                study_group_id="STUDY-T1-002",
                source_location="Thesis PDF pp. 63-64, Tables 21-22",
                key_limitations="Poison-gas blending reduced reactant flow; thesis previously excluded from primary analysis.",
                notes="Recovery after this stage was 5.4% methanol yield.",
            ),
            base_observation(
                study_id="T1-002",
                experimental_unit_id="T1-002-PFR-CU-STAGE2-YIELD",
                authors_year="Henriksson 2016",
                catalyst_family="CuO/ZnO",
                catalyst_label="Commercial BASF CuO/ZnO",
                stratum="continuous_other_cu",
                evidence_tier="C",
                eligibility_status="supporting_only_cumulative_and_flow_confounded",
                exposure_mode="continuous_cofeed",
                h2s_concentration_ppm=60,
                h2s_concentration_lower_ppm=60,
                h2s_concentration_upper_ppm=60,
                exposure_h=8,
                cumulative_exposure="yes; follows 33.2 ppm stage and recovery",
                temperature_c=230,
                pressure_bar=30,
                feed_basis="CO2/H2/N2; reactant flow diluted during poisoning",
                methanol_metric="methanol yield",
                clean_or_initial_value=5.4,
                h2s_value=3.7,
                reported_unit="percent",
                activity_retention_fraction=3.7 / 5.4,
                recovery_value=6.5,
                measurement_status="reported; retention recalculated against preceding recovery",
                censoring="none",
                duplicate_cluster_id="DUP-T1-002-CU-PFR-SEQUENCE",
                study_group_id="STUDY-T1-002",
                source_location="Thesis PDF pp. 63-64, Tables 21-22",
                key_limitations="Cumulative prior H2S exposure and altered reactant flow; not an independent fresh-catalyst dose.",
                notes="The older local row used the original 7.9% clean value. This layer uses the immediately preceding 5.4% recovery as the stage baseline.",
            ),
        ]
    )

    # Censored Cu/ZnO deactivation proxy from Ma et al.
    rows.append(
        base_observation(
            study_id="T1-010",
            experimental_unit_id="T1-010-CUZNO-X-CENSORED",
            authors_year="Ma et al. 2008",
            source_doi="10.1016/j.catcom.2008.07.045",
            catalyst_family="Cu/ZnO",
            catalyst_label="Cu/ZnO (Cu:Zn=2 molar)",
            stratum="continuous_other_cu",
            evidence_tier="B",
            eligibility_status="supporting_only_nonmethanol_censored_proxy",
            exposure_mode="continuous_cofeed",
            h2s_concentration_ppm=3,
            h2s_concentration_lower_ppm=3,
            h2s_concentration_upper_ppm=3,
            exposure_h=7,
            cumulative_exposure="no",
            temperature_c=240,
            pressure_bar=30,
            feed_basis="syngas: 61.3% H2, 30.6% CO, 5.1% CO2, 3% N2",
            feed_h2_fraction=0.613,
            feed_co_fraction=0.306,
            feed_co2_fraction=0.051,
            ghsv_h_minus_1=1000,
            methanol_metric="CO conversion proxy; methanol selectivity remained above 90%",
            clean_or_initial_value=24.5,
            reported_unit="percent CO conversion",
            retention_upper_bound=1 / 24.5,
            measurement_status="reported bound",
            censoring="left-censored endpoint: CO conversion <1%",
            duplicate_cluster_id="DUP-T1-010-CUZNO-3PPM",
            study_group_id="STUDY-T1-010",
            source_location="Article p. 2, Fig. 1 and Results section",
            key_limitations="Initial value was already measured under H2S; response is a conversion proxy rather than direct methanol output.",
            notes="The bound is preserved and is not converted into an exact activity-retention point.",
        )
    )

    # Chai laboratory H2S pulse rows: exact activity and sulfur loading, but no ppm.
    for source_id in [f"T2-001-LAB-{index:02d}" for index in range(1, 7)]:
        source = stage2_by_id[source_id]
        baseline = as_float(source["baseline_value"])
        poisoned = as_float(source["impure_value"])
        rows.append(
            base_observation(
                study_id="T2-001",
                experimental_unit_id=source_id,
                authors_year="Chai et al. 1991",
                source_doi="10.1016/S0167-2991(08)62681-6",
                catalyst_family="Cu/ZnO/Al2O3",
                catalyst_label=source["catalyst_label"],
                stratum="sulfur_loading_response",
                evidence_tier="C",
                eligibility_status="supporting_only_missing_h2s_concentration",
                exposure_mode="pulsed_cofeed",
                exposure_h=source["exposure_h"],
                cumulative_exposure="yes; repeated 0.5 h pulses",
                temperature_c=source["reaction_temp_c"],
                pressure_bar=source["pressure_bar"],
                feed_basis="14-16% CO, 68-72% H2; remainder not fully specified",
                ghsv_h_minus_1=source["ghsv_h_minus_1"],
                methanol_metric="absolute methanol activity",
                clean_or_initial_value=baseline,
                h2s_value=poisoned,
                reported_unit=source["reported_unit"],
                activity_retention_fraction=ratio(poisoned, baseline),
                measurement_status="reported; visually verified",
                censoring="none",
                duplicate_cluster_id=f"DUP-{source_id}",
                study_group_id="STUDY-T2-001",
                source_location="PDF p. 4, printed p. 542, Table 1",
                key_limitations="Gas-phase H2S concentration and delivered molar dose are not reported.",
                notes=source["notes"],
            )
        )

    # Guard-bed protection series, retained separately.
    for index in range(6):
        source_id = f"T1-015-R3-T{index:02d}"
        source = main_by_id[source_id]
        value = as_float(source["With impurity"])
        exposure_text = source["Time on stream (h)"]
        exposure_h = (
            [0, 5.85, 17.88, 30.43, 47.98, 65.05][index]
        )
        rows.append(
            base_observation(
                study_id="T1-015",
                experimental_unit_id=source_id,
                authors_year="Quinn and Toseland 2008",
                source_doi="10.1021/ie8003418",
                catalyst_family="Cu/ZnO/Al2O3",
                catalyst_label="Commercial Cu/ZnO/Al2O3 downstream of same-catalyst slurry guard bed",
                stratum="guard_bed_protection",
                evidence_tier="C",
                eligibility_status="process_protection_only",
                exposure_mode="upstream_guard_bed",
                h2s_concentration_ppm=2.76,
                h2s_concentration_lower_ppm=2.76,
                h2s_concentration_upper_ppm=2.76,
                exposure_h=exposure_h,
                cumulative_exposure="yes",
                temperature_c=250,
                pressure_bar=51.7,
                feed_basis="68.4% H2, 22.4% CO, 4.6% CO2, 4.6% N2",
                feed_h2_fraction=0.684,
                feed_co_fraction=0.224,
                feed_co2_fraction=0.046,
                ghsv_h_minus_1=6810,
                methanol_metric="normalized methanol synthesis rate constant",
                clean_or_initial_value=1,
                h2s_value=value,
                reported_unit="dimensionless",
                activity_retention_fraction=value,
                measurement_status="reported",
                censoring="none",
                duplicate_cluster_id="DUP-T1-015-RUN3",
                study_group_id="STUDY-T1-015",
                source_location="Article Table 5",
                key_limitations="H2S was captured upstream; the modeled methanol catalyst was not directly exposed.",
                notes=exposure_text,
            )
        )

    # Non-Cu supported-Pd TOF evidence. Exclude the zero-baseline SiO2-Al2O3 row.
    pd_ids = [
        "T1-007-PDSIO2-MeOH-TOF",
        "T1-007-PDAL-MeOH-TOF",
        "T1-007-PDND-MeOH-TOF",
        "T1-007-PDTIO2HTR-MeOH-TOF",
        "T1-007-PDTIO2LTR-MeOH-TOF",
    ]
    for source_id in pd_ids:
        source = main_by_id[source_id]
        baseline = as_float(source["Baseline"])
        poisoned = as_float(source["With impurity"])
        rows.append(
            base_observation(
                study_id="T1-007",
                experimental_unit_id=source_id,
                authors_year="Bérubé, Sung, and Vannice 1987",
                source_doi="10.1016/S0166-9834(00)80672-7",
                catalyst_family="supported Pd",
                catalyst_label=source["Catalyst"],
                stratum="non_cu_expansion",
                evidence_tier="D",
                eligibility_status="non_cu_expansion_only",
                exposure_mode="continuous_cofeed",
                h2s_concentration_ppm=2,
                h2s_concentration_lower_ppm=2,
                h2s_concentration_upper_ppm=2,
                exposure_h=source["Time on stream (h)"],
                cumulative_exposure="no",
                temperature_c=250,
                pressure_bar=15,
                feed_basis="CO/H2 = 1:3",
                feed_h2_fraction=0.75,
                feed_co_fraction=0.25,
                feed_co2_fraction=0,
                ghsv_h_minus_1="24 cm3 STP min^-1 total flow; GHSV unavailable",
                methanol_metric="methanol TOF per surface Pd atom",
                clean_or_initial_value=baseline,
                h2s_value=poisoned,
                reported_unit="10^-3 s^-1",
                activity_retention_fraction=ratio(poisoned, baseline),
                measurement_status="reported",
                censoring="none",
                duplicate_cluster_id=f"DUP-{source_id.replace('-MeOH-TOF', '')}",
                study_group_id="STUDY-T1-007",
                source_location="Article Table 5",
                key_limitations="Non-Cu catalyst family; some runs likely overlap T2-005.",
                notes="No H2S-removal recovery test.",
            )
        )

    # Preferred paired Pd results from T1-012; kept out of the Cu core.
    clean_pdal_yield = 20.1 * 85.1 / 100
    h2s_pdal_yield = 2.6 * 46.2 / 100
    rows.extend(
        [
            base_observation(
                study_id="T1-012",
                experimental_unit_id="T1-012-PDAL-Y-DERIVED",
                authors_year="Ma et al. 2008",
                catalyst_family="supported Pd",
                catalyst_label="15 wt% Pd/Al2O3",
                stratum="non_cu_expansion",
                evidence_tier="D",
                eligibility_status="non_cu_expansion_only",
                exposure_mode="continuous_cofeed",
                h2s_concentration_ppm=30,
                h2s_concentration_lower_ppm=30,
                h2s_concentration_upper_ppm=30,
                exposure_h=100,
                temperature_c=240,
                pressure_bar=30,
                feed_basis="61.3% H2, 30.6% CO, 5.1% CO2, 3% N2",
                feed_h2_fraction=0.613,
                feed_co_fraction=0.306,
                feed_co2_fraction=0.051,
                ghsv_h_minus_1=1000,
                methanol_metric="derived methanol yield",
                clean_or_initial_value=clean_pdal_yield,
                h2s_value=h2s_pdal_yield,
                reported_unit="percent",
                activity_retention_fraction=h2s_pdal_yield / clean_pdal_yield,
                measurement_status="calculated from reported conversion and selectivity",
                censoring="none",
                duplicate_cluster_id="DUP-T1-012-PDAL-30PPM",
                study_group_id="STUDY-T1-012",
                source_location="Article p. 2, Fig. 1a and text",
                key_limitations="Non-Cu catalyst; yield is calculated from conversion x selectivity.",
            ),
            base_observation(
                study_id="T1-012",
                experimental_unit_id="T1-012-PDCE-Y-PREFERRED",
                authors_year="Ma et al. 2008",
                catalyst_family="supported Pd",
                catalyst_label="15 wt% Pd/CeO2",
                stratum="non_cu_expansion",
                evidence_tier="D",
                eligibility_status="non_cu_expansion_only",
                exposure_mode="continuous_cofeed",
                h2s_concentration_ppm=30,
                h2s_concentration_lower_ppm=30,
                h2s_concentration_upper_ppm=30,
                exposure_h=100,
                temperature_c=240,
                pressure_bar=30,
                feed_basis="61.3% H2, 30.6% CO, 5.1% CO2, 3% N2",
                feed_h2_fraction=0.613,
                feed_co_fraction=0.306,
                feed_co2_fraction=0.051,
                ghsv_h_minus_1=1000,
                methanol_metric="methanol yield",
                clean_or_initial_value=16.4,
                h2s_value=16.4,
                reported_unit="percent",
                activity_retention_fraction=1,
                measurement_status="reported",
                censoring="none",
                duplicate_cluster_id="DUP-MA2008-PDCE-30PPM",
                study_group_id="STUDY-T1-012",
                source_location="Article pp. 3-4, Fig. 4 and text",
                key_limitations="Non-Cu catalyst; same physical series is also reported in T1-010.",
                notes="T1-012 is the preferred paired record for this duplicate cluster.",
            ),
        ]
    )

    # In2O3/ZrO2 post-exposure series from T1-001 remains non-Cu expansion.
    for exposure in (4, 18):
        for temp in (225, 250, 275):
            source_id = f"T1-001-H2S-{exposure}H-{temp}"
            source = main_by_id[source_id]
            baseline = as_float(source["Baseline"])
            poisoned = as_float(source["With impurity"])
            rows.append(
                base_observation(
                    study_id="T1-001",
                    experimental_unit_id=source_id,
                    authors_year="Schühle et al. 2020",
                    source_doi="10.1039/D0CY00946F",
                    catalyst_family="In2O3/ZrO2",
                    catalyst_label="In2O3/ZrO2 (10.5 +/- 0.3 wt% In)",
                    stratum="non_cu_expansion",
                    evidence_tier="D",
                    eligibility_status="non_cu_expansion_only",
                    exposure_mode="ex_situ_prepoisoning",
                    h2s_concentration_ppm=400,
                    h2s_concentration_lower_ppm=400,
                    h2s_concentration_upper_ppm=400,
                    exposure_h=exposure,
                    cumulative_exposure="no",
                    temperature_c=temp,
                    pressure_bar=53.8,
                    feed_basis="clean CO2/H2 test after H2S/He pretreatment",
                    feed_h2_fraction=0.75,
                    feed_co_fraction=0,
                    feed_co2_fraction=0.25,
                    h2_to_co2_ratio=3,
                    ghsv_h_minus_1=1952,
                    methanol_metric="methanol productivity",
                    clean_or_initial_value=baseline,
                    h2s_value=poisoned,
                    reported_unit="g MeOH g(In)^-1 h^-1",
                    activity_retention_fraction=ratio(poisoned, baseline),
                    measurement_status="reported",
                    censoring="none",
                    duplicate_cluster_id=f"DUP-{source_id}",
                    study_group_id="STUDY-T1-001",
                    source_location="Main article and supporting figures as recorded in local extraction",
                    key_limitations="Non-Cu catalyst and ex-situ exposure protocol.",
                )
            )

    # Other Cu formulation with a direct endpoint from T2-004.
    rows.append(
        base_observation(
            study_id="T2-004",
            experimental_unit_id="T2-004-CUSRTI-ACT",
            authors_year="Prašnikar and Likozar 2022",
            source_doi="10.1039/D1RE00486G",
            catalyst_family="Cu/Sr/Ti mixed oxide",
            catalyst_label="CuSrTi",
            stratum="continuous_other_cu",
            evidence_tier="B",
            eligibility_status="separate_formulation_supporting",
            exposure_mode="continuous_cofeed",
            h2s_concentration_ppm=8.1,
            h2s_concentration_lower_ppm=8.1,
            h2s_concentration_upper_ppm=8.1,
            exposure_h=17,
            temperature_c=240,
            pressure_bar=20,
            feed_basis="CO2 hydrogenation",
            feed_h2_fraction=0.75,
            feed_co_fraction=0,
            feed_co2_fraction=0.25,
            h2_to_co2_ratio=3,
            ghsv_h_minus_1=40000,
            methanol_metric="normalized methanol activity",
            clean_or_initial_value=1,
            h2s_value=0.05,
            reported_unit="dimensionless",
            activity_retention_fraction=0.05,
            measurement_status="reported approximate endpoint",
            censoring="none",
            duplicate_cluster_id="DUP-T2-004-CUSRTI-H2S",
            study_group_id="STUDY-T2-004",
            source_location="Open RSC article, H2S results text/Fig. 6",
            key_limitations="Different catalyst formulation; endpoint is approximate.",
        )
    )

    # He et al. SI: matched thermal-aging and H2S traces, digitized from Fig. S1.
    # This is a valuable long-duration counterfactual but the response is COx
    # conversion, not methanol output, so it remains outside the synthesis core.
    for source in read_rows(HE_2020_SI):
        rows.append(
            base_observation(
                study_id=source["study_id"],
                experimental_unit_id=source["experimental_row_id"],
                authors_year=source["authors_year"],
                source_doi=source["source_doi"],
                catalyst_family="Cu/ZnO/Al2O3",
                catalyst_label="Industrial Clariant Cu/ZnO/Al2O3",
                stratum="mechanism_only",
                evidence_tier="D",
                eligibility_status="matched_cox_proxy_only",
                exposure_mode="continuous_cofeed_with_accelerated_thermal_cycles",
                h2s_concentration_ppm=source["h2s_ppm"],
                h2s_concentration_lower_ppm=source["h2s_ppm"],
                h2s_concentration_upper_ppm=source["h2s_ppm"],
                exposure_h=source["exposure_h"],
                cumulative_exposure="yes; repeated time point from one run",
                temperature_c=source["activity_temperature_c"],
                pressure_bar=source["pressure_bar"],
                feed_basis="H2/CO/CO2/N2 syngas",
                feed_h2_fraction=source["feed_h2_fraction"],
                feed_co_fraction=source["feed_co_fraction"],
                feed_co2_fraction=source["feed_co2_fraction"],
                methanol_metric="normalized COx conversion relative to matched thermal-aging trace",
                clean_or_initial_value=source["clean_normalized_cox_conversion"],
                h2s_value=source["h2s_normalized_cox_conversion"],
                reported_unit="dimensionless",
                activity_retention_fraction=source["h2s_to_clean_ratio"],
                measurement_status=source["measurement_status"],
                censoring="approximate digitization; H2S trace approaches figure noise floor",
                duplicate_cluster_id="DUP-T1-004-HE-SI-FIG-S1",
                study_group_id="STUDY-T1-004",
                source_location=source["source_location"],
                key_limitations="COx-conversion proxy and accelerated temperature cycling; not a methanol-output endpoint.",
                notes=source["notes"],
            )
        )

    # Ying et al. Part I: exact relative-activity time series for methanol
    # decomposition over commercial C207. These data inform a source-specific
    # deactivation scenario but are not eligible for methanol-synthesis fitting.
    for source in read_rows(YING_1995_TIME_SERIES):
        rows.append(
            base_observation(
                study_id="T3-001",
                experimental_unit_id=source["experimental_row_id"].replace(
                    "SX-004", "T3-001"
                ),
                authors_year=source["authors_year"],
                source_doi=source["source_doi_or_url"],
                catalyst_family="Commercial Cu-based C207",
                catalyst_label="C207 Cu-based catalyst",
                stratum="mechanism_only",
                evidence_tier="D",
                eligibility_status="non_synthesis_supporting_only",
                exposure_mode="continuous_cofeed_during_methanol_decomposition",
                h2s_concentration_ppm=source["impurity_conc_ppm"],
                h2s_concentration_lower_ppm=source["impurity_conc_ppm"],
                h2s_concentration_upper_ppm=source["impurity_conc_ppm"],
                exposure_h=source["time_on_stream_h"],
                cumulative_exposure="yes; repeated time point from one run",
                temperature_c=source["temperature_c"],
                pressure_bar=source["pressure_bar"],
                feed_basis="6% methanol, 14% CO, 40% H2, balance N2",
                feed_h2_fraction=0.40,
                feed_co_fraction=0.14,
                feed_co2_fraction=0,
                methanol_metric="relative methanol-decomposition activity",
                clean_or_initial_value=source["baseline_value"],
                h2s_value=source["with_impurity_value"],
                reported_unit=source["unit"],
                activity_retention_fraction=source["with_impurity_value"],
                measurement_status="reported",
                censoring="none",
                duplicate_cluster_id="DUP-T3-001-YING-PART1-RUN1",
                study_group_id="STUDY-YING-C207-SERIES",
                source_location=source["evidence_location"],
                key_limitations="Atmospheric methanol decomposition, not methanol synthesis.",
                notes=source["review_note"],
            )
        )

    # Ying et al. 1992: exact macroscopic reaction-rate and pellet-effectiveness
    # tables after 4, 8, or 12 h H2S pretreatment. All table rows are retained
    # for provenance; repeated conditions within an exposure share one cluster.
    for source in read_rows(YING_1992_EFFECTIVENESS):
        exposure = source["h2s_exposure_h"]
        rows.append(
            base_observation(
                study_id=source["study_id"],
                experimental_unit_id=source["experimental_row_id"],
                authors_year=source["authors_year"],
                source_doi=source["source_url"],
                catalyst_family="Commercial Cu-based C207",
                catalyst_label="C207 cylindrical pellet (5 mm x 5 mm)",
                stratum="mechanism_only",
                evidence_tier="D",
                eligibility_status="non_synthesis_supporting_only",
                exposure_mode="h2s_prepoisoning_then_clean_methanol_decomposition",
                h2s_concentration_ppm=source["h2s_ppm"],
                h2s_concentration_lower_ppm=source["h2s_ppm"],
                h2s_concentration_upper_ppm=source["h2s_ppm"],
                exposure_h=exposure,
                cumulative_exposure="no; new catalyst sample for each exposure",
                temperature_c=source["temperature_c"],
                pressure_bar=float(source["pressure_kpa"]) / 100,
                feed_basis="atmospheric methanol decomposition after H2S pretreatment",
                feed_h2_fraction=source["inlet_h2_fraction"],
                feed_co_fraction=source["inlet_co_fraction"],
                feed_co2_fraction=0,
                methanol_metric="macroscopic methanol-decomposition rate",
                clean_or_initial_value="",
                h2s_value=source["methanol_decomposition_rate_mol_g_h"],
                reported_unit="mol MeOH g_cat^-1 h^-1",
                activity_retention_fraction="",
                measurement_status=source["measurement_status"],
                censoring="none",
                duplicate_cluster_id=f"DUP-T3-002-H{int(float(exposure)):02d}",
                study_group_id="STUDY-YING-C207-SERIES",
                source_location=source["source_location"],
                key_limitations="Atmospheric methanol decomposition; no same-condition clean rate in Tables 3-5.",
                notes=(
                    f"Reported pellet effectiveness factor={source['effectiveness_factor']}; "
                    f"total molar flow={source['total_molar_flow_mol_h']} mol/h; "
                    f"catalyst mass={source['catalyst_mass_g']} g. {source['notes']}"
                ),
            )
        )

    for exposure, measured_xc, calculated_xc in [
        (4, 0.938, 0.968),
        (8, 0.916, 0.938),
        (12, 0.896, 0.909),
    ]:
        rows.append(
            base_observation(
                study_id="T3-002",
                experimental_unit_id=f"T3-002-H{exposure:02d}-AES-XC",
                authors_year="Ying, Fang and Zhu 1992",
                source_doi="https://hgxb.cip.com.cn/EN/Y1992/V43/I2/139",
                catalyst_family="Commercial Cu-based C207",
                catalyst_label="C207 cylindrical pellet (5 mm x 5 mm)",
                stratum="mechanism_only",
                evidence_tier="D",
                eligibility_status="sulfur_penetration_proxy_only",
                exposure_mode="h2s_prepoisoning_then_aes_cross_section",
                h2s_concentration_ppm=719,
                h2s_concentration_lower_ppm=719,
                h2s_concentration_upper_ppm=719,
                exposure_h=exposure,
                cumulative_exposure="no; new catalyst sample for each exposure",
                temperature_c=260,
                pressure_bar=1.03,
                feed_basis="H2S pretreatment; AES pellet cross-section",
                methanol_metric="unpoisoned pellet-core radius ratio x_c",
                clean_or_initial_value=1,
                h2s_value=measured_xc,
                reported_unit="dimensionless",
                activity_retention_fraction="",
                measurement_status="reported AES measurement",
                censoring="none",
                duplicate_cluster_id=f"DUP-T3-002-H{exposure:02d}",
                study_group_id="STUDY-YING-C207-SERIES",
                source_location="Open Chinese PDF printed p. 142 Table 8",
                key_limitations="Sulfur-penetration geometry, not a methanol-activity retention value.",
                notes=f"Intrinsic-deactivation calculation gave x_c={calculated_xc}.",
            )
        )

    return rows


def build_kinetics(stage2_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in stage2_rows:
        if source.get("impurity_species") != "H2S":
            continue
        if source.get("analysis_family") not in {"deactivation_kinetics", "catalyst_sensitivity"}:
            continue
        is_wood = source["study_id"] == "T2-002"
        is_point = source["outcome_cohort"] == "first_order_decay_rate"
        rows.append(
            {
                "study_id": source["study_id"],
                "experimental_unit_id": source["experimental_row_id"],
                "catalyst_family": source["catalyst_family"],
                "catalyst_label": source["catalyst_label"],
                "h2s_concentration_ppm": source["impurity_conc_ppm"],
                "h2s_concentration_lower_ppm": source["impurity_conc_min_ppm"],
                "h2s_concentration_upper_ppm": source["impurity_conc_max_ppm"],
                "temperature_c": source["reaction_temp_c"],
                "pressure_bar": source["pressure_bar"],
                "ghsv_h_minus_1": source["ghsv_h_minus_1"],
                "kinetic_metric": source["outcome_cohort"],
                "reported_value": source["reported_value"],
                "reported_unit": source["reported_unit"],
                "equation_context": (
                    "Observed exponential methanol-activity decay rate"
                    if is_point
                    else (
                        "Wood first-order side-by-side poisoning coefficient, source-scaled"
                        if is_wood
                        else "Prašnikar catalyst-specific zero-order site-loss coefficient"
                    )
                ),
                "evidence_tier": "A" if is_wood else "A",
                "comparable_group": (
                    "wood_observed_decay_rate"
                    if is_point
                    else ("wood_poisoning_constant" if is_wood else "prasnikar_intrinsic_coefficient")
                ),
                "duplicate_cluster_id": (
                    f"DUP-{source['experimental_row_id']}"
                    if is_point
                    else f"DUP-{source['study_id']}-{source['catalyst_label']}-KINETIC"
                ),
                "source_location": source["evidence_location"],
                "notes": source["notes"],
            }
        )

    for source in read_rows(YING_1995_RATES):
        rows.append(
            {
                "study_id": "T3-001",
                "experimental_unit_id": f"T3-001-DERIV-{int(source['table_row']):02d}",
                "catalyst_family": "Commercial Cu-based C207",
                "catalyst_label": "C207 Cu-based catalyst",
                "h2s_concentration_ppm": source["h2s_ppm"],
                "h2s_concentration_lower_ppm": source["h2s_ppm"],
                "h2s_concentration_upper_ppm": source["h2s_ppm"],
                "temperature_c": source["temperature_c"],
                "pressure_bar": 1.02,
                "ghsv_h_minus_1": "",
                "kinetic_metric": "source-reported methanol-decomposition deactivation derivative",
                "reported_value": source["experimental_deactivation_rate_per_h"],
                "reported_unit": "h^-1",
                "equation_context": "-da/dt at the tabulated relative activity",
                "evidence_tier": "D",
                "comparable_group": "ying1995_decomposition_derivative",
                "duplicate_cluster_id": "DUP-T3-001-YING-PART1-KINETICS",
                "source_location": source["evidence_location"],
                "notes": (
                    f"Relative activity a={source['relative_activity_a']}. "
                    f"{source['review_note']}"
                ),
            }
        )

    rows.append(
        {
            "study_id": "T3-001",
            "experimental_unit_id": "T3-001-EQ7",
            "catalyst_family": "Commercial Cu-based C207",
            "catalyst_label": "C207 Cu-based catalyst",
            "h2s_concentration_ppm": "",
            "h2s_concentration_lower_ppm": 105,
            "h2s_concentration_upper_ppm": 281,
            "temperature_c": "250-265",
            "pressure_bar": 1.02,
            "ghsv_h_minus_1": "",
            "kinetic_metric": "intrinsic methanol-decomposition deactivation equation",
            "reported_value": "0.1504 x 10^5",
            "reported_unit": "ppm^-1 h^-1 pre-exponential factor",
            "equation_context": "-da/dt = 0.1504 x 10^5 exp[-81128/(R_g T)] C_H2S(ppm) a",
            "evidence_tier": "D",
            "comparable_group": "ying1995_decomposition_intrinsic_model",
            "duplicate_cluster_id": "DUP-T3-001-YING-PART1-KINETICS",
            "source_location": "PDF printed p. 282, Eq. 7",
            "notes": "The fitted exponents 1.061 for C_H2S and 1.036 for activity were rounded to 1.",
        }
    )
    return rows


def build_exclusions() -> list[dict[str, str]]:
    return [
        {
            "study_id": "T1-001",
            "record_id": "T1-001-CU-H2S-4H (legacy Stage-2)",
            "source_or_file": "data/pilot/sulfur_stage2_verified.csv",
            "reason_code": "reconciliation_error",
            "reason": "610 is helium flow, not H2S ppm; 0.82/0.74 values are not the supported H2S pair.",
            "destination": "quarantined; replaced by corrected H2S-layer record",
            "reconsideration_trigger": "none; primary paper resolves the error",
        },
        {
            "study_id": "T1-001",
            "record_id": "T1-001-CU-H2S-18H (legacy Stage-2)",
            "source_or_file": "data/pilot/sulfur_stage2_verified.csv",
            "reason_code": "reconciliation_error",
            "reason": "610 is helium flow, not H2S ppm; 0.82/0.52 values are from the SO2 series.",
            "destination": "quarantined",
            "reconsideration_trigger": "exact H2S 18 h commercial-CZA value from true SI or defensible digitization",
        },
        {
            "study_id": "T1-004",
            "record_id": "T1-004-H2S",
            "source_or_file": "T1-004 main article and Wiley supporting information",
            "reason_code": "no_numeric_meoh_response",
            "reason": "The true SI was acquired and digitized, but Fig. S1 reports normalized COx conversion rather than methanol output.",
            "destination": "matched-control conversion proxy in supporting evidence",
            "reconsideration_trigger": "underlying methanol-output data from the authors",
        },
        {
            "study_id": "T1-007",
            "record_id": "T1-007-PDSIO2AL-MeOH-TOF",
            "source_or_file": "T1-007.pdf",
            "reason_code": "undefined_retention",
            "reason": "Methanol TOF is zero before and after H2S, so a retention ratio is undefined.",
            "destination": "mechanism-only",
            "reconsideration_trigger": "none for the retention target",
        },
        {
            "study_id": "T1-010",
            "record_id": "T1-010-PDCE series",
            "source_or_file": "T1-010.pdf",
            "reason_code": "duplicate_run",
            "reason": "The 30 ppm Pd/CeO2 series overlaps T1-012; T1-012 is the clearer paired report.",
            "destination": "duplicate cluster DUP-MA2008-PDCE-30PPM",
            "reconsideration_trigger": "none; use only for cross-checking",
        },
        {
            "study_id": "T1-015",
            "record_id": "T1-015-EQ-03 and T1-015-EQ-10",
            "source_or_file": "T1-015.pdf",
            "reason_code": "thermodynamic_calculation_not_experiment",
            "reason": "Calculated equilibrium ppb values are not methanol-response observations.",
            "destination": "process-design context",
            "reconsideration_trigger": "none for experimental response modeling",
        },
        {
            "study_id": "T2-001",
            "record_id": "T2-001 industrial rows 7A-9B",
            "source_or_file": "Chai et al. 1991 Table 2",
            "reason_code": "mixed_sulfur_field_exposure",
            "reason": "Industrial service involved H2S, COS, CS2, and other sulfur compounds with unknown exposure history.",
            "destination": "external qualitative validation",
            "reconsideration_trigger": "source-resolved H2S exposure history",
        },
        {
            "study_id": "T2-005",
            "record_id": "commercial Cu catalyst curves",
            "source_or_file": "Downloads/Sulfur Tolerance.pdf",
            "reason_code": "h2s_effect_not_separable",
            "reason": "Commercial Cu catalysts lost 70-90% activity over about 300 h both with and without H2S.",
            "destination": "model-assumption and aging-correction support",
            "reconsideration_trigger": "digitized matched clean/H2S curves with a defensible aging correction",
        },
        {
            "study_id": "T2-007",
            "record_id": "Tian et al. 2025",
            "source_or_file": "DOI 10.1016/j.jes.2025.02.018",
            "reason_code": "full_text_pending",
            "reason": "Preview lacks exact methanol-performance values.",
            "destination": "targeted acquisition gap",
            "reconsideration_trigger": "obtain main PDF and supporting information",
        },
        {
            "study_id": "T2-011",
            "record_id": "Beale et al. 2014",
            "source_or_file": "DOI 10.1016/j.jcat.2014.04.007",
            "reason_code": "non_methanol_reaction",
            "reason": "WGS/imaging study has no methanol-synthesis target.",
            "destination": "mechanism-only",
            "reconsideration_trigger": "none for the methanol-response target",
        },
        {
            "study_id": "T3-001",
            "record_id": "Ying et al. methanol decomposition paper",
            "source_or_file": "Downloads/Hydrogen Sulfide Poisoning of Methanol.pdf",
            "reason_code": "wrong_reaction_direction",
            "reason": "The reaction is methanol decomposition, not methanol synthesis.",
            "destination": "mechanism-only and source-specific decomposition scenario",
            "reconsideration_trigger": "none for the synthesis target",
        },
        {
            "study_id": "T2-003",
            "record_id": "Roberts et al. 1990",
            "source_or_file": "Downloads/Cataylst Poisoning.pdf",
            "reason_code": "no_h2s_experiment",
            "reason": "The paper's direct impurity experiments cover other contaminants, not H2S.",
            "destination": "other-impurity future work",
            "reconsideration_trigger": "none for H2S",
        },
    ]


def build_gap_matrix(
    core_rows: list[dict[str, Any]],
    kinetic_rows: list[dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    gate = spec["global_fit_gate"]
    studies = {row["study_id"] for row in core_rows}
    units = {row["experimental_unit_id"] for row in core_rows}
    concentrations = {
        float(row["h2s_concentration_ppm"])
        for row in core_rows
        if as_float(row["h2s_concentration_ppm"]) is not None
    }
    matched_studies = {
        row["study_id"]
        for row in core_rows
        if row.get("clean_or_initial_value") not in ("", None)
    }
    required_fields = spec["required_core_fields"]
    field_mapping = {
        "experimental_unit_id": "experimental_unit_id",
        "catalyst_family": "catalyst_family",
        "catalyst_label": "catalyst_label",
        "exposure_mode": "exposure_mode",
        "h2s_concentration_ppm": "h2s_concentration_ppm",
        "exposure_h": "exposure_h",
        "reaction_temperature_c": "temperature_c",
        "pressure_bar": "pressure_bar",
        "feed_basis": "feed_basis",
        "space_velocity_h_minus_1": "ghsv_h_minus_1",
        "methanol_metric": "methanol_metric",
        "clean_or_initial_value": "clean_or_initial_value",
        "h2s_value": "h2s_value",
        "activity_retention_fraction": "activity_retention_fraction",
        "measurement_status": "measurement_status",
        "source_location": "source_location",
        "duplicate_cluster_id": "duplicate_cluster_id",
        "study_id": "study_id",
    }
    observed_cells = 0
    possible_cells = len(core_rows) * len(required_fields)
    for row in core_rows:
        for field in required_fields:
            value = row.get(field_mapping[field], "")
            if value not in ("", None):
                observed_cells += 1
    completeness = observed_cells / possible_cells if possible_cells else 0

    wood_points = [
        row for row in kinetic_rows if row["comparable_group"] == "wood_observed_decay_rate"
    ]

    return [
        {
            "gap_id": "G01",
            "model_requirement": "Independent core studies",
            "current_evidence": len(studies),
            "required_evidence": gate["minimum_independent_studies"],
            "numeric_gap": gate["minimum_independent_studies"] - len(studies),
            "status": "open",
            "priority": "critical",
            "research_target": "Direct continuous-H2S Cu/ZnO/Al2O3 methanol studies with matched or aging-corrected clean controls.",
            "unlock_condition": "At least four independent eligible studies.",
        },
        {
            "gap_id": "G02",
            "model_requirement": "Independent core experimental units",
            "current_evidence": len(units),
            "required_evidence": gate["minimum_independent_experimental_units"],
            "numeric_gap": gate["minimum_independent_experimental_units"] - len(units),
            "status": "open",
            "priority": "critical",
            "research_target": "Extract run-level endpoints or time series without counting repeated points as independent studies.",
            "unlock_condition": "At least 20 independent run/condition units.",
        },
        {
            "gap_id": "G03",
            "model_requirement": "Distinct core H2S concentrations",
            "current_evidence": len(concentrations),
            "required_evidence": gate["minimum_distinct_h2s_concentrations"],
            "numeric_gap": gate["minimum_distinct_h2s_concentrations"] - len(concentrations),
            "status": "open",
            "priority": "critical",
            "research_target": "Matched retention at sub-ppm, 1-5 ppm, 10-50 ppm, and above-50 ppm exposure levels.",
            "unlock_condition": "At least four concentration levels in the core stratum.",
        },
        {
            "gap_id": "G04",
            "model_requirement": "Studies with matched or aging-corrected baseline",
            "current_evidence": len(matched_studies),
            "required_evidence": gate["minimum_studies_with_matched_or_aging_corrected_baseline"],
            "numeric_gap": gate["minimum_studies_with_matched_or_aging_corrected_baseline"] - len(matched_studies),
            "status": "open",
            "priority": "critical",
            "research_target": "Clean/H2S paired curves at the same time on stream or clean-aging curves enabling correction.",
            "unlock_condition": "At least two independent studies with defensible counterfactuals.",
        },
        {
            "gap_id": "G05",
            "model_requirement": "Core required-field completeness",
            "current_evidence": round(completeness, 3),
            "required_evidence": gate["minimum_required_field_completeness_fraction"],
            "numeric_gap": max(0, round(gate["minimum_required_field_completeness_fraction"] - completeness, 3)),
            "status": "closed" if completeness >= gate["minimum_required_field_completeness_fraction"] else "open",
            "priority": "high",
            "research_target": "Preserve catalyst, concentration, time, temperature, pressure, feed, GHSV, outcome, provenance, and duplicate metadata.",
            "unlock_condition": "At least 80% completeness.",
        },
        {
            "gap_id": "G06",
            "model_requirement": "Early, intermediate, and long exposure coverage",
            "current_evidence": "core has only 30 h",
            "required_evidence": "at least one core unit in <=10 h, 10-100 h, and >100 h bands",
            "numeric_gap": 2,
            "status": "open",
            "priority": "high",
            "research_target": "Time-course data or endpoints in the missing early and long-duration bands.",
            "unlock_condition": "All three exposure bands represented in at least two studies overall.",
        },
        {
            "gap_id": "G07",
            "model_requirement": "Industrial-pressure/feed generalizability",
            "current_evidence": "core: 20 bar, CO2/H2 only",
            "required_evidence": "30-80 bar and at least one CO/CO2/H2 syngas study",
            "numeric_gap": 2,
            "status": "open",
            "priority": "high",
            "research_target": "Commercial CZA direct-H2S experiments at industrial methanol pressures and syngas compositions.",
            "unlock_condition": "At least one eligible study in each missing pressure/feed regime.",
        },
        {
            "gap_id": "G08",
            "model_requirement": "Replicate or measurement uncertainty",
            "current_evidence": "no uncertainty on the sole core endpoint",
            "required_evidence": "reported replicates/error bars or raw data sufficient to estimate them",
            "numeric_gap": 1,
            "status": "open",
            "priority": "high",
            "research_target": "Supporting information or raw data with replicate dispersion.",
            "unlock_condition": "At least two core studies with uncertainty estimates.",
        },
        {
            "gap_id": "G09",
            "model_requirement": "Recovery after H2S removal",
            "current_evidence": "no eligible core recovery curve",
            "required_evidence": "matched activity before H2S, during H2S, and after removal",
            "numeric_gap": 1,
            "status": "open",
            "priority": "medium",
            "research_target": "Fresh-catalyst continuous-cofeed recovery experiments without flow changes.",
            "unlock_condition": "At least one eligible recovery time series.",
        },
        {
            "gap_id": "G10",
            "model_requirement": "Existing Wood kinetic series fully usable",
            "current_evidence": f"{len(wood_points)} exact decay-rate points; no row-level uncertainty or raw time series",
            "required_evidence": "digitizable/source numerical activity-time points and uncertainty",
            "numeric_gap": 1,
            "status": "open",
            "priority": "high",
            "research_target": "Digitize Figure 4 and retrieve any underlying data or higher-resolution scan.",
            "unlock_condition": "Reconstructable curves with a verified clean-aging reference.",
        },
        {
            "gap_id": "G11",
            "model_requirement": "He et al. numerical H2S trace",
            "current_evidence": "true SI acquired; eight approximate matched-control COx-conversion points digitized from Fig. S1",
            "required_evidence": "supporting-information PDF",
            "numeric_gap": 0,
            "status": "closed",
            "priority": "high",
            "research_target": "No further acquisition required; seek underlying numeric data only if exact uncertainty is needed.",
            "unlock_condition": "Acquisition closed; the COx proxy remains ineligible for the primary methanol-output target.",
        },
        {
            "gap_id": "G12",
            "model_requirement": "Tian et al. 2025 direct performance data",
            "current_evidence": "paywalled preview only",
            "required_evidence": "main PDF and supporting information",
            "numeric_gap": 2,
            "status": "open",
            "priority": "critical",
            "research_target": "DOI 10.1016/j.jes.2025.02.018 main article and SI.",
            "unlock_condition": "Exact post-H2S methanol activity/selectivity, exposure, and sulfur-loading values extracted.",
        },
    ]


def validate(
    observations: list[dict[str, Any]],
    core: list[dict[str, Any]],
    kinetics: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> None:
    assert observations, "No observations produced."
    ids = [row["experimental_unit_id"] for row in observations]
    assert len(ids) == len(set(ids)), "Observation IDs must be unique."
    assert len(core) == 1, "Current evidence audit should yield exactly one core model-ready row."
    assert core[0]["experimental_unit_id"] == "T2-004-CUZNAL-ACT"
    assert abs(float(core[0]["activity_retention_fraction"]) - 0.9) < 1e-12
    assert all(row["stratum"] == "core_continuous_cuznal" for row in core)
    assert len(kinetics) == 38, (
        "Expected nine Wood/Prasnikar records plus 28 Ying derivatives "
        "and the Ying intrinsic equation."
    )
    assert len(exclusions) >= 10
    assert len(gaps) == 12
    corrected = next(
        row
        for row in observations
        if row["experimental_unit_id"] == "T1-001-CU-H2S-4H-CORRECTED"
    )
    assert float(corrected["h2s_concentration_ppm"]) == 400
    assert abs(float(corrected["activity_retention_fraction"]) - 5 / 6) < 1e-12
    assert not any(
        row["experimental_unit_id"].startswith("T1-001-CU-H2S-18H")
        for row in observations
    ), "Unsupported commercial-CZA H2S 18 h row must remain quarantined."
    assert sum(row["study_id"] == "T3-001" for row in observations) == 7
    assert sum(row["study_id"] == "T3-002" for row in observations) == 28
    assert sum(
        row["eligibility_status"] == "matched_cox_proxy_only"
        for row in observations
    ) == 8


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    main_rows = read_rows(MAIN_DATA, delimiter="\t")
    stage2_rows = read_rows(STAGE2_DATA)
    main_by_id = index_by(main_rows, "Experimental Row ID")
    stage2_by_id = index_by(stage2_rows, "experimental_row_id")

    observations = build_observations(main_by_id, stage2_by_id)
    core = [row for row in observations if row["eligibility_status"] == "core_model_ready"]
    supporting = [row for row in observations if row["eligibility_status"] != "core_model_ready"]
    kinetics = build_kinetics(stage2_rows)
    exclusions = build_exclusions()
    gaps = build_gap_matrix(core, kinetics, spec)

    validate(observations, core, kinetics, exclusions, gaps)

    write_rows(OUTPUT_DIR / "h2s_all_curated_observations.csv", observations, OBSERVATION_FIELDS)
    write_rows(OUTPUT_DIR / "h2s_core_model_ready.csv", core, OBSERVATION_FIELDS)
    write_rows(OUTPUT_DIR / "h2s_supporting_evidence.csv", supporting, OBSERVATION_FIELDS)
    write_rows(OUTPUT_DIR / "h2s_kinetic_evidence.csv", kinetics, KINETIC_FIELDS)
    write_rows(OUTPUT_DIR / "h2s_excluded_and_quarantined.csv", exclusions, EXCLUDED_FIELDS)
    write_rows(OUTPUT_DIR / "h2s_evidence_gap_matrix.csv", gaps, GAP_FIELDS)

    summary = {
        "spec_version": spec["spec_version"],
        "all_curated_observations": len(observations),
        "core_model_ready": len(core),
        "supporting_evidence": len(supporting),
        "kinetic_records": len(kinetics),
        "excluded_or_quarantined_records": len(exclusions),
        "open_gaps": sum(row["status"] == "open" for row in gaps),
        "global_fit_gate_passed": False,
        "global_fit_gate_reason": (
            "Only one independent core study/experimental unit and one H2S "
            "concentration are currently eligible."
        ),
    }
    (OUTPUT_DIR / "h2s_dataset_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
