@echo off
echo ========================================
echo Instalacion Simple OCR
echo ========================================
echo.

echo Actualizando pip...
python -m pip install --upgrade pip
echo.

echo Instalando dependencias...
pip install -r requirements.txt
echo.

echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Para iniciar el servidor ejecuta:
echo   python main.py
echo.
pause