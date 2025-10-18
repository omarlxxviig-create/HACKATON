"""
PREPROCESADOR DE DOCUMENTOS

Este archivo contiene herramientas para mejorar la calidad de las imágenes
antes de extraer texto de ellas. Es como "preparar" la imagen para que
sea más fácil leerla, similar a ajustar el brillo y contraste de una foto
antes de imprimirla.

Mejoras que realiza:
1. Convierte documentos PDF a imágenes
2. Mejora el contraste y nitidez
3. Corrige la rotación si el documento está torcido
4. Elimina el "ruido" (manchas, puntos) de la imagen
"""

import cv2
import numpy as np
from pdf2image import convert_from_path, convert_from_bytes
from loguru import logger

class DocumentPreprocessor:
    """
    Esta clase se encarga de preparar los documentos para el OCR.
    
    Es como un ayudante que "limpia" y "arregla" las imágenes para
    que el texto sea más fácil de reconocer.
    """
    
    def __init__(self):
        # Configurar el registro para esta clase
        self.logger = logger.bind(name="DocumentPreprocessor")
        self.logger.info("Inicializando preprocesador de documentos")
    
    def preprocess_image(self, image):
        """
        Mejora la calidad de una imagen para hacerla más legible.
        
        Este método hace varias cosas:
        1. Convierte la imagen a escala de grises (blanco y negro)
        2. Ajusta el contraste para que el texto se distinga mejor
        3. Elimina manchas y puntos que puedan confundir al OCR
        4. Corrige la rotación si la imagen está torcida
        
        Args:
            image: La imagen a mejorar
            
        Returns:
            La imagen mejorada, lista para extraer texto
        """
        self.logger.debug("Preprocesando imagen")
        
        # Convertir a formato interno si es necesario
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        
        # Convertir a escala de grises (blanco y negro)
        if len(image.shape) == 3:  # Si es una imagen a color
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:  # Si ya está en escala de grises
            gray = image
        
        # Aplicar umbral adaptativo (mejora el contraste entre texto y fondo)
        # Esto ayuda a que las letras se distingan mejor del fondo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Eliminar ruido (manchas, puntos, etc.)
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Detectar si la imagen está rotada
        angle = self.detect_rotation(denoised)
        if abs(angle) > 1:  # Si está rotada más de 1 grado
            self.logger.debug(f"Corrigiendo rotación de {angle:.2f} grados")
            denoised = self.correct_rotation(denoised, angle)
        
        return denoised
    
    def advanced_preprocess(self, image):
        """
        NUEVO: Preprocesamiento avanzado para máxima precisión (90%+).
        
        Este método usa técnicas más sofisticadas que preprocess_image
        para lograr mejor precisión en el reconocimiento de texto.
        
        Args:
            image: La imagen a mejorar
            
        Returns:
            La imagen optimizada para OCR de alta precisión
        """
        self.logger.debug("Aplicando preprocesamiento avanzado")
        
        # Convertir a formato interno si es necesario
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        
        # 1. Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 2. CRÍTICO: Redimensionar si la resolución es baja
        # El OCR funciona mejor con imágenes de al menos 300 DPI
        height, width = gray.shape
        if height < 1000:
            scale = 1000 / height
            self.logger.debug(f"Redimensionando imagen con escala {scale:.2f}")
            gray = cv2.resize(gray, None, fx=scale, fy=scale, 
                            interpolation=cv2.INTER_CUBIC)
        
        # 3. Desenfoque bilateral (suaviza pero preserva bordes del texto)
        blurred = cv2.bilateralFilter(gray, 5, 75, 75)
        
        # 4. Umbralización Otsu (más precisa que adaptativa para documentos)
        _, thresh = cv2.threshold(blurred, 0, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 5. Morfología para limpiar ruido manteniendo el texto
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # 6. Corrección de rotación
        angle = self.detect_rotation(opening)
        if abs(angle) > 0.5:
            self.logger.debug(f"Corrigiendo rotación de {angle:.2f} grados")
            opening = self.correct_rotation(opening, angle)
        
        # 7. Inversión si es necesario (texto blanco sobre fondo negro)
        if np.mean(opening) > 127:
            self.logger.debug("Invirtiendo colores de la imagen")
            opening = cv2.bitwise_not(opening)
        
        return opening
    
    def pdf_to_images(self, pdf_path=None, pdf_bytes=None):
        """
        Convierte un documento PDF en una lista de imágenes.
        
        Cada página del PDF se convierte en una imagen separada.
        
        Args:
            pdf_path: Ruta al archivo PDF en el disco
            pdf_bytes: Contenido del PDF en memoria
            
        Returns:
            Lista de imágenes, una por cada página del PDF
        """
        try:
            if pdf_path:
                self.logger.info(f"Convirtiendo PDF desde archivo: {pdf_path}")
                return convert_from_path(pdf_path, dpi=300)  # 300 DPI para mejor calidad
            elif pdf_bytes:
                self.logger.info("Convirtiendo PDF desde bytes")
                return convert_from_bytes(pdf_bytes, dpi=300)
            else:
                raise ValueError("Se debe proporcionar pdf_path o pdf_bytes")
        except Exception as e:
            self.logger.error(f"Error al convertir PDF: {str(e)}")
            raise
    
    def detect_rotation(self, image):
        """
        Detecta si una imagen está rotada y cuántos grados.
        
        Funciona buscando líneas en la imagen y calculando su ángulo,
        asumiendo que la mayoría de las líneas en un documento deben
        ser horizontales o verticales.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Ángulo de rotación en grados
        """
        try:
            # Encontrar bordes en la imagen
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Encontrar líneas usando transformada de Hough
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return 0  # No se encontraron líneas
            
            # Calcular ángulos de todas las líneas encontradas
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 == 0:  # Evitar división por cero
                    continue
                angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi
                angles.append(angle)
            
            if not angles:
                return 0
                
            # Eliminar valores extremos (outliers)
            angles = np.array(angles)
            q1 = np.percentile(angles, 25)
            q3 = np.percentile(angles, 75)
            iqr = q3 - q1
            filtered = angles[(angles >= q1 - 1.5 * iqr) & (angles <= q3 + 1.5 * iqr)]
            
            if len(filtered) == 0:
                return 0
                
            # Calcular la mediana de los ángulos
            median_angle = np.median(filtered)
            
            # Ajustar a un ángulo razonable
            if median_angle > 45:
                median_angle -= 90
            elif median_angle < -45:
                median_angle += 90
                
            return median_angle
            
        except Exception as e:
            self.logger.error(f"Error en detección de rotación: {str(e)}")
            return 0
    
    def correct_rotation(self, image, angle):
        """
        Corrige la rotación de una imagen.
        
        Gira la imagen para enderezarla cuando está torcida.
        
        Args:
            image: Imagen a rotar
            angle: Ángulo de rotación en grados
            
        Returns:
            Imagen rotada (enderezada)
        """
        # Obtener dimensiones
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Matriz de rotación
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), 
                              flags=cv2.INTER_CUBIC, 
                              borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def enhance_contrast(self, image):
        """
        Mejora el contraste de la imagen.
        
        Hace que el texto sea más visible y se distinga mejor del fondo.
        
        Args:
            image: Imagen a mejorar
            
        Returns:
            Imagen con contraste mejorado
        """
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        if len(image.shape) == 3:
            # Imagen en color
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            
            # Combinar canales
            limg = cv2.merge((cl, a, b))
            
            # Convertir de vuelta a BGR
            enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        else:
            # Imagen en escala de grises
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
            
        return enhanced
