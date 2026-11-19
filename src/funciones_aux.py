"""
Funciones auxiliares para el Taller de Renta Fija (MIAX15).
Valoración de bonos, spreads, yields, duración y convexidad.
"""
import numpy as np
import pandas as pd


def fechas_cupon(ancla, frecuencia, desde, hasta):
    """
    Devuelve las fechas de cupón del bono comprendidas en el intervalo (desde, hasta].

    Las fechas se generan sumando múltiplos del periodo a una fecha 'ancla' que pertenece
    al calendario de cupones (el vencimiento, o el primer cupón en los perpetuos).

    ancla      : fecha que pertenece al calendario de cupones
    frecuencia : nº de cupones al año (1 = anual, 2 = semestral)
    desde      : se excluyen las fechas <= desde
    hasta      : se excluyen las fechas > hasta
    """
    paso = 12 // int(frecuencia)          # meses entre cupones

    # Empezamos un poco antes de 'desde' para no dejarnos ninguna fecha
    k = int(np.floor((desde - ancla).days / 365.25 * frecuencia)) - 1

    fechas = []
    while True:
        # Sumamos siempre desde el ancla (y no desde la fecha anterior) para evitar
        # que se desplace el día en meses cortos (p. ej. 31/01 -> 28/02 -> 28/03...)
        fecha = ancla + pd.DateOffset(months=k * paso)
        if fecha > hasta:
            break
        if fecha > desde:
            fechas.append(fecha)
        k += 1
    return fechas


def proximo_cupon(bono, fecha_valor):
    """Próxima fecha de cupón del bono posterior a fecha_valor."""
    # Anclamos el calendario al vencimiento; en los perpetuos, al primer cupón
    if pd.notna(bono['Maturity']):
        ancla = bono['Maturity']
    else:
        ancla = bono['First Coupon Date']

    # Como mucho hay un año hasta el próximo cupón (cupones anuales)
    hasta = fecha_valor + pd.DateOffset(years=1)
    return fechas_cupon(ancla, bono['Coupon Frequency'], fecha_valor, hasta)[0]


def fecha_vencimiento_efectiva(bono, fecha_valor):
    """
    Fecha hasta la que valoramos el bono, según las hipótesis del enunciado:
    - Sin call: su vencimiento.
    - Con call futura (incluye perpetuos): la próxima fecha call (asumimos que se ejerce).
    - Con call ya pasada (la opción ya era ejercitable y el emisor NO la ha ejercido, porque el
      bono sigue cotizando): su vencimiento final. Asumir amortización en el próximo cupón daba
      z-spreads absurdos (miles de pb) en bonos que cotizan muy por debajo de la par.
      Excepción: un perpetuo con call pasada no tiene vencimiento; se usa el próximo cupón
      (FR0014005EJ6, único caso; conviene excluirlo del mandato).
    """
    fecha_call = bono['Next Call Date']

    if pd.isna(fecha_call):
        return bono['Maturity']
    if fecha_call > fecha_valor:
        return fecha_call
    if pd.notna(bono['Maturity']):
        return bono['Maturity']
    return proximo_cupon(bono, fecha_valor)

def factor_descuento(t, curva):
    """
    Factor de descuento para un plazo t (en años), interpolando exponencialmente
    los factores de descuento de la curva (= interpolación lineal de log(DF)).

    t     : plazo en años (un número o un array de plazos)
    curva : DataFrame con las columnas 'Plazo' (años) y 'Discount' (factor de descuento)
    """
    t = np.asarray(t, dtype=float)

    # Comprobamos que no salimos de la curva: np.interp no extrapola,
    # devolvería el último factor de descuento, lo que sería incorrecto
    if np.any(t > curva['Plazo'].max()):
        raise ValueError('Plazo fuera de la curva: hace falta extrapolar')

    # Interpolación lineal del logaritmo del factor de descuento
    log_df = np.interp(t, curva['Plazo'], np.log(curva['Discount']))
    return np.exp(log_df)

def ancla_cupones(bono):
    """Fecha de referencia del calendario de cupones: vencimiento, o primer cupón si es perpetuo."""
    if pd.notna(bono['Maturity']):
        return bono['Maturity']
    return bono['First Coupon Date']


