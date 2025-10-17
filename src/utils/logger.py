"""
SISTEMA DE REGISTRO (LOGGER)

Este archivo configura cómo el sistema guarda información sobre lo que está haciendo.
Es como el "diario" o "bitácora" del sistema, que registra todo lo que ocurre.

Estos registros (logs) son muy útiles para:
1. Entender qué está haciendo el sistema en cada momento
2. Diagnosticar problemas cuando algo no funciona
3. Tener un historial de actividades para auditoría

La información se guarda tanto en un archivo como en la consola,
con diferentes colores según la importancia del mensaje.
"""

import logging
import sys
from loguru import logger
import config

# Quitar la configuración predeterminada
logger.remove()

# Configurar el registro en archivo
# - Rotación diaria: cada día se crea un nuevo archivo
# - Retención: se guardan los registros de los últimos 30 días
# - Se usa el nivel de detalle definido en la configuración
logger.add(
    config.LOG_FILE,
    rotation="1 day",
    retention="30 days",
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Configurar el registro en consola (con colores)
logger.add(
    sys.stderr,
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    colorize=True
)

def get_logger(name):
    """
    Crea un registrador personalizado para cada parte del sistema.
    
    Esto permite saber qué componente generó cada mensaje de registro.
    """
    return logger.bind(name=name)

# --- INTEGRACIÓN CON OTRAS BIBLIOTECAS ---
# Esta parte es técnica y permite que otras bibliotecas
# también usen nuestro sistema de registro

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Obtener el logger correspondiente desde loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

# Configurar el manejador para las bibliotecas que usan logging
logging.basicConfig(handlers=[InterceptHandler()], level=0)

# Reemplazar los loggers de bibliotecas comunes
for _log in ['uvicorn', 'uvicorn.error', 'fastapi']:
    _logger = logging.getLogger(_log)
    _logger.handlers = [InterceptHandler()]
