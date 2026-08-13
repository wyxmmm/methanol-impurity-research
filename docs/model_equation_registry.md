# Model Equation Registry

## Purpose and status labels

This is the controlled record of the mathematical equations used in this
project. It is intended to support code review, the Methods section of a paper,
and later model revision. An equation must not silently enter the analysis:
future equations must be added here with their variables, units, provenance,
applicability domain, and implementation status.

Status labels used below:

- **Implemented — published:** reproduced from a named source model without
  fitting it to the external validation studies.
- **Implemented — project-derived:** a transparent conversion, statistical
  operation, or numerical method introduced in this project.
- **Implemented — source-specific:** reproduced from one sulfur study and not
  transferable outside that study's stated domain.
- **Candidate — not implemented:** a possible next-stage equation. It is not a
  current model result and must not be described as validated.

The project's scientific endpoint is the effect of an impurity on methanol
output. The clean-catalyst model is a necessary reference layer, not the final
research question:

$$
\text{operating conditions}\longrightarrow M_{\mathrm{clean}}
\longrightarrow R_{\mathrm{impurity}}
\longrightarrow M_{\mathrm{impure}}.
$$

The clean baseline and impurity-response data must refer to the same catalyst
family and sufficiently comparable catalyst state. A model for unsupported
In2O3 cannot by itself supply the clean baseline for In2O3/ZrO2 or
Cu/ZnO/Al2O3.

## Symbols and units

| Symbol | Meaning | Unit or scale |
|---|---|---|
| $T$ | absolute temperature | K |
| $T_C$ | temperature | degrees C |
| $P$ or $p_i$ | total or species partial pressure | bar |
| $F_i$ | molar flow of species $i$ | mol/s |
| $W$ | catalyst mass coordinate used by PFR integration | kg catalyst |
| $r_j$ | rate of reaction $j$ | mol/(kg catalyst s) |
| $X_{CO2}$ | CO2 conversion | fraction or percent as stated |
| $S_{MeOH}$ | carbon-based methanol selectivity | fraction or percent |
| $Y_{MeOH}$ | carbon-based methanol yield | fraction or percent |
| $R_{imp}$ | activity or output retained under impurity | fraction |
| $C_{H2S}$ | H2S concentration | ppm unless stated otherwise |
| $t$ | exposure or time on stream | h unless stated otherwise |
| WHSV | standard gas volume per catalyst mass per time | mL/(g h) |
| $y_I$ | inlet inert mole fraction | fraction |

Percent-valued variables must be divided by 100 before being used as
fractions. Pressure standards, flow standards, and catalyst-mass bases must be
preserved from each source rather than assumed equivalent.

## A. Ghosh unsupported-In2O3 clean-catalyst PFR

Implementation: `src/ghosh_in2o3_pfr.py`. These equations reproduce the Ghosh
unsupported-In2O3 kinetic model (DOI `10.1016/j.cej.2021.129120`). External
studies were used as locked tests, not as inputs to refit the published
parameters.

### Reactions and thermodynamics

**EQ-G-001 — reaction network. Implemented — published.**

$$
\begin{aligned}
CO_2+3H_2 &\rightleftharpoons CH_3OH+H_2O,\\
CO_2+H_2 &\rightleftharpoons CO+H_2O,\\
CO_2+4H_2 &\rightleftharpoons CH_4+2H_2O.
\end{aligned}
$$

**EQ-G-002 — NASA enthalpy polynomial. Implemented — published standard.**

$$
\frac{h_i^\circ(T)}{RT}=a_1+\frac{a_2T}{2}+\frac{a_3T^2}{3}
+\frac{a_4T^3}{4}+\frac{a_5T^4}{5}+\frac{a_6}{T}.
$$

**EQ-G-003 — NASA entropy polynomial. Implemented — published standard.**

$$
\frac{s_i^\circ(T)}{R}=a_1\ln T+a_2T+\frac{a_3T^2}{2}
+\frac{a_4T^3}{3}+\frac{a_5T^4}{4}+a_7.
$$

**EQ-G-004 — dimensionless Gibbs energy. Implemented — derived from
EQ-G-002/003.**

