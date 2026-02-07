# =============================================================
# SYNC TO GOOGLE DRIVE - Adrian David Project
# Mirror completo: Local -> Drive (misma estructura)
# Excluye: .git, .claude, data/ (datasets pesados), __pycache__
# =============================================================

$ErrorActionPreference = "Continue"

# --- CONFIGURACION ---
$LOCAL_BASE = "C:\Users\arlex\Documents\Adrian David"
$DRIVE_BASE = "G:\My Drive\Adrian David"

# Carpetas a EXCLUIR del sync (no van al Drive)
$EXCLUDE_DIRS = @(".git", ".claude", "data", "__pycache__", "node_modules", ".venv", "logs", ".next")

# --- FUNCIONES ---
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $Message" -ForegroundColor $Color
}

# --- MAIN ---
Write-Host ""
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "  SINCRONIZACION: Adrian David -> Google Drive" -ForegroundColor Magenta
Write-Host "  Local:  $LOCAL_BASE" -ForegroundColor DarkGray
Write-Host "  Drive:  $DRIVE_BASE" -ForegroundColor DarkGray
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host ""

# Verificar Drive montado
if (-not (Test-Path "G:\My Drive")) {
    Write-Log "ERROR: Google Drive no montado en G:\" "Red"
    exit 1
}

$startTime = Get-Date

# Robocopy: copiar todo sin borrar archivos de Adrian en Drive
Write-Log "Sincronizando carpetas locales al Drive..." "Cyan"
$robocopyArgs = @(
    $LOCAL_BASE,
    $DRIVE_BASE,
    "/E",         # Copiar subdirectorios (incluidos vacios)
    "/XO",        # No sobreescribir si destino es mas nuevo
    "/R:1",       # Reintentar 1 vez
    "/W:1",       # Esperar 1 segundo entre reintentos
    "/NP",        # Sin progreso
    "/NDL",       # Sin listado de directorios
    "/XF", "desktop.ini", "Thumbs.db", ".gitignore", ".gitattributes",
    "/XD"         # Excluir directorios (nombres matchean en cualquier nivel)
) + $EXCLUDE_DIRS

Write-Log "Exclusiones: $($EXCLUDE_DIRS -join ', ')" "DarkGray"

$output = & robocopy @robocopyArgs
$exitCode = $LASTEXITCODE

# Robocopy exit codes: 0-7 = success, 8+ = error
if ($exitCode -lt 8) {
    # Contar archivos copiados del output
    $copied = ($output | Select-String "^\s*(Files|Archivos)\s*:" | Out-String).Trim()
    $dirs = ($output | Select-String "^\s*(Dirs|Dirs\.)\s*:" | Out-String).Trim()

    Write-Log "OK (codigo: $exitCode)" "Green"

    # Mostrar resumen de robocopy
    $summaryLines = $output | Select-String "^\s+(Total|Copied|Copiado|Skipped|Omitido|Mismatch|FAILED|Extras)"
    # Mostrar las ultimas lineas del resumen
    $output | Select-Object -Last 12 | ForEach-Object {
        if ($_ -match '\S') {
            Write-Host "  $_" -ForegroundColor DarkGray
        }
    }
} else {
    Write-Log "ERROR en robocopy (codigo: $exitCode)" "Red"
    $output | Select-Object -Last 15 | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
}

$endTime = Get-Date
$dur = [math]::Round(($endTime - $startTime).TotalSeconds, 1)

Write-Host ""
Write-Host "======================================================" -ForegroundColor Magenta
Write-Log "COMPLETADO en $dur segundos" "Green"
Write-Host "======================================================" -ForegroundColor Magenta

# Log file
$logDir = "$LOCAL_BASE\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$logPath = "$logDir\sync_drive.log"
$status = if ($exitCode -lt 8) { "OK" } else { "ERR" }
$logLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $status (code:$exitCode) | ${dur}s"
Add-Content -Path $logPath -Value $logLine -ErrorAction SilentlyContinue
