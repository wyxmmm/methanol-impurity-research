# H₂S stage — paper-ready explanation

## Plain-language conclusion

The literature confirms that H₂S can rapidly and severely deactivate copper-based methanol catalysts, but the available experiments are too different to support one accurate universal equation yet. Catalyst formulation, pressure, feed composition, exposure method, response metric, and clean baseline differ across studies. Treating every spreadsheet row as if it were the same experiment would produce a precise-looking but scientifically misleading model.

For that reason, this stage separated the evidence into compatible groups and required a minimum evidence gate before fitting a cross-study model. The strict target was continuous H₂S exposure over Cu/ZnO/Al₂O₃ during methanol synthesis, with activity retention calculated against a matched or aging-corrected clean baseline.

Only one study currently satisfies that exact target: a commercial Cu/ZnO/Al₂O₃ catalyst exposed to 8.1 ppm H₂S at 240°C and 20 bar retained approximately 90% normalized methanol activity after 30 h. The target dataset therefore has one independent study, one condition, and one concentration. The planned minimum is four independent studies, 20 independent experimental units, four concentrations, and two matched-baseline studies.

The correct result is consequently an evidence engine, not a universal fitted curve. It preserves:

- the one strict commercial-CZA endpoint;
- source-specific Wood exponential decay rates;
- a matched clean/H₂S COx-conversion trace from He et al.;
- Ying’s atmospheric methanol-decomposition activity series and intrinsic equation;
- ex-situ damage, guard-bed, sulfur-loading, non-Cu, and mechanism evidence in separate strata.

These components can be inspected and calculated within their original experimental domains, but they are not pooled.

## Methods paragraph

Experimental H₂S observations were audited at the physical-run level and classified by catalyst family, reaction direction, exposure protocol, outcome, and baseline quality. The primary outcome was methanol-activity retention, defined as methanol output under H₂S divided by a matched or aging-corrected clean-feed counterfactual. Continuous cofeed, ex-situ poisoning, sulfur-loading, guard-bed, non-Cu, and mechanism-only evidence were analyzed separately. Repeated time points from one run and companion publications from the same experimental series were not counted as independent units. A universal model required at least four independent studies, 20 independent experimental units, four H₂S concentrations, two studies with defensible clean counterfactuals, and 80% required-field completeness. Validation was specified as whole-study holdout rather than random row splitting.

## Results paragraph

After reconciliation and targeted research, the H₂S evidence layer contained 75 curated observations and 38 source-specific kinetic records, but only one observation met the strict Cu/ZnO/Al₂O₃ continuous-cofeed methanol-synthesis definition. The fit gate failed at 1/4 studies, 1/20 independent units, 1/4 concentrations, and 1/2 matched-baseline studies; required-field completeness passed. Whole-study validation was not estimable because holding out the sole eligible study left no training evidence. Source-specific calculations were therefore retained without cross-study pooling. Ying’s fitted methanol-decomposition equation reproduced its seven exact Table II activity points with a within-source MAE of approximately 0.0595 and RMSE of 0.0657, but this result does not validate transfer to methanol synthesis.

## Interpretation paragraph

The evidence supports a qualitative conclusion that H₂S is a strong copper-catalyst poison and that its observed effect depends on concentration, exposure time, catalyst formulation, and protocol. It does not yet support a general numerical prediction across industrial methanol catalysts. The distinction is important: a COx-conversion proxy, a methanol-decomposition rate, an ex-situ poisoned sample, and a continuous methanol-synthesis run constrain different parts of the problem. Combining them as interchangeable outcomes would hide protocol effects and underestimate uncertainty.

## Limitation paragraph

The main limitation is not the number of extracted rows but the number of independent, compatible experiments. Many rows are repeated points from one curve, different outcomes from one physical run, or companion reports from one experiment. Several studies omit H₂S concentration, exposure dose, a matched clean-aging trace, raw uncertainty, or a methanol-output endpoint. The most important unresolved source is Tian et al. 2025, for which the main article and supporting information are still required. Even if that paper supplies a second eligible experiment, the dataset would remain below the preregistered four-study gate.

## Defensible claim

Use:

> The available literature was sufficient to build source-specific H₂S deactivation calculations and an auditable evidence structure, but insufficient to validate a universal cross-study methanol-activity model.

Do not use:

> The model accurately predicts methanol loss for any Cu/ZnO/Al₂O₃ catalyst at any H₂S concentration.

## What would unlock the next model

The highest-value experiments would measure the same commercial catalyst under:

1. at least four H₂S concentrations spanning sub-ppm to above 50 ppm;
2. early, intermediate, and long exposure times;
3. matched clean-aging and H₂S curves;
4. fixed temperature, pressure, feed, flow, and GHSV;
5. methanol rate/productivity/yield rather than selectivity alone;
6. replicates or raw uncertainty;
7. recovery after H₂S removal.

With at least four independent studies and two defensible counterfactuals, the next stage could test a parsimonious concentration–time model using entire held-out studies.

