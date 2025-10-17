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
    log = get_logger("principal")
    
    # Configurar argumentos de línea de comandos
    # Estos argumentos permiten personalizar cómo se inicia el programa
    analizador = argparse.ArgumentParser(
        description="Sistema de Extracción y Análisis Inteligente de Documentos"
    )
    analizador.add_argument(
        "--solo-api", 
        action="store_true", 
        help="Iniciar solo el servidor API"
    )
    analizador.add_argument(
        "--host", 
        type=str, 
        default=config.API_HOST,
        help=f"Host para el servidor API (predeterminado: {config.API_HOST})"
    )
    analizador.add_argument(
        "--puerto", 
        type=int, 
        default=config.API_PORT,
        help=f"Puerto para el servidor API (predeterminado: {config.API_PORT})"
    )
    
    # Procesar los argumentos proporcionados
    argumentos = analizador.parse_args()
    
    # Actualizar configuración si se especificaron argumentos
    if argumentos.host != config.API_HOST:
        config.API_HOST = argumentos.host
        log.info(f"Host de API actualizado a: {argumentos.host}")
        
    if argumentos.puerto != config.API_PORT:
        config.API_PORT = argumentos.puerto
        log.info(f"Puerto de API actualizado a: {argumentos.puerto}")
    
    # Verificar que existan los directorios necesarios
    for directorio in [config.INPUT_DIR, config.OUTPUT_DIR, config.LOG_DIR]:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            log.info(f"Directorio creado: {directorio}")
    
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
