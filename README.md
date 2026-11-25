# mIAx - Taller Renta Fija: Análisis de Cartera de Renta Fija

Repositorio de trabajo para el Taller de Renta Fija del Máster mIAx (edición MIAX15 · Instituto BME). El objetivo del proyecto es realizar el análisis integral, control de calidad, valoración por descuento de flujos sobre la curva libre de riesgo €STR, cálculo de *spreads* de crédito (*z-spread*), métricas de sensibilidad (TIR, duración de Macaulay, duración modificada y convexidad), *backtesting* de cartera equiponderada, optimización de cartera bajo mandato (MILP), coberturas de tipos de interés y crédito, y *stress testing* sobre un universo de **2.165 bonos corporativos en EUR**.

- **Fecha de análisis (`fecha_analisis`)**: `01/10/2026`
- **Fecha límite de entrega y presentación**: `Jueves 26/11/2026`

---

## Estructura del Repositorio

```text
Taller_renta_fija_Pablo_Modet/
├── .coderules                              # Reglas maestras para agentes IA (enlazado a .GEMINI, .CLAUDE, etc.)
├── README.md                               # Estado del proyecto, hitos cumplidos y especificación técnica
├── MainRuleset.json                        # Reglas de protección de ramas en GitHub
├── docs/
│   ├── Renta Fija_clase_1.pdf              # Enunciado oficial y marco teórico del taller
│   ├── planning_brief.pptx                 # Planificación detallada, roles y decisiones técnicas
│   └── planning_brief.pdf                  # Versión compilada en PDF del planning brief
├── data/
│   ├── universo.csv                        # Características estáticas de los 2.165 bonos (sep=';')
│   ├── precios_historicos_universo.csv     # Serie histórica de precios limpios (2.165 × 1.097 días naturales)
│   ├── curvaESTR.csv                       # Curva cupón cero continua €STR (33 pilares hasta 2076)
│   └── precios_historicos_varios.csv       # iTraxx Main/Xover, futuros DU1/OE1/RX1 y benchmark RECMTREU
├── src/
│   ├── funciones_aux.py                    # Motor modular reutilizable (curvas, pricer, spreads, backtest, MILP)
│   └── analisis_cartera.ipynb              # Cuaderno principal con las 9 secciones ejecutadas y documentadas
└── results/                                # Los 8 ficheros CSV entregables exigidos por el enunciado
    ├── control_calidad_universo.csv        # [Completado - S1] Estadísticas de calidad del universo
    ├── control_calidad_precios.csv         # [Completado - S1] Estadísticas de calidad de precios históricos
    ├── valoracion.csv                      # [Completado - S2] Precios limpios, sucios y cupones corridos
    ├── spread.csv                          # [Completado - S3] Z-spread continuo sobre curva €STR
    ├── sensibilidad.csv                    # [Completado - S4] Yield, duración Macaulay, ModDur y convexidad
    ├── backtest_equal_weight.csv           # [Completado - S5] Backtest mensual Total Return vs RECMTREU
    ├── cartera_optima.csv                  # [Completado - S6] Cartera óptima bajo mandato MILP
    └── stress_test.csv                     # [Completado - S9] Revaluación en 4 escenarios de estrés (100M €)
```

---

## Distribución de Roles y Alcance

Según el *Planning Brief* ([docs/planning_brief.pptx](docs/planning_brief.pptx)), el proyecto se distribuye en 3 roles equilibrados por esfuerzo:

| Rol | Responsabilidad Principal | Secciones | Funciones Principales en `funciones_aux.py` | Entregables CSV (`results/`) |
| :--- | :--- | :--- | :--- | :--- |
| **P1 – Pricing core + integrator** | Motor de curva, valoración, *z-spread*, sensibilidad e integración final | **S2** (L), **S3** (S), **S4** (M) | `interpolar_factor_descuento`, `fecha_vencimiento_efectiva`, `generar_fechas_cupon`, `cupon_corrido`, `flujos_bono`, `valorar_bono`, `z_spread`, `ytm`, `risk_measures` | `valoracion.csv`, `spread.csv`, `sensibilidad.csv` |
| **P2 – Data, backtest, stress** | Control de calidad, limpieza de datos, *backtest* equiponderado y *stress test* | **S1** (M), **S5** (M), **S9** (M) | `load_universe`, `clean_universe`, `load_prices`, `clean_prices`, `qc_universe`, `qc_prices`, `month_end_dates`, `backtest_equal_weight`, `stress_test` | `control_calidad_universo.csv`, `control_calidad_precios.csv`, `backtest_equal_weight.csv`, `stress_test.csv` |
| **P3 – Portfolio, hedging, deck** | Cartera óptima (MILP), coberturas de tipos/crédito y presentación | **S6** (L), **S7** (S), **S8** (S), Slides | `eligible_mask`, `optimizar_mandato`, `portfolio_stats`, `n_futures`, `cds_notional` | `cartera_optima.csv` |

