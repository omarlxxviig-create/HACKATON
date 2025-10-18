# OCR Simple API

Sistema minimalista para extraer texto de imágenes y PDFs.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Instala Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

Crea `.env`:

```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Uso

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
