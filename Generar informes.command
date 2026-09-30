#!/bin/bash
# Doble clic en este archivo: abre Terminal y ejecuta el programa.
cd "$(dirname "$0")"
./generar_informes
echo
read -p "Presioná Enter para cerrar..."