$$
\frac{g_i^\circ}{RT}=\frac{h_i^\circ}{RT}-\frac{s_i^\circ}{R},\qquad
\frac{\Delta_rG_j^\circ}{RT}=\sum_i\nu_{ij}\frac{g_i^\circ}{RT}.
$$

**EQ-G-005 — equilibrium constant. Implemented — thermodynamic identity.**

$$K_{p,j}(T)=\exp\left(-\frac{\Delta_rG_j^\circ}{RT}\right).$$

### Kinetics

**EQ-G-006 — Arrhenius-style temperature adjustment. Implemented —
published.** For a reported reference value $\psi_{ref}$,

$$
\psi(T)=\psi_{ref}\exp\left[
\frac{E\,1000}{R}\left(\frac{1}{T_{ref}}-\frac{1}{T}\right)
\right].
$$

$E$ is entered in kJ/mol in the implementation, hence the factor 1000.

**EQ-G-007 — adsorption/inhibition denominator. Implemented — published.**

$$D=\left(1+K_{CO2}p_{CO2}+\sqrt{K_{H2}p_{H2}}\right)^2.$$

**EQ-G-008 — methanol synthesis rate. Implemented — published.**

$$
r_{MeOH}=k_{MeOH}
\frac{p_{CO2}p_{H2}^3-p_{MeOH}p_{H2O}/K_{p,MeOH}}
{p_{H2}^2D}.
$$

**EQ-G-009 — reverse water-gas-shift rate. Implemented — published.**

$$
r_{RWGS}=k_{RWGS}
\frac{p_{CO2}p_{H2}-p_{CO}p_{H2O}/K_{p,RWGS}}
{\sqrt{p_{H2}}D}.
$$

**EQ-G-010 — methane formation rate. Implemented — published.**

$$
r_{CH4}=k_{CH4}\sqrt{p_{CO2}p_{H2}}
\frac{1-p_{CH4}p_{H2O}^2/
(p_{CO2}p_{H2}^4K_{p,CH4})}{D}.
$$

### Feed construction and inert gas

**EQ-G-011 — standard-volume flow conversion. Implemented —
project-derived.**

$$
F_{tot,in}=\frac{WHSV\,m_{cat}}{22414\times3600}.
$$

Here 22414 mL/mol is the standard molar volume assumed by the current program.
This assumption must be revisited if a paper defines its standard flow at a
different temperature or pressure.

**EQ-G-012 — split inert from reactive feed. Implemented — project-derived.**

$$F_{reactive}=(1-y_I)F_{tot,in},\qquad F_I=y_IF_{tot,in}.$$

**EQ-G-013 — split H2 and CO2 using inlet ratio $R_f=H_2/CO_2$.
Implemented — project-derived.**

$$
F_{CO2,in}=\frac{F_{reactive}}{1+R_f},\qquad
F_{H2,in}=F_{reactive}-F_{CO2,in}.
$$

**EQ-G-014 — partial pressure with inert dilution. Implemented — physical
definition.**

$$
p_i=P\,\frac{F_i}{F_I+\sum_{k\in reactive}F_k}.
$$

The inert has zero stoichiometric source term but remains in total flow. This
is why adding inert is more than simply renaming the feed: it lowers every
reactive partial pressure and changes residence-time bookkeeping. At $y_I=0$,
the original implementation is recovered exactly.

### PFR integration

**EQ-G-015 — isothermal plug-flow material balance. Implemented — reactor
model identity.**

$$\frac{dF_i}{dW}=\sum_j\nu_{ij}r_j.$$

**EQ-G-016 — fourth-order Runge-Kutta step. Implemented — numerical method.**

$$
\begin{aligned}
k_1&=f(W,F),\\
k_2&=f(W+h/2,F+hk_1/2),\\
k_3&=f(W+h/2,F+hk_2/2),\\
k_4&=f(W+h,F+hk_3),\\
F_{n+1}&=F_n+\frac{h}{6}(k_1+2k_2+2k_3+k_4).
\end{aligned}
$$

### Reported outputs

**EQ-G-017 — CO2 conversion. Implemented — definition.**

$$X_{CO2}(\%)=100\frac{F_{CO2,in}-F_{CO2,out}}{F_{CO2,in}}.$$

**EQ-G-018 — carbon selectivity. Implemented — definition.**

