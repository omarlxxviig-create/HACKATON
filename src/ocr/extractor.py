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
from loguru import logger

from .preprocessor import DocumentPreprocessor
import config

class TextExtractor:
    """
    Clase principal para extraer texto de imágenes y PDFs.
    
    Esta clase usa la herramienta Tesseract OCR para "leer" el texto
    en imágenes, y también puede procesar PDFs convirtiéndolos primero
    a imágenes.
    """
    
    def __init__(self, tesseract_path=None, languages=None):
        """
        Inicializa el extractor de texto.
        
        Args:
            tesseract_path: Ubicación del programa Tesseract OCR
            languages: Idiomas que puede reconocer (ej: ["eng", "spa"])
        """
        self.logger = logger.bind(name="TextExtractor")
        self.preprocessor = DocumentPreprocessor()
        
        # Configurar tesseract (programa que hace el OCR)
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif hasattr(config, 'TESSERACT_PATH'):
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
            
        self.languages = languages if languages else config.OCR_LANGUAGES
        self.logger.info(f"Inicializando extractor de texto con idiomas: {self.languages}")
    
    def extract_from_image(self, image, preprocess=True):
        """
        Extrae texto de una imagen.
        
        Es como "leer" lo que hay escrito en una fotografía o un escaneo.
        
        Args:
            image: La imagen de la que extraer texto
            preprocess: Si se debe mejorar la imagen antes
            
        Returns:
            El texto extraído de la imagen
        """
        try:
            # Preprocesar la imagen si se solicita
            if preprocess:
                if isinstance(image, np.ndarray):
                    # Es una imagen OpenCV
                    img_for_ocr = self.preprocessor.preprocess_image(image)
                else:
                    # Es una imagen PIL
                    img_np = np.array(image)
                    img_processed = self.preprocessor.preprocess_image(img_np)
                    img_for_ocr = Image.fromarray(img_processed)
            else:
                img_for_ocr = image
            
            # Ejecutar OCR (reconocimiento de texto)
            self.logger.debug("Ejecutando OCR en imagen")
            text = pytesseract.image_to_string(
                img_for_ocr, 
                lang='+'.join(self.languages)
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error en OCR: {str(e)}")
            raise
    
    def extract_from_pdf(self, pdf_path=None, pdf_bytes=None):
        """
        Extrae texto de un documento PDF.
        
        Funciona convirtiendo cada página del PDF a imagen y luego
        extrayendo el texto de cada imagen.
        
        Args:
            pdf_path: Ruta al archivo PDF
            pdf_bytes: Contenido del PDF en memoria
            
        Returns:
            Lista de textos, uno por cada página del PDF
        """
        try:
            # Convertir PDF a imágenes
            images = self.preprocessor.pdf_to_images(pdf_path, pdf_bytes)
            
            # Extraer texto de cada página
            results = []
            for i, img in enumerate(images):
                self.logger.info(f"Procesando página {i+1}")
                text = self.extract_from_image(img)
                results.append(text)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error al extraer texto de PDF: {str(e)}")
            raise
    
    def get_text_with_coordinates(self, image):
        """
        Extrae texto junto con su ubicación en la imagen.
        
        Además de "leer" el texto, también indica dónde está cada texto
        en la imagen (coordenadas x, y, ancho y alto).
        
        Args:
            image: La imagen de la que extraer texto
            
        Returns:
            Lista de textos encontrados con sus coordenadas
        """
        try:
            # Preprocesar imagen
            if isinstance(image, np.ndarray):
                img_for_ocr = self.preprocessor.preprocess_image(image)
            else:
                img_np = np.array(image)
                img_processed = self.preprocessor.preprocess_image(img_np)
                img_for_ocr = Image.fromarray(img_processed)
            
            # Usar pytesseract para obtener datos
            data = pytesseract.image_to_data(
                img_for_ocr,
                lang='+'.join(self.languages),
                output_type=pytesseract.Output.DICT
            )
            
            # Estructurar resultados
            result = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    result.append({
                        'text': data['text'][i],               # El texto encontrado
                        'confidence': data['conf'][i],         # Confianza (0-100)
                        'x': data['left'][i],                  # Posición X
                        'y': data['top'][i],                   # Posición Y
                        'width': data['width'][i],             # Ancho
                        'height': data['height'][i],           # Alto
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al extraer texto con coordenadas: {str(e)}")
            raise
