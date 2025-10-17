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
    ExtractTextResponse, 
    AnalysisResponse, 
    DocumentType, 
    AnalysisRequest,
    ProcessingStatus
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
text_extractor = TextExtractor()
keyword_extractor = KeywordExtractor()
entity_extractor = EntityExtractor()

# Directorio para archivos temporales
TEMP_DIR = Path(config.OUTPUT_DIR) / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Almacenamiento en memoria para trabajos en proceso
# Esto nos permite seguir el estado de las solicitudes que están siendo procesadas
processing_jobs = {}

def save_uploaded_file(upload_file: UploadFile) -> Path:
    """
    Guarda un archivo subido a un directorio temporal.
    
    Args:
        upload_file: Archivo subido por el usuario
        
    Returns:
        Ruta donde se guardó el archivo
    """
    # Generar nombre único para evitar conflictos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Identificador único
    original_name = upload_file.filename
    safe_name = f"{timestamp}_{unique_id}_{original_name}"
    
    # Ruta de destino
    file_path = TEMP_DIR / safe_name
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def process_document_background(job_id: str, file_path: Path, language: str, extract_keywords: bool, extract_entities: bool):
    """
    Procesa un documento en segundo plano.
    
    Esta función se ejecuta en segundo plano para no bloquear la API
    mientras se procesa un documento, que puede llevar tiempo.
    
    Args:
        job_id: Identificador único del trabajo
        file_path: Ruta al archivo a procesar
        language: Idioma del documento
        extract_keywords: Si se deben extraer palabras clave
        extract_entities: Si se deben extraer entidades
    """
    try:
        # Actualizar estado
        processing_jobs[job_id]["status"] = ProcessingStatus.PROCESSING
        
        # Extraer texto según el tipo de archivo
        file_extension = file_path.suffix.lower()
        
        if file_extension == ".pdf":
            # Procesar PDF
            extracted_texts = text_extractor.extract_from_pdf(pdf_path=str(file_path))
            # Unir textos de todas las páginas
            extracted_text = "\n\n".join(extracted_texts)
        else:  # Tratar como imagen
            # Procesar imagen
            import cv2
            img = cv2.imread(str(file_path))
            extracted_text = text_extractor.extract_from_image(img)
        
        # Guardar el texto extraído
        processing_jobs[job_id]["text"] = extracted_text
        
        # Procesar con NLP si se solicita
        if extract_keywords:
            # Extraer palabras clave
            keywords = keyword_extractor.extract_keywords(extracted_text, method="combined")
            processing_jobs[job_id]["keywords"] = keywords
        
        if extract_entities:
            # Extraer entidades nombradas
            entities = entity_extractor.extract_main_entities(extracted_text)
            processing_jobs[job_id]["entities"] = entities
        
        # Actualizar estado a completado
        processing_jobs[job_id]["status"] = ProcessingStatus.COMPLETED
        
    except Exception as e:
        logger.error(f"Error procesando documento {job_id}: {str(e)}")
        processing_jobs[job_id]["status"] = ProcessingStatus.FAILED
        processing_jobs[job_id]["error"] = str(e)

