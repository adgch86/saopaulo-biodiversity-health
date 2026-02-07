@echo off
REM =====================================================
REM SYNC TO DRIVE - Doble clic para sincronizar
REM =====================================================
echo.
echo Sincronizando con Google Drive...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0sync_to_drive.ps1"

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
