#!/usr/bin/env python
"""
PROGRAMA PRINCIPAL DEL SISTEMA DE EXTRACCIÓN Y ANÁLISIS INTELIGENTE DE DOCUMENTOS

Este es el punto de entrada principal del sistema.
"""

import os
import sys
import argparse

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar configuración primero
import config

# Importar logger
from src.utils.logger import get_logger

def main():
    """
    Función principal del programa.
    """
    # Configurar logger para registrar actividades
    log = get_logger("principal")
    
    # Configurar argumentos de línea de comandos
    analizador = argparse.ArgumentParser(
        description="Sistema de Extracción y Análisis Inteligente de Documentos"
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
    log.info(f"Documentación disponible en: http://{config.API_HOST}:{config.API_PORT}/docs")
    
    try:
        # Importar aquí para evitar problemas de importación circular
        from src.api.app import iniciar
        iniciar()
    except KeyboardInterrupt:
        log.info("Sistema detenido por el usuario")
    except Exception as e:
        log.error(f"Error al iniciar el sistema: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
