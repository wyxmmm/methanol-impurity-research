# Ghosh unsupported-In2O3 model input audit

Checkpoint date: 2026-08-03

## Scope and source identity

This audit covers the single-site LHHW/PFR model in Ghosh et al. (2021),
DOI `10.1016/j.cej.2021.129120`, and its genuine Supporting Information.
The model catalyst was unsupported In2O3 mixed physically with commercial
silica in a 2:1 mass ratio. It was not the supported In2O3/ZrO2 catalyst in
T1-001.

The supplied SI is a DOCX file. Its text, three tables, equations, and six
embedded figures were extracted and checked. A complete page-layout render
could not be produced because LibreOffice is unavailable in the local
environment; the embedded figures were inspected separately.

## Reactor and experimental basis

- 1.0 g total composite bed, comprising In2O3 and silica in a 2:1 mass ratio;
- stainless-steel fixed bed, 1.27 cm internal diameter and 21.5 cm length;
- approximately 1.4 cm catalyst-bed depth;
- 200-400 °C, reported total pressure 20-40 bar;
- H2/CO2 molar ratio 2-6;
- WHSV 6000-16000 mL gcat^-1 h^-1;
- steady-state results and carbon balance above 95%;
- water condensation occurred only after pressure reduction and cooling when
  conversion was approximately above 10%, and was accounted for in the
  reported gas composition.

The reactor was represented as a one-dimensional, pseudo-homogeneous,
isothermal, isobaric, steady-state plug-flow reactor with no axial dispersion
and negligible heat- and mass-transfer resistance. The SI reports Mears
parameters below 0.0015 and Weisz-Prater parameters below 0.1 over the tested
temperature range.

## Implemented chemistry

The three reactions are:

1. CO2 + 3 H2 ⇌ CH3OH + H2O
2. CO2 + H2 ⇌ CO + H2O
3. CO2 + 4 H2 ⇌ CH4 + 2 H2O

The published single-site inhibition term is:

```text
D = (1 + K_CO2 P_CO2 + sqrt(K_H2 P_H2))^2
```

The implemented rates are exact transcriptions of equations 8-10:

```text
r_MeOH = k1 * (P_CO2 P_H2^3 - P_MeOH P_H2O / Keq_MeOH)
          / (P_H2^2 D)

r_RWGS = k2 * (P_CO2 P_H2 - P_CO P_H2O / Keq_RWGS)
         / (sqrt(P_H2) D)

r_CH4 = k3 sqrt(P_CO2) sqrt(P_H2)
        * (1 - P_CH4 P_H2O^2 / (P_CO2 P_H2^4 Keq_CH4)) / D
```

The plug-flow balance is `dF_j/dw = sum_i(nu_ij r_i)`.

## Published parameters

At the 300 °C reference temperature:

| Quantity | Value |
| --- | ---: |
| MeOH k_ref | 6.9e-4 mol s^-1 bar^-2 kgcat^-1 |
| MeOH Ea | 35.7 kJ mol^-1 |
| RWGS k_ref | 1.8e-3 mol s^-1 bar^-1.5 kgcat^-1 |
| RWGS Ea | 54.5 kJ mol^-1 |
| methanation k_ref | 1.1e-4 mol s^-1 bar^-1 kgcat^-1 |
| methanation Ea | 42.5 kJ mol^-1 |
| H2 K_ref | 0.76 bar^-1 |
| CO2 K_ref | 0.79 bar^-1 |
| H2 adsorption enthalpy, Table 4 | -12.5 kJ mol^-1 |
| CO2 adsorption enthalpy, Table 4 | -25.9 kJ mol^-1 |

No parameters were refitted in this checkpoint.

## Reproducibility choices not fully specified by the source

The source does not provide executable thermochemical correlations or an
exact standard-volume convention. The implementation therefore uses:

- GRI-Mech 3.0 low-temperature NASA-7 polynomials for reaction equilibrium
  constants, with a dimensionless 1-bar standard state;
- 22,414 mL mol^-1 at 273.15 K and 1 atm to convert reported inlet volume;
- the full 1.0 g composite mass as the primary catalyst-weight basis;
- reported pressure as absolute pressure for the primary calculation;
- Table 4, rather than the contradictory prose, for adsorption enthalpies.

These choices are included in every machine-readable prediction.

## Source ambiguities explicitly tested

1. **Adsorption enthalpy conflict.** Table 4 assigns -12.5 kJ mol^-1 to H2
   and -25.9 kJ mol^-1 to CO2. Later prose states the reverse. Both variants
   were run; Table 4 reproduces the data better.
2. **Pressure convention.** Most of the article says total pressure, while a
   kinetic-analysis passage compares mean partial pressures with a 40 bar
   gauge feed. Reported-as-absolute and gauge-plus-atmosphere variants were
   run. Their errors are close, so this ambiguity is not fully resolved.
3. **Catalyst-mass basis.** The bed contained 1.0 g of a 2:1 In2O3/silica
   composite. Using total composite mass fits much better than integrating
   over only the two-thirds active-In2O3 mass.
4. **Optimization-set wording.** One passage says Series 5 was important for
   adsorption heats, while the parity-plot section says runs 1a-4d were used
   for optimization. The code reports results for all 32 Table 2 rows and
   does not invent a training split.

## Validation inputs and missing outputs

SI Table S3 provides six additional conditions, now curated in
`ghosh_2021_validation_inputs.csv`. It does not tabulate their measured outlet
values. Figure 12 shows six anonymous square markers in each parity panel,
but does not map a marker to run 6a-6f. Therefore the six inputs can be
predicted as a block, but condition-level held-out errors cannot be calculated
without the authors' underlying data.
