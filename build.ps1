# Build script for the Aggregated Box Costing standalone .exe.
#
# Prerequisites on the build machine (NOT on end-user machines):
#   - Python 3.12 with pip
#   - Node.js 18+ with npm
#   - Two environment variables set (User-scope is fine):
#       CONFIG_REPO_RAW_URL  e.g. https://api.github.com/repos/AmarBox/Calculators/contents/config/app_config.json?ref=main
#       CONFIG_REPO_PAT      fine-grained read-only PAT for the config repo
#
# Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File build.ps1
#
# Output: backend\dist\AggregatedBoxCosting.exe (single self-contained .exe)

$ErrorActionPreference = "Stop"

$RepoRoot   = $PSScriptRoot
$Backend    = Join-Path $RepoRoot "backend"
$Frontend   = Join-Path $RepoRoot "frontend"
$DistDir    = Join-Path $Backend "dist"
$SecretsPy  = Join-Path $Backend "calculator\_build_secrets.py"

function Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }

# 1. Validate build env vars
Step "Checking build-time secrets"
if (-not $env:CONFIG_REPO_RAW_URL) { throw "CONFIG_REPO_RAW_URL is not set" }
if (-not $env:CONFIG_REPO_PAT)     { throw "CONFIG_REPO_PAT is not set" }
Write-Host "  CONFIG_REPO_RAW_URL = $env:CONFIG_REPO_RAW_URL"
Write-Host "  CONFIG_REPO_PAT     = (length $($env:CONFIG_REPO_PAT.Length))"

# 2. Build the React app
Step "Building frontend (npm run build)"
Push-Location $Frontend
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "  installing npm deps..."
        npm install
    }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
} finally {
    Pop-Location
}

# 3. Install Python build deps
Step "Installing Python build deps"
Push-Location $Backend
try {
    python -m pip install --quiet --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
    python -m pip install --quiet -r requirements.txt pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "pip install of requirements + pyinstaller failed" }
    # Sanity check: PyInstaller importable in this Python environment
    python -c "import PyInstaller, sys; print('  PyInstaller', PyInstaller.__version__, 'on Python', sys.version.split()[0])"
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller installed but not importable" }
} finally {
    Pop-Location
}

# 4-6. Generate secrets, run PyInstaller, ALWAYS clean up secrets afterward.
try {
    Step "Writing _build_secrets.py (gitignored, deleted after build)"
    $secretsContent = @"
# AUTO-GENERATED at build time by build.ps1. Do not commit.
CONFIG_REPO_RAW_URL = "$($env:CONFIG_REPO_RAW_URL)"
CONFIG_REPO_PAT = "$($env:CONFIG_REPO_PAT)"
"@
    Set-Content -Path $SecretsPy -Value $secretsContent -Encoding UTF8

    Step "Running PyInstaller"
    Push-Location $Backend
    try {
        if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
        if (Test-Path "build")  { Remove-Item "build" -Recurse -Force }
        if (Test-Path "AggregatedBoxCosting.spec") { Remove-Item "AggregatedBoxCosting.spec" -Force }

        python -m PyInstaller `
            --onefile `
            --windowed `
            --name "AggregatedBoxCosting" `
            --icon "app_icon.ico" `
            --add-data "..\frontend\dist;frontend\dist" `
            --add-data "calculator\app_config.default.json;calculator" `
            --add-data "app_icon.ico;." `
            --collect-data "pint" `
            --hidden-import "pint" `
            --hidden-import "openpyxl" `
            --hidden-import "pystray._win32" `
            --hidden-import "PIL.Image" `
            launcher.py

        if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
    } finally {
        Pop-Location
    }
} finally {
    if (Test-Path $SecretsPy) {
        Remove-Item $SecretsPy -Force
        Write-Host "  cleaned up _build_secrets.py" -ForegroundColor DarkGray
    }
}

# 7. Done
$ExePath = Join-Path $DistDir "AggregatedBoxCosting.exe"
if (Test-Path $ExePath) {
    $sizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
    Write-Host "`nBuild complete: $ExePath ($sizeMB MB)" -ForegroundColor Green
} else {
    throw "Build did not produce an .exe"
}
