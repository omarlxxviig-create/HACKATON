"""
EXTRACCIÓN DE ENTIDADES

Este archivo contiene herramientas para identificar y extraer
entidades nombradas en un texto como personas, organizaciones, lugares, etc.
"""

import spacy
from loguru import logger
import config
import subprocess
import sys

class ExtractorEntidades:
    """
    Clase para extraer entidades nombradas de textos usando spaCy.
    """
    
    def __init__(self, idioma="spa"):
        """
        Inicializa el extractor de entidades.
        
        Args:
            idioma: Código de idioma (spa=español, eng=inglés)
        """
        self.logger = logger.bind(name="ExtractorEntidades")
        self.idioma = idioma
        
        # Obtener nombre del modelo de spaCy
        nombre_modelo = config.NLP_MODELS.get(idioma)
        
        if nombre_modelo is None:
            self.logger.error(f"No hay modelo configurado para: {idioma}")
            # Usar modelo por defecto
            nombre_modelo = "es_core_news_sm" if idioma == "spa" else "en_core_web_sm"
            self.logger.warning(f"Usando modelo por defecto: {nombre_modelo}")
        
        # Intentar cargar el modelo
        self.nlp = None
        self.logger.info(f"Intentando cargar modelo spaCy: {nombre_modelo}")
        
        try:
            self.nlp = spacy.load(nombre_modelo)
            self.logger.info(f"Modelo {nombre_modelo} cargado correctamente")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar {nombre_modelo}: {str(e)}")
            self.logger.info("Intentando descargar el modelo...")
            
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "spacy", "download", nombre_modelo],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.nlp = spacy.load(nombre_modelo)
                self.logger.info(f"Modelo {nombre_modelo} descargado y cargado")
            except Exception as e2:
                self.logger.error(f"No se pudo descargar {nombre_modelo}: {str(e2)}")
                
                # Intentar con modelo de respaldo
                modelo_respaldo = "es_core_news_sm" if idioma == "spa" else "en_core_web_sm"
                self.logger.info(f"Intentando modelo de respaldo: {modelo_respaldo}")
                
                try:
                    self.nlp = spacy.load(modelo_respaldo)
                    self.logger.info(f"Modelo de respaldo {modelo_respaldo} cargado")
                except Exception as e3:
                    self.logger.error(f"Error crítico: No se pudo cargar ningún modelo de spaCy")
                    raise ValueError(f"No se pudo inicializar spaCy: {str(e3)}")
    
    def extraer_entidades(self, texto: str) -> list[dict]:
        """
        Extrae todas las entidades nombradas del texto.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Lista de diccionarios con información de cada entidad
        """
        if not self.nlp:
            self.logger.error("Modelo spaCy no está disponible")
            return []
        
        try:
            self.logger.debug("Procesando texto para extracción de entidades")
            doc = self.nlp(texto)
            
            entidades = []
            for ent in doc.ents:
                # Obtener descripción de la etiqueta
                descripcion = None
                try:
                    descripcion = spacy.explain(ent.label_)
                except (AttributeError, KeyError):
                    descripcion = ent.label_
                
                entidades.append({
                    "texto": ent.text,
                    "inicio": ent.start_char,
                    "fin": ent.end_char,
                    "etiqueta": ent.label_,
                    "descripcion": descripcion or ent.label_
                })
            
            self.logger.info(f"Se encontraron {len(entidades)} entidades")
            return entidades
            
        except Exception as e:
            self.logger.error(f"Error extrayendo entidades: {str(e)}")
            return []
    
    def extraer_entidades_por_tipo(self, texto: str) -> dict:
        """
        Extrae entidades agrupadas por tipo.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Diccionario con entidades agrupadas por tipo
        """
        try:
            entidades = self.extraer_entidades(texto)
            
            entidades_por_tipo = {}
            for entidad in entidades:
                tipo = entidad["etiqueta"]
                if tipo not in entidades_por_tipo:
                    entidades_por_tipo[tipo] = []
                
                entidades_por_tipo[tipo].append({
                    "texto": entidad["texto"],
                    "inicio": entidad["inicio"],
                    "fin": entidad["fin"]
                })
            
            return entidades_por_tipo
            
        except Exception as e:
            self.logger.error(f"Error agrupando entidades: {str(e)}")
            return {}
    
    def extraer_entidades_principales(self, texto: str) -> dict:
        """
        Extrae entidades organizadas en categorías amigables.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Diccionario con entidades en categorías legibles
        """
        try:
            entidades = self.extraer_entidades(texto)
            
            # Mapeo de etiquetas técnicas a categorías amigables
            mapeo_categorias = {
                "PERSON": "personas",
                "PER": "personas",
                "ORG": "organizaciones",
                "GPE": "lugares",
                "LOC": "lugares",
                "DATE": "fechas",
                "TIME": "tiempo",
                "MONEY": "valores_monetarios",
                "PERCENT": "porcentajes",
                "CARDINAL": "numeros",
                "ORDINAL": "ordinales",
                "PRODUCT": "productos",
                "EVENT": "eventos",
                "WORK_OF_ART": "obras",
                "LAW": "leyes",
                "LANGUAGE": "idiomas",
                "FAC": "instalaciones",
                "NORP": "grupos"
            }
            
            # Inicializar resultado con categorías principales
            resultado = {
                "personas": [],
                "organizaciones": [],
                "lugares": [],
                "fechas": [],
                "valores_monetarios": [],
                "otros": []
            }
            
            # Clasificar entidades
            for entidad in entidades:
                categoria = mapeo_categorias.get(entidad["etiqueta"], "otros")
                
                # Crear categoría si no existe
                if categoria not in resultado:
                    resultado[categoria] = []
                
                # Evitar duplicados
                texto_entidad = entidad["texto"]
                if not any(e["texto"] == texto_entidad for e in resultado[categoria]):
                    resultado[categoria].append({
                        "texto": texto_entidad,
                        "etiqueta": entidad["etiqueta"]
                    })
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error extrayendo entidades principales: {str(e)}")
            return {"error": str(e)}

# Alias para compatibilidad
EntityExtractor = ExtractorEntidades
