# mIAx - Taller Renta Fija: Análisis de Cartera de Renta Fija

Repositorio de trabajo para el Taller de Renta Fija del Máster mIAx (edición MIAX15). El objetivo del proyecto es realizar el control de calidad, valoración por descuento de flujos sobre la curva €STR, análisis de *spreads* de crédito, métricas de sensibilidad (TIR, duración y convexidad), *backtesting* equiponderado, optimización de cartera bajo mandato (MILP), cobertura de tipos y crédito, y *stress testing* sobre un universo de **2.165 bonos corporativos en EUR**.

- **Fecha de análisis (`fecha_analisis`)**: `01/10/2026`
- **Fecha límite de entrega y presentación**: `Jueves 26/11/2026`

---

## Estructura del Proyecto

```text
Taller_renta_fija_Pablo_Modet/
├── .coderules                              # Reglas para agentes IA (enlazado a .GEMINI, .CLAUDE, GEMINI.md, CLAUDE.md)
├── README.md
├── docs/
│   ├── Renta Fija_clase_1.pdf              # Enunciado y marco teórico del taller
│   └── planning_brief.pptx                 # Planificación detallada, roles y decisiones técnicas
├── data/
│   ├── universo.csv                        # Características estáticas de los 2.165 bonos
│   ├── precios_historicos_universo.csv     # Serie histórica de precios limpios (2.165 × 1.097 días)
│   ├── curvaESTR.csv                       # Curva libre de riesgo €STR (33 pilares hasta 2076)
│   └── precios_historicos_varios.csv       # iTraxx Main/Xover, futuros DU1/OE1/RX1 y benchmark RECMTREU
├── src/
│   ├── funciones_aux.py                    # Motor de valoración, curvas, spreads y funciones auxiliares
│   └── analisis_cartera.ipynb              # Cuaderno principal con las 9 secciones del análisis
└── results/                                # Ficheros CSV de salida exigidos por el enunciado
    ├── valoracion.csv                      # [Completado - P1] Sección 2
    ├── spread.csv                          # [Completado - P1] Sección 3
    └── sensibilidad.csv                    # [Completado - P1] Sección 4
```

---

## Distribución de Roles y Alcance

Según el *Planning Brief* ([docs/planning_brief.pptx](docs/planning_brief.pptx)), el trabajo se divide en 3 roles balanceados por carga de esfuerzo:

| Rol | Responsabilidad Principal | Secciones | Funciones en `funciones_aux.py` | Entregables CSV (`results/`) |
| :--- | :--- | :--- | :--- | :--- |
| **P1 – Pricing core + integrator** | Motor de curva, valoración, *z-spread*, sensibilidad e integración final del notebook | **S2** (L), **S3** (S), **S4** (M) | `interpolar_factor_descuento`, `fecha_vencimiento_efectiva`, `generar_fechas_cupon`, `cupon_corrido`, `flujos_bono`, `valorar_bono`, `z_spread`, `ytm`, `risk_measures` | `valoracion.csv`, `spread.csv`, `sensibilidad.csv` |
| **P2 – Data, backtest, stress** | Control de calidad de datos, *backtest* equiponderado y *stress test* | **S1** (M), **S5** (M), **S9** (M) | `load_universe`, `clean_universe`, `load_prices`, `clean_prices`, `qc_universe`, `qc_prices`, `month_end_dates`, `backtest_equal_weight`, `stress_test` | `control_calidad_universo.csv`, `control_calidad_precios.csv`, `backtest_equal_weight.csv`, `stress_test.csv` |
| **P3 – Portfolio, hedging, deck** | Construcción de cartera óptima (MILP), coberturas de tipos/crédito y presentación | **S6** (L), **S7** (S), **S8** (S), Slides | `eligible_mask`, `optimise_mandate`, `portfolio_stats`, `n_futures`, `cds_notional` | `cartera_optima.csv` |

---

## Cronograma y Estado Actual (Mon 16 – Thu 26 Nov)

Estado de avance respecto a la planificación original:

