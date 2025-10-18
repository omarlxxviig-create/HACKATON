"""
APLICACIÓN API PRINCIPAL

Este archivo crea y configura la interfaz de programación (API)
que permite a otros sistemas comunicarse con nuestro servicio.

Es como crear una "ventanilla de atención" donde otros programas
pueden solicitar servicios específicos a nuestro sistema.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import uuid
from pathlib import Path
import cv2
import config
from ..ocr.extractor import extraer_texto_imagen, extraer_texto_pdf

app = FastAPI(title="OCR Simple API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def inicio():
    return {"mensaje": "API OCR funcionando. Usa POST /extraer-texto"}

@app.post("/extraer-texto")
async def extraer_texto(archivo: UploadFile = File(...)):
    """Extrae texto de una imagen o PDF"""
    
    if archivo.filename is None:
        raise HTTPException(400, "Nombre de archivo inválido")
    
    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        raise HTTPException(400, "Formato no soportado")
    
    ruta_temp = config.OUTPUT_DIR / f"{uuid.uuid4()}{extension}"
    
    try:
        # Guardar archivo temporal
        contenido = await archivo.read()
        with open(ruta_temp, "wb") as f:
            f.write(contenido)
        
        # Extraer texto según tipo
        if extension == ".pdf":
            texto = extraer_texto_pdf(str(ruta_temp))
        else:
            imagen = cv2.imread(str(ruta_temp))
            if imagen is None:
                raise HTTPException(400, "No se pudo leer la imagen")
            texto = extraer_texto_imagen(imagen)
        
        return {"texto": texto, "archivo": archivo.filename}
    
    except Exception as e:
        raise HTTPException(500, f"Error al procesar: {str(e)}")
    
    finally:
        # Limpiar archivo temporal con reintentos
        try:
            if ruta_temp.exists():
                import time
                time.sleep(0.1)  # Esperar un momento
                ruta_temp.unlink()
        except:
            pass  # Ignorar errores al eliminar

def iniciar():
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)

if __name__ == "__main__":
    iniciar()
