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

class TipoDocumento(str, Enum):
    """Tipos de documentos soportados"""
    PDF = "pdf"
    IMAGEN = "imagen"

class EstadoProcesamiento(str, Enum):
    """Estados posibles de un trabajo de procesamiento"""
    EN_COLA = "en_cola"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"

class RespuestaExtraccionTexto(BaseModel):
    """Respuesta a la solicitud de extracción de texto"""
    id_trabajo: str
    estado: EstadoProcesamiento
    mensaje: str

class SolicitudAnalisis(BaseModel):
    """Solicitud para analizar un documento"""
    archivo: UploadFile
    idioma: str = "spa"
    extraer_palabras_clave: bool = True
    extraer_entidades: bool = True
    
    class Config:
        arbitrary_types_allowed = True

class RespuestaAnalisis(BaseModel):
    """Respuesta a la solicitud de análisis de documento"""
    id_trabajo: str
    estado: EstadoProcesamiento
    mensaje: str

class ResultadoPalabraClave(BaseModel):
    """Resultado de extracción de palabras clave"""
    palabra_clave: str
    puntuacion: float

class ResultadoEntidad(BaseModel):
    """
    Resultado de extracción de entidades.
    
    Define cómo se representan las entidades extraídas.
    """
    texto: str                      # El texto de la entidad encontrada
    etiqueta: str                   # El tipo de entidad (PERSON, ORG, etc.)
    descripcion: Optional[str] = None  # Descripción del tipo de entidad

class ResultadoTrabajo(BaseModel):
    """
    Resultado completo de un trabajo de procesamiento.
    
    Esta estructura contiene todos los resultados obtenidos
    al procesar un documento, tanto el texto extraído como
    los análisis realizados.
    """
    id_trabajo: str                               # ID único del trabajo
    estado: EstadoProcesamiento                   # Estado del trabajo
    creado_en: str                                # Fecha y hora de creación
    nombre_archivo: str                           # Nombre del archivo original
    tipo: TipoDocumento                           # Tipo de documento (PDF o imagen)
    texto: Optional[str] = None                   # Texto extraído (si está completado)
    palabras_clave: Optional[List[ResultadoPalabraClave]] = None  # Palabras clave encontradas
    entidades: Optional[Dict[str, List[ResultadoEntidad]]] = None  # Entidades encontradas
    error: Optional[str] = None                   # Mensaje de error (si falló)