| Día | P1 (Pricing Core + Integrator) | P2 (Data, Backtest, Stress) | P3 (Portfolio, Hedging, Deck) | Hito de Equipo / Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Mon 16 Nov** | ✅ Curva, `interpolar_factor_descuento`, *stubs* (`ytm`, `risk_measures`) | 🔄 Loaders y EDA inicial en S1 (`analisis_cartera.ipynb`) | ⏳ Filtros de elegibilidad y esqueleto MILP | ✅ Kickoff: contratos de interfaz y decisiones |
| **Tue 17 Nov** | ✅ Calendario de cupones, `cupon_corrido`, `valorar_bono`, regla de *calls* pasadas | ⏳ Generación de CSVs de QC y gráficos S1 | ⏳ MILP sobre *stubs* y borrador S6 | ✅ Motor de valoración operativo |
| **Wed 18 Nov** | ✅ `valoracion.csv`, `z_spread`, `spread.csv`, *Golden Fixtures* y filtro `ZSpread_PocoFiable` | ⏳ S5 rentabilidad en precio (v1) | ⏳ Fórmulas y markdown de S7 y S8 | ✅ Golden Fixtures superados |
| **Thu 19 Nov** | ✅ `ytm` real, `risk_measures` completas, `sensibilidad.csv` (S4) | ⏳ S5 *Total Return* y respuestas S1 | ⏳ Integrar *yields* reales en MILP | ✅ Motor completo P1 operativo |
| **Fri 20 Nov** | ✅ Respuestas markdown S2–S4; congelación de API de `funciones_aux.py` | ⏳ S9 versión Duración/Convexidad | ⏳ `cartera_optima.csv` (v1) | ✅ **Bloque P1 (S2–S4) 100% completado** |
| **Sat 21 – Sun 22** | ⏳ Integrar S1–S4 en notebook único | ⏳ S9 revaluación completa (*full reval*) | ⏳ Números definitivos S7/S8 y presentación | ⏳ Revisión asíncrona |
| **Mon 23 Nov** | ⏳ Integrar S5–S9; *Restart & Run All* | ⏳ Ajustes y correcciones | ⏳ Finalizar S6–S8 | — |
| **Tue 24 Nov** | ⏳ Revisar bloque P2 | ⏳ Revisar bloque P3 | ⏳ Revisar bloque P1 | ⏳ Revisión cruzada de *checklist* |
| **Wed 25 Nov** | ⏳ Ejecución final limpia y empaquetado `.zip` | ⏳ Ensayo de presentación | ⏳ Ensayo de presentación | ⏳ *Code Freeze* (20:00) |
| **Thu 26 Nov** | ⏳ Entrega final | ⏳ Presentación en clase | ⏳ Presentación en clase | ⏳ **Entrega y defensa** |

*(Leyenda: ✅ Completado · 🔄 En progreso · ⏳ Pendiente)*

---

## Detalle del Trabajo Realizado Hasta Ahora

### 1. Exploración Preliminar de Datos (Sección 1 – En progreso)
En [analisis_cartera.ipynb](src/analisis_cartera.ipynb) se ha implementado la carga y el análisis exploratorio visual del universo (`universo.csv`):
- Inspección de divisas (100% EUR), tipos de cupón (`FIXED` vs `VARIABLE`), prelación (`Seniority`), opcionalidad (`Callable`) e identificación de los 18 bonos perpetuos.
- Análisis de concentración sectorial (45% sector financiero) y por emisor, distribución de *ratings* crediticios, riesgo de liquidez (horquilla *bid-ask* vs nominal vivo) y detección de valores *missing*.

