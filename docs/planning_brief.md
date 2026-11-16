# Planning brief – mIAx Taller Renta Fija

- **Analysis date:** 2026-10-01
- **Deadline and in-class presentation:** Thu 26-Nov-2026
- **Team:** 3 people
- **Grading:** up to 1 point per section (9 sections) + up to 1 point for the presentation

Every number below comes from profiling the files in `Taller_RF_MIAX15/data/` and reading `Taller_RF_MIAX15/src/analisis_cartera.ipynb`.
This folder (`planning/`) sits **outside** the delivery folder on purpose. Do not include it in the zip.

Companion deck: `planning_brief.pptx`.

---

## 1. Data profile

### `universo.csv`

| Fact / pitfall | Count / value |
|---|---|
| Format: separator `;`, UTF-8 with BOM (`encoding="utf-8-sig"`), dates `dd/mm/yyyy`, decimal `.` | 2165 rows × 21 cols |
| ISIN unique; every bond is EUR | 2165 / 2165 |
| Missing values | `Maturity` 18, `Rating` 3, `PD 1YR` 23, `Next Call Date` 583, `Penultimate Coupon Date` 18 |
| `Callable` Y / N (call date consistent with flag) | 1582 / 583 (0 mismatches) |
| **Call date already passed (≤ 2026-10-01)** | **11**: 10 with future maturity + 1 perpetual (`FR0014005EJ6`, call 16/09/2026). No bond has maturity ≤ analysis date |
| Perpetuals (no `Maturity`) | 18, all `VARIABLE`; 17 Jr Subordinated + 1 Subordinated |
| `Coupon Type` FIXED / VARIABLE | 1835 / 330. All VARIABLE bonds are callable; 309 are Financial |
| `Coupon Frequency` 1 / 2 | 2156 / 9. The 9 semi-annual bonds are all FIXED |
| Zero-coupon bonds | 14 |
| Par-call pattern (call within 95 days of maturity) | 1201 of 1564 callables with a maturity (median gap 92 days) |
| Call date not on the coupon schedule (final stub period) | 1328 |
| Optional calls (call more than 1 y before maturity) | 193; 35 priced < 95, 18 priced < 90 (yield-to-call overstated) |
| `Penultimate Coupon Date` day/month ≠ `First Coupon Date` day/month | 182 (cause unknown – verify in `universo.csv`) |
| First coupon period ≠ 1 y (annual bonds) | 468. Harmless: every first coupon is ≤ 2025-02-01 |
| Ratings | BBB+ 415, **NR 372**, A- 363, BBB 300, A 222, A+ 180, BBB- 176, AA- 96, AA 20, **BB+ 8**, AA+ 6, AAA 4, **NaN 3**. Nothing below BB+ |
| NR bonds whose issuer has other rated bonds | 35 of 372 |
| `PD 1YR` is not monotone in rating | AA+ median 5.7e-3 > BBB- 1.1e-3 |
| `Seniority` | Sr Unsecured 1614, **Sr Non Preferred 182**, Sr Preferred 165, Subordinated 147, Jr Subordinated 24, Secured 20, 1st lien 13 |
| Sector concentration | Financial 969 (45 %); 605 issuers; top issuer BANQUE FED CRED MUTUEL with 32 bonds |
| Same group under several issuer names | VOLKSWAGEN ×4 entities, E.ON ×2, TELEFONICA ×2 |
| `Outstanding Amount` ≤ 500 M | 767, of which **641 exactly 500 M** (excluded by "igual o inferior") |
| `Price` = (Bid + Ask) / 2 | all 2165; also equals the historical price on 01/10/2026 for all 2165 |
| Bid-ask (price points) | mean 0.235, median 0.202, max 1.538 |
| Duplicate `Description` with different ISIN | 2 pairs (VW 3 ⅞ PERP, ORAFP 1 ¾ PERP), genuine distinct bonds |
| Mandate pre-filter (alive, > 500 M, not Sub / Jr Sub) | 1298 bonds, 388 issuers; 1160 if SNP is also excluded; includes 140 NR and 4 BB+; 708 have effective maturity ≤ 3 y |

### `precios_historicos_universo.csv`

