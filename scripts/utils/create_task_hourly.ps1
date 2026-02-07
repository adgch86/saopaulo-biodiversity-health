$taskName = "SyncAdrianDavidToDrive"
$scriptPath = "C:\Users\arlex\Documents\Adrian David\scripts\sync_to_drive.ps1"

# Eliminar tarea existente si hay
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Crear trigger: cada hora
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

# Crear accion
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

# Configuracion
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar tarea
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Sincroniza proyecto Adrian David con Google Drive cada hora"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  TAREA PROGRAMADA CREADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Nombre: $taskName"
Write-Host "  Frecuencia: Cada hora"
Write-Host "  Script: $scriptPath"
Write-Host ""
Write-Host "  La sincronizacion se ejecutara automaticamente."
Write-Host "  Para ver/modificar: Task Scheduler > $taskName"
Write-Host ""
