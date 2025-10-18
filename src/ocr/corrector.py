"""
CORRECTOR DE TEXTO POST-OCR

Este archivo contiene herramientas para corregir errores comunes
que comete el OCR al leer documentos.
"""

from spellchecker import SpellChecker
import re
from loguru import logger

class TextCorrector:
    """
    Clase para corregir errores comunes del OCR.
    
    El OCR a veces confunde letras con números (O con 0, l con 1, etc.)
    Esta clase corrige esos errores comunes.
    """
    
    def __init__(self, language='es'):
        """
        Inicializa el corrector de texto.
        
        Args:
            language: Idioma para corrección ortográfica ('es' o 'en')
        """
        self.logger = logger.bind(name="TextCorrector")
        self.spell = SpellChecker(language=language)
        
        # Diccionario de correcciones comunes OCR
        # Estos son errores típicos que comete el OCR
        self.ocr_replacements = {
            r'\b0(?=[a-zA-Z])': 'o',  # 0 seguido de letra -> o
            r'(?<=[a-zA-Z])0\b': 'o',  # 0 precedido de letra -> o
            r'\bl(?=\d)': '1',         # l seguido de número -> 1
            r'(?<=\d)l\b': '1',        # l precedido de número -> 1
        }
        
        self.logger.info(f"Corrector inicializado con idioma: {language}")
    
    def correct_common_ocr_errors(self, text):
        """
        Corrige errores comunes de OCR usando patrones.
        
        Args:
            text: Texto con posibles errores
            
        Returns:
            Texto con correcciones aplicadas
        """
        corrected = text
        for pattern, replacement in self.ocr_replacements.items():
            corrected = re.sub(pattern, replacement, corrected)
        return corrected
    
    def correct_spelling(self, text):
        """
        Corrige errores ortográficos en el texto.
        
        Args:
            text: Texto con posibles errores ortográficos
            
        Returns:
            Texto corregido
        """
        words = text.split()
        corrected = []
        
        for word in words:
            # Solo corregir palabras alfabéticas de más de 2 caracteres
            if word.isalpha() and len(word) > 2:
                # Obtener corrección sugerida
                correction = self.spell.correction(word)
                if correction and correction != word:
                    self.logger.debug(f"Corrección: '{word}' -> '{correction}'")
                    corrected.append(correction)
                else:
                    corrected.append(word)
            else:
                corrected.append(word)
        
        return ' '.join(corrected)
    
    def correct_text(self, text):
        """
        Método principal: aplica todas las correcciones.
        
        Args:
            text: Texto a corregir
            
        Returns:
            Texto completamente corregido
        """
        # 1. Limpiar espacios múltiples
        text = re.sub(r' +', ' ', text)
        
        # 2. Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # 3. Corregir errores comunes de OCR
        text = self.correct_common_ocr_errors(text)
        
        # 4. Corrección ortográfica
        text = self.correct_spelling(text)
        
        return text.strip()