| Fact / pitfall | Count / value |
|---|---|
| **Wide** layout: rows `"<ISIN> Corp"`, columns are calendar days 01/10/2023 → 01/10/2026, NA token `#N/D` | 2165 × 1097 |
| ISIN match with the universe after stripping `" Corp"` | 100 % both ways |
| Weekend columns (all NaN) | 313 |
| Holiday weekdays with > 50 % of bonds NaN | 10 |
| Dates with > 50 % stale (repeated) prices | 5 (2025-12-25/26, 2026-01-01, 2026-04-03/06) |
| Weekday NaN inside each bond's quoting window | median 10, max 41 |
| Longest identical-price run | 18 days (`XS2265360359`) |
| **Outlier** | `DE000A180B80` = 240.27 on 2024-12-24 (bond median 91.68) |
| Daily moves > 10 % | 65 across 31 bonds; 33 reverse by > 8 % within 5 days (spikes); clustered on 2026-05-25/26 |
| Prices before `Issue date` (grey market) | 85 bonds (median 5 days early, max 9) |
| Issued after 2023-10-01 (late start) | 78 |
| Survivorship bias | every bond is alive at 01/10/2026 and none stops quoting early |
| Month-ends | 37 points → 36 periods; 11 calendar month-ends fall on weekends; 2023-12-31 has 0 prices |
| Prices < 50 are genuine (long, low-coupon bonds) | 8 bonds |

### `curvaESTR.csv`

| Fact / pitfall | Count / value |
|---|---|
| Columns `Date;Market Rate;Zero Rate;Discount`; row 1 = 01/10/2026, DF = 1, rates NaN | 33 rows; last pillar 05/10/2076 (50.05 y) |
| `Zero Rate` = −ln(DF)/t, continuous compounding, ACT/365 | verified to 5 dp |
| Bonds with effective maturity before the first pillar (12/10/2026) | 2 → interpolate from t = 0 |
| Effective maturity beyond the curve | 0 (max 34.47 y) |

### `precios_historicos_varios.csv`

| Fact / pitfall | Count / value |
|---|---|
| Business days only | 774 rows, 02/10/2023 → 01/10/2026 |
| NaN | iTraxx Main / XOVER 15 each, DU1 / OE1 / RX1 12 each, RECMTREU 0 |
| Bond trading days missing from `varios` | 10 |
| Levels on 01/10/2026 | Main 65.728, XOVER 314.398, DU1 104.925, OE1 112.52, RX1 120.35, RECMTREU 168.2581 |
| RECMTREU total return over the file | +12.90 % |

### Notebook

- Two date variables with different types: `fecha_analisis` (`pd.Timestamp`) and `fecha_valor` (`datetime.datetime`).
- A column name must be copied with its typo intact: **`DiferenciaMecadoCalculo`**.

---

## 2. Section-by-section summary

Effort scale: S = 1, M = 2, L = 3.

| # | Section | Effort | Output CSV (column names verbatim) | Depends on |
|---|---|---|---|---|
| 1 | Datos | M | `control_calidad_universo.csv`, `control_calidad_precios.csv` (column names not specified) | all CSVs |
| 2 | Valoración | **L** | `valoracion.csv`: `ISIN, PrecioMercado, PrecioSucioCalculado, CuponCorrido, PrecioLimpioCalculado, DiferenciaMecadoCalculo, DiferenciaPct` | S1, curve |
| 3 | Spread | S | `spread.csv`: `ISIN, Spread, PrecioSpreadCero, PrecioSpreadCalculado` | S2 |
| 4 | Yield / Dur / Conv | M | `sensibilidad.csv`: `ISIN, Yield, Dur, ModDur, Convexidad, VarPrecioDurConv` | S2 |
| 5 | Cartera equiponderada | M | `backtest_equal_weight.csv`: `Fecha Mes, Rent cartera, Rent benchmark, Dif` | S1, S2 (accrued), varios |
| 6 | Cartera mandato | **L** | `cartera_optima.csv`: `ISIN, Peso, Yield, Duration, Rating, Issuer, Outstanding Amount, Seniority, Industry Sector` + row `CARTERA` | S1, S4 |
| 7 | Cobertura tipos | S | none | S6, varios |
| 8 | Cobertura crédito | S | none | S6, S3/S4, varios |
| 9 | Stress Test | M | `stress_test.csv`: `Escenario, ValorCartera, P&L` | S2, S3, S6 |

