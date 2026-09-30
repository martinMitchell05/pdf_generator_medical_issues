"""Aplicación del criterio de positividad del informe (según config.json)."""


def _aumento_maximo(valores, ventana):
    """Mayor aumento sobre el basal (minuto 0) hasta 'ventana' minutos inclusive."""
    basal = valores[0]
    aumentos = [v - basal for t, v in valores.items() if 0 < t <= ventana]
    return max(aumentos) if aumentos else 0


def evaluar(reg, cfg):
    c = cfg["criterios"]
    aum_h2 = _aumento_maximo(reg["h2"], c["ventana_min"])
    aum_ch4 = _aumento_maximo(reg["ch4"], c["ventana_min"])
    sibo = aum_h2 > c["h2_umbral_ppm"]
    imo = aum_ch4 > c["ch4_umbral_ppm"]

    textos = c["conclusiones"]
    if sibo and imo:
        clave = "ambos"
    elif sibo:
        clave = "sibo"
    elif imo:
        clave = "imo"
    else:
        clave = "normal"
    return {"aumento_h2": aum_h2, "aumento_ch4": aum_ch4,
            "sibo": sibo, "imo": imo, "conclusion": textos[clave]}
