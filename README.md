# Informes de test de aire espirado (H2 / CH_4)

Genera informes PDF con una estructura prefijada: encabezado, tabla + curva (gráfica), criterio explícito, y diagnóstico.

## Estructura
- `main.py`      menú de consola
- `datos.py`     carga (Excel/CSV/manual), validación, planilla modelo (openpyxl)
- `grafico.py`   gráfica (matplotlib)
- `pdf.py`       armado del PDF (ReportLab)
- `config.json`  centros, umbrales, profesional

## Funcionalidades

**Requeridas (inicialmente):**

1. Datos filiatorios ***Preguntar por algún otro dato*** []
2. Valores: [x] ***Completado***
    - *H2 (4 tipos según sustrato):*  glucosa, lactulosa, lactosa, fructosa
    - *CH_4* 
3. Diagnóstico [x] ***Completado***

**Opcionales (mejoran la prácticidad):**

- Intervalos de tiempo variables [x]    ***Completado***
- Escritura de diagnóstico práctica [x]
- Meter links de contacto (Ig, Mail, etc) [x] ***Completado***
- Guardar en el JSON los datos de las distintas "sedes" en las que trabaja (Poder elegir entre ellas automáticamente) [x] ***Parcialmente completo***

Para las "sedes", guardar por ID en el JSON, por si en algún momento hay muchas sedes, acceder directamente a cfg["sede"]["id"]

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

