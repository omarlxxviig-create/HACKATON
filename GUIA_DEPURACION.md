# Guía de Depuración del Proyecto

Esta guía te ayudará a depurar y probar el proyecto de manera efectiva.

## Configuración de VS Code

El proyecto incluye archivos de configuración para VS Code en la carpeta `.vscode/`:

- `launch.json`: Configuraciones de depuración
- `settings.json`: Configuración del editor y Python
- `tasks.json`: Tareas automatizadas
- `extensions.json`: Extensiones recomendadas

### Instalar Extensiones Recomendadas

1. Abre VS Code
2. Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac)
3. Escribe "Extensions: Show Recommended Extensions"
4. Haz clic en "Install All"

## Modos de Depuración

### 1. Iniciar Sistema Completo

Ejecuta el sistema completo con todas sus funcionalidades:

- Presiona `F5` o ve a "Run and Debug" (Ctrl+Shift+D)
- Selecciona "Iniciar Sistema Completo"
- El servidor iniciará en `http://localhost:8000`

### 2. Depurar con Puerto Personalizado

Si el puerto 8000 está ocupado:

- Selecciona "Iniciar con Puerto Personalizado"
- El servidor iniciará en `http://localhost:5000`

### 3. Depurar solo la API

Para depurar específicamente la API:

- Selecciona "Depurar API (FastAPI)"
- Incluye recarga automática al modificar archivos

### 4. Probar Módulos Individuales

#### Probar OCR:

```bash
python test_ocr.py ruta/a/documento.pdf
```

o

```bash
python test_ocr.py ruta/a/imagen.jpg
```

#### Probar NLP:

```bash
python test_nlp.py "Texto a analizar"
```

## Puntos de Interrupción (Breakpoints)

Para agregar un breakpoint:

1. Haz clic en el margen izquierdo del editor (junto al número de línea)
2. Aparecerá un punto rojo
3. Cuando el código llegue a esa línea, se pausará

### Lugares Útiles para Breakpoints

- `endpoints.py`, línea del `@router.post`: Para ver las solicitudes entrantes
- `extractor.py`, función `extract_from_image`: Para depurar OCR
- `keyword_extraction.py`, función `extract_keywords`: Para depurar palabras clave

## Tareas Automatizadas

Presiona `Ctrl+Shift+P` y escribe "Tasks: Run Task" para ejecutar:

### Instalar Dependencias

Instala o actualiza todos los paquetes necesarios

### Iniciar Servidor

Inicia el servidor sin depuración

### Ejecutar Tests

Ejecuta todas las pruebas unitarias

### Limpiar Caché

Elimina archivos `__pycache__` antiguos

### Formatear Código (Black)

Formatea automáticamente el código según estándares

### Verificar Estilo (Flake8)

Verifica que el código siga las convenciones de estilo

### Ver Logs

Muestra los registros (logs) del sistema

## Atajos de Teclado Útiles

- `F5`: Iniciar depuración
- `F10`: Ejecutar siguiente línea (Step Over)
- `F11`: Entrar en función (Step Into)
- `Shift+F11`: Salir de función (Step Out)
- `Shift+F5`: Detener depuración
- `Ctrl+Shift+F5`: Reiniciar depuración

## Inspeccionar Variables

Cuando el código está pausado en un breakpoint:

1. **Panel Variables**: Muestra todas las variables locales y globales
2. **Panel Watch**: Agrega expresiones para monitorear
3. **Debug Console**: Escribe código Python para evaluar

Ejemplo en Debug Console:

```python
# Ver el valor de una variable
print(texto_extraido)

# Ejecutar código
len(palabras_clave)

# Llamar funciones
extractor_texto.languages
```

## Depurar Problemas Comunes

### Error: "No se puede conectar al puerto"

El puerto está ocupado. Soluciones:

1. Usa la configuración "Iniciar con Puerto Personalizado"
2. O cierra la aplicación que usa el puerto:
   ```bash
   netstat -ano | findstr :8000
   taskkill /PID <número_de_proceso> /F
   ```

### Error: "Module not found"

El entorno virtual no está activado:

1. Abre terminal integrada (Ctrl+`)
2. Verifica que veas `(venv)` al inicio
3. Si no, activa manualmente:
   ```bash
   venv\Scripts\activate
   ```

### Error en OCR: "TesseractNotFoundError"

Tesseract no está instalado o no se encuentra:

1. Verifica instalación: `tesseract --version`
2. Si no está instalado, revisa `GUIA_INSTALACION.md`
3. Actualiza la ruta en `.env`

### Logs no aparecen

El archivo de log no existe:

1. Crea el directorio: `mkdir logs`
2. O ejecuta el sistema una vez para que se cree automáticamente

## Probar la API con la Interfaz Web

1. Inicia el servidor (F5)
2. Abre tu navegador
3. Ve a: `http://localhost:8000/docs`
4. Verás la interfaz Swagger UI
5. Puedes probar todos los endpoints desde ahí

### Ejemplo de Prueba:

1. En `/docs`, busca `POST /api/v1/procesar-documento`
2. Haz clic en "Try it out"
3. Sube un archivo
4. Selecciona opciones
5. Haz clic en "Execute"
6. Verás la respuesta con el ID de trabajo
7. Usa ese ID en `GET /api/v1/trabajos/{id_trabajo}` para ver resultados

## Consejos para Depuración Efectiva

1. **Usa logs abundantemente**: Agrega `logger.info()` y `logger.debug()` para seguir el flujo
2. **Prueba componentes aislados**: Usa `test_ocr.py` y `test_nlp.py` antes de probar todo junto
3. **Verifica datos intermedios**: Coloca breakpoints para ver qué datos se están procesando
4. **Revisa los logs**: El archivo `logs/app.log` contiene información detallada de errores
5. **Usa la consola de depuración**: Evalúa expresiones en tiempo real

## Recursos Adicionales

- Documentación de FastAPI: https://fastapi.tiangolo.com/
- Documentación de Tesseract: https://tesseract-ocr.github.io/
- Documentación de spaCy: https://spacy.io/
