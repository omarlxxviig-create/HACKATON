# Guía de instalación paso a paso

Esta guía te ayudará a instalar y configurar el Sistema de Extracción y Análisis Inteligente de Documentos, incluso si nunca has programado antes.

## Requisitos previos

Necesitarás instalar dos cosas:

1. **Python** (el lenguaje de programación)
2. **Tesseract OCR** (el motor que reconoce texto en imágenes)

## Paso 1: Instalar Python

1. **Descargar Python**:

   - Ve a [python.org](https://www.python.org/downloads/)
   - Haz clic en el botón "Download Python" (la versión más reciente)

2. **Instalar Python**:

   - Ejecuta el instalador descargado
   - **¡IMPORTANTE!** Marca la casilla "Add Python to PATH"
   - Haz clic en "Install Now"

3. **Verificar la instalación**:
   - Abre la línea de comandos:
     - En Windows: Presiona la tecla Windows, escribe "cmd" y presiona Enter
     - En Mac: Abre Terminal desde Aplicaciones > Utilidades
   - Escribe `python --version` y presiona Enter
   - Deberías ver algo como "Python 3.9.x"

## Paso 2: Instalar Tesseract OCR

### Para Windows:

1. **Descargar Tesseract**:

   - Ve a [este enlace](https://github.com/UB-Mannheim/tesseract/wiki)
   - Descarga la versión más reciente (por ejemplo, tesseract-ocr-w64-setup-v5.0.0.20190623.exe)

2. **Instalar Tesseract**:

   - Ejecuta el instalador
   - Recuerda la ruta de instalación (por defecto es `C:\Program Files\Tesseract-OCR`)
   - En "Additional language data", selecciona los idiomas que necesites (al menos English)
   - Completa la instalación

3. **Verificar la instalación**:
   - Abre la línea de comandos (cmd)
   - Escribe `"C:\Program Files\Tesseract-OCR\tesseract.exe" --version` y presiona Enter
   - Deberías ver la versión de Tesseract

### Para Mac:

1. **Instalar Homebrew** (si no lo tienes):

   - Abre Terminal
   - Ejecuta:
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

2. **Instalar Tesseract**:

   - Ejecuta:
     ```
     brew install tesseract
     ```

3. **Verificar la instalación**:
   - Ejecuta:
     ```
     tesseract --version
     ```

### Para Linux (Ubuntu/Debian):

1. **Instalar Tesseract**:

   - Abre Terminal
   - Ejecuta:
     ```
     sudo apt update
     sudo apt install tesseract-ocr
     sudo apt install libtesseract-dev
     ```

2. **Verificar la instalación**:
   - Ejecuta:
     ```
     tesseract --version
     ```

## Paso 3: Instalar el sistema

1. **Descargar el proyecto**:

   - Descarga y descomprime el proyecto en tu computadora
   - Recuerda la ubicación donde lo descomprimiste

2. **Abrir una terminal o línea de comandos**:

   - Navega hasta la carpeta del proyecto:
     ```
     cd ruta/a/la/carpeta/HACKATON
     ```
     Reemplaza "ruta/a/la/carpeta" con la ubicación real

3. **Crear entorno virtual** (aísla las dependencias):

   - Ejecuta:
     ```
     python -m venv venv
     ```

4. **Activar el entorno virtual**:

   - En Windows:
     ```
     venv\Scripts\activate
     ```
   - En Mac/Linux:
     ```
     source venv/bin/activate
     ```
   - Sabrás que está activado cuando veas `(venv)` al inicio de la línea de comandos

5. **Instalar dependencias**:

   - Ejecuta:
     ```
     pip install -r requirements.txt
     ```
   - Este paso puede tardar varios minutos

6. **Descargar modelos de lenguaje**:

   - Ejecuta:
     ```
     python -m spacy download en_core_web_md
     python -m spacy download es_core_news_md
     ```

7. **Configurar el sistema**:
   - Crea un archivo llamado `.env` en la carpeta principal
   - Copia el contenido de `.env.example` a este nuevo archivo
   - Si estás en Windows, actualiza la ruta de Tesseract:
     ```
     TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
     ```

## Paso 4: Iniciar el sistema

1. **Activar el entorno virtual** (si no está activo):

   - En Windows:
     ```
     venv\Scripts\activate
     ```
   - En Mac/Linux:
     ```
     source venv/bin/activate
     ```

2. **Iniciar el sistema**:

   - Ejecuta:
     ```
     python main.py
     ```
   - Deberías ver mensajes indicando que el servidor ha iniciado

3. **Verificar que el sistema está funcionando**:
   - Abre tu navegador web
   - Ve a:
     ```
     http://localhost:8000/docs
     ```
   - Deberías ver la interfaz de documentación de la API

## Paso 5: Usar el sistema

Ahora que el sistema está funcionando, puedes:

1. **Ver la documentación interactiva**:

   - Navega a `http://localhost:8000/docs`
   - Esta interfaz te permite probar todas las funcionalidades

2. **Procesar un documento**:

   - En la interfaz de documentación, haz clic en `/api/v1/analyze`
   - Haz clic en "Try it out"
   - Sube un archivo PDF o imagen
   - Haz clic en "Execute"
   - Obtendrás un ID de trabajo

3. **Consultar resultados**:
   - En la interfaz de documentación, haz clic en `/api/v1/jobs/{job_id}`
   - Introduce el ID de trabajo obtenido anteriormente
   - Haz clic en "Execute"
   - Verás los resultados del procesamiento (texto extraído, palabras clave, entidades)

## Solución de problemas comunes

### "No se pudo encontrar tesseract"

- **Causa**: La ruta a Tesseract no está bien configurada
- **Solución**: Edita el archivo `.env` y asegúrate de que TESSERACT_PATH apunte a la ubicación correcta

### "No module named X"

- **Causa**: Alguna dependencia no está instalada
- **Solución**:
  - Asegúrate de que el entorno virtual está activado (verás `(venv)` al inicio de la línea de comandos)
  - Vuelve a ejecutar `pip install -r requirements.txt`

### "No se pueden descargar modelos de spaCy"

- **Causa**: Problemas de conexión o permisos
- **Solución**:
  - Asegúrate de tener conexión a internet
  - Prueba ejecutar el comando con permisos de administrador

### "El servidor no inicia"

- **Causa**: Puerto en uso o problemas de permisos
- **Solución**:
  - Cambia el puerto en el archivo `.env` (por ejemplo, API_PORT=8080)
  - Cierra aplicaciones que puedan estar usando el puerto
