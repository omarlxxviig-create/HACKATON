"""
APLICACIÓN API PRINCIPAL

Este archivo crea y configura la interfaz de programación (API)
que permite a otros sistemas comunicarse con nuestro servicio.

Es como crear una "ventanilla de atención" donde otros programas
pueden solicitar servicios específicos a nuestro sistema.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger

import config
from .endpoints import router as api_router

# Configurar logger
logger = logger.bind(name="api")

def create_app():
    """
    Crea y configura la aplicación FastAPI.
    
    FastAPI es un framework para crear APIs web rápidas y fáciles de usar.
    Esta función configura todos los aspectos necesarios de la API.
    """
    logger.info("Iniciando aplicación FastAPI")
    
    # Crear la aplicación con información descriptiva
    app = FastAPI(
        title="Sistema de Extracción y Análisis Inteligente de Documentos",
        description="API para extraer texto y realizar análisis de contenido en documentos PDF e imágenes",
        version="1.0.0",
    )
    
    # Configurar CORS (Cross-Origin Resource Sharing)
    # Esto permite que páginas web en otros dominios puedan usar nuestra API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permitir todas las fuentes (en producción es mejor restringirlo)
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
        allow_headers=["*"],  # Permitir todas las cabeceras HTTP
    )
    
    # Incluir todos los endpoints (rutas de la API) definidos en endpoints.py
    app.include_router(api_router, prefix="/api/v1")
    
    # Endpoint simple para verificar si la API está funcionando
    @app.get("/health")
    async def health_check():
        """Endpoint para verificar el estado del servicio"""
        return {"status": "healthy"}
    
    return app

def start_server():
    """
    Inicia el servidor web para la API.
    
    Esta función crea la aplicación y luego inicia un servidor
    web (uvicorn) que la hace disponible en la red.
    """
    app = create_app()
    logger.info(f"Iniciando servidor en {config.API_HOST}:{config.API_PORT}")
    
    # Iniciar el servidor uvicorn
    uvicorn.run(
        app, 
        host=config.API_HOST,  # Dirección IP donde escuchar
        port=config.API_PORT,  # Puerto donde escuchar
        log_level="info",      # Nivel de detalle de los logs
    )

# Si este archivo se ejecuta directamente, iniciar el servidor
if __name__ == "__main__":
    start_server()