def cupon_anterior(bono, fecha):
    """Última fecha de cupón del bono anterior o igual a 'fecha'."""
    # En un intervalo de un año siempre hay al menos una fecha de cupón
    desde = fecha - pd.DateOffset(years=1)
    return fechas_cupon(ancla_cupones(bono), bono['Coupon Frequency'], desde, fecha)[-1]


def flujos_bono(bono, fecha_valor):
    """
    Flujos futuros del bono (por 100 de nominal) hasta su vencimiento efectivo.
    Devuelve un DataFrame con columnas: Fecha, Plazo (años, ACT/365) y Flujo.
    """
    vto = fecha_vencimiento_efectiva(bono, fecha_valor)
    frecuencia = int(bono['Coupon Frequency'])
    cupon_periodo = bono['Coupon'] / frecuencia       # cupón regular (cupón anual / frecuencia)

    # Fechas de cupón regulares entre la fecha valor y el vencimiento efectivo
    fechas = fechas_cupon(ancla_cupones(bono), frecuencia, fecha_valor, vto)
    flujos = [cupon_periodo] * len(fechas)

    if fechas and fechas[-1] == vto:
        # El vencimiento efectivo coincide con una fecha de cupón: último cupón + nominal
        flujos[-1] += 100
    else:
        # La call cae entre dos fechas de cupón: se paga el nominal más el cupón
        # devengado desde el último cupón hasta la fecha call (ACT/365)
        ultimo = cupon_anterior(bono, vto)
        devengado = bono['Coupon'] * (vto - ultimo).days / 365
        fechas.append(vto)
        flujos.append(100 + devengado)

    # Plazo de cada flujo en años desde la fecha valor (ACT/365)
    plazos = [(f - fecha_valor).days / 365 for f in fechas]
    return pd.DataFrame({'Fecha': fechas, 'Plazo': plazos, 'Flujo': flujos})

def cupon_corrido(bono, fecha_valor):
    """Cupón corrido (por 100 de nominal) a fecha valor, en base ACT/365."""
    ultimo = cupon_anterior(bono, fecha_valor)
    return bono['Coupon'] * (fecha_valor - ultimo).days / 365


def valorar_bono(bono, curva, fecha_valor, spread=0.0):
    """
    Valoración de un bono descontando sus flujos con la curva más un spread de crédito.

    bono        : fila del DataFrame universo
    curva       : DataFrame con 'Plazo' y 'Discount'
    fecha_valor : fecha de valoración
    spread      : spread de crédito en tanto por uno (0.01 = 100 pb), aplicado como
                  desplazamiento paralelo de la curva cero (capitalización continua)

    Devuelve un diccionario con precio sucio, cupón corrido y precio limpio (por 100 nominal).
    """
    flujos = flujos_bono(bono, fecha_valor)

    # Factores de descuento de la curva, ajustados por el spread: DF(t) · exp(-s·t)
    df = factor_descuento(flujos['Plazo'], curva) * np.exp(-spread * flujos['Plazo'])

    precio_sucio = (flujos['Flujo'] * df).sum()
    cc = cupon_corrido(bono, fecha_valor)

    return {
        'PrecioSucio': precio_sucio,
        'CuponCorrido': cc,
        'PrecioLimpio': precio_sucio - cc
    }


# ----------------------------------------------------------------------------------
# SECCION 3: z-spread (y stubs de la sección 4)
# ----------------------------------------------------------------------------------

def _resolver_raiz(f, a, b, tol=1e-12, max_iter=200):
    """
    Raíz de f en [a, b] por bisección (f(a) y f(b) deben tener signo contrario).
    Se implementa a mano para no depender de scipy; es robusta y suficientemente rápida.
    """
    fa_, fb_ = f(a), f(b)
    if fa_ * fb_ > 0:
        raise ValueError('La raíz no está en el intervalo indicado')
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa_ * fm <= 0:
            b, fb_ = m, fm
        else:
            a, fa_ = m, fm
        if (b - a) < tol:
            break
    return 0.5 * (a + b)


def z_spread(bono, curva, fecha_valor, precio_limpio_mercado):
    """
    Z-spread (decimal, capitalización continua): desplazamiento paralelo de la curva cero que
    hace que el precio SUCIO calculado iguale al de mercado (limpio de mercado + cupón corrido).
    """
    objetivo = precio_limpio_mercado + cupon_corrido(bono, fecha_valor)
    # Flujos y factores de descuento de la curva se calculan UNA vez (el spread solo añade e^(-s·t));
    # equivale a llamar a valorar_bono en cada iteración, pero es mucho más rápido.
    flujos = flujos_bono(bono, fecha_valor)
    t = flujos['Plazo'].values
    cf_df = flujos['Flujo'].values * factor_descuento(t, curva)
    f = lambda s: (cf_df * np.exp(-s * t)).sum() - objetivo
    # El precio es decreciente en el spread: buscamos entre -10% y +100%
    return _resolver_raiz(f, -0.10, 1.00)


