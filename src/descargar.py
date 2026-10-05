"""Descarga completa de la API. Uso: python -m src.descargar"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
URL='https://amazon-reviews-api-g5ae.onrender.com/reviews'
COLUMNAS=['id','text','label','label_text']

def crear_sesion():
    sesion=requests.Session()
    reintentos=Retry(total=4,backoff_factor=1,status_forcelist=[429,500,502,503,504],allowed_methods=['GET'],respect_retry_after_header=True)
    sesion.mount('https://',HTTPAdapter(max_retries=reintentos))
    return sesion

def validar_pagina(respuesta,offset):
    if not isinstance(respuesta,dict):raise ValueError('Respuesta JSON inesperada.')
    filas=respuesta.get('data')
    if not isinstance(filas,list):raise ValueError('La API no devolvió una lista en data.')
    cantidad=respuesta.get('returned');total=respuesta.get('total_matching')
    if type(cantidad) is not int or cantidad!=len(filas):raise ValueError('returned no coincide con la cantidad de reseñas.')
    if type(total) is not int or total<0:raise ValueError('total_matching inválido.')
    if respuesta.get('offset')!=offset:raise ValueError('La API devolvió otra página.')
    if not filas and offset<total:raise ValueError('Página vacía antes del final: se detiene para evitar un bucle infinito.')
    if offset+cantidad>total:raise ValueError('La página supera el total informado.')
    for fila in filas:
        if not isinstance(fila,dict) or not set(COLUMNAS).issubset(fila):raise ValueError('Faltan columnas en una reseña.')
    return filas,cantidad,total

def obtener_resenias(tamanio=1000,destino=ROOT/'data/raw/dataset.csv'):
    """Sin muestreo: descarga todo. El CSV final se publica solo al completar la descarga."""
    if not 1<=tamanio<=1000:raise ValueError('tamanio debe estar entre 1 y 1000.')
    destino=Path(destino);destino.parent.mkdir(parents=True,exist_ok=True)
    temporal=destino.with_suffix('.csv.part')
    inicio=datetime.now(timezone.utc).isoformat()
    with crear_sesion() as sesion:
        offset=0;total_inicial=None;primera=True
        while True:
            r=sesion.get(URL,params={'limit':tamanio,'offset':offset},timeout=(20,180))
            r.raise_for_status()
            filas,cantidad,total=validar_pagina(r.json(),offset)
            if total_inicial is None:total_inicial=total
            if total!=total_inicial:raise ValueError('El total cambió durante la descarga. Reintentar para obtener una captura consistente.')
            lote=pd.DataFrame(filas,columns=COLUMNAS)
            lote.to_csv(temporal,mode='w' if primera else 'a',header=primera,index=False,encoding='utf-8')
            primera=False;offset+=cantidad
            print(f'Descargadas {offset:,} de {total:,} reseñas.',flush=True)
            if offset>=total:break
    os.replace(temporal,destino)
    registro={'fuente':URL,'endpoint_descarga':URL,'metodo':'paginado','inicio_utc':inicio,'fin_utc':datetime.now(timezone.utc).isoformat(),'filas_descargadas':total,'tamanio_pagina':tamanio,'columnas':COLUMNAS,'sha256':hashlib.sha256(destino.read_bytes()).hexdigest()}
    (destino.parent/'origen.json').write_text(json.dumps(registro,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'CSV guardado en {destino} ({total:,} filas).')
    return destino

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Descargar reseñas de Amazon desde la API del curso.')
    parser.add_argument('--tamanio',type=int,default=1000)
    args=parser.parse_args();obtener_resenias(args.tamanio)
