# Instalación Simplificada (Sin configuración de PATH)

Esta guía te ayuda a instalar el sistema usando solo PyMuPDF para PDFs, eliminando la necesidad de configurar Poppler en el PATH.

## Requisitos

Solo necesitas:

1. **Python 3.9+**
2. **Tesseract OCR**

## Paso 1: Instalar Tesseract OCR

### Windows:

1. Descarga el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecuta el instalador
3. Anota la ruta de instalación (ejemplo: `C:\Program Files\Tesseract-OCR`)

### Linux:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

### macOS:

```bash
brew install tesseract
```

## Paso 2: Instalar el proyecto

1. **Clonar o descargar el proyecto**
2. **Crear entorno virtual**:

   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**:

   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Descargar modelos de lenguaje**:
   ```bash
   python -m spacy download en_core_web_md
   python -m spacy download es_core_news_md
   ```

## Paso 3: Configurar

1. **Crear archivo `.env`** en la raíz del proyecto:

   ```
   # Solo necesitas configurar la ruta de Tesseract
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

   # El resto usa valores por defecto
   OCR_LANGUAGES=eng+spa
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

   **Nota**: En Linux/Mac, generalmente no necesitas configurar `TESSERACT_PATH` si Tesseract está en el PATH del sistema.

## Paso 4: Probar la instalación

```bash
python diagnostico_ocr.py
```

Esto verificará que todo esté configurado correctamente.

## Paso 5: Iniciar el sistema

```bash
python main.py
```

## Ventajas de usar PyMuPDF en lugar de pdf2image

1. ✅ **No requiere Poppler**: PyMuPDF es una biblioteca Python pura
2. ✅ **Más rápido**: Conversión más eficiente de PDF a imágenes
3. ✅ **Más fácil de instalar**: Solo `pip install PyMuPDF`
4. ✅ **Multiplataforma**: Funciona igual en Windows, Linux y macOS
5. ✅ **Sin configuración de PATH**: Todo se maneja dentro de Python

## Solución de problemas

### "TesseractNotFoundError"

- Asegúrate de que Tesseract esté instalado
- Verifica la ruta en el archivo `.env`
- En Windows, usa barras invertidas dobles: `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`

### "No module named 'fitz'"

- Instala PyMuPDF: `pip install PyMuPDF`

### El PDF no se procesa

- Verifica que el PDF no esté protegido con contraseña
- Asegúrate de que el archivo PDF no esté corrupto
- Revisa los logs en `logs/app.log`
