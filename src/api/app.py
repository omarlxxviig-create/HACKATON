"""
APLICACIÓN API PRINCIPAL

Este archivo crea y configura la interfaz de programación (API)
que permite a otros sistemas comunicarse con nuestro servicio.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import os
import uuid
import cv2
import config
from ..ocr.extractor import extraer_texto_imagen, extraer_texto_pdf
from ..nlp.keyword_extraction import ExtractorPalabrasClave
from ..nlp.entity_extraction import ExtractorEntidades

app = FastAPI(title="API de Extracción y Análisis de Documentos", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar extractores NLP
extractor_palabras_es = ExtractorPalabrasClave(idioma="es")
extractor_palabras_en = ExtractorPalabrasClave(idioma="en")
extractor_entidades_es = ExtractorEntidades(idioma="spa")
extractor_entidades_en = ExtractorEntidades(idioma="eng")

@app.get("/")
def inicio():
    return {
        "mensaje": "API de Extracción y Análisis de Documentos",
        "version": "1.0",
        "endpoints": {
            "procesar": "POST /procesar-documento - Extrae texto y análisis NLP",
            "conciliar": "POST /conciliar-documentos - Compara pedido y factura"
        },
        "descripcion": "Sube archivos (imágenes o PDFs) para procesar y analizar",
        "documentacion": "/docs"
    }

@app.post("/procesar-documento")
async def procesar_documento(
    archivo: UploadFile = File(...),
    preprocesar: bool = Query(True, description="Mejorar calidad de imagen antes de extraer texto"),
    analisis_nlp: bool = Query(False, description="Realizar análisis NLP (palabras clave y entidades)"),
    idioma: str = Query("es", description="Idioma del documento (es/en)"),
    num_palabras_clave: int = Query(10, description="Número de palabras clave a extraer")
):
    """
    Procesa un documento completo: extracción de texto y análisis NLP opcional.
    
    - Extrae texto de imágenes o PDFs usando OCR
    - Opcionalmente realiza análisis NLP (palabras clave y entidades)
    - Devuelve confianza y calidad del OCR
    """
    
    if archivo.filename is None:
        raise HTTPException(400, "Nombre de archivo inválido")
    
    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        raise HTTPException(400, "Formato no soportado. Use: PDF, PNG, JPG, JPEG, TIFF o BMP")
    
    ruta_temp = config.OUTPUT_DIR / f"{uuid.uuid4()}{extension}"
    
    try:
        # Guardar archivo temporal
        contenido = await archivo.read()
        with open(ruta_temp, "wb") as f:
            f.write(contenido)
        
        # Extraer texto con OCR
        if extension == ".pdf":
            texto, confianza = extraer_texto_pdf(str(ruta_temp), preprocesar=preprocesar)
        else:
            imagen = cv2.imread(str(ruta_temp))
            if imagen is None:
                raise HTTPException(400, "No se pudo leer la imagen")
            texto, confianza = extraer_texto_imagen(imagen, preprocesar=preprocesar)
        
        # Preparar respuesta base
        resultado = {
            "archivo": archivo.filename,
            "texto": texto,
            "ocr": {
                "preprocesado": preprocesar,
                "confianza": round(confianza, 2),
                "calidad": (
                    "excelente" if confianza >= 80 else 
                    "buena" if confianza >= 60 else 
                    "aceptable" if confianza >= 40 else 
                    "baja"
                )
            }
        }
        
        # Análisis NLP opcional
        if analisis_nlp and texto.strip():
            # Seleccionar extractores según idioma
            extractor_palabras = extractor_palabras_es if idioma == "es" else extractor_palabras_en
            extractor_ents = extractor_entidades_es if idioma == "es" else extractor_entidades_en
            
            resultado["nlp"] = {
                "idioma": idioma
            }
            
            # Extraer palabras clave
            try:
                palabras_clave = extractor_palabras.extraer_palabras_clave(
                    texto, 
                    metodo="yake", 
                    cantidad=num_palabras_clave
                )
                resultado["nlp"]["palabras_clave"] = [
                    {"palabra": kw, "relevancia": round(score, 3)} 
                    for kw, score in palabras_clave
                ]
            except Exception as e:
                resultado["nlp"]["palabras_clave"] = []
                resultado["nlp"]["error_palabras_clave"] = str(e)
            
            # Extraer entidades
            try:
                entidades = extractor_ents.extraer_entidades_principales(texto)
                resultado["nlp"]["entidades"] = entidades
            except Exception as e:
                resultado["nlp"]["entidades"] = {}
                resultado["nlp"]["error_entidades"] = str(e)
        
        return resultado
    
    except Exception as e:
        raise HTTPException(500, f"Error al procesar documento: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        try:
            if ruta_temp.exists():
                import time
                time.sleep(0.1)
                ruta_temp.unlink()
        except:
            pass

@app.post("/conciliar-documentos")
async def conciliar_documentos(
    pedido: UploadFile = File(..., description="Archivo del pedido (PDF o imagen)"),
    factura: UploadFile = File(..., description="Archivo de la factura (PDF o imagen)"),
    preprocesar: bool = Query(True, description="Mejorar calidad de imagen"),
    idioma: str = Query("es", description="Idioma de los documentos (es/en)")
):
    """
    Concilia un pedido con una factura, identificando discrepancias.
    
    Compara:
    - Productos y cantidades
    - Montos totales
    - Fechas
    - Información del cliente
    
    Retorna estado de conciliación y lista de discrepancias encontradas.
    """
    
    rutas_temp = []
    
    try:
        # Validar archivos
        for archivo in [pedido, factura]:
            if archivo.filename is None:
                raise HTTPException(400, "Nombre de archivo inválido")
            
            extension = os.path.splitext(archivo.filename)[1].lower()
            if extension not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                raise HTTPException(400, f"Formato no soportado en {archivo.filename}")
        
        # Procesar pedido
        ext_pedido = os.path.splitext(pedido.filename)[1].lower()
        ruta_pedido = config.OUTPUT_DIR / f"pedido_{uuid.uuid4()}{ext_pedido}"
        rutas_temp.append(ruta_pedido)
        
        contenido_pedido = await pedido.read()
        with open(ruta_pedido, "wb") as f:
            f.write(contenido_pedido)
        
        if ext_pedido == ".pdf":
            texto_pedido, conf_pedido = extraer_texto_pdf(str(ruta_pedido), preprocesar)
        else:
            img_pedido = cv2.imread(str(ruta_pedido))
            if img_pedido is None:
                raise HTTPException(400, "No se pudo leer el pedido")
            texto_pedido, conf_pedido = extraer_texto_imagen(img_pedido, preprocesar)
        
        # Procesar factura
        ext_factura = os.path.splitext(factura.filename)[1].lower()
        ruta_factura = config.OUTPUT_DIR / f"factura_{uuid.uuid4()}{ext_factura}"
        rutas_temp.append(ruta_factura)
        
        contenido_factura = await factura.read()
        with open(ruta_factura, "wb") as f:
            f.write(contenido_factura)
        
        if ext_factura == ".pdf":
            texto_factura, conf_factura = extraer_texto_pdf(str(ruta_factura), preprocesar)
        else:
            img_factura = cv2.imread(str(ruta_factura))
            if img_factura is None:
                raise HTTPException(400, "No se pudo leer la factura")
            texto_factura, conf_factura = extraer_texto_imagen(img_factura, preprocesar)
        
        # Análisis NLP para extraer entidades
        extractor_ents = extractor_entidades_es if idioma == "es" else extractor_entidades_en
        
        entidades_pedido = extractor_ents.extraer_entidades_principales(texto_pedido)
        entidades_factura = extractor_ents.extraer_entidades_principales(texto_factura)
        
        # Realizar conciliación
        resultado_conciliacion = _conciliar_documentos_internos(
            texto_pedido, texto_factura,
            entidades_pedido, entidades_factura
        )
        
        # Preparar respuesta completa
        return {
            "estado": resultado_conciliacion["estado"],
            "discrepancias": resultado_conciliacion["discrepancias"],
            "explicacion_posible": resultado_conciliacion["explicacion_posible"],
            "detalles": {
                "pedido": {
                    "archivo": pedido.filename,
                    "confianza_ocr": round(conf_pedido, 2),
                    "resumen": resultado_conciliacion["resumen_pedido"]
                },
                "factura": {
                    "archivo": factura.filename,
                    "confianza_ocr": round(conf_factura, 2),
                    "resumen": resultado_conciliacion["resumen_factura"]
                }
            },
            "textos": {
                "pedido": texto_pedido[:500] + "..." if len(texto_pedido) > 500 else texto_pedido,
                "factura": texto_factura[:500] + "..." if len(texto_factura) > 500 else texto_factura
            }
        }
    
    except Exception as e:
        raise HTTPException(500, f"Error al conciliar documentos: {str(e)}")
    
    finally:
        # Limpiar archivos temporales
        for ruta in rutas_temp:
            try:
                if ruta.exists():
                    import time
                    time.sleep(0.1)
                    ruta.unlink()
            except:
                pass

def _conciliar_documentos_internos(texto_pedido: str, texto_factura: str, 
                                   entidades_pedido: dict, entidades_factura: dict) -> dict:
    """
    Lógica interna de conciliación entre pedido y factura.
    """
    import re
    from difflib import SequenceMatcher
    
    discrepancias = []
    
    # Extraer información clave
    def extraer_numeros(texto):
        """Extrae todos los números del texto"""
        return re.findall(r'\d+(?:[.,]\d+)*', texto)
    
    def extraer_fechas(texto):
        """Extrae fechas en varios formatos"""
        patrones = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        ]
        fechas = []
        for patron in patrones:
            fechas.extend(re.findall(patron, texto))
        return fechas
    
    def buscar_monto_total(texto):
        """Busca el monto total en el texto"""
        patrones = [
            r'total[:\s]+\$?\s*(\d+(?:[.,]\d+)*)',
            r'monto\s+total[:\s]+\$?\s*(\d+(?:[.,]\d+)*)',
            r'total\s+a\s+pagar[:\s]+\$?\s*(\d+(?:[.,]\d+)*)',
            r'\$\s*(\d+(?:[.,]\d+)*)\s*(?:total|final)',
        ]
        for patron in patrones:
            match = re.search(patron, texto.lower())
            if match:
                return match.group(1)
        return None
    
    def contar_productos(texto):
        """Estima cantidad de productos listados"""
        # Buscar líneas con cantidades y productos
        lineas_productos = re.findall(r'(?:\d+\s+(?:x|unid|pza|pcs)|\bx\s*\d+)', texto.lower())
        return len(lineas_productos)
    
    # Análisis de productos
    productos_pedido = contar_productos(texto_pedido)
    productos_factura = contar_productos(texto_factura)
    
    if abs(productos_pedido - productos_factura) > 1:
        discrepancias.append(
            f"PRODUCTOS DIFERENTES: Pedido tiene {productos_pedido} productos, "
            f"Factura tiene {productos_factura} producto{'s' if productos_factura != 1 else ''}"
        )
    
    # Análisis de cantidades totales
    numeros_pedido = extraer_numeros(texto_pedido)
    numeros_factura = extraer_numeros(texto_factura)
    
    if numeros_pedido and numeros_factura:
        # Buscar cantidades grandes (probablemente unidades totales)
        def normalizar_numero(num_str):
            return float(num_str.replace(',', ''))
        
        try:
            nums_p = [normalizar_numero(n) for n in numeros_pedido if len(n) >= 2]
            nums_f = [normalizar_numero(n) for n in numeros_factura if len(n) >= 2]
            
            if nums_p and nums_f:
                max_p = max(nums_p)
                max_f = max(nums_f)
                
                if max_f > max_p * 2 or max_p > max_f * 2:
                    discrepancias.append(
                        f"CANTIDADES NO COINCIDEN: Pedido {int(max_p)} unidades vs "
                        f"Factura {int(max_f)} unidades"
                    )
        except:
            pass
    
    # Análisis de montos
    monto_pedido = buscar_monto_total(texto_pedido)
    monto_factura = buscar_monto_total(texto_factura)
    
    if monto_pedido and monto_factura:
        try:
            mp = float(monto_pedido.replace(',', ''))
            mf = float(monto_factura.replace(',', ''))
            
            diferencia_porcentual = abs(mp - mf) / max(mp, mf) * 100
            
            if diferencia_porcentual > 10:  # Más de 10% de diferencia
                factor = max(mp, mf) / min(mp, mf)
                discrepancias.append(
                    f"MONTO TOTAL: Pedido ${monto_pedido} vs Factura ${monto_factura} "
                    f"({int(factor)}x {'mayor' if mf > mp else 'menor'})"
                )
        except:
            pass
    
    # Análisis de fechas
    fechas_pedido = extraer_fechas(texto_pedido)
    fechas_factura = extraer_fechas(texto_factura)
    
    if fechas_pedido and fechas_factura:
        if fechas_pedido[0] != fechas_factura[0]:
            discrepancias.append(
                f"FECHAS: Pedido {fechas_pedido[0]} vs Factura {fechas_factura[0]}"
            )
    
    # Análisis de entidades (cliente, organizaciones)
    clientes_pedido = set(e["texto"].lower() for e in entidades_pedido.get("personas", []))
    clientes_factura = set(e["texto"].lower() for e in entidades_factura.get("personas", []))
    
    orgs_pedido = set(e["texto"].lower() for e in entidades_pedido.get("organizaciones", []))
    orgs_factura = set(e["texto"].lower() for e in entidades_factura.get("organizaciones", []))
    
    # Verificar similitud de textos
    similitud = SequenceMatcher(None, texto_pedido.lower()[:500], texto_factura.lower()[:500]).ratio()
    
    # Determinar estado
    if not discrepancias:
        estado = "✅ CONCILIADO"
        explicacion = "Los documentos coinciden en todos los aspectos verificados"
    elif len(discrepancias) <= 2 and similitud > 0.3:
        estado = "⚠️ CONCILIADO CON DIFERENCIAS MENORES"
        explicacion = "Hay algunas diferencias menores que podrían deberse a errores de captura o ajustes posteriores"
    else:
        estado = "❌ NO CONCILIADO"
        if similitud < 0.2:
            explicacion = "Estos documentos parecen ser de TRANSACCIONES DIFERENTES"
        else:
            explicacion = "Hay discrepancias significativas que requieren revisión manual"
    
    # Agregar información sobre cliente
    cliente_comun = clientes_pedido.intersection(clientes_factura)
    org_comun = orgs_pedido.intersection(orgs_factura)
    
    if cliente_comun or org_comun:
        if estado == "❌ NO CONCILIADO":
            explicacion += " con el mismo cliente"
    
    return {
        "estado": estado,
        "discrepancias": discrepancias,
        "explicacion_posible": explicacion,
        "resumen_pedido": {
            "productos_detectados": productos_pedido,
            "monto_total": monto_pedido,
            "fechas": fechas_pedido,
            "clientes": list(clientes_pedido)[:3],
            "organizaciones": list(orgs_pedido)[:3]
        },
        "resumen_factura": {
            "productos_detectados": productos_factura,
            "monto_total": monto_factura,
            "fechas": fechas_factura,
            "clientes": list(clientes_factura)[:3],
            "organizaciones": list(orgs_factura)[:3]
        }
    }

def iniciar():
    """Inicia el servidor API"""
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)

if __name__ == "__main__":
    iniciar()
