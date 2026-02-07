# Script para crear tarea programada - Watch Papers Daily
# Science Team - Dr. Adrian David González Chaves

$taskName = "Watch Papers Daily - Science Team"
$batPath = "C:\Users\arlex\Documents\Adrian David\scripts\utils\run_watch_papers.bat"
$workDir = "C:\Users\arlex\Documents\Adrian David"

# Crear acción
$action = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $workDir

# Crear trigger (diariamente a las 8:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "8:00AM"

# Configuración
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries

# Registrar tarea
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Convierte automaticamente PDFs nuevos a Markdown en la carpeta de Papers de Adrian David" -Force

Write-Host "`nTarea creada exitosamente!"
Get-ScheduledTask -TaskName $taskName | Format-List TaskName, State, Description