$$
S_q(\%)=100\frac{F_{q,out}}
{F_{CO2,in}-F_{CO2,out}},\qquad q\in\{MeOH,CO,CH_4\}.
$$

This form assumes one carbon atom in each listed product.

**EQ-G-019 — methanol yield. Implemented — definition.**

$$
Y_{MeOH}(\%)=\frac{X_{CO2}(\%)S_{MeOH}(\%)}{100}
=100\frac{F_{MeOH,out}}{F_{CO2,in}}.
$$

**EQ-G-020 — outlet mole fraction. Implemented — definition.**

$$y_{i,out}=\frac{F_{i,out}}{F_I+\sum_kF_{k,out}}.$$

**EQ-G-021 — methanol mass output and space-time yield. Implemented —
project-derived.**

$$
\dot m_{MeOH}=F_{MeOH,out}MW_{MeOH}(3600),\qquad
STY_{MeOH}=\frac{\dot m_{MeOH}}{m_{cat}}.
$$

The implementation reports $\dot m_{MeOH}$ in g/h and $STY_{MeOH}$ in
g-MeOH/(g-catalyst h).

**EQ-G-022 — composite active-mass sensitivity. Implemented — explicit
sensitivity assumption, not a measured universal constant.**

$$m_{active}=\frac{2}{3}m_{composite}.$$

This factor is used only where the documented catalyst composition justifies
that sensitivity case. It must not be silently generalized.

**EQ-G-023 — normalized catalyst-mass equivalence for mass-normalized flow.
Implemented — project-derived identity.**

If a source directly reports $WHSV=\dot V/m_{cat}$ but not the physical mass,
the conversion/selectivity/yield simulation may use a declared normalization
$m_{cat}^*=c m_{cat}$ and $\dot V^*=c\dot V$, because

$$
\frac{\dot V^*}{m_{cat}^*}
=\frac{c\dot V}{cm_{cat}}=WHSV.
$$

The current PFR then preserves feed-to-catalyst ratio and dimensionless reactor
outputs. Absolute outlet flow is not physical under this normalization. This
identity does not authorize converting a conventional volume-based GHSV in
h$^{-1}$ into mass-normalized WHSV.

## B. Unsupported-In2O3 empirical clean-catalyst model

Implementation: `src/unsupported_in2o3_first_model.py`. This is an
interpretable literature-derived regression layer, distinct from Ghosh's
mechanistic model.

**EQ-E-001 — temperature features. Implemented — project-derived.**

$$
A(T_C)=1000\left(\frac{1}{573.15}-\frac{1}{T_C+273.15}\right),\qquad
C(T_C)=\left(\frac{T_C-300}{100}\right)^2.
$$

**EQ-E-002 — log ratio features. Implemented — project-derived.**

$$
P'=\ln(P/40),\qquad R'=\ln[(H_2/CO_2)/3],\qquad
SV'=\ln(SV/10000).
$$

**EQ-E-003 — catalyst-phase indicators. Implemented — project-derived.**

$$I_p=1\ \text{if phase category }p\text{ is reported, otherwise }0.$$

Here `phase` means the reported solid/catalyst structural category used as a
categorical predictor; it does not mean gas phase. Cubic In2O3 is the current
reference category.

**EQ-E-004 — logit transform for a percentage response. Implemented —
project-derived.**

$$z=\ln\frac{u}{1-u},\qquad u=\operatorname{clip}(y/100,\epsilon,1-\epsilon).$$

**EQ-E-005 — inverse logit. Implemented — mathematical inverse.**

$$\widehat y(\%)=100\frac{1}{1+e^{-\widehat z}}.$$

**EQ-E-006 — log transform for positive STY. Implemented —
project-derived.**

$$z=\ln(STY),\qquad \widehat{STY}=e^{\widehat z}.$$

**EQ-E-007 — feature standardization. Implemented — statistical definition.**

$$x_j^{std}=\frac{x_j-\mu_j}{s_j}.$$

**EQ-E-008 — linear predictor. Implemented — regression definition.**

$$\widehat z_i=\beta_0+\sum_j\beta_jx_{ij}^{std}.$$

**EQ-E-009 — evidence weight. Implemented — project policy.**

For row quality $q_i$ (reported $=1.00$, calculated $=0.75$, digitized
$=0.35$), weights are normalized within study:

