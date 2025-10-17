"""
MODELOS DE DATOS DE LA API

Este archivo define las estructuras de datos que se utilizan
en la API para comunicarse con los clientes.

Es como definir los "formularios" y "reportes" que se utilizarán
para intercambiar información entre el sistema y sus usuarios.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from fastapi import UploadFile

class DocumentType(str, Enum):
    """Tipos de documentos soportados"""
    PDF = "pdf"
    IMAGE = "image"

class ProcessingStatus(str, Enum):
    """Estados posibles de un trabajo de procesamiento"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExtractTextResponse(BaseModel):
    """Respuesta a la solicitud de extracción de texto"""
    job_id: str
    status: ProcessingStatus
    message: str

class AnalysisRequest(BaseModel):
    """Solicitud para analizar un documento"""
    file: UploadFile
    language: str = "eng"
    extract_keywords: bool = True
    extract_entities: bool = True
    
    class Config:
        arbitrary_types_allowed = True

class AnalysisResponse(BaseModel):
    """Respuesta a la solicitud de análisis de documento"""
    job_id: str
    status: ProcessingStatus
    message: str

class KeywordResult(BaseModel):
    """Resultado de extracción de palabras clave"""
    keyword: str
    score: float

class EntityResult(BaseModel):
    """
    Resultado de extracción de entidades.
    
    Define cómo se representan las entidades extraídas.
    """
    text: str                      # El texto de la entidad encontrada
    label: str                      # El tipo de entidad (PERSON, ORG, etc.)
    description: Optional[str] = None  # Descripción del tipo de entidad

class JobResult(BaseModel):
    """
    Resultado completo de un trabajo de procesamiento.
    
    Esta estructura contiene todos los resultados obtenidos
    al procesar un documento, tanto el texto extraído como
    los análisis realizados.
    """
    job_id: str                               # ID único del trabajo
    status: ProcessingStatus                  # Estado del trabajo
    created_at: str                           # Fecha y hora de creación
    filename: str                             # Nombre del archivo original
    type: DocumentType                        # Tipo de documento (PDF o imagen)
    text: Optional[str] = None                # Texto extraído (si está completado)
    keywords: Optional[List[KeywordResult]] = None  # Palabras clave encontradas
    entities: Optional[Dict[str, List[EntityResult]]] = None  # Entidades encontradas
    error: Optional[str] = None               # Mensaje de error (si falló)
