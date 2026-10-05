# Taller II — Parte 1: API y preprocesamiento de reseñas

**UNSTA · Ingeniería en Inteligencia Artificial**

Primera entrega: obtener reseñas desde la API indicada, organizarlas en columnas de un CSV y limpiar el texto. Incluye los archivos generados y el código para repetir el proceso. Los modelos, vectorizaciones y métricas de clasificación corresponden a una etapa posterior.

## Fuente y alcance

API: https://amazon-reviews-api-g5ae.onrender.com/reviews

Se descargan **todas las reseñas disponibles**, paginando de a 1.000 con `limit` y `offset`, como en el código de referencia. La captura incluida contiene **210.000 reseñas en inglés**. No se usa una muestra para el dataset principal.

El PDF general menciona Trustpilot; para esta primera parte se usa la API de Amazon indicada posteriormente en la actividad. Este proyecto consume esa API; no crea una nueva API.

## Archivos de la entrega

| Archivo | Contenido |
|---|---|
| `data/raw/dataset.csv` | Todas las reseñas originales en cuatro columnas |
| `data/processed/dataset_limpio.csv` | Dataset completo luego de la limpieza y tokenización |
| `data/processed/ejemplos_paso_a_paso.csv` | Primeras 100 reseñas con cada transformación en una columna |
| `data/raw/origen.json` | URL, fecha de descarga, filas y hash del CSV |
| `data/processed/control_preprocesamiento.json` | Control de filas, etiquetas y textos vacíos/repetidos |
| `data/resources/stopwords_english.txt` | Lista local de stopwords inglesas de NLTK |
| `src/descargar.py` | Obtención desde la API y exportación a CSV |
| `src/preprocesar.py` | Funciones de limpieza y tokenización |
| `main.py` | Ejecución de ambos pasos |

Los controles de cantidad de filas sirven para comprobar que no se perdieron reseñas ni se alteraron las etiquetas; no son métricas de modelos.

## Columnas del CSV original

| Columna | Significado |
|---|---|
| `id` | Identificador original de la reseña |
| `text` | Texto original, sin modificaciones |
| `label` | Etiqueta numérica original (0–4) |
| `label_text` | Representación textual de la etiqueta entregada por la API |

Se conservan exactamente las etiquetas 0–4: no se convierten a estrellas 1–5 ni a positivo/negativo.

## Preprocesamiento

1. Manejo de valores nulos y eliminación de etiquetas HTML.
2. Normalización Unicode y conversión a minúsculas.
3. Identificación y eliminación de emojis, incluidos emojis compuestos.
4. Eliminación de enlaces y correos electrónicos.
5. Expansión de negaciones inglesas: `don't` → `do not`, `can't` → `can not`.
6. Eliminación de puntuación, números y otros caracteres especiales. Se conservan letras Unicode, incluidas tildes y ñ.
7. Eliminación de espacios repetidos y separación en palabras (**tokenización**).
8. Eliminación de **stopwords**, palabras frecuentes como `the`, `and`, `is`.
9. Unión de las palabras restantes para obtener el texto limpio y exportación a CSV.

No se aplica lematización ni stemming en esta parte.

Se conservan `no`, `not`, `nor` y `never`: eliminar `not` haría que `not good` y `good` quedaran iguales. Si el docente pide aplicar la lista estándar completa, ejecutar:

```bash
python -m src.preprocesar --quitar-negaciones
```

Quitar emojis, números y símbolos puede perder información del sentimiento o del producto; se realiza porque forma parte de la limpieza solicitada. El texto original siempre permanece disponible.

## Columnas del CSV procesado

| Columna | Significado |
|---|---|
| `id` | Permite relacionar la fila con su texto original |
| `label`, `label_text` | Etiquetas originales sin cambios |
| `texto_limpio` | Texto final sin emojis, caracteres especiales ni stopwords, salvo negaciones preservadas |
| `tokens` | Lista final de palabras, como arreglo JSON dentro de una celda |
| `cantidad_tokens` | Cantidad de palabras finales |
| `texto_vacio` | Indica si la reseña quedó vacía después de limpiar |

Se mantiene una fila por ID original, incluso si queda vacía. Ante IDs ausentes o repetidos se detiene la ejecución para revisar la descarga. Textos iguales con IDs diferentes se conservan y se cuentan: no se eliminan datos silenciosamente.

`ejemplos_paso_a_paso.csv` incluye columnas de original, minúsculas, emojis eliminados, texto sin emojis, texto sin caracteres especiales, tokens antes de filtrar, stopwords eliminadas, tokens finales y texto limpio. **Son 100 ejemplos para inspeccionar, no el dataset principal.**

Ejemplos ilustrativos:

| Original | Texto limpio |
|---|---|
| `The product is GREAT!!! 😍 100%` | `product great` |
| `I don't like it!` | `not like` |

## Ejecución

Python 3.12 recomendado. Abrir la terminal dentro de esta carpeta:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

Para limpiar el CSV incluido sin descargarlo otra vez:

```bash
python main.py --solo-preprocesar
```

En Windows también se puede abrir `INICIAR_WINDOWS.bat`, que instala las dependencias y ejecuta ese paso.

Para descargar desde cero y limpiar todo:

```bash
python main.py
```

O por separado:

```bash
python -m src.descargar --tamanio 1000
python -m src.preprocesar
```

La descarga puede demorar mientras se activa el servidor. El programa usa tiempos máximos, reintentos limitados, validación de cada página y un archivo temporal. Solo reemplaza el CSV original al completar la descarga. Si hay un error, lo informa y se detiene; no entra en un bucle infinito. Una nueva ejecución reinicia la descarga.

CSV con separador coma, UTF-8 y `index=False` (sin índice extra de pandas). Si Excel lo muestra en una sola columna: **Datos → Desde texto/CSV → UTF-8 → separador coma**. Los tokens son una celda JSON, no una columna por palabra. No dividir filas manualmente por comas: las reseñas pueden contener comas y el CSV las protege con comillas.

## Verificación

```bash
python -m unittest discover -s tests -v
```

Se comprueban emojis, HTML, enlaces, negaciones, valores nulos y protección contra páginas inconsistentes. Los archivos de control también verifican IDs, etiquetas y cantidades sobre los CSV completos.

## Repositorio y entrega

Nombre sugerido: `taller2-preprocesamiento-resenas`.

Subir esta carpeta sin `.venv`, temporales ni credenciales. Los CSV completos son grandes: utilizar Git o GitHub Desktop para subirlos, en lugar del cargador web para archivos grandes. Compartir el enlace al repositorio y comprobar que el docente tenga acceso.

Este README explica cómo reproducir la primera entrega. El informe integrador se prepara por separado en la etapa correspondiente.
