#!/bin/bash
# Ejecutar en una Mac (PyInstaller no compila para otro sistema).
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pyinstaller

pyinstaller --onefile --name generar_informes \
  --hidden-import matplotlib.backends.backend_agg main.py

PAQUETE="dist/TEST_SIBO_paquete"
rm -rf "$PAQUETE" && mkdir -p "$PAQUETE"
cp dist/generar_informes "$PAQUETE/"
cp config.json "Generar informes.command" LEEME_USUARIO.txt "$PAQUETE/"
cp logo.png firma.png "$PAQUETE/" 2>/dev/null || true
python3 -c "import json; from datos import crear_planilla_modelo as c; c('$PAQUETE/pacientes_modelo.xlsx', json.load(open('config.json', encoding='utf-8')))"
(cd dist && zip -r Paquete.zip TEST_SIBO_paquete)
echo "Listo: dist/Paquete.zip"
