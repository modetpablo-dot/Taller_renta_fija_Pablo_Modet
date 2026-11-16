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
# STUBS (Thu 19, SECCION 4): firma final, lógica simplificada hasta que se implemente
# ----------------------------------------------------------------------------------

def ytm(bono, fecha_valor, precio_limpio_mercado):
    """STUB: yield aproximada = cupón / precio limpio (decimal). Pendiente: yield anual exacta."""
    return bono['Coupon'] / 100 / (precio_limpio_mercado / 100)


def risk_measures(bono, fecha_valor, y):
    """STUB: duración aproximada = años hasta el vencimiento efectivo (bullet). Pendiente: Macaulay/Mod/Convexidad."""
    plazo = (fecha_vencimiento_efectiva(bono, fecha_valor) - fecha_valor).days / 365
    return {'Dur': plazo, 'ModDur': plazo / (1 + y), 'Convexidad': np.nan}