### S1 – Datos (M)

- **Goal:** profile, clean and document the universe and the price history.
- **Compute:**
  - Value counts and cross-tabs: currency, coupon type, frequency, seniority, callable, perpetual, sector, issuer share, rating, PD, bid-ask, outstanding.
  - Price grid on business days.
  - The two QC tables.
- **Questions to answer in markdown:**
  - Currencies.
  - Fixed or floating; ranking; optionality; perpetuals.
  - Sectors and issuers. Is an all-bonds portfolio diversified? No: 45 % is Financial.
  - Ratings.
  - Liquidity: bid-ask and outstanding.
  - Gaps.
  - At least 2 quality problems, each with *problema / tratamiento / nº bonos afectados / consecuencia*.
  - Conclusions.
- **Pitfalls:** BOM; `#N/D`; the `" Corp"` suffix; 313 weekend columns; 11 passed calls; the 240.27 outlier; 85 pre-issue prices; 182 schedule mismatches.

### S2 – Valoración (L, root of the critical path)

- **Effective maturity:** T* = call date if callable, otherwise maturity. For perpetuals, T* = next call.
- **Schedule:** roll backward from the real maturity on the coupon anniversary, then truncate at T*.
- **Cash flows:** C/freq per period, plus 100 at T*. Time t = days/365.
- **Discount factor interpolation:** `DF(t) = DF1^((t2−t)/(t2−t1)) · DF2^((t−t1)/(t2−t1))`
- **Prices:**
  - `Dirty = Σ CF_i · DF(t_i) · e^(−s·t_i)`
  - `AI = C · (fecha − prev_coupon)/365`
  - `Clean = Dirty − AI`
- **Questions:**
  - Market vs calculated prices at s = 0. The calculated price should be above the market price for almost every bond.
  - Is the difference credit only?
  - Other factors: liquidity, ranking, optionality, technicals, the ESTR basis, the callable assumption.
- **Pitfalls:** 11 passed calls; 1328 off-schedule calls (stub period); 9 semi-annual bonds; 14 zero-coupon bonds; 2 bonds that mature before the first pillar; 161 first coupons on day ≥ 29.

### S3 – Spread (S)

- **Method:** `brentq` on `Dirty(s) − (P_mkt + AI) = 0`. Check that the residual is below 1e-6.
- **Questions:**
  - Are the results coherent?
  - Compare with: Rating, `PD 1YR`, bid-ask, outstanding, iTraxx Main 65.7 bp and XOVER 314.4 bp, sector and seniority averages.
- **Pitfalls:** 35 optional callables trade below 95, so their spreads come out inflated. Fix the unit (bp or decimal) and document it.

### S4 – Yield, Duración, Convexidad (M)

- **Yield:** solve `P_dirty = Σ CF_i (1+y)^(−t_i)` (annual compounding, ACT/365).
- **Risk measures:**
  - `Dur = Σ t_i·PV_i / P`
  - `ModDur = Dur/(1+y)`
  - `Conv = Σ t_i(t_i+1)·CF_i·(1+y)^(−t_i−2) / P`
- **Price change estimate:** `VarPrecioDurConv = −ModDur·Δy + ½·Conv·Δy²` with Δy = −0.01.
- **Questions:**
  - Yield vs spread: y ≈ zero(≈ Dur) + s.
  - Duration vs maturity.
  - What duration reflects.
  - Other ways to measure the sensitivity: effective duration, key-rate durations, spread duration.
  - Estimate the price change for a −1 % move.
- **Pitfalls:** "caída de un 1 %" is ambiguous. For zero-coupon bonds Dur = T*, which makes a good unit test.

### S5 – Cartera equiponderada (M)

- **Rebalance dates:** last bond trading day of each month (37 points, 36 periods).
- **Bond return:** `r_i = (P_t + AI_t + coupons paid) / (P_{t−1} + AI_{t−1}) − 1`.
- **Portfolio return:** the mean of r_i over bonds alive at t−1.
- **Benchmark:** RECMTREU on the same dates. `Dif = Rent cartera − Rent benchmark`.
- **Questions:**
  - Better than MID: buy at ask and sell at bid, or model transaction costs.
  - Alternative benchmarks: an IG corporate index matched to the universe's duration, such as 1–5 y Euro corporate or Euro-Agg Corporate (tickers: verify).
