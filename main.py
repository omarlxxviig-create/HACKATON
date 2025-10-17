#!/usr/bin/env python
"""
PROGRAMA PRINCIPAL DEL SISTEMA DE EXTRACCIÓN Y ANÁLISIS INTELIGENTE DE DOCUMENTOS

Este es el punto de entrada principal del sistema. Al ejecutar este archivo,
se inicia todo el sistema con su API y procesamiento de documentos.

Es como el "botón de encendido" de toda la aplicación.
"""

import os
import argparse
from loguru import logger

# Importar componentes
from src.api.app import start_server
from src.utils.logger import get_logger
import config

def main():
    """
    Función principal del programa.
    
    Esta función se ejecuta cuando iniciamos el programa y se encarga de:
    1. Configurar los registros (logs)
    2. Procesar argumentos de línea de comandos
    3. Verificar directorios necesarios
    4. Iniciar el servidor API
    """
    # Configurar logger para registrar actividades
    log = get_logger("main")
    
    # Configurar argumentos de línea de comandos
    # Estos argumentos permiten personalizar cómo se inicia el programa
    parser = argparse.ArgumentParser(
        description="Sistema de Extracción y Análisis Inteligente de Documentos"
    )
    parser.add_argument(
        "--api-only", 
        action="store_true", 
        help="Iniciar solo el servidor API"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default=config.API_HOST,
        help=f"Host para el servidor API (default: {config.API_HOST})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=config.API_PORT,
        help=f"Puerto para el servidor API (default: {config.API_PORT})"
    )
    
    # Procesar los argumentos proporcionados
    args = parser.parse_args()
    
    # Actualizar configuración si se especificaron argumentos
    if args.host != config.API_HOST:
        config.API_HOST = args.host
        log.info(f"Host de API actualizado a: {args.host}")
        
    if args.port != config.API_PORT:
        config.API_PORT = args.port
        log.info(f"Puerto de API actualizado a: {args.port}")
    
    # Verificar que existan los directorios necesarios
    for directory in [config.INPUT_DIR, config.OUTPUT_DIR, config.LOG_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            log.info(f"Directorio creado: {directory}")
    
    # Iniciar servidor API
    log.info("Iniciando Sistema de Extracción y Análisis Inteligente de Documentos")
    try:
        # Esta función inicia el servidor web y no retorna hasta que se detenga
        start_server()
    except KeyboardInterrupt:
        # Capturar cuando el usuario presiona Ctrl+C para detener el programa
        log.info("Sistema detenido por el usuario")
    except Exception as e:
        # Capturar cualquier error inesperado
        log.error(f"Error al iniciar el sistema: {str(e)}")
        return 1
    
    return 0

# Este bloque se ejecuta cuando el archivo se corre directamente
if __name__ == "__main__":
    exit(main())
