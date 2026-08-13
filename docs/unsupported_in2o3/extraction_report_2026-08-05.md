# Unsupported In2O3 Catalyst 1: complete extraction checkpoint

Date: 2026-08-05

## Bottom line

The evidence base is now large enough to proceed to an interpretable, cross-study empirical model of unsupported In2O3. It is not sufficient for a universal mechanistic model with one transferable parameter set.

The consolidated package contains:

- 174 condition-level response rows from 9 experimental studies;
- 64 rows whose primary response is reported in a table or the article text;
- 110 rows containing at least one graph-digitized response;
- 48 separately stored deactivation/time-series points;
- 28 kinetic or mechanistic constraints;
- 18 catalyst-description records; and
- 20 audited primary/review sources.

All automated quality checks pass: unique run identifiers, DOI completeness, physical percentage ranges, methanol-yield identities where available, and methanol rate unit conversions. Missing experimental values were not imputed.

## What changed in this checkpoint

The earlier search was incomplete. In particular, it missed studies that directly test whether unsupported In2O3 phase, morphology, and particle history change performance. The corrected audit added:

1. **Dang et al. 2020**, DOI `10.1126/sciadv.aaz2060` — cubic versus hexagonal/corundum In2O3 with facet and morphology control. Its full text and SI are open. This study adds temperature, H2/CO2-ratio, space-velocity, water-cofeed, and stability evidence. The paper shows that a hexagonal rod-like material with high {104} exposure behaves differently from cubic In2O3 and retains methanol selectivity at high temperature.
2. **Yang et al. 2020**, DOI `10.1016/j.cclet.2020.05.031` — cubic bixbyite versus rhombohedral/corundum In2O3. An open accepted manuscript was obtained and extracted. It adds temperature, pressure, GHSV, stability, activation-energy, and adsorption/reduction descriptors.
3. **Sun et al. 2020**, DOI `10.1039/D0GC01597K` — a Pt/In2O3 study containing an independent pure-In2O3 reference. Only the pure reference is included in Catalyst 1. The Pt-promoted rows remain outside the clean unsupported-In2O3 fit.
4. **Shi et al. 2021**, DOI `10.1021/acs.iecr.0c04688` — a high-priority mixed-phase study. Relevance was verified, but primary values were not copied from a review because the main paper/SI is still unavailable.
5. **Khatamirad et al. 2023**, DOI `10.1039/D3CY00148B` — relevant to later promoted-catalyst descriptor modeling and validation architecture, but not a clean Catalyst 1 parameter source.

This correction materially changes the model specification. “Unsupported In2O3” cannot be represented by one catalyst label. At minimum, phase/morphology, preparation, study identity, and time/history must be available to the model.

## What each supplied source contributed

| Source | Role in the evidence package |
|---|---|
| Ghosh 2021 | 32 exact condition rows and a published kinetic-model architecture; its fitted parameters are not treated as universal. |
| Wei 2025 | 9 exact pressure/temperature rows from SI Table S1. |
| Sun 2015 | 24 temperature-by-pressure rows; two text/table anchors and digitized figures. |
| Martin 2016 | 21 bulk-In2O3 mass-transfer, pressure, H2/CO2, and GHSV rows. The file named `Martin 2026.pdf` is the 2016 article, DOI `10.1002/anie.201600943`. |
| Araujo 2021 | 18 history-dependent hybrid CO2/CO feed rows; retained as a separate feed-extension branch. |
| Becker 2026 | 5 exact undoped/doped performance rows and detailed structural descriptors; doped rows are not clean Catalyst 1 rows. |
| Tsoukalou 2019 | 20 deactivation points and operando context; retained as time-series evidence. |
| Frei 2018 | Apparent activation energies and reaction orders; mechanistic constraints rather than a condition-output matrix. |
| Zou 2024 | Pressure-dependent H2-dissociation barriers; theoretical constraints rather than reactor outputs. |
| Dou 2018 | Elementary-step barriers for ZrO2-supported In2O3; explicitly excluded from unsupported-In2O3 fitting. |
| Schuhle 2020 and Jiang 2020 | Supported In2O3/ZrO2 impurity/water evidence; retained for later supported-catalyst and H2S work. |
| Cai 2023 and Wang 2021 | Reviews used only to audit literature coverage and locate primary studies. Review-transcribed values were not promoted to primary evidence. |
| Sun 2023 | Pt-promoted/supported extension; outside unsupported Catalyst 1. |