- **Pitfalls:** 2023-12-31 is empty; 11 month-ends fall on weekends; 78 late issues; 85 pre-issue prices; survivorship bias; price spikes.

### S6 – Cartera mandato (L, heaviest section)

- **Model:** MILP.
  - Variables: weights w_i ∈ [0, 0.10] and binaries z_i.
  - `w_i ≤ 0.10·z_i`, `Σ z_i ≤ 20`, `Σ w_i = 1`.
  - Duration: `Σ w_i·Dur_i ≤ 3`.
  - HY: `Σ_HY w_i ≤ 0.10`.
  - Issuer: `Σ_issuer w_i ≤ 0.15`.
  - Objective: `max Σ w_i·y_i`.
  - The 10 % cap per issue forces at least 10 bonds.
- **Questions:**
  - Q2, extra restrictions: sector cap, minimum average rating, maximum bid-ask, cap on callables, group-level issuer cap.
  - Q3, credit-risk measures: weighted rating, PD·LGD, spread duration / DTS, CS01, HHI.
  - Q4, liquidity measures: bid-ask, outstanding, share of the issue held. Missing data that would help: volumes, trade prints, dealer count.
  - Q5, backtest design: monthly, point-in-time data, constraints applied at each date, costs from the bid-ask, total return.
- **Pitfalls:** 641 bonds at exactly 500 M are excluded; 372 NR + 3 NaN ratings; 182 SNP; group issuers; 7 eligible optional callables priced below 95.

### S7 – Cobertura tipos (S)

- **Contracts:** `N = V·D_p / (D_f · F/100 · 100 000)`, sold.
- **Example:** one DU1 contract carries 1.92 × 104 925 = 201 456 € of duration, so 100 DU1 ≈ 20.1 M duration-€, against at most 30 M for the portfolio.
- **Questions:**
  - Reason for the chosen instrument and number of contracts.
  - What happens with 100 futures (with RX1, 100 contracts ≈ 120 M duration-€).
  - Alternatives: IRS/OIS, swaptions, Bund options, short govies, ESTR futures.

### S8 – Cobertura crédito (S)

- **Index sensitivity:** 4 500 €/bp per 10 M implies an index spread duration of about 4.5.
- **Portfolio CS01:** about 1 000·D €/bp per 10 M. Full-hedge notional = 10 M·D_s/4.5. A partial hedge applies a β. Position: buy protection.
- **Questions:**
  - Does a full hedge make sense? No: it gives away the carry and the basis remains.
  - Other instruments: single-name CDS, CDS options, TRS, short bonds, credit ETFs.
  - At least 3 residual risks: index basis, jump-to-default, maturity mismatch (5 y vs ≤ 3 y), roll, counterparty, liquidity, residual rate risk.

### S9 – Stress Test (M)

- **Method:** full revaluation `P(curve + Δr, s* + Δs)` for each holding on 100 M. Scenarios: Base, A (+100 bp rates), B (credit), C (A + B). `P&L = V_scen − V_base`.
- **Pitfalls:**
  - Scenario B looks inverted. Statement text: *"Escenario B: shock de crédito: movimiento del spread de crédito (50 pbs para bonos high yield y 150 pbs para bonos investment grade)"*.
  - The notional is 100 M here but 10 M in S7 and S8.
  - The statement does not say whether hedges are included.

---

## 3. Dependency graph and critical path

```
data/*.csv ──► S1 clean universe + price grid
                 │
                 ├──► S2 pricer (curve, interp, schedule, accrued) ──► S3 z-spread ──► S9 stress
                 │        │                                                      ▲
                 │        └──► S4 yield/dur/conv ──► S6 mandate MILP ──┬──► S7 rate hedge
                 │                                                      ├──► S8 credit hedge
                 │                                                      └──────────┘ (weights)
                 └──► S5 equal-weight backtest (needs accrued() + coupon dates from S2)
```

