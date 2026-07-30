# H₂S Phase 5 — Evidence engine and model decision

Date: 2026-07-29

## Outcome

No universal H₂S prediction curve was fitted. The preregistered gate fails because the strict Cu/ZnO/Al₂O₃ continuous-cofeed methanol-synthesis core contains one study, one independent condition, one H₂S concentration, and one usable baseline. Holding out that study leaves no training set.

Instead, `src/h2s_evidence_engine.py` implements five source-specific tools:

| Tool | What it calculates | Allowed domain | Primary synthesis model? |
|---|---|---|---:|
| `prasnikar_cza_endpoint` | Normalized methanol activity between the reported 0 h and 30 h endpoints | 8.1 ppm, CZA, 240°C, 20 bar, H₂:CO₂=3, GHSV 40,000 h⁻¹ | Only as bounded exact-condition interpolation |
| `wood_c79_exponential` | `A(t)=exp(-k_obs t)` using one of three reported C79-1 rates | Exact 1.6, 3.2, or 33 ppm runs at 230°C and 34.47 bar gauge | Separate historical source/catalyst |
| `he_matched_cox_proxy` | H₂S/clean normalized COx-conversion ratio | 50 ppm, 60 bar, syngas, 50–1,000 h, accelerated temperature cycling | No |
| `ying_empirical_decomposition` | Interpolated relative methanol-decomposition activity | 211 ppm, 260°C, atmospheric, 0–24 h | No |
| `ying_intrinsic_decomposition` | Analytic solution to Ying Eq. 7 | 105–281 ppm, 250–265°C, atmospheric | No |

Each function rejects out-of-domain inputs instead of silently extrapolating.

## What the code does

### Prašnikar exact-condition interpolation

The only strict core endpoint is 90% activity after 30 h at 8.1 ppm H₂S. The engine can interpolate between `(0 h, 1.0)` and `(30 h, 0.9)` at those exact conditions. It cannot vary concentration or predict beyond 30 h.

This is deliberately modest. A straight line through one endpoint is not evidence for the universal physical shape of deactivation.

### Wood source-specific exponential calculation

For the C79-1 catalyst, Wood reported observed first-order decay rates:

- 1.6 ppm: `0.011 h⁻¹`;
- 3.2 ppm: `0.025 h⁻¹`;
- 33 ppm: `0.153 h⁻¹`.

The engine applies `A(t)=exp(-k_obs t)` only for those exact runs. It does not interpolate a new concentration-response curve. The 33 ppm result retains the source warning that transport influenced the response.

### He matched-control proxy

The He SI is useful because it contains a clean-aging counterfactual. The engine interpolates the digitized ratio of the H₂S trace to the clean trace. A ±0.01 absolute trace-read sensitivity is propagated to a lower/upper range. That range is a digitization sensitivity, not a statistical confidence interval.

The output remains explicitly labeled COx conversion. It cannot be presented as methanol productivity.

### Ying empirical and intrinsic decomposition tools

The empirical tool interpolates exact Table II values. The intrinsic tool solves:

`-da/dt = 0.1504 × 10^5 exp[-81128/(R_g T)] C_H2S(ppm) a`.

For the exact 260°C/211 ppm series, Eq. 7 has a within-source MAE of approximately `0.0595` and RMSE of `0.0657` against the seven Table II activity values. This is a reproduction check, not external validation.

## Study-held-out validation

The required validation unit is an entire study. The only strict core study is T2-004:

| Held-out study | Training studies left | Result |
|---|---:|---|
| T2-004 | 0 | Not estimable |

The engine writes this result rather than manufacturing a score from random row splits or from supporting proxy studies.

## Uncertainty handling

- Reported uncertainty is preserved when available.
- Missing error bars remain missing.
- The approximate Prašnikar endpoint is labeled approximate.
- He values include digitization sensitivity only.
- Wood coefficients have no row-level uncertainty in the accessible source.
- Ying Eq. 7 is labeled a within-source fitted equation with no external validation.

No confidence interval is invented from the spread of scientifically incompatible studies.

## Running the engine

Rebuild every H₂S result:

```powershell
.\.venv\Scripts\python.exe -m src.h2s_evidence_engine
```

Query one bounded source model:

```powershell
.\.venv\Scripts\python.exe -m src.h2s_evidence_engine `
  --model prasnikar_cza_endpoint `
  --h2s-ppm 8.1 `
  --time-h 20
```

The estimate is about `0.933`, but it means only:

> endpoint-anchored interpolation for the exact T2-004 conditions.

It does not mean that every CZA catalyst exposed to 8.1 ppm H₂S will retain 93.3% activity after 20 h.

## Generated results

- `results/h2s/model_decision.json`
- `results/h2s/evidence_gate.csv`
- `results/h2s/scenario_catalog.csv`
- `results/h2s/scenario_predictions.csv`
- `results/h2s/source_model_reproduction.csv`
- `results/h2s/held_out_study_validation.csv`
- `results/h2s/h2s_source_specific_scenarios.svg`
- `results/h2s/h2s_source_specific_scenarios.png`