# ----------------------------------------------------------------------------------
# SECCION 4: yield, duración y convexidad
# ----------------------------------------------------------------------------------

def ytm(bono, fecha_valor, precio_limpio_mercado):
    """
    Yield to maturity (TIR) del bono, en tanto por uno y capitalización ANUAL:
    el tipo único y que iguala el valor actual de los flujos al precio SUCIO de mercado.

        Precio sucio = Σ Flujo_i / (1 + y)^t_i      (t_i en años, base ACT/365)

    Usa los mismos flujos que la valoración: hasta el vencimiento efectivo
    (fecha call en los callable), como pide el enunciado.
    """
    flujos = flujos_bono(bono, fecha_valor)
    t = flujos['Plazo'].values
    cf = flujos['Flujo'].values

    # Objetivo: precio sucio de mercado = precio limpio + cupón corrido
    objetivo = precio_limpio_mercado + cupon_corrido(bono, fecha_valor)

    # Diferencia entre el valor actual con la yield y y el precio objetivo
    f = lambda y: (cf / (1 + y) ** t).sum() - objetivo

    # El valor actual baja al subir y: buscamos la raíz entre -50% y +500%
    return _resolver_raiz(f, -0.5, 5.0)


def risk_measures(bono, fecha_valor, y):
    """
    Medidas de sensibilidad del bono a su yield y (tanto por uno, capitalización anual):
    - Dur       : duración de Macaulay (años) = plazo medio de los flujos ponderado por su valor actual
    - ModDur    : duración modificada = Dur / (1 + y); variación % del precio ante +1 de yield
    - Convexidad: curvatura de la relación precio-yield
    Usa los mismos flujos que la valoración (hasta el vencimiento efectivo).
    """
    flujos = flujos_bono(bono, fecha_valor)
    t = flujos['Plazo'].values
    cf = flujos['Flujo'].values

    # Valor actual de cada flujo descontado con la yield
    va = cf / (1 + y) ** t
    precio = va.sum()

    dur = (t * va).sum() / precio
    mod_dur = dur / (1 + y)
    convexidad = (t * (t + 1) * va).sum() / ((1 + y) ** 2 * precio)

    return {'Dur': dur, 'ModDur': mod_dur, 'Convexidad': convexidad}

def variacion_precio_dur_conv(mod_dur, convexidad, dy):
    """
    Variación porcentual estimada del precio ante un cambio dy de la yield (tanto por uno),
    con la aproximación de duración y convexidad:
        ΔP/P ≈ -ModDur · dy + ½ · Convexidad · dy²
    Devuelve la variación en % (p. ej. 5.09 = +5,09%).
    """
    return (-mod_dur * dy + 0.5 * convexidad * dy ** 2) * 100


def variacion_precio_exacta(bono, fecha_valor, y, dy):
    """
    Variación porcentual EXACTA del precio ante un cambio dy de la yield: revaloramos
    los flujos con la yield y + dy y la comparamos con el precio a la yield y.
    Sirve para comprobar la precisión de la aproximación de duración y convexidad.
    """
    flujos = flujos_bono(bono, fecha_valor)
    t = flujos['Plazo'].values
    cf = flujos['Flujo'].values

    precio_ini = (cf / (1 + y) ** t).sum()
    precio_fin = (cf / (1 + y + dy) ** t).sum()
    return (precio_fin / precio_ini - 1) * 100

# ----------------------------------------------------------------------------------
# SECCION 5: backtest de la cartera equiponderada
# ----------------------------------------------------------------------------------

def fechas_fin_de_mes(fechas):
    """Último día con mercado de cada mes, a partir de las fechas con precios."""
    fechas = pd.DatetimeIndex(fechas)
    serie = pd.Series(fechas, index=fechas)
    # Agrupamos por (año, mes) y nos quedamos con la fecha máxima de cada grupo
    return pd.DatetimeIndex(serie.groupby([fechas.year, fechas.month]).max().values)