**Critical path:** S1 → S2 → S4 → S6 → S9 → integration → "restart and run all".
S3, S5, S7 and S8 have slack.

---

## 4. Work split

### Ownership

| | P1 – Pricing core (+ integrator from Fri 20) | P2 – Data, backtest, stress | P3 – Portfolio, hedging (+ deck lead) |
|---|---|---|---|
| Sections | S2 (L), S3 (S), S4 (M) | S1 (M), S5 (M), S9 (M) | S6 (L), S7 (S), S8 (S), presentation |
| Effort points | 6 + integration 1 = 7 (front-loaded) | 6 | 5 + deck 1 = 6 |
| `funciones_aux.py` | `load_curve`, `interp_df`, `effective_maturity`, `coupon_schedule`, `accrued`, `price_bond`, `z_spread`, `ytm`, `risk_measures` | `load_universe`, `clean_universe`, `load_prices`, `clean_prices`, `qc_universe`, `qc_prices`, `month_end_dates`, `backtest_equal_weight`, `stress_test` | `eligible_mask`, `optimise_mandate`, `portfolio_stats`, `n_futures`, `cds_notional` |
| CSVs | `valoracion.csv`, `spread.csv`, `sensibilidad.csv` | `control_calidad_universo.csv`, `control_calidad_precios.csv`, `backtest_equal_weight.csv`, `stress_test.csv` | `cartera_optima.csv` |
| Markdown | S2 (3 questions), S3 (2), S4 (3) | S1 (all + ≥ 2 quality issues), S5 (2), S9 conclusions | S6 Q2–Q5, S7, S8 (3 questions) |

### Day-1 interface contracts

**Units**
- Rates and spreads are decimals internally; use bp only for display.
- Prices are per 100 nominal.
- Time: `t = (date − fecha).days / 365`.
- Dates are `pd.Timestamp`. Use `fecha_analisis` everywhere.

**Cleaned universe:** one row per ISIN, indexed by `ISIN`.

| Column | Type | Rule |
|---|---|---|
| original 21 columns | as is | keep the original names (needed verbatim in `cartera_optima.csv`) |
| date columns | Timestamp / NaT | parsed with `%d/%m/%Y` |
| `Coupon` | float, % | unchanged (2.5 = 2.5 %) |
| `CallableBool` | bool | `Callable == "Y"` |
| `IsPerpetual` | bool | `Maturity` is NaT |
| `EffMaturity` | Timestamp / NaT | see decision 2 |
| `EffRule` | str | `call` / `maturity` / `call_passed_maturity` / `excluded` |
| `RatingClean` | str | NaN → `NR` |
| `IsHY` | bool | see decision 1 |
| `IsSubordinated` | bool | see decision 20 |
| `BidAsk` | float | Ask − Bid |
| `Valuable` | bool | `EffMaturity > fecha` |
| `ExclReason` | str / None | audit trail |

**Prices:** a DataFrame indexed by business date (784 weekdays on the bond grid) with one column per ISIN. The cleaned version sets outliers to NaN and forward-fills up to 5 days.

**Pseudo-signatures**

```
interp_df(curve, t) -> np.ndarray
coupon_schedule(bond, fecha) -> DataFrame[date, t, cf]
accrued(bond, fecha) -> float
price_bond(bond, curve, fecha, spread=0.0, rate_shift=0.0) -> dict(dirty, accrued, clean)
z_spread(bond, curve, fecha, clean_mkt) -> float
ytm(bond, fecha, clean_mkt) -> float
risk_measures(bond, fecha, y) -> dict(dur, moddur, conv)
backtest_equal_weight(prices, universe, bench, dates) -> DataFrame
optimise_mandate(universe, max_n=20, max_dur=3, max_hy=.10, max_issue=.10, max_issuer=.15) -> DataFrame[ISIN, Peso]
n_futures(V, D_p, D_f, F_price, size=1e5) -> float
cds_notional(V, cs01_p, cs01_idx_per_10m=4500, beta=1.0) -> float
stress_test(weights, universe, curve, fecha, V=1e8, scenarios) -> DataFrame[Escenario, ValorCartera, P&L]
```

### Stub strategy

