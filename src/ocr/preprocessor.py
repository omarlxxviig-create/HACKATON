"""
PREPROCESADOR DE DOCUMENTOS

Este archivo contiene herramientas para mejorar la calidad de las imágenes
antes de extraer texto de ellas.

Mejoras que realiza:
1. Convierte documentos PDF a imágenes usando PyMuPDF
2. Mejora el contraste y nitidez
3. Elimina el "ruido" (manchas, puntos) de la imagen
"""

import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from loguru import logger

class DocumentPreprocessor:
    """
    Clase para preparar documentos e imágenes para el OCR.
    """
    
    def __init__(self):
        self.logger = logger.bind(name="DocumentPreprocessor")
        self.logger.info("Inicializando preprocesador de documentos")
    
    def preprocess_image(self, image):
        """
        Mejora la calidad de una imagen para OCR.
        
        Pasos:
        1. Convierte a escala de grises
        2. Mejora el contraste
        3. Elimina ruido
        
        Args:
            image: Imagen a mejorar (PIL Image o numpy array)
            
        Returns:
            Imagen mejorada lista para OCR
        """
        self.logger.debug("Preprocesando imagen")
        
        # Convertir a numpy array si es necesario
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        
        # Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Mejorar contraste con CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Eliminar ruido
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        return denoised
    
    def pdf_to_images(self, pdf_path=None, pdf_bytes=None):
        """
        Convierte un PDF en lista de imágenes usando PyMuPDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            pdf_bytes: Contenido del PDF en bytes
            
        Returns:
            Lista de imágenes PIL (una por página)
        """
        try:
            # Abrir PDF
            if pdf_path:
                self.logger.info(f"Convirtiendo PDF: {pdf_path}")
                import os
                
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
                
                if os.path.getsize(pdf_path) == 0:
                    raise ValueError("El archivo PDF está vacío")
                
                pdf_document = fitz.open(pdf_path)
                
            elif pdf_bytes:
                self.logger.info("Convirtiendo PDF desde bytes")
                
                if not pdf_bytes or len(pdf_bytes) == 0:
                    raise ValueError("Los bytes del PDF están vacíos")
                
                pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            else:
                raise ValueError("Debe proporcionar pdf_path o pdf_bytes")
            
            num_pages = len(pdf_document)
            if num_pages == 0:
                raise ValueError("El PDF no tiene páginas")
            
            self.logger.info(f"Procesando {num_pages} páginas")
            
            # Convertir cada página
            images = []
            for page_num in range(num_pages):
                try:
                    page = pdf_document[page_num]
                    
                    # Zoom 2x para mejor calidad (aprox 144 DPI)
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convertir a PIL Image
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    images.append(img)
                    
                except Exception as e:
                    self.logger.error(f"Error en página {page_num + 1}: {str(e)}")
                    continue
            
            pdf_document.close()
            
            if not images:
                raise ValueError("No se pudo convertir ninguna página")
            
            self.logger.info(f"Convertidas {len(images)} páginas exitosamente")
            return images
                
        except Exception as e:
            self.logger.error(f"Error al convertir PDF: {str(e)}")
            raise
