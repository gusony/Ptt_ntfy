#!/bin/bash
# PTT 爬蟲通知程式 - Linux/macOS 安裝腳本

set -e

echo "=============================================="
echo "  PTT 爬蟲通知程式 - 安裝腳本"
echo "=============================================="

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/4] 檢查 Python..."

# 檢查 Python 版本
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[X] 找不到 Python，請先安裝 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python 版本: $PYTHON_VERSION"

# 檢查版本是否 >= 3.8
MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    echo "[X] Python 版本需要 3.8 以上"
    exit 1
fi

echo ""
echo "[2/4] 建立虛擬環境..."

cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "[OK] 虛擬環境已建立"
else
    echo "[OK] 虛擬環境已存在"
fi

# 啟動虛擬環境
source venv/bin/activate

echo ""
echo "[3/4] 安裝依賴套件..."
pip install --upgrade pip
pip install -r requirements.txt
echo "[OK] 依賴套件安裝完成"

echo ""
echo "[4/4] 檢查環境..."
$PYTHON_CMD check_env.py

echo ""
echo "=============================================="
echo "  安裝完成！"
echo "=============================================="
echo ""
echo "下一步："
echo "  1. 設定 Telegram Bot Token (編輯 config.py)"
echo "  2. 執行環境檢查: python check_env.py"
echo "  3. 啟動程式: python main.py"
echo ""