- **P2, by Mon EOD:** `clean_universe` v0 with `EffMaturity`, `IsHY` and `IsSubordinated`. The rules can change later; the schema cannot.
- **P1, Mon:** commit stubs with the final signatures:
  - `ytm` returns the current yield `Coupon/Price`.
  - `risk_measures` returns `dur` = years to EffMaturity, `moddur = dur/(1+y)` and `conv = dur²`.
  - `price_bond` uses a bullet approximation.
  - `accrued` is real from day 1.
- **P3:** builds the MILP on the stub values and switches to the real yields and durations on Thu 19.
- **P2:** builds S9 on dur/conv first, then switches to full revaluation. Runs S5 as price return first, then total return.
- **Golden fixtures** (hand-checked, asserted in a test cell):

  | ISIN | Case |
  |---|---|
  | `XS0161488498` | annual fixed bullet |
  | `XS1821883102` | semi-annual |
  | `FR0014001I50` | zero coupon (Dur = T*) |
  | `XS1206541366` | perpetual |
  | `XS1186176571` | passed call |
  | `XS1405762805` | par-call stub |

### Timeline

| Day | P1 | P2 | P3 | Team |
|---|---|---|---|---|
| Mon 16 | curve, `interp_df`, stubs | loaders, `clean_universe` v0 | eligibility filters, MILP skeleton | 1 h kickoff: sign off contracts and decisions |
| Tue 17 | `coupon_schedule`, `accrued`, `price_bond` | QC CSVs, S1 plots | MILP on stubs, S6 Q2–Q5 drafts | stand-up |
| Wed 18 | `valoracion.csv`, `z_spread`, `spread.csv` | S5 price return v1, rebalance dates | S7 and S8 formulas and markdown | fixtures pass |
| Thu 19 | `ytm`, `risk_measures`, `sensibilidad.csv` (**critical**) | S5 total return, S1 markdown | real yields into the MILP | send instructor questions |
| Fri 20 | S2–S4 markdown; **freeze the API** | S9 dur/conv version | `cartera_optima.csv` v1 | integration #1 |
| Sat 21 – Sun 22 | integrate S1–S4 into the notebook | S9 full revaluation, `stress_test.csv` | S7 and S8 numbers, deck draft | async review |
| Mon 23 | integrate S5–S9; first **restart and run all** | fixes | finalise S6–S8 | — |
| Tue 24 | review P2 | review P3 | review P1 | checklist: verbatim columns, every question answered, code commented |
| Wed 25 | final **restart and run all**, 9 CSVs present, zip named after the captain | rehearsal | rehearsal | freeze 20:00 |
| Thu 26 | submit before class | present | present | — |

### Collaboration rule for the notebook

1. **One writer.** Before Fri 20, nobody edits `analisis_cartera.ipynb`. Everyone works in private scratch notebooks outside `src/` and in `funciones_aux.py`. From Fri 20, only P1 edits the delivered notebook.
2. **Logic lives in `.py`.** Notebook cells only call `funciones_aux`, plot, and hold markdown.
3. **Markdown hand-off.** Answers are delivered as `.md` snippets keyed by cell ID (e.g. `c5562ad5` = S1 conclusions).
4. **Outputs.** Strip outputs from intermediate commits. Only the final run on Wed 25 is committed with outputs.

---

## 5. Decisions

Format per decision: **A / B** options, then the trade-off (accuracy · effort · grading risk), then **Rec**.

1. **NR / NaN ratings and the HY limit** [S1, S6, S9]
   - **A:** NR (372) + NaN (3) count as HY.
   - **B:** infer the rating from the issuer's rated bonds (35 cases), then from PD; otherwise HY.
   - Trade-off: B is more realistic, but PD is noisy · B is M effort · A cannot breach the mandate.
   - **Rec: A**, with B shown as a sensitivity.
2. **Passed calls (11)** [S2–S6, S9]
   - **A:** use `Maturity` for the 10 bonds that have one; exclude `FR0014005EJ6`.
   - **B:** exclude all 11.
   - Trade-off: A is right, since the bonds still trade · both S · A deviates from the literal assumption and must be flagged.
   - **Rec: A.**