### 2. Motor de Valoración y Vencimiento Efectivo (P1 – Mon 16 & Tue 17)
Implementado en [funciones_aux.py](src/funciones_aux.py) y ejecutado en la **Sección 2** de [analisis_cartera.ipynb](src/analisis_cartera.ipynb):
- **Interpolación de la curva €STR (`interpolar_factor_descuento`)**: interpolación exponencial (log-lineal) de factores de descuento con base `ACT/365` y extrapolación plana en tipo continuo en los extremos.
- **Vencimiento efectivo y tratamiento de *calls* pasadas (`fecha_vencimiento_efectiva`)**:
  - Bonos *callable* con `Next Call Date > 01/10/2026` (1.572 bonos, incluyendo 17 perpetuos): se valoran a su próxima fecha de *call*.
  - **Corrección de los 11 bonos con *call* vencida (`Next Call Date <= 01/10/2026`)**: dado que la fecha de *call* ya ha pasado y el bono sigue vivo, se toma `Maturity` como vencimiento efectivo para los 10 bonos con vencimiento fijo (evitando *z-spreads* artificialmente inflados), y la fecha del próximo cupón para el único perpetuo afectado (`FR0014005EJ6`).
- **Generación de flujos y valoración (`generar_fechas_cupon`, `cupon_corrido`, `flujos_bono`, `valorar_bono`)**:
  - Reconstrucción hacia atrás desde el último cupón ordinario (`Penultimate Coupon Date` o `Maturity`), respetando frecuencias anuales (1), semestrales (2) y cupón cero.
  - Tratamiento exacto de *calls* fuera del calendario de cupón (1.328 bonos, de los cuales 1.201 son *par-calls* $\le 95$ días antes de vencimiento): en la fecha de *call* se abona el principal (100) más el cupón devengado (*stub* en base `ACT/365`) en lugar de un cupón completo.
- **Validación con 6 *Golden Fixtures***: celda de control que verifica el comportamiento exacto sobre `XS0161488498` (anual estándar), `XS1821883102` (semestral), `FR0014001I50` (cupón cero), `XS1206541366` (perpetuo), `XS1186176571` (*call* pasada valorada a vencimiento con *z-spread* de `80,6 pb`) y `XS1405762805` (*par-call* con *stub*).
- **Entregable generado**: [results/valoracion.csv](results/valoracion.csv) (`ISIN;PrecioSucio;CuponCorrido;PrecioLimpio`, 2.165 bonos, 0 `NaN`).

### 3. Cálculo de *Z-Spread* y Filtrado de Fiabilidad (P1 – Wed 18)
Implementado en [funciones_aux.py](src/funciones_aux.py) y analizado en la **Sección 3** de [analisis_cartera.ipynb](src/analisis_cartera.ipynb):
- **Solver numérico (`_resolver_raiz` y `z_spread`)**: bisección pura (`tol=1e-12`, sin dependencia de `scipy`) que resuelve el desplazamiento paralelo $z$ con capitalización continua ($\text{FD}_i(z) = \text{FD}_i \cdot e^{-z \cdot t_i}$) para igualar el precio sucio teórico al precio sucio de mercado ($\text{Precio Limpio} + \text{Cupón Corrido}$). Pre-calcula flujos y factores de descuento fuera del bucle (~2 segundos para los 2.165 bonos).
- **Análisis de coherencia crediticia**:
  - Escalonamiento monotónico por calidad crediticia (IG vs HY/NR) y por nivel de prelación (`Sr Preferred` < `Sr Non Preferred` < `Subordinated` < `Jr Subordinated`).
  - Correlación positiva de rangos (Spearman) frente a `PD 1YR` y `Horquilla` *bid-ask*, y comparación con los niveles de **iTraxx Main** (`~55 pb`) e **iTraxx Xover** (`~310 pb`) a `01/10/2026`.
