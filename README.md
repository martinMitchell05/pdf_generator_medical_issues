# Informes de test de aire espirado (H2 / C_13)

Genera informes PDF con una estructura prefijada: encabezado, tabla + curva (gráfica), criterio explícito, y diagnóstico.

## Estructura
- `main.py`      menú de consola
- `datos.py`     carga (Excel/CSV/manual), validación, planilla modelo
- `criterios.py` criterio de positividad y conclusión sugerida ---> *Eliminar*
- `grafico.py`   gráfica (matplotlib)
- `pdf.py`       armado del PDF (ReportLab)
- `config.json`  centro, procedimiento, criterio, umbrales, profesional ---> *Modificar: procedimientos, criterios, umbrales*

## Funcionalidades

**Requeridas (inicialmente):**

1. Datos filiatorios ***Preguntar por algún otro dato***
2. Valores: [x] ***Completado***
    - *H2 (4 tipos según sustrato):*  glucosa, lactulosa, lactosa, fructosa
    - *C_13 (Carbono 13 activado)* 
3. Diagnóstico [x] ***Completado***

**Opcionales (mejoran la prácticidad):**

- Intervalos de tiempo variables [x]    ***Completado***
- Escritura de diagnóstico práctica [x]
- Meter links de contacto (Ig, Mail, etc) []
- Guardar en el JSON los datos de las distintas "sedes" en las que trabaja (Poder elegir entre ellas automáticamente) []

## Desarrollo
    pip install -r requirements.txt
    python3 main.py


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