def cupones_cobrados(bono, desde, hasta):
    """Cupones (por 100 de nominal) que paga el bono en el periodo (desde, hasta]."""
    frecuencia = int(bono['Coupon Frequency'])
    fechas = fechas_cupon(ancla_cupones(bono), frecuencia, desde, hasta)
    return len(fechas) * bono['Coupon'] / frecuencia

def rentabilidad_total_bono(bono, precio_ini, precio_fin, fecha_ini, fecha_fin):
    """
    Rentabilidad total de un bono entre dos fechas: variación de precio + cupón corrido
    + cupones cobrados, sobre el precio sucio inicial.
    """
    sucio_ini = precio_ini + cupon_corrido(bono, fecha_ini)
    valor_fin = precio_fin + cupon_corrido(bono, fecha_fin) + cupones_cobrados(bono, fecha_ini, fecha_fin)
    return valor_fin / sucio_ini - 1

def backtest_equiponderado(universo, precios, fechas_reb):
    """
    Backtest de una cartera equiponderada con rebalanceo en cada fecha de fechas_reb.
    En cada fecha se invierte el mismo peso en todos los bonos vivos (ya emitidos y con precio).

    Devuelve un DataFrame indexado por la fecha de fin de cada periodo con:
    - 'Rent cartera': rentabilidad total de la cartera en el periodo (decimal)
    - 'NumBonos'    : número de bonos en cartera durante el periodo
    """
    resultados = []

    # Recorremos los periodos: (fecha inicio, fecha fin) consecutivas
    for t0, t1 in zip(fechas_reb[:-1], fechas_reb[1:]):

        # Bonos vivos en t0: ya emitidos y con precio en esa fecha
        vivos = universo.index[(universo['Issue date'] <= t0) & precios.loc[t0].notna()]

        # Rentabilidad total de cada bono vivo en el periodo
        rent_bonos = [
            rentabilidad_total_bono(bono, precios.at[t0, isin], precios.at[t1, isin], t0, t1)
            for isin, bono in universo.loc[vivos].iterrows()
        ]

        # Cartera equiponderada: la rentabilidad es la media simple de los bonos
        resultados.append({
            'Fecha': t1,
            'Rent cartera': np.mean(rent_bonos),
            'NumBonos': len(vivos)
        })

    return pd.DataFrame(resultados).set_index('Fecha')

# ----------------------------------------------------------------------------------
# SECCION 6: cartera bajo mandato (optimización)
# ----------------------------------------------------------------------------------

def optimizar_mandato(candidatos, max_n=20, max_dur=3, max_hy=0.10, max_emision=0.10, max_emisor=0.15,  col_emisor='Issuer'):
    """
    Cartera que maximiza la yield media ponderada cumpliendo las restricciones del mandato.
    Se resuelve como un problema de programación lineal entera mixta (MILP):

    Variables: w_i (peso de cada bono, continuo) y z_i (1 si el bono entra en cartera, binario).
    Max  Σ w_i·Yield_i
    s.a. Σ w_i = 1                         (invertimos el 100%)
         Σ z_i <= max_n                    (como máximo max_n bonos)
         Σ w_i·Dur_i <= max_dur            (duración de la cartera)
         Σ w_i·HY_i <= max_hy              (exposición HY, incluidos los sin rating)
         w_i <= max_emision · z_i          (máximo por emisión; y w_i = 0 si el bono no entra)
         Σ w_i (mismo emisor) <= max_emisor

    candidatos : DataFrame (índice ISIN) con columnas 'Yield', 'Dur', 'HY' (bool) e 'Issuer'
    col_emisor : columna con la que se aplica el límite por emisor (p. ej. 'Grupo' para agrupar filiales)
    Devuelve una Serie con los pesos de los bonos seleccionados (índice ISIN).
    """
    from scipy.optimize import milp, LinearConstraint, Bounds

    n = len(candidatos)
    yields = candidatos['Yield'].values
    dur = candidatos['Dur'].values
    hy = candidatos['HY'].values.astype(float)
    ceros, unos = np.zeros(n), np.ones(n)

    # Vector de variables: [w_1..w_n, z_1..z_n]. milp minimiza, así que usamos -yield
    objetivo = np.concatenate([-yields, ceros])

    # Restricciones generales (una fila cada una)
    A = np.array([
        np.concatenate([unos, ceros]),     # suma de pesos
        np.concatenate([ceros, unos]),     # número de bonos
        np.concatenate([dur, ceros]),      # duración
        np.concatenate([hy, ceros]),       # exposición HY
    ])
    generales = LinearConstraint(A, [1, 0, -np.inf, -np.inf], [1, max_n, max_dur, max_hy])

    # w_i - max_emision · z_i <= 0  (enlaza peso y selección)
    enlace = LinearConstraint(np.hstack([np.eye(n), -max_emision * np.eye(n)]), -np.inf, 0)

    # Una fila por emisor: suma de los pesos de sus bonos <= max_emisor
    emisores = pd.get_dummies(candidatos[col_emisor]).T.values.astype(float)
    por_emisor = LinearConstraint(np.hstack([emisores, np.zeros_like(emisores)]), -np.inf, max_emisor)

    # Límites: 0 <= w_i <= max_emision ; z_i binaria (0 o 1)
    limites = Bounds(0, np.concatenate([np.full(n, max_emision), unos]))
    enteras = np.concatenate([ceros, unos])

    resultado = milp(objetivo, constraints=[generales, enlace, por_emisor],
                     integrality=enteras, bounds=limites)
    if not resultado.success:
        raise ValueError(f'No se ha encontrado una cartera válida: {resultado.message}')

    pesos = pd.Series(resultado.x[:n], index=candidatos.index, name='Peso')
    return pesos[pesos > 1e-6]

