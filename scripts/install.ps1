# PTT 爬蟲通知程式 - Windows 安裝腳本 (PowerShell)

Write-Host "=============================================="
Write-Host "  PTT 爬蟲通知程式 - 安裝腳本"
Write-Host "=============================================="

# 取得腳本所在目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host ""
Write-Host "[1/4] 檢查 Python..."

# 檢查 Python
$PythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} else {
    Write-Host "[X] 找不到 Python，請先安裝 Python 3.8+"
    exit 1
}

$PythonVersion = & $PythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "[OK] Python 版本: $PythonVersion"

# 檢查版本
$Major = & $PythonCmd -c "import sys; print(sys.version_info.major)"
$Minor = & $PythonCmd -c "import sys; print(sys.version_info.minor)"

if ([int]$Major -lt 3 -or ([int]$Major -eq 3 -and [int]$Minor -lt 8)) {
    Write-Host "[X] Python 版本需要 3.8 以上"
    exit 1
}

Write-Host ""
Write-Host "[2/4] 建立虛擬環境..."

Set-Location $ProjectDir

if (-not (Test-Path "venv")) {
    & $PythonCmd -m venv venv
    Write-Host "[OK] 虛擬環境已建立"
} else {
    Write-Host "[OK] 虛擬環境已存在"
}

# 啟動虛擬環境
& "$ProjectDir\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "[3/4] 安裝依賴套件..."
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "[OK] 依賴套件安裝完成"

Write-Host ""
Write-Host "[4/4] 檢查環境..."
& $PythonCmd check_env.py

Write-Host ""
Write-Host "=============================================="
Write-Host "  安裝完成！"
Write-Host "=============================================="
Write-Host ""
Write-Host "下一步："
Write-Host "  1. 設定 Telegram Bot Token (編輯 config.py)"
Write-Host "  2. 執行環境檢查: python check_env.py"
Write-Host "  3. 啟動程式: python main.py"
Write-Host ""
