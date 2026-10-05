"""Ejecutar toda la primera entrega: python main.py"""
import argparse
from src.descargar import obtener_resenias
from src.preprocesar import preprocesar
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--solo-preprocesar',action='store_true',help='Usar el CSV original ya incluido.')
    args=parser.parse_args()
    if not args.solo_preprocesar:obtener_resenias(tamanio=1000)
    preprocesar()