# ----------------------------------------------------------------------------------
# SECCION 1: tablas de control de calidad
# ----------------------------------------------------------------------------------

def control_calidad_universo(df):
    """
    Tabla de control de calidad del universo: una fila por característica (columna) con
    nº de observaciones (datos no vacíos), nº de missing, nº de valores únicos y
    mínimo/máximo (solo para columnas numéricas o de fecha).
    """
    filas = []
    for col in df.columns:
        serie = df[col]
        # El mínimo y el máximo solo tienen sentido en números y fechas, no en texto
        aplica_min_max = (pd.api.types.is_numeric_dtype(serie)
                          or pd.api.types.is_datetime64_any_dtype(serie))
        filas.append({
            'Caracteristica': col,
            'NumObservaciones': serie.notna().sum(),
            'NumMissing': serie.isna().sum(),
            'NumValoresUnicos': serie.nunique(),
            'Minimo': serie.min() if aplica_min_max else np.nan,
            'Maximo': serie.max() if aplica_min_max else np.nan,
        })
    return pd.DataFrame(filas).set_index('Caracteristica')

def control_calidad_precios(precios):
    """
    Tabla de control de calidad de los precios históricos: una fila por bono con
    nº de observaciones (precios disponibles), nº de missing, mínimo, máximo,
    fecha de inicio y de fin de cotización, y nº de huecos dentro del periodo de cotización.

    precios : DataFrame con filas = fechas y columnas = bonos (ISIN)
    """
    inicio = precios.apply(lambda serie: serie.first_valid_index())
    fin = precios.apply(lambda serie: serie.last_valid_index())

    # Huecos "reales": días sin precio ENTRE la primera y la última cotización
    # (los NaN antes de la emisión no son un problema de calidad)
    huecos = precios.apply(
        lambda serie: serie.loc[serie.first_valid_index():serie.last_valid_index()].isna().sum()
    )

    tabla = pd.DataFrame({
        'NumObservaciones': precios.notna().sum(),
        'NumMissing': precios.isna().sum(),
        'Minimo': precios.min(),
        'Maximo': precios.max(),
        'FechaInicio': inicio,
        'FechaFin': fin,
        'HuecosEntreCotizaciones': huecos,
    })
    tabla.index.name = 'ISIN'
    return tabla

def filtrar_spikes(precios, umbral=0.05):
    """
    Detecta precios anómalos (spikes): variación diaria mayor que 'umbral' que revierte
    al día siguiente con otra variación mayor que 'umbral' de signo contrario.

    Devuelve:
    - una copia de los precios con esos valores a NaN (para rellenarlos después con el
      último precio válido mediante forward fill)
    - la máscara (True/False) de los spikes detectados
    """
    # Variación diaria de cada bono (rellenamos huecos solo para este cálculo)
    rent = precios.ffill().pct_change(fill_method=None)
    siguiente = rent.shift(-1)

    # Spike: salto grande seguido de otro salto grande en sentido contrario
    spikes = (rent.abs() > umbral) & (siguiente.abs() > umbral) & (rent * siguiente < 0)

    # mask() pone NaN donde la condición es True; el resto de precios no cambia
    return precios.mask(spikes), spikes


