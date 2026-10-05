import unittest
from src.preprocesar import limpiar_texto,cargar_stopwords
from src.descargar import validar_pagina
class PreprocesamientoTests(unittest.TestCase):
    def test_limpieza(self):
        r=limpiar_texto('The product is GREAT!!! 😍 100% https://example.com',cargar_stopwords())
        self.assertEqual(r['texto_limpio'],'product great')
        self.assertEqual(r['emojis_eliminados'],['😍'])
        self.assertIn('the',r['stopwords_eliminadas'])
    def test_negacion(self):
        r=limpiar_texto("I don't like it!",cargar_stopwords())
        self.assertEqual(r['texto_limpio'],'not like')
    def test_unicode(self):
        r=limpiar_texto('CAFÉ, niño 👨‍👩‍👧‍👦',set())
        self.assertEqual(r['texto_limpio'],'café niño')
    def test_nulo(self):
        self.assertEqual(limpiar_texto(None,set())['texto_limpio'],'')
    def test_html_y_correo(self):
        self.assertEqual(limpiar_texto('<b>Great</b> &amp; nice! mail@test.com',set())['texto_limpio'],'great nice')
    def test_pagina_vacia_no_final(self):
        with self.assertRaises(ValueError):validar_pagina({'data':[],'returned':0,'offset':0,'total_matching':20},0)
    def test_cantidad_inconsistente(self):
        with self.assertRaises(ValueError):validar_pagina({'data':[],'returned':1,'offset':0,'total_matching':20},0)
if __name__=='__main__':unittest.main()
