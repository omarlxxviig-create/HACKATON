"""
EXTRACCIÓN DE PALABRAS CLAVE

Este archivo contiene herramientas para identificar las palabras
y frases más importantes de un texto.

Es como tener un asistente que lee un documento y subraya
las palabras clave o temas principales.
"""

import yake
from keybert import KeyBERT
import spacy
from loguru import logger
import nltk
from collections import Counter

# Descargar recursos necesarios
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

from nltk.corpus import stopwords

class KeywordExtractor:
    """
    Clase para extraer palabras clave de textos.
    
    Utiliza diferentes algoritmos para encontrar las palabras o
    frases más importantes en un texto. Es como identificar
    los conceptos principales de un documento.
    """
    
    def __init__(self, language="en"):
        """
        Inicializa el extractor de palabras clave.
        
        Args:
            language: Idioma del texto (en=inglés, es=español, etc.)
        """
        self.logger = logger.bind(name="KeywordExtractor")
        self.language = language
        
        # Mapeo entre códigos de idioma para diferentes bibliotecas
        self.lang_map = {
            "en": "english",
            "es": "spanish",
            "fr": "french",
            "de": "german",
            "it": "italian",
            "pt": "portuguese"
        }
        
        # Inicializar KeyBERT (modelo basado en IA para palabras clave)
        try:
            self.keybert_model = KeyBERT()
            self.logger.info("KeyBERT inicializado correctamente")
        except Exception as e:
            self.logger.error(f"Error al inicializar KeyBERT: {str(e)}")
            self.keybert_model = None
            
        # Inicializar YAKE (otro algoritmo para palabras clave)
        self.yake_extractor = yake.KeywordExtractor()
        
        # Cargar "stopwords" (palabras comunes como "el", "la", "y", "que", etc.)
        # que normalmente se excluyen del análisis
        nltk_lang = self.lang_map.get(language, "english")
        self.stop_words = set(stopwords.words(nltk_lang))
        
    def extract_with_keybert(self, text, top_n=10):
        """
        Extrae palabras clave usando el algoritmo KeyBERT.
        
        KeyBERT usa modelos de IA avanzados para entender el significado
        del texto y encontrar las palabras más relevantes.
        
        Args:
            text: Texto del que extraer palabras clave
            top_n: Número de palabras clave a extraer
            
        Returns:
            Lista de palabras clave con su puntuación de relevancia
        """
        if not self.keybert_model:
            self.logger.warning("KeyBERT no está disponible")
            return []
            
        try:
            keywords = self.keybert_model.extract_keywords(
                text, 
                keyphrase_ngram_range=(1, 2),  # Permite palabras individuales o pares
                stop_words=self.stop_words,    # Ignora palabras comunes
                top_n=top_n                    # Número máximo de resultados
            )
            return keywords
        except Exception as e:
            self.logger.error(f"Error en extracción KeyBERT: {str(e)}")
            return []
    
    def extract_with_yake(self, text, top_n=10):
        """
        Extrae palabras clave usando el algoritmo YAKE.
        
        YAKE es un algoritmo que no requiere entrenamiento y funciona
        analizando características estadísticas del texto.
        
        Args:
            text: Texto del que extraer palabras clave
            top_n: Número de palabras clave a extraer
            
        Returns:
            Lista de palabras clave con su puntuación de relevancia
        """
        try:
            # Configurar YAKE para el idioma actual
            language = self.language
            max_ngram_size = 2  # Permite palabras individuales o pares
            deduplication_threshold = 0.9  # Evitar palabras clave muy similares
            
            custom_kw_extractor = yake.KeywordExtractor(
                lan=language, 
                n=max_ngram_size, 
                dedupLim=deduplication_threshold, 
                top=top_n
            )
            
            keywords = custom_kw_extractor.extract_keywords(text)
            # YAKE da puntuaciones menores a mejores palabras clave, invertir
            return [(kw, 1/score) for kw, score in keywords]
        except Exception as e:
            self.logger.error(f"Error en extracción YAKE: {str(e)}")
            return []
    
    def extract_with_tfidf(self, text, top_n=10):
        """
        Extrae palabras clave usando TF-IDF básico.
        
        TF-IDF es un método estadístico que identifica palabras
        importantes basándose en su frecuencia en el texto.
        
        Args:
            text: Texto del que extraer palabras clave
            top_n: Número de palabras clave a extraer
            
        Returns:
            Lista de palabras clave con su puntuación
        """
        try:
            # Dividir el texto en palabras
            tokens = nltk.word_tokenize(text.lower())
            
            # Filtrar palabras:
            # - Solo palabras alfanuméricas
            # - No incluir palabras comunes como "el", "la", etc.
            # - Palabras con más de 2 caracteres
            tokens = [token for token in tokens 
                     if token.isalnum() 
                     and token not in self.stop_words 
                     and len(token) > 2]
            
            # Contar frecuencias de cada palabra
            word_freq = Counter(tokens)
            
            # Obtener las palabras más frecuentes
            keywords = word_freq.most_common(top_n)
            
            # Normalizar puntuaciones
            return [(kw, freq/len(tokens)) for kw, freq in keywords]
        except Exception as e:
            self.logger.error(f"Error en extracción TF-IDF: {str(e)}")
            return []
    
    def extract_keywords(self, text, method="combined", top_n=10):
        """
        Método principal: extrae palabras clave usando el método especificado.
        
        Puede usar diferentes algoritmos o combinarlos para obtener
        mejores resultados.
        
        Args:
            text: Texto del que extraer palabras clave
            method: Método a usar ('keybert', 'yake', 'tfidf', 'combined')
            top_n: Número de palabras clave a extraer
            
        Returns:
            Lista de palabras clave con sus puntuaciones
        """
        if not text or len(text.strip()) < 50:
            self.logger.warning("Texto demasiado corto para extraer palabras clave")
            return []
        
        self.logger.info(f"Extrayendo palabras clave con método: {method}")
        
        if method == "keybert":
            # Usar solo KeyBERT
            return self.extract_with_keybert(text, top_n)
        elif method == "yake":
            # Usar solo YAKE
            return self.extract_with_yake(text, top_n)
        elif method == "tfidf":
            # Usar solo TF-IDF
            return self.extract_with_tfidf(text, top_n)
        elif method == "combined":
            # Método combinado: usar varios algoritmos y combinar sus resultados
            
            # Obtener palabras clave de diferentes métodos
            keywords1 = dict(self.extract_with_keybert(text, top_n))
            keywords2 = dict(self.extract_with_yake(text, top_n))
            
            # Combinar puntuaciones
            all_keywords = set(list(keywords1.keys()) + list(keywords2.keys()))
            combined_scores = {}
            
            for kw in all_keywords:
                score1 = keywords1.get(kw, 0)
                score2 = keywords2.get(kw, 0)
                # Peso para cada método (60% KeyBERT, 40% YAKE)
                combined_scores[kw] = 0.6 * score1 + 0.4 * score2
            
            # Ordenar y devolver los top_n
            sorted_keywords = sorted(combined_scores.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True)[:top_n]
            
            return sorted_keywords
        else:
            self.logger.error(f"Método de extracción desconocido: {method}")
            return []