3. **Perpetuals (18)** [S2–S4]
   - **A:** T* = next call (as in the statement).
   - **B:** optional extension: also price to later calls.
   - Trade-off: B shows extension risk · A is S · A matches the statement.
   - **Rec: A.** All 18 are excluded from S6 anyway.
4. **Variable coupons (330)** [S2–S4]
   - **A:** fixed to T*.
   - **B:** model the reset.
   - Trade-off: B is impossible because there is no margin data · B is L · A matches the statement.
   - **Rec: A.**
5. **Semi-annual coupons (9)** [S2, S4]
   - **A:** frequency-aware, C/2 per period.
   - **B:** treat as annual.
   - Trade-off: B mis-times cash flows · A is trivial · B is a visible error.
   - **Rec: A.**
6. **Coupon amount** [S2]
   - **A:** C/freq.
   - **B:** C × ACT/365 year fraction.
   - Trade-off: A is how coupons are actually paid · both S · B is defensible.
   - **Rec: A.** Use ACT/365 for t and accrued interest.
7. **Last cash flow at an off-schedule call (1328)** [S2]
   - **A:** 100 + stub accrued at T*.
   - **B:** full coupon at T*.
   - Trade-off: A is correct · both S · B overprices 1201 par calls.
   - **Rec: A.**
8. **Schedule anchor** [S2, S5]
   - **A:** roll backward from maturity (forward from the first coupon for perpetuals).
   - **B:** roll forward from the first coupon for all bonds.
   - Trade-off: the two differ only on the 182 mismatches · both S · low risk.
   - **Rec: A.**
9. **Interpolation** [S2]
   - **A:** log-linear DF (as in the statement).
   - **B:** linear in the zero rate.
   - Trade-off: similar accuracy · both S · B contradicts the statement.
   - **Rec: A.**
10. **How the spread enters the discounting** [S2, S3, S9]
    - **A:** `DF·e^(−s·t)`.
    - **B:** `(1+z+s)^(−t)`.
    - Trade-off: A is consistent with the curve's continuous zero rates · both S · low risk.
    - **Rec: A.**
11. **Accrued-interest convention** [S2, S5]
    - **A:** ACT/365.
    - **B:** ACT/ACT ICMA.
    - Trade-off: B is the market standard · both S · B contradicts the statement.
    - **Rec: A.**
12. **Market price convention and difference definitions** [S2, S3]
    - **A:** `Price` is clean. `DiferenciaMecadoCalculo` = Mkt − Clean calc. `DiferenciaPct` = that / Clean calc.
    - **B:** `Price` is dirty.
    - Trade-off: A matches Bloomberg mid · both S · B mixes clean and dirty.
    - **Rec: A.**
13. **Yield compounding** [S4]
    - **A:** annual, ACT/365.
    - **B:** continuous.
    - Trade-off: A is the EUR convention · both S · with B, ModDur = Dur.
    - **Rec: A.**
14. **"caída de un 1 %"** [S4]
    - **A:** −100 bp absolute.
    - **B:** relative (y × 0.99).
    - Trade-off: A is the standard reading · both S · B is unusual.
    - **Rec: A**, stored in %.
15. **Missing count in the QC price table** [S1]
    - **A:** count on business days.
    - **B:** count on all 1097 calendar columns.
    - Trade-off: B inflates the count by 313 weekend columns · both S · A is more informative.
    - **Rec: A**, plus a total column.
16. **Missing, stale and outlier prices** [S1, S5]
    - **A:** spike filter, then forward-fill up to 5 days.
    - **B:** drop the bond-dates.
    - Trade-off: A avoids 33 spike round-trips · A is M · A answers the quality-problem question.
    - **Rec: A.**
17. **Rebalance dates** [S5]
    - **A:** last bond trading day of the month.
    - **B:** calendar month-end with forward fill.
    - Trade-off: B hits 11 weekend month-ends and an empty 2023-12-31 · both S · low risk.
    - **Rec: A.**
18. **Total return vs price return** [S5]
    - **A:** total return.
    - **B:** price return.
    - Trade-off: B understates by about the carry (mean coupon 2.28 %/y) · A is M · the statement warns "¡OJO! El índice es *Total Return*".
    - **Rec: A.**
