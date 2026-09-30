# Informes de test de aire espirado (H2 / CH4)

Genera informes PDF con la estructura del centro: encabezado, tabla + curva,
procedimiento, criterio explícito, conclusión y validación.

## Estructura
- `main.py`      menú de consola
- `datos.py`     carga (Excel/CSV/manual), validación, planilla modelo
- `criterios.py` criterio de positividad y conclusión sugerida
- `grafico.py`   gráfica (matplotlib)
- `pdf.py`       armado del PDF (ReportLab)
- `config.json`  centro, procedimiento, criterio, umbrales, profesional

## Desarrollo
    pip install -r requirements.txt
    python main.py

## Generar el ejecutable para Mac (hay que compilar EN una Mac)
    ./build_mac.sh          # deja dist/Informes_AirTest.zip

Sin Mac: subir el proyecto a GitHub y correr el workflow "Compilar para macOS"
(Actions > Run workflow). Descargar el ZIP desde "Artifacts".
El workflow usa `macos-latest` (Apple Silicon). Si la MacBook es Intel, cambiar
`runs-on` por un runner Intel vigente (verificar el nombre en la documentación
de GitHub Actions).

## Antes de entregar
- Poner `logo.png` y `firma.png` junto a `config.json` (si no están, el logo se
  reemplaza por texto y la firma queda en blanco).
- Revisar en `config.json` los umbrales y la ventana de tiempo (`ventana_min`).
