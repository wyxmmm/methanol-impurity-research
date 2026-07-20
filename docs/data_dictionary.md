# Main Data Dictionary

The primary dataset is `data/main_data.tsv`. One row represents one experimental condition or source-defined comparison.

| Column | Meaning |
|---|---|
| Study ID | Identifier for one original publication. |
| Experimental Row ID | Identifier for one experimental condition. |
| Paired Baseline ID | Clean or reference condition paired within the same publication. |
| Authors & Year | Short citation. |
| Short Title | Abbreviated source title. |
| DOI / Link | DOI or retrieval link. |
| Catalyst | Catalyst family or concise composition. |
| Catalyst Details | Support, loading, preparation, particle size, or other useful details. |
| Hydrogen Source | Explicitly supported hydrogen source or a neutral label when unknown. |
| Impurity Category | Broad contaminant family. |
| Impurity Species | Exact tested species or mixture. |
| Impurity Conc (ppm) | Standardized concentration when conversion to ppm is valid. |
| Temp (C) | Reaction or exposure temperature. |
| Pressure (bar) | Reaction pressure. |
| H2:CO2 ratio | Reported reactant ratio or feed notation. |
| Space velocity (GHSV, /h) | Gas hourly space velocity. |
| Time on stream (h) | Exposure or observation time. |
| MeOH metric type | Exact methanol or deactivation measurement. |
| Baseline | Compatible clean or reference value. |
| With impurity | Value during impurity exposure or for the poisoned condition. |
| Recovery Value | Value after returning to clean feed, when measured. |
| % change in MeOH | Calculated change for a valid baseline-impurity pair. |
| Measured / Calculated / Digitized | How the numerical value was obtained. |
| Reversible? | Whether lost performance returned after impurity removal or regeneration. |
| Deactivation noted? | Whether the study reports catalyst deactivation. |
| Notes / mechanism | Mechanism, caveat, or technical detail. |
| Source quote & page | Evidence location in the source. |
| Data Quality | Confidence level for the extracted row. |
| Modeling Status | Whether and how the row may be used quantitatively. |
| Duplicate Status | Whether the observation may overlap with another publication. |

Repeated Study IDs are expected because a single paper can report many useful experimental conditions. Experimental Row IDs should be unique.