19. **Which bonds are "vivos"** [S5]
    - **A:** priced, on or after the issue date, and EffMaturity > t.
    - **B:** the whole universe from the start.
    - Trade-off: B includes 78 not-yet-issued bonds and 85 grey-market prices · both S · B is look-ahead.
    - **Rec: A.**
20. **Is Sr Non Preferred subordinated?** [S6]
    - **A:** exclude SNP (182 bonds; 1298 → 1160 eligible).
    - **B:** include SNP.
    - Trade-off: B is the legal reading · both S · A cannot be marked as a breach.
    - **Rec: A**, with the yield given up shown as a sensitivity.
21. **Solver** [S6]
    - **A:** MILP with `scipy.optimize.milp` (SciPy 1.15.3 installed).
    - **B:** greedy heuristic.
    - Trade-off: A is optimal · A is M · B is hard to defend.
    - **Rec: A**, with greedy as a sanity check.
22. **Objective with deep-discount callables** [S6]
    - **A:** maximise yield to T*.
    - **B:** optional extension: yield-to-worst, yield − PD·LGD, or exclude the 7 eligible optional callables priced below 95.
    - Trade-off: A can chase artificial yields · B is M · B earns improvement points.
    - **Rec: A** for the deliverable, plus B.
23. **Duration measure in the constraint** [S6]
    - **A:** Macaulay ≤ 3.
    - **B:** ModDur ≤ 3.
    - Trade-off: both are common · both S · A satisfies both readings.
    - **Rec: A.**
24. **Issuer concentration key** [S6]
    - **A:** the `Issuer` field.
    - **B:** group mapping.
    - Trade-off: B is the true exposure · B needs a manual map · A is reproducible.
    - **Rec: A**, plus a manual group check.
25. **Rate hedge future and contract formula** [S7]
    - **A:** DU1 with price-adjusted N.
    - **B:** OE1 with unadjusted N.
    - Trade-off: A matches the curve point, and the price adjustment changes N by 5–20 % · both S · show both formulas.
    - **Rec: A.**
26. **Credit hedge size** [S8]
    - **A:** full CS01 hedge on Main.
    - **B:** partial β/DTS hedge on Main.
    - Trade-off: B accounts for the basis · B is M · the statement's question points to B.
    - **Rec: B**, with A as the upper bound.
27. **Inverted Scenario B** [S9]
    - **A:** apply as written.
    - **B:** swap the shocks.
    - Trade-off: B is plausible · both S · material: on 100 M the IG leg is ≈ 4.05 M vs ≈ 1.35 M.
    - **Rec: A** in the CSV, B as a labelled sensitivity, and ask the instructor.
28. **Full revaluation vs duration/convexity** [S9]
    - **A:** full revaluation.
    - **B:** dur/conv approximation.
    - Trade-off: A captures convexity · A is cheap once S2 exists · low risk.
    - **Rec: A**, with B as a cross-check.
29. **Hedged or unhedged stress** [S9]
    - **A:** unhedged.
    - **B:** include the S7/S8 hedges.
    - Trade-off: B shows the hedge working · B is M · B is not asked for.
    - **Rec: A** in the CSV, B in markdown.
30. **QC CSV column names** [S1]
    - **A:** Spanish names that mirror the statement.
    - **B:** raw `describe()` output.
    - Trade-off: equal accuracy · both S · A maps 1:1 to the request.
    - **Rec: A.**

---

## 6. Open questions for the instructor (send Thu 19)

1. **Scenario B.** "50 pbs para bonos high yield y 150 pbs para bonos investment grade": is this intentional or inverted?
2. **HY and subordination.** Do NR (372) and missing ratings (3) count as HY? Does "deuda subordinada" include Sr Non Preferred (182)?
3. **Passed calls.** For the 11 bonds with a call ≤ 01/10/2026, is using `Maturity` acceptable, excluding the perpetual `FR0014005EJ6`?
4. **Price conventions.** Is `Price` clean? What are the sign and the denominator of `DiferenciaMecadoCalculo` and `DiferenciaPct`? Are there required column names for the QC CSVs?
5. **Stress-test scope.** Should the 100 M stress test include the S7/S8 hedges? Is "caída de un 1 %" meant as −100 bp absolute?
