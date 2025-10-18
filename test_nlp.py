"""
Script de prueba para el módulo NLP

Este archivo te permite probar rápidamente la funcionalidad de NLP
sin tener que iniciar toda la API.
"""

from src.nlp.keyword_extraction import KeywordExtractor
from src.nlp.entity_extraction import EntityExtractor
from loguru import logger
import sys

def main():
    """Función principal para probar el NLP"""
    logger.info("Iniciando prueba de NLP")
    
    # Verificar que se proporcionó texto
    if len(sys.argv) < 2:
        logger.error("Uso: python test_nlp.py <texto_a_analizar>")
        logger.info("Ejemplo: python test_nlp.py \"Este es un texto de prueba sobre Madrid y Microsoft\"")
        return 1
    
    texto = " ".join(sys.argv[1:])
    logger.info(f"Analizando texto: {texto[:100]}...")
    
    # Crear extractores
    extractor_palabras = KeywordExtractor(language="es")
    extractor_entidades = EntityExtractor(language="spa")
    
    # Extraer palabras clave
    logger.info("\n--- Palabras Clave ---")
    palabras_clave = extractor_palabras.extract_keywords(texto, method="combined", top_n=10)
    for palabra, puntuacion in palabras_clave:
        print(f"  - {palabra}: {puntuacion:.4f}")
    
    # Extraer entidades
    logger.info("\n--- Entidades ---")
    entidades = extractor_entidades.extract_main_entities(texto)
    for categoria, items in entidades.items():
        if items:
            print(f"\n{categoria.upper()}:")
            for text, label in items:
                print(f"  - {text} ({label})")
    
    logger.info("\nPrueba completada")
    return 0

if __name__ == "__main__":
    exit(main())
