
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "Ruta CEDIA Innovacion" -ForegroundColor Cyan
Write-Host "Buscando Python..." -ForegroundColor Yellow

$pythonCmd = $null

# 1) Comandos disponibles en PowerShell (incluye alias de Microsoft Store)
foreach ($name in @("python", "py", "python3")) {
    try {
        $cmd = Get-Command $name -ErrorAction Stop
        & $name --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $name
            break
        }
    } catch {}
}

# 2) Alias típico de Microsoft Store
if (-not $pythonCmd) {
    $storePython = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\python.exe"
    if (Test-Path $storePython) {
        try {
            & $storePython --version *> $null
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = $storePython
            }
        } catch {}
    }
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "Python esta instalado, pero Windows no lo esta exponiendo a la terminal." -ForegroundColor Red
    Write-Host ""
    Write-Host "Haz esta prueba manual:" -ForegroundColor Yellow
    Write-Host "1. Abre PowerShell NUEVO."
    Write-Host "2. Escribe: python --version"
    Write-Host ""
    Write-Host "Si sale Python 3.12.x, reinicia Windows y vuelve a ejecutar este archivo."
    Write-Host "Si NO sale, activa el alias en:"
    Write-Host "Configuracion > Aplicaciones > Configuracion avanzada de aplicaciones > Alias de ejecucion de aplicaciones"
    Write-Host "y activa python.exe / python3.exe."
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

Write-Host "Python detectado con: $pythonCmd" -ForegroundColor Green
& $pythonCmd --version

if (-not (Test-Path ".venv")) {
    Write-Host ""
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    & $pythonCmd -m venv .venv
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "No se pudo crear el entorno virtual."
}

Write-Host ""
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host ""
Write-Host "Iniciando Ruta CEDIA Innovacion..." -ForegroundColor Green
& $venvPython -m streamlit run app.py