@router.post("/extract-text", response_model=ExtractTextResponse)
async def extract_text(
    file: UploadFile = File(...),
    language: str = Form("eng"),
):
    """
    Endpoint para extraer texto de un archivo PDF o imagen.
    
    Este es el punto de entrada para la funcionalidad básica de OCR.
    Los usuarios envían un archivo y reciben un ID de trabajo para
    consultar el resultado más tarde.
    
    Args:
        file: Archivo a procesar (PDF o imagen)
        language: Idioma del documento
        
    Returns:
        ID del trabajo y estado inicial
    """
    try:
        logger.info(f"Recibiendo archivo: {file.filename}")
        
        # Validar tipo de archivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Guardar archivo
        file_path = save_uploaded_file(file)
        logger.info(f"Archivo guardado en: {file_path}")
        
        # Determinar tipo de documento
        doc_type = DocumentType.PDF if file_extension == ".pdf" else DocumentType.IMAGE
        
        # Generar ID de trabajo único
        job_id = str(uuid.uuid4())
        
        # Inicializar estado del trabajo
        processing_jobs[job_id] = {
            "id": job_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "type": doc_type,
            "language": language,
            "status": ProcessingStatus.QUEUED,
            "created_at": datetime.now().isoformat(),
            "text": None,
            "keywords": None,
            "entities": None,
            "error": None
        }
        
        return ExtractTextResponse(
            job_id=job_id,
            status=ProcessingStatus.QUEUED,
            message="Archivo recibido. Procesamiento en cola."
        )
        
    except Exception as e:
        logger.error(f"Error en extract_text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest
):
    """
    Endpoint para analizar un documento completo.
    
    Este endpoint es más avanzado y puede extraer texto, palabras clave
    y entidades de un documento. El procesamiento se realiza en segundo
    plano para no bloquear la API.
    
    Args:
        background_tasks: Gestor de tareas en segundo plano
        request: Solicitud con el archivo y opciones
        
    Returns:
        ID del trabajo y estado inicial
    """
    try:
        logger.info(f"Recibiendo solicitud de análisis para archivo")
        
        # Validar tipo de archivo
        file_extension = os.path.splitext(request.file.filename)[1].lower()
        if file_extension not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Guardar archivo
        file_path = save_uploaded_file(request.file)
        logger.info(f"Archivo guardado en: {file_path}")
        
        # Determinar tipo de documento
        doc_type = DocumentType.PDF if file_extension == ".pdf" else DocumentType.IMAGE
        
        # Generar ID de trabajo único
        job_id = str(uuid.uuid4())
        
        # Inicializar estado del trabajo
        processing_jobs[job_id] = {
            "id": job_id,
            "filename": request.file.filename,
            "file_path": str(file_path),
            "type": doc_type,
            "language": request.language,
            "status": ProcessingStatus.QUEUED,
            "created_at": datetime.now().isoformat(),
            "text": None,
            "keywords": None,
            "entities": None,
            "error": None
        }
        
        # Iniciar procesamiento en segundo plano
        # Esto permite que la API responda inmediatamente mientras
        # el procesamiento ocurre en paralelo
        background_tasks.add_task(
            process_document_background,
            job_id,
            file_path,
            request.language,
            request.extract_keywords,
            request.extract_entities
        )
        
        return AnalysisResponse(
            job_id=job_id,
            status=ProcessingStatus.QUEUED,
            message="Archivo recibido. Procesamiento iniciado."
        )
        
    except Exception as e:
        logger.error(f"Error en analyze_document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Obtiene el estado actual y resultados de un trabajo.
    
    Este endpoint permite a los clientes verificar si su trabajo
    ha sido completado y obtener los resultados.
    
    Args:
        job_id: ID del trabajo a consultar
        
    Returns:
        Estado actual y resultados si está completado
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    job = processing_jobs[job_id]
    
    # Formatear respuesta según el estado
    response = {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "filename": job["filename"],
        "type": job["type"]
    }
    
    # Incluir resultados si está completo
    if job["status"] == ProcessingStatus.COMPLETED:
        response["text"] = job["text"]
        if job["keywords"]:
            response["keywords"] = job["keywords"]
        if job["entities"]:
            response["entities"] = job["entities"]
    
    # Incluir error si falló
    if job["status"] == ProcessingStatus.FAILED:
        response["error"] = job["error"]
    
    return response

@router.get("/jobs")
async def list_jobs():
    """
    Lista todos los trabajos de procesamiento.
    
    Este endpoint permite ver un resumen de todos los trabajos
    que están en el sistema, tanto completados como en proceso.
    
    Returns:
        Lista de resúmenes de trabajos
    """
    job_summaries = []
    for job_id, job in processing_jobs.items():
        job_summaries.append({
            "job_id": job_id,
            "status": job["status"],
            "created_at": job["created_at"],
            "filename": job["filename"],
            "type": job["type"]
        })
    
    return {"jobs": job_summaries}
