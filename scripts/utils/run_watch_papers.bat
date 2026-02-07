@echo off
REM =============================================================================
REM Watch Papers Daily - Ejecutar conversión automática
REM Science Team - Dr. Adrian David González Chaves
REM =============================================================================

cd /d "C:\Users\arlex\Documents\Adrian David"
python scripts\watch_papers_daily.py

REM Mantener ventana abierta si hay error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Ocurrió un error. Presiona cualquier tecla para cerrar.
    pause > nul
)
