"""
Script de prueba para el módulo OCR

Este archivo te permite probar rápidamente la funcionalidad de OCR
sin tener que iniciar toda la API.
"""

import cv2
from src.ocr.extractor import TextExtractor
from loguru import logger
import sys

def main():
    """Función principal para probar el OCR"""
    logger.info("Iniciando prueba de OCR")
    
    # Verificar que se proporcionó una imagen
    if len(sys.argv) < 2:
        logger.error("Uso: python test_ocr.py <ruta_a_imagen_o_pdf>")
        return 1
    
    archivo = sys.argv[1]
    logger.info(f"Procesando archivo: {archivo}")
    
    # Crear extractor
    extractor = TextExtractor()
    
    # Determinar si es PDF o imagen
    if archivo.lower().endswith('.pdf'):
        logger.info("Detectado como PDF")
        textos = extractor.extract_from_pdf(pdf_path=archivo)
        
        for i, texto in enumerate(textos):
            logger.info(f"\n--- Página {i+1} ---")
            print(texto)
            print("\n" + "="*50 + "\n")
    else:
        logger.info("Detectado como imagen")
        imagen = cv2.imread(archivo)
        
        if imagen is None:
            logger.error("No se pudo cargar la imagen")
            return 1
        
        texto = extractor.extract_from_image(imagen)
        logger.info("\n--- Texto Extraído ---")
        print(texto)
    
    logger.info("Prueba completada")
    return 0

if __name__ == "__main__":
    exit(main())