$$w_i=\frac{q_i}{\sum_{k\in study(i)}q_k}.$$

This prevents a paper with many rows from dominating solely because it reports
more conditions.

**EQ-E-010 — weighted ridge fit. Implemented — statistical method.**

$$
\widehat\beta=\arg\min_\beta
\left[\sum_iw_i(z_i-x_i^T\beta)^2+\lambda\sum_{j>0}\beta_j^2\right].
$$

The intercept is not penalized. In matrix form,

$$\widehat\beta=(X^TWX+\lambda L)^{-1}X^TWz.$$

**EQ-E-011 — leave-one-study-out benchmark. Implemented —
project-derived.**

For a held-out study, the baseline prediction is the median of the training
study medians. No row from the held-out publication is used to form it.

**EQ-E-012 — empirical prediction interval. Implemented —
project-derived.**

$$q_{0.95}=Q_{0.95}(|y_i-\widehat y_i|),\qquad
[\widehat y-q_{0.95},\widehat y+q_{0.95}].
$$

The residuals come from whole-study-held-out predictions. This is an empirical
error band, not a mechanistic confidence interval.

**EQ-E-013 — derived yield. Implemented — identity.**

$$Y_{MeOH}(\%)=X_{CO2}(\%)S_{MeOH}(\%)/100.$$

## C. Validation equations

Used in the empirical and locked multi-study Ghosh comparisons.

**EQ-V-001 — residual and absolute error. Implemented.**

$$e_i=\widehat y_i-y_i,\qquad AE_i=|e_i|.$$

**EQ-V-002 — aggregate errors. Implemented.**

$$
MAE=\frac1n\sum_i|e_i|,\quad
RMSE=\sqrt{\frac1n\sum_ie_i^2},\quad
Bias=\frac1n\sum_ie_i.
$$

**EQ-V-003 — study-balanced error. Implemented — project-derived.**

$$
E_{balanced}=\frac1S\sum_{s=1}^S
\left(\frac1{n_s}\sum_{i\in s}L_i\right).
$$

Each publication receives equal top-level weight even if it contributes a
different number of rows.

**EQ-V-004 — benchmark improvement. Implemented.**

$$Improvement(\%)=100\frac{E_{benchmark}-E_{model}}{E_{benchmark}}.$$

**EQ-V-005 — Pearson residual association. Implemented — descriptive
diagnostic.**

$$
r_{xy}=\frac{\sum_i(x_i-\bar x)(e_i-\bar e)}
{\sqrt{\sum_i(x_i-\bar x)^2\sum_i(e_i-\bar e)^2}}.
$$

**EQ-V-006 — Spearman residual association. Implemented — descriptive
diagnostic.**

$$\rho_s=r_{\operatorname{rank}(x),\operatorname{rank}(e)}.$$

Average ranks are used for ties. EQ-V-005/006 describe associations and do not
establish that an operating variable causes a model error. Pooled values can
be confounded by study, phase, and preparation, so complete-study values are
reported alongside them.

**EQ-V-007 — ordinary least-squares diagnostic slope. Implemented —
descriptive diagnostic.**

$$
b=\frac{\sum_i(x_i-\bar x)(e_i-\bar e)}
{\sum_i(x_i-\bar x)^2}.
$$

No fitted slope is inserted into the kinetic model.

**EQ-V-008 — exact methanol-yield error decomposition. Implemented —
project-derived identity.**

For $Y=XS/100$, $\Delta X=\widehat X-X$, and
$\Delta S=\widehat S-S$,

$$
\widehat Y-Y
=\frac{\Delta X\,S}{100}
+\frac{X\,\Delta S}{100}
+\frac{\Delta X\,\Delta S}{100}.
$$

The three terms are labeled the conversion contribution, selectivity
contribution, and interaction contribution. Opposite signs in the first two
terms reveal within-row error cancellation. Cross-row or cross-study
cancellation can also make mean signed yield bias appear small despite large
absolute errors.

These error equations quantify transfer performance; they do not prove that a
mechanism is correct. In the initial locked external Ghosh run, all 88
conditions were computationally solvable and 62 were treated as scientifically
interpretable while Yang's unit wording was held. The Part A source audit later
verified Yang's mass-normalized unit in the main Figure 2 caption, releasing
all 26 Yang rows as lower-certainty graph-digitized comparisons. Automated
tests passing means software checks passed; it does not mean the corresponding
number of experiments validated the chemistry.

