"""
EXTRACTOR DE TEXTO

Este archivo contiene las herramientas para extraer texto de imágenes y PDFs
usando reconocimiento óptico de caracteres (OCR).

Es como tener un asistente que "lee" los documentos y escribe el texto 
que encuentra en ellos, pero lo hace automáticamente.
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import fitz
import os
import config

# Configurar Tesseract
if config.TESSERACT_PATH and config.TESSERACT_PATH != "tesseract":
    if os.path.exists(config.TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    else:
        print(f"ADVERTENCIA: Tesseract no encontrado en {config.TESSERACT_PATH}")

def extraer_texto_imagen(imagen):
    """Extrae texto de una imagen usando Tesseract"""
    try:
        if isinstance(imagen, np.ndarray):
            imagen = Image.fromarray(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
        return pytesseract.image_to_string(imagen, lang='spa+eng').strip()
    except pytesseract.TesseractNotFoundError:
        raise Exception(
            "Tesseract no está instalado. "
            "Descárgalo de: https://github.com/UB-Mannheim/tesseract/wiki "
            "y configura la ruta en el archivo .env"
        )

def extraer_texto_pdf(ruta_pdf):
    """Extrae texto de un PDF convirtiéndolo a imágenes"""
    try:
        documento = fitz.open(ruta_pdf)
        textos = []
        
        for pagina_num in range(len(documento)):
            pagina = documento[pagina_num]
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            texto = extraer_texto_imagen(img)
            textos.append(texto)
        
        documento.close()
        return "\n\n".join(textos)
    
    except Exception as e:
        raise Exception(f"Error al procesar PDF: {str(e)}")
