# Stopwords

`stopwords_english.txt` es una copia de las 198 stopwords inglesas distribuidas por el corpus `stopwords` de NLTK, obtenida con NLTK 3.9.2. Se incluye para que la limpieza no necesite descargar recursos cada vez.

Fuente: https://www.nltk.org/nltk_data/ y https://github.com/nltk/nltk_data/tree/gh-pages/packages/corpora

El listado efectivo que aplica el programa conserva `no`, `not`, `nor` y `never` si aparecen en la lista, porque son importantes para el significado de una reseña. La opción `--quitar-negaciones` permite aplicar la lista estándar completa cuando lo solicite el docente.
