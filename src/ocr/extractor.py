"""
EXTRACTOR DE TEXTO

Este archivo contiene las herramientas para extraer texto de imágenes y PDFs
usando reconocimiento óptico de caracteres (OCR).
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import config
from .preprocessor import DocumentPreprocessor

# Configurar Tesseract
if config.TESSERACT_PATH and config.TESSERACT_PATH != "tesseract":
    if os.path.exists(config.TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    else:
        print(f"ADVERTENCIA: Tesseract no encontrado en {config.TESSERACT_PATH}")

# Inicializar preprocessor
preprocessor = DocumentPreprocessor()

def calcular_confianza_texto(texto):
    """
    Calcula un porcentaje de confianza basado en la calidad del texto extraído.
    
    Args:
        texto: Texto extraído por OCR
        
    Returns:
        Porcentaje de confianza (0-100)
    """
    if not texto or len(texto.strip()) == 0:
        return 0.0
    
    texto_limpio = texto.strip()
    total_chars = len(texto_limpio)
    
    # Contar caracteres alfabéticos y numéricos (contenido válido)
    chars_validos = sum(1 for c in texto_limpio if c.isalnum() or c.isspace())
    
    # Contar palabras reconocibles (más de 2 caracteres)
    palabras = texto_limpio.split()
    palabras_validas = sum(1 for p in palabras if len(p) > 2 and any(c.isalpha() for c in p))
    
    # Contar caracteres extraños o de error (?, �, etc.)
    chars_error = sum(1 for c in texto_limpio if c in ['�', '□', '▪'])
    
    # Calcular porcentaje base de caracteres válidos
    porcentaje_chars = (chars_validos / total_chars) * 100 if total_chars > 0 else 0
    
    # Bonus si hay palabras válidas
    bonus_palabras = min(20, (palabras_validas / max(1, len(palabras))) * 20)
    
    # Penalización por caracteres de error
    penalizacion = (chars_error / total_chars) * 30 if total_chars > 0 else 0
    
    # Calcular confianza final
    confianza = porcentaje_chars + bonus_palabras - penalizacion
    
    # Limitar entre 0 y 100
    return max(0.0, min(100.0, confianza))

def extraer_texto_imagen(imagen, preprocesar=True):
    """
    Extrae texto de una imagen usando Tesseract.
    
    Args:
        imagen: Imagen a procesar (PIL Image o numpy array)
        preprocesar: Si True, mejora la imagen antes de extraer texto
    
    Returns:
        Tupla (texto_extraído, confianza_porcentaje)
    """
    try:
        # Preprocesar imagen si está habilitado
        if preprocesar:
            imagen = preprocessor.preprocess_image(imagen)
        
        # Convertir a PIL Image si es necesario
        if isinstance(imagen, np.ndarray):
            # Si ya está en escala de grises (del preprocesamiento)
            if len(imagen.shape) == 2:
                imagen = Image.fromarray(imagen)
            else:
                imagen = Image.fromarray(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
        
        texto = pytesseract.image_to_string(imagen, lang='spa+eng').strip()
        confianza = calcular_confianza_texto(texto)
        
        return texto, confianza
    
    except pytesseract.TesseractNotFoundError:
        raise Exception(
            "Tesseract no está instalado. "
            "Descárgalo de: https://github.com/UB-Mannheim/tesseract/wiki "
            "y configura la ruta en el archivo .env"
        )

def extraer_texto_pdf(ruta_pdf, preprocesar=True):
    """
    Extrae texto de un PDF usando el preprocessor para convertir a imágenes.
    
    Args:
        ruta_pdf: Ruta al archivo PDF
        preprocesar: Si True, mejora las imágenes antes de extraer texto
    
    Returns:
        Tupla (texto_extraído, confianza_promedio)
    """
    try:
        # Usar el preprocessor para convertir PDF a imágenes
        imagenes = preprocessor.pdf_to_images(pdf_path=ruta_pdf)
        
        textos = []
        confianzas = []
        
        for img in imagenes:
            texto, confianza = extraer_texto_imagen(img, preprocesar=preprocesar)
            textos.append(texto)
            confianzas.append(confianza)
        
        # Calcular confianza promedio de todas las páginas
        confianza_promedio = sum(confianzas) / len(confianzas) if confianzas else 0.0
        
        return "\n\n".join(textos), confianza_promedio
    
    except Exception as e:
        raise Exception(f"Error al procesar PDF: {str(e)}")