- **Etiquetado de *z-spreads* poco fiables (`universo['ZSpread_PocoFiable']`)**:
  - Se identifican y marcan **248 bonos (11,5% del universo)** donde el supuesto simplificador de valorar siempre a la fecha de *call* distorsiona el *spread* implícito:
    1. Plazo efectivo ultra-corto (`Plazo_efectivo < 0.25` años: 80 bonos), donde diferencias mínimas de precio o *bid-ask* amplifican exponencialmente el *spread*.
    2. Bonos con *par-call* próxima a vencimiento (`<= 95` días antes de `Maturity` y plazo `< 1` año: 218 bonos) que cotizan por encima de la par y el mercado valora a `Maturity` en lugar de a la fecha de *call*.
    3. Valores extremos residuales (`Spread_pb < 0` o `Spread_pb > 500`: 24 bonos).
  - En los **1.917 bonos fiables** (`~universo['ZSpread_PocoFiable']`), el *z-spread* presenta una distribución limpia con media `90,5 pb`, mediana `87,9 pb`, desviación típica `35,9 pb` y rango `[4,2, 320,5] pb`.
- **Entregable generado**: [results/spread.csv](results/spread.csv) (`ISIN;Spread` en tanto por uno, 2.165 bonos, 0 `NaN`).

### 4. Cálculo de *Yield*, Duración, Convexidad y Respuestas Markdown S2–S4 (P1 – Thu 19 & Fri 20)
Implementado en [funciones_aux.py](src/funciones_aux.py) y analizado en la **Sección 4** de [analisis_cartera.ipynb](src/analisis_cartera.ipynb):
- ***Yield* anual (`ytm`)**: resolución exacta por bisección de la TIR con capitalización compuesta anual y base `ACT/365` ($\sum_{i=1}^n \frac{\text{CF}_i}{(1+y)^{t_i}} = P_{\text{sucio, mkt}}$) hasta la fecha de vencimiento efectiva $T^*$. Media del universo: **`4,16%`** ($0{,}0416$), mediana **`4,06%`** ($0{,}0406$).
- **Medidas de sensibilidad (`risk_measures`)**:
  - **Duración de Macaulay ($\text{Dur} = \sum_{i=1}^n w_i \cdot t_i$)**: vida media financiera ponderada por el valor actual de cada flujo ($w_i = \frac{\text{PV}_i}{P_{\text{sucio}}}$, con media $3{,}13\text{ años}$, mediana $2{,}44\text{ años}$, máx. $23{,}13\text{ años}$). Se verifica que $\text{Dur} = T^*$ exactamente en los 14 bonos cupón cero y en los 407 bonos con un único flujo restante, y $\text{Dur} < T^*$ en los 1.746 bonos restantes.
  - **Duración Modificada ($\text{ModDur} = -\frac{1}{P}\frac{dP}{dy} = \frac{\text{Dur}}{1 + y}$)** y **Convexidad ($\text{Convexidad} = \frac{1}{P}\frac{d^2 P}{dy^2} = \frac{1}{(1+y)^2}\sum_{i=1}^n w_i \cdot t_i(t_i+1)$)**: verificadas analíticamente y contrastadas frente a diferencias finitas numéricas centradas (*bump & reprice* de $\pm 1\text{ pb}$, con discrepancia $< 10^{-8}$ en duración y $< 10^{-5}$ en convexidad).
  - **Estimación de variación de precio ante $\Delta y = -1\%$ (`VarPrecioDurConv`)**: aproximación de Taylor de 2º orden $\frac{\Delta P}{P} \approx -\text{ModDur}\cdot \Delta y + \frac{1}{2}\,\text{Convexidad}\cdot (\Delta y)^2$ (expresada en $\%$), que estima una apreciación media del **`+3,10%`** (mediana **`+2,39%`**) y reduce el error medio frente a la revaluación exacta en casi 30 veces respecto a usar solo duración ($0{,}0038\%$ vs $0{,}1047\%$).
- **Respuestas Markdown completas (Secciones 2, 3 y 4)**: redactadas e integradas en [analisis_cartera.ipynb](src/analisis_cartera.ipynb) con todas las ecuaciones en modo matemático LaTeX (`$...$` / `$$...$$`), celdas ejecutadas y gráficos guardados.
- **Entregable generado**: [results/sensibilidad.csv](results/sensibilidad.csv) (`ISIN;Yield;Dur;ModDur;Convexidad;VarPrecioDurConv`, 2.165 bonos, 0 `NaN`).
