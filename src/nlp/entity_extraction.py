"""
EXTRACCIÓN DE ENTIDADES

Este archivo contiene herramientas para identificar y extraer
entidades nombradas en un texto, como nombres de personas, 
organizaciones, lugares, fechas, etc.

Es como tener un asistente que lee un texto y subraya todos los
nombres propios, empresas, lugares, fechas y otros elementos importantes.
"""

import spacy
from loguru import logger
import config

class EntityExtractor:
    """
    Clase para extraer entidades nombradas de textos.
    
    Utiliza modelos de lenguaje de spaCy para identificar
    automáticamente elementos como nombres de personas,
    organizaciones, lugares, fechas, etc. en un texto.
    """
    
    def __init__(self, language="eng"):
        """
        Inicializa el extractor de entidades.
        
        Args:
            language: Código de idioma (eng=inglés, spa=español)
        """
        self.logger = logger.bind(name="EntityExtractor")
        self.language = language
        
        # Determinar qué modelo de spaCy usar según el idioma
        model_name = config.NLP_MODELS.get(language, config.NLP_MODELS.get("eng"))
        
        try:
            # Intentar cargar el modelo de lenguaje
            self.logger.info(f"Cargando modelo spaCy: {model_name}")
            self.nlp = spacy.load(model_name)
            self.logger.info(f"Modelo {model_name} cargado correctamente")
        except Exception as e:
            # Si no está instalado, intentar descargarlo
            self.logger.error(f"Error cargando modelo {model_name}: {str(e)}")
            self.logger.warning("Intentando descargar el modelo...")
            try:
                spacy.cli.download(model_name)
                self.nlp = spacy.load(model_name)
                self.logger.info(f"Modelo {model_name} descargado y cargado correctamente")
            except Exception as e2:
                self.logger.error(f"No se pudo descargar el modelo {model_name}: {str(e2)}")
                # Intentar con un modelo más pequeño como respaldo
                fallback_model = "en_core_web_sm" if language == "eng" else "es_core_news_sm"
                try:
                    self.logger.info(f"Intentando cargar modelo de respaldo: {fallback_model}")
                    self.nlp = spacy.load(fallback_model)
                except:
                    self.logger.error("No se pudo cargar ningún modelo de spaCy")
                    raise ValueError("No se pudo cargar ningún modelo de spaCy")
    
    def extract_entities(self, text):
        """
        Extrae entidades nombradas de un texto.
        
        Analiza el texto para encontrar nombres de personas, organizaciones,
        lugares, fechas, cantidades, etc.
        
        Args:
            text: Texto del que extraer entidades
            
        Returns:
            Lista de entidades encontradas con detalles
        """
        try:
            self.logger.debug("Procesando texto para extracción de entidades")
            # Procesar el texto con spaCy
            doc = self.nlp(text)
            
            # Recopilar todas las entidades encontradas
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,                # El texto de la entidad
                    "start_char": ent.start_char,    # Posición inicial en el texto
                    "end_char": ent.end_char,        # Posición final en el texto
                    "label": ent.label_,             # Tipo de entidad (PERSON, ORG, etc.)
                    "description": spacy.explain(ent.label_)  # Descripción del tipo
                })
            
            self.logger.info(f"Se encontraron {len(entities)} entidades en el texto")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error extrayendo entidades: {str(e)}")
            return []
    
    def extract_entities_by_type(self, text):
        """
        Extrae entidades nombradas y las agrupa por tipo.
        
        Similar a extract_entities, pero organiza los resultados
        por categorías (personas, organizaciones, etc.)
        
        Args:
            text: Texto del que extraer entidades
            
        Returns:
            Diccionario con entidades agrupadas por tipo
        """
        try:
            # Obtener todas las entidades
            entities = self.extract_entities(text)
            
            # Agrupar por tipo
            entities_by_type = {}
            for entity in entities:
                entity_type = entity["label"]
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                
                entities_by_type[entity_type].append({
                    "text": entity["text"],
                    "start_char": entity["start_char"],
                    "end_char": entity["end_char"]
                })
            
            return entities_by_type
            
        except Exception as e:
            self.logger.error(f"Error agrupando entidades por tipo: {str(e)}")
            return {}

    def extract_main_entities(self, text):
        """
        Extrae y organiza las entidades principales en categorías amigables.
        
        Convierte los códigos técnicos de spaCy en categorías más
        comprensibles como "personas", "organizaciones", "lugares", etc.
        
        Args:
            text: Texto del que extraer entidades
            
        Returns:
            Diccionario con entidades organizadas en categorías fáciles de entender
        """
        try:
            # Obtener todas las entidades
            entities = self.extract_entities(text)
            
            # Mapeo de tipos técnicos a categorías amigables
            main_categories = {
                "PERSON": "personas",         # Personas
                "PER": "personas",            # Personas (otro código)
                "ORG": "organizaciones",      # Organizaciones, empresas
                "GPE": "lugares",             # Países, ciudades
                "LOC": "lugares",             # Ubicaciones
                "DATE": "fechas",             # Fechas
                "TIME": "tiempo",             # Horas, períodos de tiempo
                "MONEY": "valores_monetarios", # Cantidades monetarias
                "PERCENT": "porcentajes",     # Porcentajes
                "CARDINAL": "números",        # Números
                "ORDINAL": "ordinales",       # Números ordinales (primero, segundo...)
                "PRODUCT": "productos",       # Productos
                "EVENT": "eventos",           # Eventos
                "WORK_OF_ART": "obras",       # Obras artísticas
                "LAW": "leyes",               # Leyes, normativas
                "LANGUAGE": "idiomas",        # Idiomas
                "FAC": "instalaciones",       # Instalaciones, edificios
                "NORP": "grupos"              # Grupos, nacionalidades
            }
            
            # Crear diccionario para resultados con categorías predefinidas
            main_entities = {
                "personas": [],
                "organizaciones": [],
                "lugares": [],
                "fechas": [],
                "valores_monetarios": [],
                "otros": []
            }
            
            # Clasificar cada entidad en su categoría correspondiente
            for entity in entities:
                # Determinar la categoría según el tipo de entidad
                category = main_categories.get(entity["label"], "otros")
                
                # Crear la categoría si no existe
                if category not in main_entities:
                    main_entities[category] = []
                    
                # Evitar duplicados
                if entity["text"] not in [e["text"] for e in main_entities[category]]:
                    main_entities[category].append({
                        "text": entity["text"],   # El texto de la entidad
                        "label": entity["label"]  # El tipo técnico original
                    })
            
            return main_entities
            
        except Exception as e:
            self.logger.error(f"Error extrayendo entidades principales: {str(e)}")
            return {"error": str(e)}
