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
import re

from .preprocessor import DocumentPreprocessor
from .corrector import TextCorrector
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
        
        # Inicializar corrector de texto
        lang_for_corrector = 'es' if 'spa' in self.languages else 'en'
        self.corrector = TextCorrector(language=lang_for_corrector)
        
        self.logger.info(f"Inicializando extractor de texto con idiomas: {self.languages}")
    
    def extract_from_image(self, image, preprocess=True, use_advanced=True):
        """
        Extrae texto de una imagen con máxima precisión.
        
        Es como "leer" lo que hay escrito en una fotografía o un escaneo.
        
        Args:
            image: La imagen de la que extraer texto
            preprocess: Si se debe mejorar la imagen antes
            use_advanced: Si se usa preprocesamiento avanzado (mayor precisión)
            
        Returns:
            El texto extraído de la imagen
        """
        try:
            # Preprocesar la imagen si se solicita
            if preprocess:
                if isinstance(image, np.ndarray):
                    # Es una imagen OpenCV
                    if use_advanced:
                        img_for_ocr = self.preprocessor.advanced_preprocess(image)
                    else:
                        img_for_ocr = self.preprocessor.preprocess_image(image)
                else:
                    # Es una imagen PIL
                    img_np = np.array(image)
                    if use_advanced:
                        img_processed = self.preprocessor.advanced_preprocess(img_np)
                    else:
                        img_processed = self.preprocessor.preprocess_image(img_np)
                    img_for_ocr = Image.fromarray(img_processed)
            else:
                img_for_ocr = image
            
            # CRÍTICO: Configuración optimizada de Tesseract
            # --oem 3: Usa LSTM (red neuronal, más precisa)
            # --psm 6: Asume bloque uniforme de texto
            # tessedit_char_whitelist: Lista de caracteres permitidos
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789áéíóúñÁÉÍÓÚÑüÜ.,;:()[]{}¿?¡!@#$%&*/\-_+="\' '
            
            # Ejecutar OCR (reconocimiento de texto)
            self.logger.debug("Ejecutando OCR en imagen con configuración optimizada")
            text = pytesseract.image_to_string(
                img_for_ocr, 
                lang='+'.join(self.languages),
                config=custom_config
            )
            
            # NUEVO: Post-procesamiento con corrección
            corrected_text = self.post_process_text(text)
            
            return corrected_text
            
        except Exception as e:
            self.logger.error(f"Error en OCR: {str(e)}")
            raise
    
    def post_process_text(self, text):
        """
        NUEVO: Limpia y corrige el texto extraído por OCR.
        
        Elimina errores comunes y mejora la calidad del texto.
        
        Args:
            text: Texto crudo del OCR
            
        Returns:
            Texto limpio y corregido
        """
        self.logger.debug("Post-procesando texto extraído")
        
        # 1. Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # 2. Corregir espacios múltiples
        text = re.sub(r' +', ' ', text)
        
        # 3. Eliminar espacios antes de puntuación
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # 4. Corrección ortográfica y errores OCR
        text = self.corrector.correct_text(text)
        
        return text.strip()
    
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
                self.logger.info(f"Procesando página {i+1}/{len(images)}")
                text = self.extract_from_image(img, use_advanced=True)
                results.append(text)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error al extraer texto de PDF: {str(e)}")
            raise
    
    def get_text_with_coordinates(self, image, min_confidence=60):
        """
        Extrae texto junto con su ubicación en la imagen.
        
        Además de "leer" el texto, también indica dónde está cada texto
        en la imagen (coordenadas x, y, ancho y alto).
        
        Solo retorna texto con nivel de confianza >= min_confidence.
        
        Args:
            image: La imagen de la que extraer texto
            min_confidence: Confianza mínima (0-100) para incluir el texto
            
        Returns:
            Lista de textos encontrados con sus coordenadas
        """
        try:
            # Preprocesar imagen con método avanzado
            if isinstance(image, np.ndarray):
                img_for_ocr = self.preprocessor.advanced_preprocess(image)
            else:
                img_np = np.array(image)
                img_processed = self.preprocessor.advanced_preprocess(img_np)
                img_for_ocr = Image.fromarray(img_processed)
            
            # Configuración optimizada
            custom_config = r'--oem 3 --psm 6'
            
            # Usar pytesseract para obtener datos
            data = pytesseract.image_to_data(
                img_for_ocr,
                lang='+'.join(self.languages),
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Estructurar resultados filtrando por confianza
            result = []
            for i in range(len(data['text'])):
                # NUEVO: Filtrar por confianza mínima
                if data['text'][i].strip() and int(data['conf'][i]) >= min_confidence:
                    result.append({
                        'text': data['text'][i],               # El texto encontrado
                        'confidence': int(data['conf'][i]),    # Confianza (0-100)
                        'x': data['left'][i],                  # Posición X
                        'y': data['top'][i],                   # Posición Y
                        'width': data['width'][i],             # Ancho
                        'height': data['height'][i],           # Alto
                    })
            
            self.logger.info(f"Extraídos {len(result)} bloques de texto con confianza >= {min_confidence}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al extraer texto con coordenadas: {str(e)}")
            raise
    
    def extract_with_confidence(self, image):
        """
        NUEVO: Extrae texto completo e indica el nivel de confianza promedio.
        
        Args:
            image: Imagen de la que extraer texto
            
        Returns:
            Diccionario con texto y métricas de confianza
        """
        try:
            # Obtener texto con coordenadas y confianza
            text_data = self.get_text_with_coordinates(image, min_confidence=0)
            
            if not text_data:
                return {
                    'text': '',
                    'average_confidence': 0,
                    'word_count': 0
                }
            
            # Calcular confianza promedio
            confidences = [item['confidence'] for item in text_data]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Extraer texto completo
            full_text = ' '.join([item['text'] for item in text_data])
            full_text = self.post_process_text(full_text)
            
            return {
                'text': full_text,
                'average_confidence': round(avg_confidence, 2),
                'word_count': len(text_data),
                'low_confidence_words': len([c for c in confidences if c < 60])
            }
            
        except Exception as e:
            self.logger.error(f"Error extrayendo con confianza: {str(e)}")
            raise