## D. Implemented sulfur/impurity data equations

These calculations normalize within-study impurity effects. They do not make
different catalysts interchangeable.

**EQ-I-001 — activity/output retention. Implemented — project-derived.**

$$R_{imp}=\frac{M_{impure}}{M_{clean}},\qquad
Retention(\%)=100R_{imp}.$$

**EQ-I-002 — percentage loss. Implemented — definition.**

$$Loss(\%)=100-Retention(\%).$$

**EQ-I-003 — log retention. Implemented — project-derived.**

$$\ell_R=\ln(R_{imp})=\ln[Retention(\%)/100].$$

**EQ-I-004 — concentration-time exposure index. Implemented — descriptive
proxy only.**

$$D_{ppm\cdot h}=C_{impurity,ppm}\,t_h.$$

Equal $C\times t$ values are not assumed chemically equivalent. Exposure mode,
temperature, catalyst, recovery, and cumulative history remain separate.

**EQ-I-005 — yield retention from conversion and selectivity retention.
Implemented only where both normalized factors share the same baseline.**

$$R_Y=R_XR_S.$$

**EQ-I-006 — paired yield from reported conversion and selectivity.
Implemented — identity.**

$$Y_{MeOH}=X_{CO2}S_{MeOH}.$$

Here all three terms are fractions; if percentages are used, divide the product
by 100 as in EQ-G-019.

**EQ-I-007 — unit conversion from grams to millimoles. Implemented.**

$$n_{mmol}=1000\frac{m_g}{MW_{g/mol}}.$$

## E. Source-specific H2S equations

Implementation: `src/h2s_evidence_engine.py`. These are deliberately protected
by domain checks and must not be presented as one universal H2S model.

**EQ-S-001 — bounded linear interpolation. Implemented — mathematical
connector between reported points.**

$$y(x)=y_0+\frac{x-x_0}{x_1-x_0}(y_1-y_0).$$

No extrapolation beyond the source-specific point range is allowed.

**EQ-S-002 — Prasnikar endpoint interpolation. Implemented — source-specific.**

$$R(t)=1-\frac{0.1}{30}t,$$

only for the reported 8.1 ppm H2S condition and $0\le t\le30$ h. This joins
reported endpoints; it is not a fitted concentration-response law.

**EQ-S-003 — Wood exponential retention. Implemented — source-specific.**

$$R(t)=\exp(-k_{obs}t).$$

Only the exact reported Wood C79-1 concentration/rate pairs (1.6, 3.2, or 33
ppm) are accepted by the program.

**EQ-S-004 — He COx proxy interpolation. Implemented — source-specific
proxy.** EQ-S-001 is used between the digitized time points. The response is a
COx-related proxy, not methanol yield, and therefore cannot directly validate a
methanol-output equation.

**EQ-S-005 — Ying empirical time-series interpolation. Implemented —
source-specific.** EQ-S-001 is used only within the exact reported run.

**EQ-S-006 — Ying intrinsic deactivation coefficient. Implemented —
source-specific.**

$$
k_d=0.1504\times10^5\exp\left(-\frac{81128}{RT}\right)C_{H2S}.
$$

**EQ-S-007 — Ying analytic activity solution. Implemented —
source-specific.**

$$R(t)=R_0\exp(-k_dt).$$

The implementation restricts EQ-S-006/007 to 105--281 ppm H2S and 250--265
degrees C. The source concerns methanol decomposition, not a universal methanol
synthesis poisoning law.

## F. Tuning equations under consideration

Everything in this section is **Candidate — not implemented**. Tuning does not
belong before catalyst/impurity scope is fixed, unit ambiguities are resolved,
and a locked untuned baseline has been diagnosed.

**EQ-T-001 — limited reaction-rate multipliers. Candidate — not
implemented.**

$$
r_{MeOH}^*=\alpha_{MeOH}r_{MeOH}^{Ghosh},\quad
r_{RWGS}^*=\alpha_{RWGS}r_{RWGS}^{Ghosh},\quad
r_{CH4}^*=\alpha_{CH4}r_{CH4}^{Ghosh}.
$$