# ----------------------------------------------------------------------------------
# SECCION 7: cobertura de tipos de interés con futuros sobre deuda alemana
# ----------------------------------------------------------------------------------

PB = 1e-4                  # 1 pb en tanto por uno
TAMANO_CONTRATO = 1e5      # nominal de un contrato de futuro (€)


def dv01(valor, duracion_modificada):
    """Euros que pierde una posición de `valor` si los tipos suben 1 pb."""
    return valor * duracion_modificada * PB


def dv01_futuro(duracion, precio_futuro, tamano_contrato=TAMANO_CONTRATO):
    """DV01 de un contrato de futuro. Su valor es precio/100 * tamaño del contrato."""
    return dv01(precio_futuro / 100 * tamano_contrato, duracion)


def num_futuros(valor, duracion_cartera, duracion_futuro, precio_futuro,
                tamano_contrato=TAMANO_CONTRATO):
    """
    Contratos a vender (sin redondear) para que el DV01 de los futuros iguale al de la cartera:
        N = DV01 de la cartera / DV01 de un contrato
    Las duraciones son las modificadas.
    """
    return dv01(valor, duracion_cartera) / dv01_futuro(duracion_futuro, precio_futuro,
                                                       tamano_contrato)


def tabla_cobertura_tipos(valor, duracion_cartera, futuros, contratos=None,
                          tamano_contrato=TAMANO_CONTRATO):
    """
    Resultado de cubrir la cartera con cada futuro (una fila por ticker). `futuros` debe
    tener las columnas 'Duracion' y 'Precio'.

    Si `contratos` es None se venden los que cubren el 100% del DV01 (redondeados); si es un
    número, ese mismo a todos los futuros (positivo = vender, negativo = comprar).
    DV01Neto es el DV01 de cartera + futuros, y DuracionNeta ese DV01 pasado a duración.
    Pct1Contrato es lo que pesa un contrato en el DV01 de la cartera.
    """
    dv01_c = dv01(valor, duracion_cartera)
    t = pd.DataFrame(index=futuros.index)
    t['Nocional1Contrato'] = futuros['Precio'] / 100 * tamano_contrato
    t['DV01Contrato'] = dv01_futuro(futuros['Duracion'], futuros['Precio'], tamano_contrato)
    t['Pct1Contrato'] = t['DV01Contrato'] / dv01_c * 100
    t['ContratosExactos'] = num_futuros(valor, duracion_cartera, futuros['Duracion'],
                                        futuros['Precio'], tamano_contrato)
    if contratos is None:
        t['Contratos'] = t['ContratosExactos'].round()
    else:
        t['Contratos'] = float(contratos)
    t['NocionalFuturos'] = t['Contratos'] * t['Nocional1Contrato']
    t['DV01Cobertura'] = -t['Contratos'] * t['DV01Contrato']    # si vendemos, restan
    t['DV01Neto'] = dv01_c + t['DV01Cobertura']
    t['PctCubierto'] = -t['DV01Cobertura'] / dv01_c * 100
    t['DuracionNeta'] = t['DV01Neto'] / (valor * PB)
    return t


def cobertura_por_tramos(dv01_tramos, futuro_por_tramo, futuros, tamano_contrato=TAMANO_CONTRATO):
    """
    Cubre el DV01 de cada tramo de la curva con el futuro que le asignamos.
    dv01_tramos      : Series con el DV01 (€/pb) de cada tramo
    futuro_por_tramo : diccionario tramo -> ticker del futuro
    futuros          : DataFrame con las columnas 'Duracion' y 'Precio'
    """
    t = pd.DataFrame({'DV01Tramo': dv01_tramos})
    for tramo in t.index:
        futuro = futuros.loc[futuro_por_tramo[tramo]]
        t.loc[tramo, 'Futuro'] = futuro_por_tramo[tramo]
        t.loc[tramo, 'DV01Contrato'] = dv01_futuro(futuro['Duracion'], futuro['Precio'],
                                                   tamano_contrato)
    t['Contratos'] = (t['DV01Tramo'] / t['DV01Contrato']).round()
    t['DV01Neto'] = t['DV01Tramo'] - t['Contratos'] * t['DV01Contrato']
    return t
