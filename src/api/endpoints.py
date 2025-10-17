"""
ENDPOINTS DE LA API

Este archivo define todas las "rutas" o "endpoints" disponibles en nuestra API.

Un endpoint es como un "mostrador de servicio" específico donde otros programas
pueden solicitar una función concreta, como extraer texto de un documento
o analizar su contenido.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import shutil
from typing import List, Optional
import json
from pathlib import Path
from loguru import logger

from .models import (
    RespuestaExtraccionTexto, 
    RespuestaAnalisis, 
    TipoDocumento, 
    SolicitudAnalisis,
    EstadoProcesamiento
)
from ..ocr.extractor import TextExtractor
from ..nlp.keyword_extraction import KeywordExtractor
from ..nlp.entity_extraction import EntityExtractor
import config

# Configurar logger
logger = logger.bind(name="api.endpoints")

# Crear router (gestor de rutas)
router = APIRouter()

# Inicializar los componentes principales
extractor_texto = TextExtractor()
extractor_palabras_clave = KeywordExtractor()
extractor_entidades = EntityExtractor()

# Directorio para archivos temporales
DIRECTORIO_TEMPORAL = Path(config.OUTPUT_DIR) / "temp"
os.makedirs(DIRECTORIO_TEMPORAL, exist_ok=True)

# Almacenamiento en memoria para trabajos en proceso
# Esto nos permite seguir el estado de las solicitudes que están siendo procesadas
trabajos_en_proceso = {}

def guardar_archivo_subido(archivo_subido: UploadFile) -> Path:
    """
    Guarda un archivo subido a un directorio temporal.
    
    Args:
        archivo_subido: Archivo subido por el usuario
        
    Returns:
        Ruta donde se guardó el archivo
    """
    # Generar nombre único para evitar conflictos
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    id_unico = str(uuid.uuid4())[:8]  # Identificador único
    nombre_original = archivo_subido.filename
    nombre_seguro = f"{marca_tiempo}_{id_unico}_{nombre_original}"
    
    # Ruta de destino
    ruta_archivo = DIRECTORIO_TEMPORAL / nombre_seguro
    
    # Guardar archivo
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(archivo_subido.file, buffer)
    
    return ruta_archivo

def procesar_documento_segundo_plano(id_trabajo: str, ruta_archivo: Path, idioma: str, extraer_palabras_clave: bool, extraer_entidades: bool):
    """
    Procesa un documento en segundo plano.
    
    Esta función se ejecuta en segundo plano para no bloquear la API
    mientras se procesa un documento, que puede llevar tiempo.
    
    Args:
        id_trabajo: Identificador único del trabajo
        ruta_archivo: Ruta al archivo a procesar
        idioma: Idioma del documento
        extraer_palabras_clave: Si se deben extraer palabras clave
        extraer_entidades: Si se deben extraer entidades
    """
    try:
        # Actualizar estado
        trabajos_en_proceso[id_trabajo]["estado"] = EstadoProcesamiento.PROCESANDO
        
        # Extraer texto según el tipo de archivo
        extension_archivo = ruta_archivo.suffix.lower()
        
        if extension_archivo == ".pdf":
            # Procesar PDF
            textos_extraidos = extractor_texto.extract_from_pdf(pdf_path=str(ruta_archivo))
            # Unir textos de todas las páginas
            texto_extraido = "\n\n".join(textos_extraidos)
        else:  # Tratar como imagen
            # Procesar imagen
            import cv2
            imagen = cv2.imread(str(ruta_archivo))
            texto_extraido = extractor_texto.extract_from_image(imagen)
        
        # Guardar el texto extraído
        trabajos_en_proceso[id_trabajo]["texto"] = texto_extraido
        
        # Procesar con NLP si se solicita
        if extraer_palabras_clave:
            # Extraer palabras clave
            palabras_clave = extractor_palabras_clave.extract_keywords(texto_extraido, method="combined")
            trabajos_en_proceso[id_trabajo]["palabras_clave"] = palabras_clave
        
        if extraer_entidades:
            # Extraer entidades nombradas
            entidades = extractor_entidades.extract_main_entities(texto_extraido)
            trabajos_en_proceso[id_trabajo]["entidades"] = entidades
        
        # Actualizar estado a completado
        trabajos_en_proceso[id_trabajo]["estado"] = EstadoProcesamiento.COMPLETADO
        
    except Exception as e:
        logger.error(f"Error procesando documento {id_trabajo}: {str(e)}")
        trabajos_en_proceso[id_trabajo]["estado"] = EstadoProcesamiento.FALLIDO
        trabajos_en_proceso[id_trabajo]["error"] = str(e)

@router.post("/extraer-texto", response_model=RespuestaExtraccionTexto)
async def extraer_texto(
    archivo: UploadFile = File(...),
    idioma: str = Form("spa"),
):
    """
    Endpoint para extraer texto de un archivo PDF o imagen.
    
    Este es el punto de entrada para la funcionalidad básica de OCR.
    Los usuarios envían un archivo y reciben un ID de trabajo para
    consultar el resultado más tarde.
    
    Args:
        archivo: Archivo a procesar (PDF o imagen)
        idioma: Idioma del documento
        
    Returns:
        ID del trabajo y estado inicial
    """
    try:
        logger.info(f"Recibiendo archivo: {archivo.filename}")
        
        # Validar tipo de archivo
        extension_archivo = os.path.splitext(archivo.filename)[1].lower()
        if extension_archivo not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Guardar archivo
        ruta_archivo = guardar_archivo_subido(archivo)
        logger.info(f"Archivo guardado en: {ruta_archivo}")
        
        # Determinar tipo de documento
        tipo_doc = TipoDocumento.PDF if extension_archivo == ".pdf" else TipoDocumento.IMAGEN
        
        # Generar ID de trabajo único
        id_trabajo = str(uuid.uuid4())
        
        # Inicializar estado del trabajo
        trabajos_en_proceso[id_trabajo] = {
            "id": id_trabajo,
            "nombre_archivo": archivo.filename,
            "ruta_archivo": str(ruta_archivo),
            "tipo": tipo_doc,
            "idioma": idioma,
            "estado": EstadoProcesamiento.EN_COLA,
            "creado_en": datetime.now().isoformat(),
            "texto": None,
            "palabras_clave": None,
            "entidades": None,
            "error": None
        }
        
        return RespuestaExtraccionTexto(
            id_trabajo=id_trabajo,
            estado=EstadoProcesamiento.EN_COLA,
            mensaje="Archivo recibido. Procesamiento en cola."
        )
        
    except Exception as e:
        logger.error(f"Error en extraer_texto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analizar", response_model=RespuestaAnalisis)
async def analizar_documento(
    tareas_segundo_plano: BackgroundTasks,
    archivo: UploadFile = File(...),
    idioma: str = Form("spa"),
    extraer_palabras_clave: bool = Form(True),
    extraer_entidades: bool = Form(True)
):
    """
    Endpoint para analizar un documento completo.
    
    Este endpoint es más avanzado y puede extraer texto, palabras clave
    y entidades de un documento. El procesamiento se realiza en segundo
    plano para no bloquear la API.
    
    Args:
        tareas_segundo_plano: Gestor de tareas en segundo plano
        archivo: Archivo a procesar
        idioma: Idioma del documento
        extraer_palabras_clave: Si se deben extraer palabras clave
        extraer_entidades: Si se deben extraer entidades
        
    Returns:
        ID del trabajo y estado inicial
    """
    try:
        logger.info(f"Recibiendo solicitud de análisis para archivo: {archivo.filename}")
        
        # Validar tipo de archivo
        extension_archivo = os.path.splitext(archivo.filename)[1].lower()
        if extension_archivo not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Guardar archivo
        ruta_archivo = guardar_archivo_subido(archivo)
        logger.info(f"Archivo guardado en: {ruta_archivo}")
        
        # Determinar tipo de documento
        tipo_doc = TipoDocumento.PDF if extension_archivo == ".pdf" else TipoDocumento.IMAGEN
        
        # Generar ID de trabajo único
        id_trabajo = str(uuid.uuid4())
        
        # Inicializar estado del trabajo
        trabajos_en_proceso[id_trabajo] = {
            "id": id_trabajo,
            "nombre_archivo": archivo.filename,
            "ruta_archivo": str(ruta_archivo),
            "tipo": tipo_doc,
            "idioma": idioma,
            "estado": EstadoProcesamiento.EN_COLA,
            "creado_en": datetime.now().isoformat(),
            "texto": None,
            "palabras_clave": None,
            "entidades": None,
            "error": None
        }
        
        # Iniciar procesamiento en segundo plano
        # Esto permite que la API responda inmediatamente mientras
        # el procesamiento ocurre en paralelo
        tareas_segundo_plano.add_task(
            procesar_documento_segundo_plano,
            id_trabajo,
            ruta_archivo,
            idioma,
            extraer_palabras_clave,
            extraer_entidades
        )
        
        return RespuestaAnalisis(
            id_trabajo=id_trabajo,
            estado=EstadoProcesamiento.EN_COLA,
            mensaje="Archivo recibido. Procesamiento iniciado."
        )
        
    except Exception as e:
        logger.error(f"Error en analizar_documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trabajos/{id_trabajo}")
async def obtener_estado_trabajo(id_trabajo: str):
    """
    Obtiene el estado actual y resultados de un trabajo.
    
    Este endpoint permite a los clientes verificar si su trabajo
    ha sido completado y obtener los resultados.
    
    Args:
        id_trabajo: ID del trabajo a consultar
        
    Returns:
        Estado actual y resultados si está completado
    """
    if id_trabajo not in trabajos_en_proceso:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    trabajo = trabajos_en_proceso[id_trabajo]
    
    # Formatear respuesta según el estado
    respuesta = {
        "id_trabajo": id_trabajo,
        "estado": trabajo["estado"],
        "creado_en": trabajo["creado_en"],
        "nombre_archivo": trabajo["nombre_archivo"],
        "tipo": trabajo["tipo"]
    }
    
    # Incluir resultados si está completo
    if trabajo["estado"] == EstadoProcesamiento.COMPLETADO:
        respuesta["texto"] = trabajo["texto"]
        if trabajo["palabras_clave"]:
            respuesta["palabras_clave"] = trabajo["palabras_clave"]
        if trabajo["entidades"]:
            respuesta["entidades"] = trabajo["entidades"]
    
    # Incluir error si falló
    if trabajo["estado"] == EstadoProcesamiento.FALLIDO:
        respuesta["error"] = trabajo["error"]
    
    return respuesta

@router.get("/trabajos")
async def listar_trabajos():
    """
    Lista todos los trabajos de procesamiento.
    
    Este endpoint permite ver un resumen de todos los trabajos
    que están en el sistema, tanto completados como en proceso.
    
    Returns:
        Lista de resúmenes de trabajos
    """
    resumenes_trabajos = []
    for id_trabajo, trabajo in trabajos_en_proceso.items():
        resumenes_trabajos.append({
            "id_trabajo": id_trabajo,
            "estado": trabajo["estado"],
            "creado_en": trabajo["creado_en"],
            "nombre_archivo": trabajo["nombre_archivo"],
            "tipo": trabajo["tipo"]
        })
    
    return {"trabajos": resumenes_trabajos}
