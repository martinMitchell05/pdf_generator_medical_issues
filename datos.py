"""Carga de datos: planilla Excel/CSV, carga manual y planilla modelo."""
import csv
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from criterios import evaluar

CAMPOS_TEXTO = [
    "nombre", "dni", "edad", "cobertura", "nro_afiliado", "fecha_estudio",
    "sede", "estimulo", "dieta_previa", "causa", "comentarios", "conclusion",
]


# --------------------------------------------------------------------------
# Tiempos y columnas
# --------------------------------------------------------------------------
def tiempos_medicion(cfg):
    e = cfg["estudio"]
    return list(range(0, e["duracion_min"] + 1, e["intervalo_min"]))


def tiempos_tabla(cfg):
    e = cfg["estudio"]
    return list(range(0, e["tabla_hasta_min"] + 1, e["intervalo_min"]))


def columnas(cfg):
    t = tiempos_medicion(cfg)
    return CAMPOS_TEXTO + [f"h2_{x}" for x in t] + [f"ch4_{x}" for x in t]


# --------------------------------------------------------------------------
# Conversión de valores
# --------------------------------------------------------------------------
def parse_num(valor):
    """Devuelve None si está vacío; acepta coma o punto decimal."""
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.strip().replace(",", ".")
        if valor == "":
            return None
    try:
        n = float(valor)
    except ValueError:
        raise ValueError(f"'{valor}' no es un número válido")
    return int(n) if n == int(n) else n


def parse_fecha(valor):
    """Devuelve la fecha como texto AAAA-MM-DD."""
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    texto = str(valor or "").strip()
    if not texto:
        raise ValueError("falta la fecha del estudio")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(texto, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"fecha '{texto}' no reconocida (usar AAAA-MM-DD o DD/MM/AAAA)")


def _texto(valor):
    if valor is None:
        return ""
    if isinstance(valor, float) and valor == int(valor):
        return str(int(valor))
    return str(valor).strip()


# --------------------------------------------------------------------------
# Armado y validación de un registro
# --------------------------------------------------------------------------
def armar_registro(fila, cfg):
    """fila: dict con las columnas de la planilla. Lanza ValueError si hay problemas."""
    est = cfg["estudio"]
    reg = {c: _texto(fila.get(c)) for c in CAMPOS_TEXTO if c != "fecha_estudio"}

    if not reg["nombre"]:
        raise ValueError("falta el nombre del paciente")
    reg["fecha_estudio"] = parse_fecha(fila.get("fecha_estudio"))
    reg["cobertura"] = reg["cobertura"] or est["cobertura_default"]
    reg["sede"] = reg["sede"] or cfg["centro"]["sede_default"]
    reg["estimulo"] = reg["estimulo"] or est["estimulo_default"]
    reg["dieta_previa"] = reg["dieta_previa"] or est["dieta_default"]

    reg["h2"], reg["ch4"] = {}, {}
    for t in tiempos_medicion(cfg):
        for gas in ("h2", "ch4"):
            v = parse_num(fila.get(f"{gas}_{t}"))
            if v is not None:
                if v < 0:
                    raise ValueError(f"{gas.upper()} a los {t} min es negativo")
                reg[gas][t] = v
    if 0 not in reg["h2"] or 0 not in reg["ch4"]:
        raise ValueError("faltan los valores basales (minuto 0) de H2 y/o CH4")

    if not reg["conclusion"] and cfg["criterios"].get("conclusion_automatica", True):
        reg["conclusion"] = evaluar(reg, cfg)["conclusion"]
    return reg


# --------------------------------------------------------------------------
# Lectura de planilla
# --------------------------------------------------------------------------
def _normalizar(encabezado):
    return str(encabezado or "").strip().lower().replace(" ", "_")


def _filas_xlsx(ruta):
    wb = load_workbook(ruta, data_only=True)
    ws = wb.worksheets[0]
    filas = ws.iter_rows(values_only=True)
    enc = [_normalizar(c) for c in next(filas)]
    for vals in filas:
        yield dict(zip(enc, vals))


def _filas_csv(ruta):
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
        f.seek(0)
        try:
            dialecto = csv.Sniffer().sniff(muestra, delimiters=";,\t")
        except csv.Error:
            dialecto = csv.excel
        for fila in csv.DictReader(f, dialect=dialecto):
            yield {_normalizar(k): v for k, v in fila.items()}


