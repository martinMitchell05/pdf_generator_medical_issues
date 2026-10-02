""" main : menú de CLI """
import json
import re
import sys
import unicodedata
from pathlib import Path

from datos import crear_planilla_modelo, leer_planilla, pedir_manual
from pdf import generar_pdf


def carpeta_base():
    """Carpeta del ejecutable (o del script en desarrollo)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent  # retorna ruta absoluta del archivo + directorio dentro del que se encuentra


BASE = carpeta_base()


def cargar_config():
    ruta = BASE / "config.json"     # crear el path al json (absoluto)
    if not ruta.exists():
        raise FileNotFoundError(f"Falta el archivo config.json en {BASE}")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)     # cargar el archivo json


# --- limpiar el nombre del archivo final
def nombre_archivo(reg):
    limpio = unicodedata.normalize("NFKD", reg["nombre"]).encode("ascii", "ignore").decode()
    limpio = re.sub(r"[^A-Za-z0-9]+", "_", limpio).strip("_") or "paciente"
    return f"{limpio}_{reg['fecha_estudio']}"


# --- crear igualmente la ruta si ya existía ( (1), (2), ... )
def ruta_libre(carpeta, file):
    ruta = carpeta / f"{file}.pdf"
    n = 1
    while ruta.exists():
        ruta = carpeta / f"{file}_{n}.pdf"
        n += 1
    return ruta

# --- generar los archivos pdf
def generar_todos(registros, cfg):
    salida = BASE / cfg["carpeta_salida"]
    salida.mkdir(exist_ok=True)
    generados = []
    for reg in registros:
        ruta = ruta_libre(salida, nombre_archivo(reg))
        generar_pdf(reg, cfg, ruta, BASE)
        generados.append(ruta)
        print(f"  OK  {ruta.name}")
    return salida, generados


def limpiar_ruta(texto):
    """Permite arrastrar el archivo a la terminal (quita comillas y barras)."""
    texto = texto.strip().strip("'\"")
    return Path(texto.replace("\\ ", " ")).expanduser()


# --- carga de datos manual
def opcion_manual(cfg):
    reg = pedir_manual(cfg)
    # print(f"\nConclusión que saldrá en el informe:\n  {reg['conclusion'] or '(vacía)'}")

    salida, gen = generar_todos([reg], cfg)
    print(f"\nInforme guardado en: {salida}")


# --- carga de datos desde una planilla
def opcion_planilla(cfg):

    defecto = BASE / "pacientes.xlsx"
    r = input(f"\nArchivo Excel/CSV (arrastralo acá o Enter para cargar desde '{defecto.name}'): ")
    ruta = limpiar_ruta(r) if r.strip() else defecto

    registros, errores = leer_planilla(ruta, cfg)
    print(f"\nPacientes válidos: {len(registros)}   Con errores: {len(errores)}")

    for e in errores:
        print(f"  ERROR  {e}")
    if not registros:
        return
    if errores and input("\nHay filas con errores que se omitirán. ¿Continuar? (s/n): ").lower() != "s":
        return

    
    print("\nGenerando informes...")
    salida, gen = generar_todos(registros, cfg)

    print(f"\n{len(gen)} informes guardados en: {salida}")


# --- opción de ver/crear un modelo de planilla
def opcion_modelo():
    ruta = BASE / "pacientes_modelo.xlsx"
    cfg = cargar_config()
    crear_planilla_modelo(ruta, cfg)
    print(f"\nPlanilla modelo creada: {ruta}")


MENU = """
==============================================
  INFORMES DE TEST DE AIRE ESPIRADO
==============================================
  1) Cargar un paciente manualmente
  2) Generar informes desde una planilla (Excel/CSV)
  3) Crear planilla modelo vacía
  4) Salir
"""


def main():
    try:
        cfg = cargar_config()
    except Exception as e:
        print(f"No se pudo leer la configuración: {e}")
        input("\nPresioná Enter para salir...")
        return

    while True:
        print(MENU)
        op = input("Elegí una opción: ").strip()
        try:
            if op == "1":
                opcion_manual(cfg)
            elif op == "2":
                opcion_planilla(cfg)
            elif op == "3":
                opcion_modelo()
            elif op == "4":
                break
            else:
                print("Opción no válida.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
        except Exception as e:  # el programa no debe cerrarse ante un error
            print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()