This is a small calibration layer, not permission to refit every kinetic and
adsorption parameter.

**EQ-T-002 — penalized, study-balanced calibration objective. Candidate — not
implemented.**

$$
J(\theta)=\sum_s\frac1{n_s}\sum_{i\in s}\sum_qw_{iq}
\left[\frac{\widehat y_{iq}(\theta)-y_{iq}}{\sigma_q}\right]^2
+\lambda\|L(\theta-\theta_{ref})\|_2^2.
$$

$q$ identifies outputs such as conversion, selectivity, and yield;
$\sigma_q$ prevents different numeric scales from dominating; the penalty
discourages unjustified departure from published parameters.

**EQ-T-003 — bounded parameters. Candidate — not implemented.**

$$\theta_{min}\le\theta\le\theta_{max}.$$

Bounds must be chemically justified and declared before looking at the final
held-out studies.

**EQ-T-004 — nested whole-study selection. Candidate — not implemented.**

$$
Score(\lambda)=\frac1S\sum_s
L_s\left[\widehat\theta_{(-s)}(\lambda)\right].
$$

An outer study remains untouched for final evaluation; inner held-out studies
choose regularization or the small set of tunable parameters. Randomly mixing
rows from the same paper across train and test is prohibited.

**EQ-T-005 — optional phase deviation with shrinkage. Candidate — not
implemented.**

$$\log\alpha_{r,p}=\log\alpha_{r,global}+\delta_{r,p}.$$

This would require enough independent studies in each phase. Otherwise it is
not identifiable and must not be used.

## G. Impurity-layer equations under consideration

Everything in this section is **Candidate — not implemented as a universal
model**.

**EQ-P-001 — clean baseline plus impurity retention. Candidate architecture.**

$$
M_{impure}(x,C,t,z)=M_{clean}(x)R_{imp}(C,t,z).
$$

$x$ contains clean operating conditions; $z$ contains catalyst-matched and
protocol variables such as exposure mode, cumulative history, and recovery.
This factorization is meaningful only when $M_{clean}$ and $R_{imp}$ describe
the same catalyst family and compatible output metric.

**EQ-P-002 — candidate concentration/temperature deactivation law. Not
implemented.**

$$
k_d(C,T)=k_{d,0}\exp\left(-\frac{E_d}{RT}\right)C^n,\qquad
R_{imp}=\exp[-k_d(C,T)t].
$$

This is a hypothesis to test only if catalyst-matched multi-point data support
identifying $k_{d,0}$, $E_d$, and $n$. It is not inferred from the mere presence
of EQ-S-003 or EQ-S-007.

**EQ-P-003 — reversible and irreversible components. Candidate — symbolic
only.**

$$R_{imp}(t)=R_{rev}(t)R_{irrev}(t).$$

The components require exposure/recovery experiments capable of separating
them; without those data the decomposition is not identifiable.

**EQ-P-004 — observed recovery fraction. Candidate data metric.**

$$
Recovery=\frac{M_{post-clean}-M_{impure}}
{M_{pre-clean}-M_{impure}}.
$$

It is valid only when pre-exposure clean, impurity-exposed, and post-removal
measurements share a consistent output basis.

## Required modeling sequence

1. Select one catalyst--impurity pairing and define comparable output metrics.
2. Audit units, catalyst state, feed composition, and experimental protocol.
3. Lock and test the clean-catalyst baseline without tuning.
4. Diagnose residuals by whole study and determine whether calibration is
   scientifically warranted.
5. If warranted, tune only a small declared parameter set using nested
   whole-study validation and retain a final untouched study set.
6. Build the impurity retention layer from catalyst-matched paired data.
7. Combine the layers using EQ-P-001 and test impure methanol output against
   entire held-out studies.
8. Report uncertainty, failure domains, and unmatched evidence explicitly.

## Current scientific boundary

The Ghosh model is a clean unsupported-In2O3 proof of concept. It is useful for
learning whether a published mechanistic baseline transfers across clean
unsupported-In2O3 studies. It cannot be tuned into an H2S model using
In2O3/ZrO2 or Cu/ZnO/Al2O3 poisoning data without changing the catalyst being
modeled. Therefore, catalyst work has not replaced the impurity question; it
has exposed the need to select a catalyst-matched impurity branch before the
next tuning stage.
