"""
EXTRACCIÓN DE PALABRAS CLAVE

Este archivo contiene herramientas para identificar las palabras
y frases más importantes de un texto.
"""

import yake
from loguru import logger
from collections import Counter
import re

class ExtractorPalabrasClave:
    """
    Clase simplificada para extraer palabras clave de textos.
    """
    
    def __init__(self, idioma="es"):
        """
        Inicializa el extractor de palabras clave.
        
        Args:
            idioma: Código del idioma (es=español, en=inglés)
        """
        self.logger = logger.bind(name="ExtractorPalabrasClave")
        self.idioma = idioma
        
        # Palabras comunes básicas en español e inglés
        self.palabras_comunes = {
            "es": {"el", "la", "de", "que", "y", "a", "en", "un", "ser", "se", "no", "haber", "por", "con", "su", "para", "como", "estar", "tener", "le", "lo", "todo", "pero", "más", "hacer", "o", "poder", "decir", "este", "ir", "otro", "ese", "si", "me", "ya", "ver", "porque", "dar", "cuando", "él", "muy", "sin", "vez", "mucho", "saber", "qué", "sobre", "mi", "alguno", "mismo", "yo", "también", "hasta", "año", "dos", "querer", "entre", "así", "primero", "desde", "grande", "eso", "ni", "nos", "llegar", "pasar", "tiempo", "ella", "sí", "día", "uno", "bien", "poco", "deber", "entonces", "poner", "cosa", "tanto", "hombre", "parecer", "nuestro", "tan", "donde", "ahora", "parte", "después", "vida", "quedar", "siempre", "creer", "hablar", "llevar", "dejar", "nada", "cada", "seguir", "menos", "nuevo", "encontrar", "algo", "solo", "decir", "son", "las", "los", "una", "del"},
            "en": {"the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us", "is", "was", "are", "been", "has", "had", "were", "said", "did", "having", "may"}
        }
        
        # Inicializar YAKE
        try:
            self.extractor_yake = yake.KeywordExtractor(
                lan=idioma,
                n=2,
                dedupLim=0.9,
                top=20
            )
            self.logger.info("YAKE inicializado correctamente")
        except Exception as e:
            self.logger.error(f"Error al inicializar YAKE: {str(e)}")
            self.extractor_yake = None
    
    def limpiar_texto(self, texto: str) -> list[str]:
        """
        Limpia y tokeniza el texto.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Lista de palabras limpias
        """
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover puntuación pero mantener espacios
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Dividir en palabras
        palabras = texto.split()
        
        # Filtrar palabras
        palabras_comunes = self.palabras_comunes.get(self.idioma, set())
        palabras_filtradas = [
            p for p in palabras 
            if len(p) > 2 
            and p not in palabras_comunes
            and not p.isdigit()
        ]
        
        return palabras_filtradas
    
    def extraer_con_yake(self, texto: str, cantidad: int = 10) -> list[tuple[str, float]]:
        """
        Extrae palabras clave usando YAKE.
        
        Args:
            texto: Texto a analizar
            cantidad: Número de palabras clave a extraer
            
        Returns:
            Lista de tuplas (palabra_clave, puntuación)
        """
        if not self.extractor_yake:
            self.logger.warning("YAKE no está disponible, usando método simple")
            return self.extraer_con_frecuencia(texto, cantidad)
            
        try:
            palabras_clave = self.extractor_yake.extract_keywords(texto)
            # Normalizar puntuaciones (YAKE da valores bajos a palabras importantes)
            if palabras_clave:
                max_score = max(score for _, score in palabras_clave) + 0.001
                return [(palabra, max_score - score) for palabra, score in palabras_clave[:cantidad]]
            return []
        except Exception as e:
            self.logger.error(f"Error en YAKE: {str(e)}")
            return self.extraer_con_frecuencia(texto, cantidad)
    
    def extraer_con_frecuencia(self, texto: str, cantidad: int = 10) -> list[tuple[str, float]]:
        """
        Extrae palabras clave por frecuencia (método de respaldo).
        
        Args:
            texto: Texto a analizar
            cantidad: Número de palabras clave a extraer
            
        Returns:
            Lista de tuplas (palabra_clave, puntuación)
        """
        try:
            palabras = self.limpiar_texto(texto)
            
            if not palabras:
                return []
            
            # Contar frecuencias
            contador = Counter(palabras)
            palabras_frecuentes = contador.most_common(cantidad)
            
            # Normalizar puntuaciones
            total = len(palabras)
            return [(palabra, freq / total) for palabra, freq in palabras_frecuentes]
            
        except Exception as e:
            self.logger.error(f"Error en extracción por frecuencia: {str(e)}")
            return []
    
    def extraer_palabras_clave(self, texto: str, metodo: str = "yake", cantidad: int = 10) -> list[tuple[str, float]]:
        """
        Extrae palabras clave del texto.
        
        Args:
            texto: Texto a analizar
            metodo: Método a usar ('yake' o 'frecuencia')
            cantidad: Número de palabras clave a extraer
            
        Returns:
            Lista de tuplas (palabra_clave, puntuación)
        """
        if not texto or len(texto.strip()) < 50:
            self.logger.warning("Texto demasiado corto para extraer palabras clave")
            return []
        
        self.logger.info(f"Extrayendo {cantidad} palabras clave con método: {metodo}")
        
        if metodo == "frecuencia":
            return self.extraer_con_frecuencia(texto, cantidad)
        else:  # Por defecto usa YAKE
            return self.extraer_con_yake(texto, cantidad)

# Alias para compatibilidad
KeywordExtractor = ExtractorPalabrasClave