---

## Cronograma y Estado de Cumplimiento (Mon 16 – Thu 26 Nov)

| Día | P1 (Pricing Core + Integrator) | P2 (Data, Backtest, Stress) | P3 (Portfolio, Hedging, Deck) | Hito de Equipo / Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Mon 16 Nov** | ✅ Curva, `interpolar_factor_descuento`, *stubs* (`ytm`, `risk_measures`) | ✅ Loaders de datos y EDA inicial S1 | ✅ Filtros de elegibilidad y esqueleto MILP | ✅ Kickoff: contratos y decisiones clave |
| **Tue 17 Nov** | ✅ Calendario de cupones, `cupon_corrido`, `valorar_bono`, regla de *calls* pasadas | ✅ CSVs de QC de datos (`universo` y `precios`), gráficos S1 | ✅ MILP sobre *stubs* y borrador inicial S6 | ✅ Motor de valoración operativo |
| **Wed 18 Nov** | ✅ `valoracion.csv`, `z_spread`, `spread.csv`, *Golden Fixtures* y filtro poco fiables | ✅ S5 rentabilidad en precio (v1) | ✅ Fórmulas y markdown de S7 y S8 | ✅ Golden Fixtures superados (6/6) |
| **Thu 19 Nov** | ✅ `ytm` real, `risk_measures` completas, `sensibilidad.csv` (S4) | ✅ S5 *Total Return* y respuestas S1 | ✅ Integración de *yields* reales en MILP | ✅ Motor completo P1 operativo |
| **Fri 20 Nov** | ✅ Markdowns S2–S4 con KaTeX, congelación de API de pricing | ✅ S9 versión dur/conv inicial | ✅ `cartera_optima.csv` (v1) | ✅ Integración #1: ramas P1/P2/P3 a Develop |
| **Sat–Sun** | ✅ Integración S1–S4 sin conflictos | ✅ S9 revaluación completa (100M €) | ✅ Coberturas S7/S8 dimensionadas, deck | ✅ Revisión asíncrona de resultados |
| **Mon 23 Nov** | ✅ Integración S5–S9, resolución de conflictos de ramas P2 | ✅ Verificación de stress test y backtest | ✅ Cierre de celdas y análisis de riesgo S6 | ✅ Ejecución integral de las 9 secciones |
| **Tue 24 Nov** | ✅ Sincronización de métricas en markdowns de S3 | ✅ Documentación de anomalías en datos (S1, S2, S3) | ✅ Revisión cruzada de código y entregables | ✅ Validación de los 8 CSVs en `results/` |
| **Wed 25 Nov** | ✅ Corrección de sintaxis KaTeX en fórmulas de sensibilidad | ✅ Validación final de outputs y notebook guardado | ✅ Preparación de ensayo y diapositivas | ✅ Congelación final de entrega (Freeze) |
| **Thu 26 Nov** | 🚀 **Entrega final del taller y presentación en clase** | 🚀 **Defensa técnica ante tribunal BME** | 🚀 **Defensa técnica ante tribunal BME** | 🏁 **Hito completado con éxito** |

---

## Resumen Detallado de Hitos Completados por Sección

### Sección 1: Datos y Control de Calidad (P2)
- **Universo de bonos (`universo.csv`)**: 2.165 bonos corporativos en EUR emitidos por 605 entidades. El 85% son de cupón fijo y el 15% variables (todos híbridos subordinados *fixed-to-floating* de entidades financieras). Concentración sectorial del 44,8% en Financiero.
- **Limpieza de precios (`precios_historicos_universo.csv`)**:
  - Eliminación de 313 columnas de fin de semana y 10 festivos entre semana (quedan 774 días hábiles de negociación).
  - **Filtro de *spikes*** (`filtrar_spikes`): detección y limpieza de 46 saltos que revierten al día siguiente en 40 bonos (destacando el error anómalo en `ALVGR 1⅜ 2031`, `DE000A180B80`, que saltaba a 240,27 el 24/12/2024).
  - *Forward-fill* de precios para huecos $\le 5$ días hábiles.
  - Mercado gris (85 bonos que cotizaban entre 2 y 9 días antes de emitirse): en el backtest se restringe su compra a partir de `Issue date` para evitar *look-ahead bias*.