def leer_planilla(ruta, cfg):
    """Devuelve (registros_validos, errores). Cada error es un texto legible."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    ext = ruta.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        filas = _filas_xlsx(ruta)
    elif ext in (".csv", ".txt"):
        filas = _filas_csv(ruta)
    else:
        raise ValueError("Formato no soportado. Usar .xlsx o .csv")

    registros, errores = [], []
    for n, fila in enumerate(filas, start=2):  # la fila 1 es el encabezado
        if not any(_texto(v) for v in fila.values()):
            continue  # fila vacía
        try:
            registros.append(armar_registro(fila, cfg))
        except ValueError as e:
            nombre = _texto(fila.get("nombre")) or "(sin nombre)"
            errores.append(f"Fila {n} - {nombre}: {e}")
    return registros, errores


# --------------------------------------------------------------------------
# Carga manual por consola
# --------------------------------------------------------------------------
def _preguntar(texto, defecto="", obligatorio=False):
    while True:
        sufijo = f" [{defecto}]" if defecto else ""
        r = input(f"  {texto}{sufijo}: ").strip() or defecto
        if r or not obligatorio:
            return r
        print("    Este dato es obligatorio.")


def pedir_manual(cfg):
    est = cfg["estudio"]
    print("\n--- Datos del paciente ---")
    fila = {
        "nombre": _preguntar("Nombre y apellido", obligatorio=True),
        "dni": _preguntar("DNI"),
        "edad": _preguntar("Edad (años)"),
        "cobertura": _preguntar("Cobertura", est["cobertura_default"]),
        "nro_afiliado": _preguntar("N° de afiliado"),
    }
    print("\n--- Datos del estudio ---")
    while True:
        try:
            fila["fecha_estudio"] = parse_fecha(
                _preguntar("Fecha del estudio (AAAA-MM-DD o DD/MM/AAAA)",
                           date.today().isoformat()))
            break
        except ValueError as e:
            print(f"    {e}")
    fila["sede"] = _preguntar("Sede", cfg["centro"]["sede_default"])
    fila["estimulo"] = _preguntar("Estímulo", est["estimulo_default"])
    fila["dieta_previa"] = _preguntar("Dieta previa", est["dieta_default"])

    print("\n--- Valores en ppm (Enter para dejar vacío) ---")
    for t in tiempos_medicion(cfg):
        for gas in ("h2", "ch4"):
            while True:
                try:
                    v = parse_num(input(f"  {gas.upper():<3} a los {t:>3} min: "))
                    break
                except ValueError as e:
                    print(f"    {e}")
            fila[f"{gas}_{t}"] = v

    fila["causa"] = _preguntar("Causa (opcional)")
    fila["comentarios"] = _preguntar("Comentarios (opcional)")
    fila["conclusion"] = _preguntar(
        "Conclusión (Enter = sugerida automáticamente por el criterio)")
    return armar_registro(fila, cfg)


# --------------------------------------------------------------------------
# Planilla modelo
# --------------------------------------------------------------------------
def crear_planilla_modelo(ruta, cfg):
    cols = columnas(cfg)
    wb = Workbook()
    ws = wb.active
    ws.title = "Pacientes"
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2B7A9B")
        c.alignment = Alignment(horizontal="center")

    h2_a = [4, 8, 6, 5, 8, 4, 4, 4, 5]
    ch4_a = [6, 5, 4, 6, 5, 5, 4, 6, 6]
    h2_b = [3, 6, 12, 20, 31, 38, 35, 30, 28]
    ch4_b = [2, 2, 3, 2, 3, 2, 2, 3, 2]
    ejemplos = [
        ("Paciente Ejemplo Uno", "11111111", 35, "particular", "", "2026-09-10", h2_a, ch4_a),
        ("Paciente Ejemplo Dos", "22222222", 52, "Obra social X", "12345/01", "10/09/2026", h2_b, ch4_b),
    ]
    for nom, dni, edad, cob, afil, fecha, h2, ch4 in ejemplos:
        fila = {"nombre": nom, "dni": dni, "edad": edad, "cobertura": cob,
                "nro_afiliado": afil, "fecha_estudio": fecha}
        for t, a, b in zip(tiempos_medicion(cfg), h2, ch4):
            fila[f"h2_{t}"], fila[f"ch4_{t}"] = a, b
        ws.append([fila.get(c) for c in cols])

    for i, c in enumerate(cols, start=1):
        ancho = 22 if c in ("nombre", "cobertura", "sede", "comentarios", "conclusion") else 12
        ws.column_dimensions[get_column_letter(i)].width = ancho
    ws.freeze_panes = "B2"

    ayuda = wb.create_sheet("Instrucciones")
    for linea in [
        "Una fila por paciente. Borrar las filas de ejemplo antes de usar.",
        "Obligatorios: nombre, fecha_estudio y los valores basales (h2_0 y ch4_0).",
        "Fecha: AAAA-MM-DD o DD/MM/AAAA.",
        "Valores h2_XX / ch4_XX: ppm a los XX minutos. Dejar vacío si no se midió.",
        "Cobertura, sede, estímulo y dieta previa: si se dejan vacíos usan los valores de config.json.",
        "Conclusión: si se deja vacía se completa con la sugerida según el criterio de config.json.",
        "Causa y comentarios: opcionales.",
    ]:
        ayuda.append([linea])
    ayuda.column_dimensions["A"].width = 100
    wb.save(ruta)
