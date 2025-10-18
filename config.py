"""
ARCHIVO DE CONFIGURACIÓN

Este archivo contiene todos los ajustes y parámetros que controlan cómo funciona nuestro sistema.
Es como el "panel de control" donde podemos cambiar el comportamiento sin tocar el código principal.

Aquí definimos:
- Dónde se guardan los archivos
- Qué idiomas puede procesar el sistema
- Cómo se conecta la API (dirección y puerto)
- Configuración de registros (logs)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuraciones desde el archivo .env (si existe)
# Esto permite tener configuraciones personalizadas en cada instalación
load_dotenv()

# --- CONFIGURACIÓN DE DIRECTORIOS ---
# Estas líneas definen dónde se guardarán los diferentes tipos de archivos

# BASE_DIR: La carpeta principal del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# DATA_DIR: Carpeta para todos los datos
DATA_DIR = BASE_DIR / "data"

# INPUT_DIR: Carpeta donde se guardan los documentos originales para procesar
INPUT_DIR = DATA_DIR / "input"

# OUTPUT_DIR: Carpeta donde se guardan los resultados procesados
OUTPUT_DIR = BASE_DIR / "temp"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# LOG_DIR: Carpeta para los registros del sistema (útil para depuración)
LOG_DIR = BASE_DIR / "logs"

# Crear todas estas carpetas si no existen
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- CONFIGURACIÓN DE OCR (Reconocimiento Óptico de Caracteres) ---
# Define cómo se extraerá el texto de imágenes y PDFs

# Motor OCR a utilizar (por defecto: tesseract)
OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract")

# Ruta al programa Tesseract (necesario cambiarlo según dónde esté instalado)
TESSERACT_PATH = os.getenv("TESSERACT_PATH")

if not TESSERACT_PATH:
    # Intentar encontrar Tesseract automáticamente
    posibles_rutas = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            TESSERACT_PATH = ruta
            break

# Idiomas que puede reconocer el OCR (eng=inglés, spa=español)
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng+spa").split("+")

# --- CONFIGURACIÓN DE NLP (Procesamiento de Lenguaje Natural) ---
# Define cómo se analiza el texto extraído

# Modelos de lenguaje para cada idioma soportado
NLP_MODELS = {
    "eng": "en_core_web_md",  # Modelo en inglés
    "spa": "es_core_news_md"  # Modelo en español
}

# Idioma predeterminado para el análisis
DEFAULT_NLP_LANGUAGE = os.getenv("DEFAULT_NLP_LANGUAGE", "eng")

# --- CONFIGURACIÓN DE API ---
# Define cómo se conectarán otros programas con nuestro sistema

# Dirección IP donde se ejecutará la API (0.0.0.0 significa "todas las direcciones")
API_HOST = os.getenv("API_HOST", "0.0.0.0")

# Puerto de red para la API
API_PORT = int(os.getenv("API_PORT", "8000"))

# Modo de depuración (para desarrollo)
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# --- CONFIGURACIÓN DE REGISTROS (LOGS) ---
# Define cómo se guardan los registros de actividad del sistema

# Nivel de detalle de los registros (INFO, DEBUG, ERROR, etc.)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Archivo donde se guardan los registros
LOG_FILE = LOG_DIR / "app.log"
