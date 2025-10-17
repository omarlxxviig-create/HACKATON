# Sistema de Extracción y Análisis Inteligente de Documentos

Este proyecto implementa un sistema que utiliza Inteligencia Artificial para extraer texto y analizar el contenido de documentos PDF e imágenes. Combina técnicas de reconocimiento óptico de caracteres (OCR) y procesamiento de lenguaje natural (NLP).

## ¿Qué hace este sistema?

Este sistema es capaz de:

1. **Extraer texto** de documentos PDF y imágenes escaneadas
2. **Identificar palabras clave** importantes en el contenido
3. **Reconocer entidades** como nombres de personas, organizaciones, lugares, fechas, etc.
4. **Exponer toda esta funcionalidad** a través de una API web

Es como tener un asistente que puede leer documentos y destacar la información más relevante automáticamente.

## Componentes principales

El sistema está dividido en varios módulos:

### 1. Módulo OCR (Reconocimiento Óptico de Caracteres)

Este módulo se encarga de "leer" el texto en imágenes y PDF escaneados. Incluye:

- Preprocesamiento de imágenes para mejorar la calidad
- Corrección de orientación si el documento está rotado
- Extracción del texto usando la herramienta Tesseract

### 2. Módulo NLP (Procesamiento de Lenguaje Natural)

Este módulo analiza el texto extraído para encontrar información relevante. Incluye:

- Extracción de palabras clave usando varios algoritmos
- Identificación de entidades nombradas (personas, organizaciones, etc.)
- Clasificación del contenido

### 3. API (Interfaz de Programación)

Este módulo permite que otros sistemas se comuniquen con nuestro sistema. Incluye:

- Endpoints para subir documentos
- Procesamiento en segundo plano para tareas largas
- Consulta de resultados cuando el procesamiento termina

## Instalación para no programadores

### Requisitos previos

1. **Python**: Necesitarás Python 3.9 o superior.

   - Descarga desde [python.org](https://www.python.org/downloads/)
   - Durante la instalación, marca la opción "Add Python to PATH"

2. **Tesseract OCR**: El motor de reconocimiento de texto en imágenes.
   - Para Windows: Descarga el instalador desde [aquí](https://github.com/UB-Mannheim/tesseract/wiki)
   - Para Mac: Instala con `brew install tesseract`
   - Para Linux: Instala con `sudo apt install tesseract-ocr`

### Pasos de instalación

1. **Descargar el proyecto**:

   - Descarga y descomprime el proyecto en tu computadora

2. **Abrir una terminal o símbolo del sistema**:

   - En Windows: Busca "cmd" o "PowerShell" en el menú inicio
   - En Mac/Linux: Abre la aplicación "Terminal"

3. **Navegar a la carpeta del proyecto**:

   ```
   cd ruta/a/la/carpeta/HACKATON
   ```

4. **Crear un entorno virtual**:

   ```
   python -m venv venv
   ```

5. **Activar el entorno virtual**:

   - En Windows:
     ```
     venv\Scripts\activate
     ```
   - En Mac/Linux:
     ```
     source venv/bin/activate
     ```

6. **Instalar las dependencias**:

   ```
   pip install -r requirements.txt
   ```

7. **Descargar modelos de lenguaje**:
   ```
   python -m spacy download en_core_web_md
   python -m spacy download es_core_news_md
   ```

## Uso para no programadores

1. **Iniciar el sistema**:

   ```
   python main.py
   ```

   Esto iniciará el servidor en el puerto 8000 por defecto.

2. **Acceder a la API**:

   - Si tienes alguna interfaz para probar APIs (como Postman), puedes usarla
   - También puedes acceder desde un navegador a:
     ```
     http://localhost:8000/docs
     ```
     Esto abrirá una interfaz interactiva donde puedes probar todas las funciones.

3. **Verificar que el sistema está funcionando**:

   ```
   http://localhost:8000/health
   ```

   Deberías ver un mensaje indicando que el sistema está funcionando.

4. **Para procesar un documento**:
   - Usa el endpoint `/api/v1/analyze` para subir un archivo
   - Obtendrás un ID de trabajo
   - Usa el endpoint `/api/v1/jobs/{job_id}` con el ID obtenido para consultar el resultado

## Estructura de carpetas

```
HACKATON/
├── src/                      # Código fuente
│   ├── ocr/                  # Módulo OCR
│   ├── nlp/                  # Módulo NLP
│   ├── api/                  # Módulo API
│   └── utils/                # Utilidades
├── data/                     # Datos
│   ├── input/                # Archivos de entrada
│   └── output/               # Resultados
├── logs/                     # Registros
├── main.py                   # Punto de entrada
└── config.py                 # Configuración
```

## Solución de problemas comunes

1. **Error: "No module named X"**

   - Asegúrate de haber instalado todas las dependencias: `pip install -r requirements.txt`

2. **Error con Tesseract**

   - Verifica que Tesseract está instalado correctamente
   - Actualiza la ruta a Tesseract en un archivo `.env`:
     ```
     TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
     ```

3. **El servidor no inicia**

   - Verifica que no haya otro programa usando el puerto 8000
   - Prueba con otro puerto: `python main.py --port 8080`

4. **Procesamiento lento**
   - El OCR y NLP pueden ser procesos lentos, especialmente para documentos grandes
   - Considera dividir documentos grandes en partes más pequeñas