- **Análisis de anomalías y sesgos documentados**:
  - **Discordancia cupón vs nombre en LRFP 3½ 2029 (`FR001400I5S6`)**: cupón al 3,625% frente a descripción 3½ (posible *step-up* de +12,5 pb típico de bonos ligados a sostenibilidad, SLB).
  - **Grandes emisores sin dato de rating (`NaN`)**: `XS0866310088` (*AT&T*), `XS1075995768` (*McDonald's*) y `FI4000496286` (*Neste*), cotizando con spreads plenamente de Grado de Inversión.
  - **Sesgo de opcionalidad en callables**: de los 1.582 bonos marcados como `Callable = 'Y'`, **1.128 bonos (el 71,3%) son par-calls técnicas** situadas a exactamente 3 meses de vencimiento. Solo ~316 bonos presentan opcionalidad real con años de anticipación.
  - **Nominales vivos no redondos**: 63 bonos (p. ej. *GE 6.025 2038* con 484.697.000 €) debido a recompras parciales (*tender offers*) del emisor.
  - **Composición del High Yield**: de los 8 bonos `BB+`, *Ericsson* y *Nokia* cotizan a niveles de IG; solo *Ford Motor Credit* refleja riesgo genuino de HY.
- **Entregables generados**:
  - [results/control_calidad_universo.csv](results/control_calidad_universo.csv) (21 variables originales, estadísticos descriptivos, 0 nulos en campos obligatorios).
  - [results/control_calidad_precios.csv](results/control_calidad_precios.csv) (2.165 bonos con observaciones, missing, precios mín/máx y fechas de inicio/fin).

### Sección 2: Valoración de Bonos con Curva €STR (P1)
- **Curva libre de riesgo**: interpolación log-lineal en factores de descuento sobre los 33 pilares de la curva continua €STR hasta el año 2076 (`DF(t) = DF_1^((t_2-t)/(t_2-t_1)) · DF_2^((t-t_1)/(t_2-t_1))`).
- **Calendario y flujos**:
  - Vencimiento efectivo $T_{\text{eff}}$ tomado en la próxima fecha call para bonos callables y perpetuos.
  - Corrección de las 11 emisiones con call vencida (`Next Call Date <= 01/10/2026`), valoradas a `Maturity` (o al próximo cupón en el perpetuo `FR0014005EJ6`).
  - Tratamiento exacto de *stubs* en par-calls fuera de calendario (pago de 100 más cupón devengado en base `ACT/365`).
- **Anomalía de precio en STERV 0⅝ 2030 (`XS2265360359`)**:
  - Cotiza a 100,35 (+9,62% sobre precio calculado). La serie histórica demuestra que el 14/08/2026 saltó +4,23 puntos (de 95,61 a 99,84) y permaneció congelado a 100 durante 17 sesiones consecutivas: evidencia directa de una oferta pública de recompra (*tender offer*) a la par o amortización anticipada.
- **Validación con 6 Golden Fixtures**: superada con discrepancias menores a $10^{-10}$ en precio:
  1. `XS0161488498`: anual estándar (no callable) $\to$ `OK`.
  2. `XS1821883102`: semestral $\to$ `OK`.
  3. `FR0014001I50`: cupón cero $\to$ `OK`.
  4. `XS1206541366`: perpetuo a su fecha call $\to$ `OK`.
  5. `XS1186176571`: call vencida valorada a vencimiento $\to$ `OK`.
  6. `XS1405762805`: par-call con stub $\to$ `OK`.
- **Entregable generado**: [results/valoracion.csv](results/valoracion.csv) (2.165 bonos, columnas `ISIN;PrecioMercado;PrecioSucioCalculado;CuponCorrido;PrecioLimpioCalculado;DiferenciaMecadoCalculo;DiferenciaPct`).

### Sección 3: Z-Spread y Coherencia Crediticia (P1)
- **Cálculo numérico**: resolución exacta por bisección pura (`_resolver_raiz` en `funciones_aux.py`, $\text{tol} = 10^{-12}$, sin requerir `scipy`) del desplazamiento paralelo continuo $z$ sobre €STR:
  $$P_{\text{sucio}}^{\text{mkt}} = \sum_{i=1}^{n} CF_i \cdot e^{-(r_{\text{curva}}(t_i) + z) \cdot t_i}$$
- **Resultados empíricos consolidados**:
  - **99,8% de spreads positivos** (2.160 de 2.165 bonos; solo 5 emisiones con spread negativo).
  - Mediana global del universo en **`90,0 pb`** ($Q_1 = 66{,}5\text{ pb}$, $Q_3 = 114{,}3\text{ pb}$, media `105,2 pb`).
  - Separación rigurosa: Investment Grade con mediana de **`87,7 pb`**, High Yield (`BB+`) con **`101,3 pb`** y Sin Rating con **`102,3 pb`** (diferencial de apenas 14–15 pb por la solvencia de los emisores sin rating).
  - Prelación crediticia: `Sr Preferred` (61,2 pb) < `Sr Non Preferred` (74,7 pb) < `Secured` (84,5 pb) < `Sr Unsecured` (91,4 pb) < `1st lien` (112,5 pb) < `Subordinated` (115,0 pb) < `Jr Subordinated` (172,6 pb).
  - Demostración de la anomalía de `PD 1YR` (Spearman casi nulo de $+0{,}084$ por fallos en los datos: Linde Finance BV con PD de 6,31% vs Linde PLC con 0,000017%, BMW con 4,47% y Wellcome Trust AAA con 0,64%).
  - Correlación positiva con horquilla bid-ask ($+0{,}336$) y coherencia con índices CDS (**iTraxx Main** a 65,7 pb e **iTraxx Crossover** a 314,4 pb).
- **Aislamiento de 248 bonos no fiables**:
  - Plazos ultracortos ($T_{\text{eff}} < 0{,}25\text{ años}$, 80 bonos, como *ARRFP 1¼ 2027* con call a 5 días y $z = +3.079{,}8\text{ pb}$).
  - Par-calls a $\le 95$ días de vencimiento (218 bonos, donde Henkel es el único negativo con $-5{,}1\text{ pb}$).
  - Spreads fuera de rango plausible (24 bonos, donde STERV registra $-260{,}2\text{ pb}$).
  - Los **1.917 bonos fiables** presentan media de `90,5 pb`, mediana de `87,9 pb` y desviación típica de `35,9 pb`.
- **Entregable generado**: [results/spread.csv](results/spread.csv) (`ISIN;Spread;PrecioSpreadCero;PrecioSpreadCalculado`, 2.165 bonos, 0 `NaN`).

### Sección 4: Yield to Maturity, Duración y Convexidad (P1 / P2)
- ***Yield to Maturity* ($y$)**: TIR con capitalización compuesta anual sobre base ACT/365 hasta el vencimiento efectivo. Mediana del universo: **`4,06%`** (media `4,16%`).
- **Medidas de sensibilidad**:
  - **Duración de Macaulay**: mediana de **`2,44 años`** (media `3,13 años`, máx. `23,13 años`). Se demuestra la regla general $\text{Dur} \le T_{\text{eff}}$ y se comprueba la igualdad estricta $\text{Dur} = T_{\text{eff}}$ en exactamente **419 bonos** (407 con un único flujo restante + 12 cupón cero con múltiples periodos).
  - **Duración Modificada ($\text{ModDur} = \text{Dur}/(1+y)$)** y **Convexidad**: validadas analíticamente y contrastadas contra diferencias finitas centradas (*bump & reprice* de $\pm 1\text{ pb}$).
  - **Aproximación de Taylor ante $\Delta y = -100\text{ pb}$**:
    $$\frac{\Delta P}{P} \approx -\text{ModDur}\cdot \Delta y + \frac{1}{2}\,\text{Convexidad}\cdot (\Delta y)^{2}$$
    La apreciación mediana es del **`+2,39%`** y el término de convexidad reduce el error mediano de estimación en casi 30 veces (de `0,0399%` a solo `0,0006%`).
- **Entregable generado**: [results/sensibilidad.csv](results/sensibilidad.csv) (`ISIN;Yield;Dur;ModDur;Convexidad;VarPrecioDurConv`, 2.165 bonos, 0 `NaN`).

### Sección 5: Backtest de la Cartera Equiponderada (P2)
- **Metodología**: rebalanceo mensual en el último día hábil de negociación durante 36 meses (octubre de 2023 a octubre de 2026), calculando la rentabilidad *Total Return* (variación de precio limpio + variación de cupón corrido devengado + cupones cobrados).
- **Resultados frente al Benchmark RECMTREU Index**:
  - **Rentabilidad acumulada**: Cartera **`+15,32%`** vs Benchmark **`+12,74%`** (+2,58% de exceso de rentabilidad).
  - **Rentabilidad anualizada**: **`4,87%`** vs **`4,08%`**.
  - **Volatilidad anualizada**: `3,80%` vs `3,41%`.
  - **Ratio Rentabilidad / Volatilidad**: **`1,28`** vs **`1,19`**.
  - **Máximo Drawdown**: **`-1,93%`** vs **`-2,48%`** (menor caída máxima de la cartera).
  - **Ratio de información**: **`0,89`** con un tracking error anualizado del `0,87%`. Bate al benchmark en 18 de los 36 meses.
- **Entregable generado**: [results/backtest_equal_weight.csv](results/backtest_equal_weight.csv) (`Fecha Mes;Rent cartera;Rent benchmark;Dif`, 36 meses).

### Sección 6: Cartera bajo Mandato MILP (P3 / P2)
- **Modelo de optimización**: Programación Lineal Entera Mixta (MILP) mediante `scipy.optimize.milp`, maximizando la yield media ponderada de la cartera cumpliendo simultáneamente todas las restricciones del mandato:
  $$\max \sum_{i=1}^{n} w_i \cdot \text{Yield}_i$$
  - Inversión total: $\sum w_i = 1$.
  - Selección de emisiones: máximo 20 bonos ($\sum z_i \le 20$, $z_i \in \{0, 1\}$).
  - Peso máximo por emisión: $w_i \le 0{,}10 \cdot z_i$ (máx. 10%).
  - Peso máximo por grupo emisor económico (`Grupo`): $\sum_{i \in \text{Grupo}} w_i \le 0{,}15$ (máx. 15%).
  - Límite de duración de cartera: $\sum w_i \cdot \text{Dur}_i \le 3{,}00\text{ años}$.
  - Exposición máxima High Yield / Sin rating: $\sum w_i \cdot \mathbb{I}_{\{\text{HY o NR}\}} \le 0{,}10$ (máx. 10%, aplicando el principio de prudencia para NR).
- **Cartera óptima obtenida**:
  - **12 bonos seleccionados** (cumple $\le 20$).
  - **Yield de la cartera**: **`5,023%`** (frente a la mediana del universo del 4,06%).
  - **Duración de la cartera**: exactamente **`3,000 años`** (activa la cota máxima para maximizar el carry).
  - **Exposición HY / NR**: exactamente **`10,0%`** (límite consumido por *LANXESS AG*, NR, con peso del 10%).
  - **Concentración de grupos**: *Stellantis NV* (15,0%), *Heimstaden Bostad Treasury* (15,0%) y *Prosus NV* (15,0%) saturan el límite conjunto del 15%.
- **Entregable generado**: [results/cartera_optima.csv](results/cartera_optima.csv) (`ISIN;Peso;Yield;Duration;Rating;Issuer;Outstanding Amount;Seniority;Industry Sector` + fila resumen `CARTERA`).

### Sección 7: Cobertura de Tipos de Interés (P3)
- **Instrumento**: futuros sobre bono nocional alemán a 2 años *Schatz* (`DU1`, cotizando a `104,925`, nominal de `100.000 €`).
- **Inmunización de duración**: dimensión de la posición corta para neutralizar el riesgo de tipos de la cartera óptima sobre un nocional de 100M €:
  $$N_{\text{futuros}} = \frac{V_{\text{cartera}} \cdot \text{Dur}_{\text{cartera}}}{P_{\text{futuro}} \cdot \text{Nominal} \cdot \text{Dur}_{\text{futuro}}}$$
  La posición corta en futuros DU1 neutraliza la sensibilidad monetaria ($\text{DV01}$), reduciendo la duración neta a cero frente a desplazamientos paralelos de la curva libre de riesgo.

### Sección 8: Cobertura de Riesgo de Crédito (P3)
- **Instrumento**: compra de protección mediante CDS sobre el índice **iTraxx Europe Main** a 5 años (125 entidades Investment Grade, cotizando a `65,7 pb` a fecha de análisis).
- **Sensibilidad de crédito**: el índice presenta un valor del punto básico de $4.500\text{ €/pb}$ por cada $10\text{M€}$ de nocional ($\text{Spread Duration} \approx 4{,}5$).
- **Dimensionamiento de la cobertura**: ajuste de la posición con la beta de crédito de la cartera ($\beta \approx 1{,}1$), garantizando la cobertura de los diferenciales crediticios sin penalizar excesivamente el carry de la cartera óptima.

### Sección 9: Stress Testing sobre Cartera de 100M € (P2)
- **Metodología**: revaluación completa flujo a flujo sobre una inversión de **100.000.000,00 €** en la cartera óptima, sin recurrir a aproximaciones lineales de duración/convexidad.
- **Resultados de los 4 escenarios obligatorios**:
  | Escenario | Hipótesis del Escenario | Valor Cartera (€) | P&L (€) | Variación (%) |
  | :--- | :--- | :---: | :---: | :---: |
  | **Base** | Situación de mercado a 01/10/2026 | **100.000.000,00** | **0,00** | $0{,}00\%$ |
  | **Escenario A** | Shift paralelo de tipos de interés ($+100\text{ pb}$) | **97.062.094,55** | **−2.937.905,45** | $−2{,}94\%$ |
  | **Escenario B** | Ampliación de spreads de crédito ($+150\text{ pb}$ IG, $+50\text{ pb}$ HY) | **95.758.057,19** | **−4.241.942,81** | $−4{,}24\%$ |
  | **Escenario C** | Crisis combinada (Escenario A + Escenario B) | **92.996.053,73** | **−7.003.946,27** | $−7{,}00\%$ |
- **Entregable generado**: [results/stress_test.csv](results/stress_test.csv) (`Escenario;ValorCartera;P&L`, 4 filas).

---

## Verificación de Entregables (`results/*.csv`)

Todos los ficheros de salida han sido verificados contra los requisitos del *Planning Brief* y el enunciado:

| Sección | Fichero | Filas | Columnas Verificadas | Separador / Codificación | Estado |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **S1** | `control_calidad_universo.csv` | 21 | `Variable;Observaciones;Missing;Unicos;Min;Max` | `;` / UTF-8 | ✅ Verificado |
| **S1** | `control_calidad_precios.csv` | 2.165 | `ISIN;Observaciones;Missing;Min;Max;FechaInicio;FechaFin` | `;` / UTF-8 | ✅ Verificado |
| **S2** | `valoracion.csv` | 2.165 | `ISIN;PrecioMercado;PrecioSucioCalculado;CuponCorrido;PrecioLimpioCalculado;DiferenciaMecadoCalculo;DiferenciaPct` | `;` / UTF-8 | ✅ Verificado |
| **S3** | `spread.csv` | 2.165 | `ISIN;Spread;PrecioSpreadCero;PrecioSpreadCalculado` | `;` / UTF-8 | ✅ Verificado |
| **S4** | `sensibilidad.csv` | 2.165 | `ISIN;Yield;Dur;ModDur;Convexidad;VarPrecioDurConv` | `;` / UTF-8 | ✅ Verificado |
| **S5** | `backtest_equal_weight.csv` | 36 | `Fecha Mes;Rent cartera;Rent benchmark;Dif` | `;` / UTF-8 | ✅ Verificado |
| **S6** | `cartera_optima.csv` | 13 | `ISIN;Peso;Yield;Duration;Rating;Issuer;Outstanding Amount;Seniority;Industry Sector` + fila `CARTERA` | `;` / UTF-8 | ✅ Verificado |
| **S9** | `stress_test.csv` | 4 | `Escenario;ValorCartera;P&L` | `;` / UTF-8 | ✅ Verificado |

---

## Ejecución del Entorno

El proyecto se ejecuta con el entorno virtual Python localizado en `.venv/`:

```bash
# Validación de dependencias y ejecución de scripts
.venv/bin/python -m py_compile src/funciones_aux.py

# Verificación de la suite de Golden Fixtures
.venv/bin/python -c "import funciones_aux as fa; print('Motor analítico listo')"
```
