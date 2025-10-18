"""
Script de diagnóstico para identificar problemas con OCR y PDF
"""

import sys
import os
from pathlib import Path

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    print("=" * 60)
    print("VERIFICANDO DEPENDENCIAS")
    print("=" * 60)
    
    dependencias = {
        'pytesseract': 'OCR',
        'cv2': 'OpenCV (procesamiento de imágenes)',
        'pdf2image': 'Conversión de PDF a imágenes',
        'PIL': 'Pillow (manejo de imágenes)',
        'numpy': 'NumPy (arrays numéricos)'
    }
    
    for modulo, descripcion in dependencias.items():
        try:
            if modulo == 'cv2':
                import cv2
            elif modulo == 'PIL':
                from PIL import Image
            else:
                __import__(modulo)
            print(f"✓ {modulo:20s} - OK ({descripcion})")
        except ImportError as e:
            print(f"✗ {modulo:20s} - FALTA ({descripcion})")
            print(f"  Error: {str(e)}")

def verificar_tesseract():
    """Verifica que Tesseract esté instalado y accesible"""
    print("\n" + "=" * 60)
    print("VERIFICANDO TESSERACT OCR")
    print("=" * 60)
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract versión: {version}")
        
        # Verificar idiomas disponibles
        try:
            langs = pytesseract.get_languages()
            print(f"✓ Idiomas disponibles: {', '.join(langs)}")
        except:
            print("⚠ No se pudieron obtener los idiomas disponibles")
            
    except Exception as e:
        print(f"✗ Error con Tesseract: {str(e)}")
        print("\nSolución:")
        print("  1. Instala Tesseract OCR")
        print("  2. Agrega la ruta en tu archivo .env:")
        print("     TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

def verificar_poppler():
    """Verifica que Poppler esté instalado para conversión de PDFs"""
    print("\n" + "=" * 60)
    print("VERIFICANDO POPPLER (para PDFs)")
    print("=" * 60)
    
    try:
        from pdf2image import convert_from_path
        # Intentar con un PDF de prueba muy simple
        print("✓ pdf2image está instalado")
        
        # Verificar si poppler está en el PATH
        import subprocess
        try:
            result = subprocess.run(['pdftoppm', '-v'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            print("✓ Poppler está instalado y accesible")
        except FileNotFoundError:
            print("⚠ Poppler no está en el PATH del sistema")
            print("\nSolución:")
            print("  Windows: Descarga desde https://github.com/oschwartz10612/poppler-windows/releases/")
            print("  Linux: sudo apt-get install poppler-utils")
            print("  macOS: brew install poppler")
        except subprocess.TimeoutExpired:
            print("⚠ Timeout al verificar Poppler")
            
    except ImportError:
        print("✗ pdf2image no está instalado")
        print("  Instala con: pip install pdf2image")

def verificar_archivo_prueba(archivo):
    """Verifica un archivo específico"""
    print("\n" + "=" * 60)
    print(f"VERIFICANDO ARCHIVO: {archivo}")
    print("=" * 60)
    
    if not os.path.exists(archivo):
        print(f"✗ El archivo no existe: {archivo}")
        return
    
    print(f"✓ Archivo existe")
    
    # Verificar tamaño
    size = os.path.getsize(archivo)
    print(f"✓ Tamaño: {size:,} bytes ({size/1024:.2f} KB)")
    
    # Verificar permisos
    if os.access(archivo, os.R_OK):
        print("✓ Permisos de lectura: OK")
    else:
        print("✗ No se tienen permisos de lectura")
        return
    
    # Verificar extensión
    extension = Path(archivo).suffix.lower()
    print(f"✓ Extensión: {extension}")
    
    if extension == '.pdf':
        try:
            from pdf2image import convert_from_path
            print("\nIntentando convertir PDF...")
            images = convert_from_path(archivo, dpi=200, first_page=1, last_page=1)
            print(f"✓ PDF convertido: Primera página extraída")
            print(f"  Tamaño de imagen: {images[0].size}")
        except Exception as e:
            print(f"✗ Error al convertir PDF: {str(e)}")
    
    elif extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        try:
            import cv2
            img = cv2.imread(archivo)
            if img is not None:
                print(f"✓ Imagen cargada correctamente")
                print(f"  Dimensiones: {img.shape}")
            else:
                print(f"✗ No se pudo cargar la imagen")
        except Exception as e:
            print(f"✗ Error al cargar imagen: {str(e)}")

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "DIAGNÓSTICO DEL SISTEMA OCR" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Verificar dependencias
    verificar_dependencias()
    
    # Verificar Tesseract
    verificar_tesseract()
    
    # Verificar Poppler
    verificar_poppler()
    
    # Si se proporcionó un archivo, verificarlo
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        verificar_archivo_prueba(archivo)
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
