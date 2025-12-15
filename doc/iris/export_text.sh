#!/bin/bash
# =============================================================================
# IRIS Lore Web Export Script
# Exportuje textovou dokumentaci bez obrázků a vytvoří ZIP archiv
# =============================================================================

set -e

# Přejít do adresáře skriptu
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Najít verzi z index.html
VERSION=$(grep -oP 'IRIS \K[0-9]+\.[0-9]+' lore-web/index.html | head -1)
if [ -z "$VERSION" ]; then
    VERSION="4.1"
fi

# Název výstupního souboru
OUTPUT_NAME="Lore_export_Iris_${VERSION}"
OUTPUT_ZIP="${OUTPUT_NAME}.zip"
TEMP_DIR="/tmp/${OUTPUT_NAME}"

echo "=================================================="
echo "  IRIS Lore Web Export"
echo "  Verze: ${VERSION}"
echo "=================================================="

# Vyčistit dočasný adresář
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "[1/4] Kopíruji textové soubory..."

# Kopírovat vše kromě obrázků
rsync -av --exclude='*.png' \
          --exclude='*.jpg' \
          --exclude='*.jpeg' \
          --exclude='*.gif' \
          --exclude='*.svg' \
          --exclude='*.webp' \
          --exclude='*.ico' \
          --exclude='*.bmp' \
          --exclude='images/' \
          --exclude='*.zip' \
          lore-web/ "$TEMP_DIR/lore-web/"

echo "[2/4] Ověřuji strukturu..."

# Zobrazit co bylo zkopírováno
find "$TEMP_DIR" -type f | wc -l | xargs -I {} echo "   Zkopírováno {} souborů"

echo "[3/4] Vytvářím ZIP archiv..."

# Smazat starý archiv pokud existuje
rm -f "$OUTPUT_ZIP"

# Vytvořit ZIP
cd /tmp
zip -r "${SCRIPT_DIR}/${OUTPUT_ZIP}" "${OUTPUT_NAME}"

echo "[4/4] Čištění..."

# Vyčistit dočasný adresář
rm -rf "$TEMP_DIR"

echo "=================================================="
echo "✅ Export dokončen!"
echo "📦 Výstup: ${SCRIPT_DIR}/${OUTPUT_ZIP}"
echo "=================================================="

# Zobrazit velikost
ls -lh "${SCRIPT_DIR}/${OUTPUT_ZIP}"
