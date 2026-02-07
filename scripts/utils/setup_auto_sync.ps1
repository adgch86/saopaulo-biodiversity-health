# =============================================================
# SETUP AUTO SYNC - Configura sincronización automática
# =============================================================
# Ejecutar como Administrador para crear la tarea programada.
#
# Opciones de frecuencia:
#   1. Cada hora (recomendado para desarrollo activo)
#   2. Cada 4 horas
#   3. Una vez al día (9 AM)
#
# Autor: AP Digital
# =============================================================

$ErrorActionPreference = "Stop"

# --- CONFIGURACIÓN ---
$TASK_NAME = "SyncAdrianDavidToDrive"
$SCRIPT_PATH = "C:\Users\arlex\Documents\Adrian David\scripts\sync_to_drive.ps1"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR SINCRONIZACIÓN AUTOMÁTICA" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si ya existe la tarea
$existingTask = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "La tarea '$TASK_NAME' ya existe." -ForegroundColor Yellow
    $response = Read-Host "¿Deseas reemplazarla? (S/N)"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "Cancelado." -ForegroundColor Red
        exit
    }
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Host "Tarea anterior eliminada." -ForegroundColor Yellow
}

# Seleccionar frecuencia
Write-Host ""
Write-Host "Selecciona la frecuencia de sincronización:" -ForegroundColor White
Write-Host "  1. Cada hora (recomendado)" -ForegroundColor Green
Write-Host "  2. Cada 4 horas"
Write-Host "  3. Una vez al día (9:00 AM)"
Write-Host "  4. Solo manual (no crear tarea)"
Write-Host ""
$choice = Read-Host "Opción (1-4)"

switch ($choice) {
    "1" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
        $frequency = "cada hora"
    }
    "2" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4)
        $frequency = "cada 4 horas"
    }
    "3" {
        $trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
        $frequency = "diariamente a las 9 AM"
    }
    "4" {
        Write-Host ""
        Write-Host "No se creará tarea automática." -ForegroundColor Yellow
        Write-Host "Puedes ejecutar manualmente: scripts\sync_to_drive.bat" -ForegroundColor White
        exit
    }
    default {
        Write-Host "Opción inválida. Usando frecuencia por defecto (cada hora)." -ForegroundColor Yellow
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
        $frequency = "cada hora"
    }
}

# Crear la acción
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$SCRIPT_PATH`""

# Configuración de la tarea
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Registrar la tarea
try {
    Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Settings $settings -Description "Sincroniza outputs del proyecto Adrian David con Google Drive" -RunLevel Limited

    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "  TAREA CREADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Nombre: $TASK_NAME" -ForegroundColor White
    Write-Host "  Frecuencia: $frequency" -ForegroundColor White
    Write-Host "  Script: $SCRIPT_PATH" -ForegroundColor White
    Write-Host ""
    Write-Host "  Para modificar: Task Scheduler > $TASK_NAME" -ForegroundColor Gray
    Write-Host "  Para desactivar: Disable-ScheduledTask -TaskName '$TASK_NAME'" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: No se pudo crear la tarea." -ForegroundColor Red
    Write-Host "Intenta ejecutar PowerShell como Administrador." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
}