## Exact, calculated, and digitized values

Each response row records an `extraction_method`, `value_precision`, `source_location`, and DOI.

- `reported_table` and `reported_text` mean the source directly states the response.
- `reported_text_with_calculated_selectivity` means conversion and methanol rate were stated, and selectivity was calculated from the paper's reported flow and composition. The calculation is documented.
- `digitized_figure` means the coordinate was read from a rendered source figure and must receive lower weight or be tested in a sensitivity analysis.
- A blank cell means the paper did not provide a defensible value. It does not mean zero.

Clean-feed, water-cofeed, hybrid CO/CO2 feed, doped/supported, and deactivation rows carry separate eligibility labels.

## Wei 2025 provenance

Wei et al. 2025 was not one of the PDFs supplied by the user. The main article and SI were downloaded from the Chinese Journal of Catalysis publisher access exposed during the earlier research checkpoint and saved under:

`checkpoints/unsupported_in2o3_external_validation_2026-08-04/sources/`

The saved file inventory and hashes in that checkpoint establish provenance. Its DOI is `10.1016/S1872-2067(25)64657-2`.

## Model-readiness decision

### Defensible next model

Fit an interpretable hierarchical empirical model with separate responses for:

1. CO2 conversion;
2. methanol selectivity; and/or
3. methanol space-time yield where its mass and normalization basis are known.

Candidate operating inputs are temperature, pressure, H2/CO2 ratio, and log space velocity. Catalyst-level inputs should include phase/morphology, preparation or calcination information, particle/crystallite/BET descriptors when reported, and a study-level effect. The first validation must hold out entire studies, not random rows, because rows within one paper share a catalyst batch, apparatus, and normalization.

The primary fit should use clean-feed rows only. Graph-digitized rows should either receive lower weight or be removed in a reported sensitivity analysis. Water, CO-containing feed, promoted/supported catalysts, and time-dependent deactivation require separate model branches.

### Claims that are still not defensible

- one universal unsupported-In2O3 kinetic parameter set;
- mechanistic extrapolation across cubic, hexagonal, and rhombohedral phases without a phase term;
- validation by a random row split;
- pooling supported/doped catalysts with clean unsupported In2O3; or
- treating repeated points from one study as independent replications.

## Remaining PDFs

Highest priority:

1. Wu et al. 2023, DOI `10.1021/acs.energyfuels.3c02346` — main PDF. ACS lists free SI `ef3c02346_si_001.pdf`, but automated retrieval was blocked by the publisher's security page.
2. An et al. 2025, DOI `10.1016/j.joei.2025.102212` — main PDF and any SI.
3. Shi et al. 2021, DOI `10.1021/acs.iecr.0c04688` — main PDF and SI.
4. Yang et al. 2020, DOI `10.1016/j.cclet.2020.05.031` — SI only; the accepted main manuscript is already extracted.

Lower priority because they are outside clean Catalyst 1:

- Khatamirad et al. 2023, DOI `10.1039/D3CY00148B` — promoted-catalyst modeling architecture.
- Ng et al. 2022, DOI `10.1016/j.apcata.2022.118885` — In2O3/CeO2 dual-site architecture; CeO2 is the wrong support for Catalyst 1.

The missing PDFs can improve phase, size, preparation, and model-architecture coverage. They are not a reason to discard the current evidence package or prevent development of the first restricted empirical model.

## Recommended immediate next step

Freeze this extraction checkpoint and implement the first clean-feed, phase-aware hierarchical model. Run two versions: exact/reported rows only, then exact plus digitized rows with reduced weight. Evaluate both by whole-study holdout and report where predictions fail by catalyst phase and preparation. This will show whether the existing evidence supports a useful restricted model before more time is spent collecting every promoted or supported In2O3 paper.

After that model checkpoint, revisit H2S with the same literature-audit standard and explicitly search for missed primary sulfur studies before deciding that the H2S evidence gate cannot be met.
