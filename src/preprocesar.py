"""Limpieza por etapas; conserva IDs y etiquetas sin entrenar modelos."""
from pathlib import Path
import argparse,html,json,re,unicodedata,hashlib
import emoji
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
RECURSO=ROOT/'data/resources/stopwords_english.txt'
NEGACIONES={'no','not','nor','never'}

def cargar_stopwords(conservar_negaciones=True):
    palabras=set(RECURSO.read_text(encoding='utf-8').splitlines())
    return palabras-NEGACIONES if conservar_negaciones else palabras

def limpiar_texto(texto,stopwords):
    """Devuelve cada etapa; solo retiene letras Unicode (incluye tildes y ñ)."""
    original='' if pd.isna(texto) else str(texto)
    sin_html=re.sub(r'<[^>]*>',' ',html.unescape(original))
    minusculas=unicodedata.normalize('NFKC',sin_html).lower().replace('’',"'")
    encontrados=[x['emoji'] for x in emoji.emoji_list(minusculas)]
    sin_emojis=emoji.replace_emoji(minusculas,replace=' ')
    sin_enlaces=re.sub(r'https?://\S+|www\.\S+|\b[\w.+-]+@[\w.-]+\.[a-z]+\b',' ',sin_emojis)
    # Expandir negaciones ANTES de quitar el apóstrofo.
    expandido=re.sub(r"\bcan't\b",'can not',sin_enlaces)
    expandido=re.sub(r"\bwon't\b",'will not',expandido)
    expandido=re.sub(r"\bain't\b",'not',expandido)
    expandido=re.sub(r"n't\b",' not',expandido)
    solo_letras=''.join(c if c.isalpha() or c.isspace() else ' ' for c in expandido)
    sin_especiales=' '.join(solo_letras.split())
    tokens=sin_especiales.split()
    quitadas=[p for p in tokens if p in stopwords]
    filtrados=[p for p in tokens if p not in stopwords]
    return {'texto_original':original,'texto_minusculas':minusculas,'emojis_eliminados':encontrados,'texto_sin_emojis':sin_emojis,'texto_sin_especiales':sin_especiales,'tokens_antes':tokens,'stopwords_eliminadas':quitadas,'tokens':filtrados,'texto_limpio':' '.join(filtrados)}

def preprocesar(origen=ROOT/'data/raw/dataset.csv',destino=ROOT/'data/processed/dataset_limpio.csv',conservar_negaciones=True):
    df=pd.read_csv(origen,dtype={'id':'string','text':'string','label_text':'string'},keep_default_na=False)
    if not {'id','text','label','label_text'}.issubset(df):raise ValueError('Faltan columnas de la API.')
    if df.id.eq('').any() or df.id.duplicated().any():raise ValueError('IDs ausentes o repetidos: revisar la descarga antes de continuar.')
    if not df.label.isin([0,1,2,3,4]).all():raise ValueError('Etiquetas fuera del rango documentado por la API (0 a 4).')
    # El recurso de stopwords es inglés. No aplicar silenciosamente a otros idiomas.
    if not df.id.str.startswith('en_').all():raise ValueError('Hay IDs fuera del corpus inglés; revisar idioma y stopwords.')
    stopwords=cargar_stopwords(conservar_negaciones)
    salida=[];ejemplos=[]
    for i,fila in enumerate(df.itertuples(index=False)):
        etapas=limpiar_texto(fila.text,stopwords)
        salida.append({'id':fila.id,'label':fila.label,'label_text':fila.label_text,'texto_limpio':etapas['texto_limpio'],'tokens':json.dumps(etapas['tokens'],ensure_ascii=False),'cantidad_tokens':len(etapas['tokens']),'texto_vacio':not bool(etapas['texto_limpio'])})
        if i<100:
            ejemplos.append({'id':fila.id,**{k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in etapas.items()}})
        if (i+1)%25000==0:print(f'Procesadas {i+1:,} reseñas.',flush=True)
    limpio=pd.DataFrame(salida);destino=Path(destino);destino.parent.mkdir(parents=True,exist_ok=True)
    temporal=destino.with_suffix('.csv.part');limpio.to_csv(temporal,index=False,encoding='utf-8');temporal.replace(destino)
    pd.DataFrame(ejemplos).to_csv(destino.parent/'ejemplos_paso_a_paso.csv',index=False,encoding='utf-8-sig')
    # Control de datos, no métricas de modelos. Se conservan incluso los textos vacíos.
    registro={'filas_entrada':len(df),'filas_salida':len(limpio),'ids_unicos':int(limpio.id.nunique()),'textos_originales_vacios':int(df.text.str.strip().eq('').sum()),'textos_limpios_vacios':int(limpio.texto_vacio.sum()),'textos_originales_repetidos':int(df.text.duplicated().sum()),'textos_limpios_repetidos':int(limpio.texto_limpio.duplicated().sum()),'etiquetas_originales_conservadas':bool(df.label.equals(limpio.label)),'stopwords_aplicadas':len(stopwords),'conservar_negaciones':conservar_negaciones,'emoji_version':emoji.__version__,'sha256_origen':hashlib.file_digest(Path(origen).open('rb'),'sha256').hexdigest(),'sha256_limpio':hashlib.file_digest(destino.open('rb'),'sha256').hexdigest()}
    (destino.parent/'control_preprocesamiento.json').write_text(json.dumps(registro,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(registro,indent=2,ensure_ascii=False));return limpio

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Limpiar reseñas sin modificar las etiquetas.')
    parser.add_argument('--quitar-negaciones',action='store_true',help='También elimina las negaciones incluidas en las stopwords NLTK. Puede cambiar el sentido.')
    args=parser.parse_args();preprocesar(conservar_negaciones=not args.quitar_negaciones)
